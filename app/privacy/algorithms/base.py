"""Base interfaces for privacy algorithms."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol

import pandas as pd


@dataclass
class AlgorithmParams:
    quasi_identifiers: list[str]
    sensitive_attributes: list[str]
    identifiers: list[str] | None = None  # Columns to drop during anonymization
    k: int | None = None
    l: int | None = None
    t: float | None = None
    epsilon: float | None = None
    query_type: str | None = None  # "Mean" or "Sum" for DP
    target_column: str | None = None  # Column for DP query


class PrivacyAlgorithm(Protocol):
    name: str

    def run(self, df: pd.DataFrame, params: AlgorithmParams) -> pd.DataFrame:
        ...

