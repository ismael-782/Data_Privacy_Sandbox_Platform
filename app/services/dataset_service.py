"""Services for loading and validating datasets."""

from __future__ import annotations

from pathlib import Path
from typing import Literal

import pandas as pd

from app.core.config import settings
from app.privacy.validators.dataset_validator import (
    DatasetValidationResult,
    validate_roles,
    validate_structure,
)

SUPPORTED_EXTENSIONS = {".csv", ".tsv", ".xlsx"}


class DatasetService:
    """High-level service for ingesting datasets."""

    def __init__(self, upload_dir: Path | None = None) -> None:
        self.upload_dir = Path(upload_dir or settings.data.upload_dir)
        self.upload_dir.mkdir(parents=True, exist_ok=True)

    def load(self, file_path: Path) -> pd.DataFrame:
        if not file_path.exists():
            raise FileNotFoundError(file_path)
        if file_path.suffix.lower() not in SUPPORTED_EXTENSIONS:
            raise ValueError(f"Unsupported file extension: {file_path.suffix}")

        if file_path.stat().st_size > settings.app.max_file_size_mb * 1024 * 1024:
            raise ValueError("File exceeds maximum allowed size.")

        if file_path.suffix.lower() == ".xlsx":
            df = pd.read_excel(file_path)
        else:
            sep = "," if file_path.suffix.lower() == ".csv" else "\t"
            df = pd.read_csv(file_path, sep=sep)
        return df

    def validate_dataset(self, df: pd.DataFrame) -> DatasetValidationResult:
        return validate_structure(df)

    def validate_roles(
        self,
        df: pd.DataFrame,
        quasi_identifiers: list[str],
        sensitive_attributes: list[str],
        identifiers: list[str] | None = None,
    ) -> DatasetValidationResult:
        return validate_roles(df, quasi_identifiers, sensitive_attributes, identifiers)

