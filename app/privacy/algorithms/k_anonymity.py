"""Simplified k-anonymity implementation."""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np
import pandas as pd

from .base import AlgorithmParams, PrivacyAlgorithm


@dataclass
class KAnonymity(PrivacyAlgorithm):
    name: str = "k-anonymity"

    def run(self, df: pd.DataFrame, params: AlgorithmParams) -> pd.DataFrame:
        if not params.quasi_identifiers:
            raise ValueError("k-anonymity requires at least one quasi-identifier.")
        k = params.k or 5

        anonymised = df.copy()
        for column in params.quasi_identifiers:
            series = anonymised[column]
            if pd.api.types.is_numeric_dtype(series):
                anonymised[column] = _generalise_numeric(series, k)
            else:
                anonymised[column] = _generalise_categorical(series, k)

        return anonymised


def _generalise_numeric(series: pd.Series, k: int) -> pd.Series:
    """Coarse numeric generalisation using quantile binning."""
    non_null = series.dropna()
    if non_null.empty:
        return series
    bins = max(1, len(non_null) // k)
    try:
        labels = pd.qcut(non_null, q=min(10, bins), duplicates="drop")
    except ValueError:
        labels = pd.cut(non_null, bins=bins)
    categorical = labels.astype(str)
    return categorical.reindex(series.index).fillna("missing")


def _generalise_categorical(series: pd.Series, k: int) -> pd.Series:
    """Generalise categorical data by suppressing rare categories."""
    value_counts = series.value_counts(dropna=False)
    rare_values = value_counts[value_counts < k].index
    generalised = series.astype(str)
    generalised = generalised.where(~series.isin(rare_values), other="*")
    generalised = generalised.fillna("missing")
    return generalised

