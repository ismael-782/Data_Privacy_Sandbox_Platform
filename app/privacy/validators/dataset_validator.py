"""Dataset validation logic before running privacy algorithms."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, Iterable, List, Sequence

import numpy as np
import pandas as pd

from app.core.config import settings


class ColumnSemantic(Enum):
    NUMERIC = "numeric"
    CATEGORICAL = "categorical"
    DATETIME = "datetime"
    BOOLEAN = "boolean"
    MIXED = "mixed"


class ColumnRole(Enum):
    QI = "quasi_identifier"
    SA = "sensitive_attribute"
    IDENTIFIER = "identifier"
    IGNORE = "ignore"


@dataclass
class ColumnSummary:
    name: str
    pandas_dtype: str
    semantic_type: ColumnSemantic
    unique_values: int
    uniqueness_ratio: float
    has_missing: bool
    is_constant: bool
    example_values: list[str] = field(default_factory=list)


@dataclass
class DatasetValidationResult:
    errors: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    column_summaries: list[ColumnSummary] | None = None

    @property
    def is_valid(self) -> bool:
        return not self.errors


def infer_semantic_type(series: pd.Series) -> ColumnSemantic:
    dtype = str(series.dtype)
    if pd.api.types.is_bool_dtype(series):
        return ColumnSemantic.BOOLEAN
    if pd.api.types.is_numeric_dtype(series):
        return ColumnSemantic.NUMERIC
    if pd.api.types.is_datetime64_any_dtype(series):
        return ColumnSemantic.DATETIME
    if pd.api.types.is_categorical_dtype(series):
        return ColumnSemantic.CATEGORICAL

    # Attempt datetime parsing for object columns
    sample = series.dropna().head(5)
    try:
        pd.to_datetime(sample, errors="raise")
        return ColumnSemantic.DATETIME
    except (ValueError, TypeError):
        pass

    if series.dropna().nunique() > 0.8 * len(series):
        return ColumnSemantic.MIXED
    return ColumnSemantic.CATEGORICAL


def summarize_columns(df: pd.DataFrame) -> list[ColumnSummary]:
    summaries: list[ColumnSummary] = []
    record_count = len(df)
    for column in df.columns:
        series = df[column]
        semantic = infer_semantic_type(series)
        unique_values = series.nunique(dropna=True)
        uniqueness_ratio = unique_values / record_count if record_count else 0
        example_values = [str(val) for val in series.dropna().unique()[:3]]
        summaries.append(
            ColumnSummary(
                name=column,
                pandas_dtype=str(series.dtype),
                semantic_type=semantic,
                unique_values=unique_values,
                uniqueness_ratio=round(uniqueness_ratio, 3),
                has_missing=series.isna().any(),
                is_constant=unique_values <= 1,
                example_values=example_values,
            )
        )
    return summaries


def validate_structure(df: pd.DataFrame) -> DatasetValidationResult:
    """Validate dataset before any user role selection."""
    result = DatasetValidationResult(column_summaries=summarize_columns(df))
    if df.empty:
        result.errors.append("Dataset is empty.")
        return result

    if len(df) < settings.data.min_rows:
        result.errors.append(
            f"Dataset must contain at least {settings.data.min_rows} rows (found {len(df)})."
        )

    if df.columns.duplicated().any():
        result.errors.append("Duplicate column names detected; please rename before upload.")

    cleaned_columns = df.columns.str.replace(r"[^0-9a-zA-Z_]", "_", regex=True)
    if not cleaned_columns.equals(df.columns):
        result.warnings.append("Column names were sanitized to remove illegal characters.")

    for summary in result.column_summaries or []:
        if summary.uniqueness_ratio > 0.95:
            result.warnings.append(
                f"Column '{summary.name}' appears to be an identifier (uniqueness ratio "
                f"{summary.uniqueness_ratio:.2f}). Consider excluding it or marking as identifier."
            )
        if summary.semantic_type == ColumnSemantic.CATEGORICAL and summary.unique_values > 1000:
            result.warnings.append(
                f"Column '{summary.name}' has high cardinality ({summary.unique_values} unique). "
                "Generalisation may be difficult."
            )
        if summary.is_constant:
            result.warnings.append(
                f"Column '{summary.name}' is constant; this limits its usefulness for privacy metrics."
            )

    return result


def validate_roles(
    df: pd.DataFrame,
    quasi_identifiers: Sequence[str],
    sensitive_attributes: Sequence[str],
    identifiers: Sequence[str] | None = None,
) -> DatasetValidationResult:
    """Validate user-selected dataset roles for privacy algorithms."""
    result = DatasetValidationResult()

    identifiers = identifiers or []
    missing_qi = [col for col in quasi_identifiers if col not in df.columns]
    missing_sa = [col for col in sensitive_attributes if col not in df.columns]
    missing_id = [col for col in identifiers if col not in df.columns]
    if missing_qi:
        result.errors.append(f"Unknown QI columns: {missing_qi}")
    if missing_sa:
        result.errors.append(f"Unknown sensitive attribute columns: {missing_sa}")
    if missing_id:
        result.errors.append(f"Unknown identifier columns: {missing_id}")
    if result.errors:
        return result

    if not quasi_identifiers:
        result.errors.append("At least one quasi-identifier must be selected.")
    if not sensitive_attributes:
        result.warnings.append("No sensitive attributes selected; diversity metrics disabled.")

    subset = df[list(set(quasi_identifiers))]
    missing_qi_rows = subset.isna().any(axis=1).sum()
    if missing_qi_rows:
        result.errors.append(
            f"Found {missing_qi_rows} rows with missing values in selected QI columns."
            " Choose a strategy (drop, impute, or treat missing as category) before continuing."
        )

    for column in quasi_identifiers:
        unique_ratio = df[column].nunique(dropna=True) / len(df)
        if unique_ratio > 0.9:
            result.warnings.append(
                f"QI '{column}' is highly unique ({unique_ratio:.2f}); consider reclassifying as identifier."
            )

    for column in sensitive_attributes:
        unique_values = df[column].nunique(dropna=True)
        if unique_values < 2:
            result.errors.append(f"Sensitive attribute '{column}' must contain at least two values.")

    overlap = set(quasi_identifiers).intersection(sensitive_attributes)
    if overlap:
        result.errors.append(f"Columns cannot be both QI and SA: {', '.join(overlap)}")

    if identifiers:
        overlap_id = set(quasi_identifiers).intersection(identifiers)
        if overlap_id:
            result.errors.append(
                f"Identifiers cannot also be QI: {', '.join(overlap_id)}"
            )

    return result

