"""Coordinator for running privacy algorithms and computing metrics."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Iterable

import pandas as pd

from app.privacy.algorithms.base import AlgorithmParams
from app.privacy.algorithms.differential_privacy import DifferentialPrivacy
from app.privacy.algorithms.k_anonymity import KAnonymity
from app.privacy.algorithms.l_diversity import LDiversity
from app.privacy.algorithms.t_closeness import TCloseness


@dataclass
class AnonymizationResult:
    original_rows: int
    anonymized_rows: int
    dataframe: pd.DataFrame
    metrics: Dict[str, float]


class AnonymizationService:
    """Compose privacy algorithms based on user selection."""

    def __init__(self) -> None:
        self.registry = {
            "k-anonymity": KAnonymity(),
            "l-diversity": LDiversity(),
            "t-closeness": TCloseness(),
            "differential-privacy": DifferentialPrivacy(),
        }

    def available_algorithms(self) -> list[str]:
        return list(self.registry.keys())

    def run_pipeline(
        self,
        df: pd.DataFrame,
        algorithm_keys: Iterable[str],
        params: AlgorithmParams,
    ) -> AnonymizationResult:
        anonymized = df.copy()
        metrics: Dict[str, float] = {}
        for key in algorithm_keys:
            algorithm = self.registry.get(key)
            if not algorithm:
                raise ValueError(f"Unknown algorithm '{key}' selected.")
            anonymized = algorithm.run(anonymized, params)
            metrics[f"{key}_rows"] = len(anonymized)

        metrics["suppression_ratio"] = 1 - (len(anonymized) / len(df))
        return AnonymizationResult(
            original_rows=len(df),
            anonymized_rows=len(anonymized),
            dataframe=anonymized,
            metrics=metrics,
        )

