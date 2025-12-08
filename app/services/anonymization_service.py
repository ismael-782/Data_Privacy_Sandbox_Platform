"""Coordinator for running privacy algorithms and computing metrics."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Iterable

import pandas as pd
from anonymity_api import utility

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
        original_df = df.copy()
        anonymized = df.copy()
        metrics: Dict[str, float] = {}
        
        # Check if this is a DP query (handled differently)
        is_dp_query = "differential-privacy" in algorithm_keys
        
        for key in algorithm_keys:
            algorithm = self.registry.get(key)
            if not algorithm:
                raise ValueError(f"Unknown algorithm '{key}' selected.")
            anonymized = algorithm.run(anonymized, params)
            metrics[f"{key}_rows"] = len(anonymized)

        # For DP queries, the result is a query result table, not anonymized data
        # So skip the anonymization metrics
        if is_dp_query:
            return AnonymizationResult(
                original_rows=len(original_df),
                anonymized_rows=len(anonymized),
                dataframe=anonymized,
                metrics={"is_dp_query": 1.0},  # Flag for UI
            )

        # Calculate utility metrics for anonymization algorithms
        if params.quasi_identifiers:
            try:
                # Average Equivalence Class Size - closer to 1 is better
                aecs = utility.average_equivalence_class_size(
                    original_df, anonymized, params.quasi_identifiers
                )
                metrics["avg_equivalence_class_size"] = float(aecs)
                
                # Discernibility Metric - lower is better utility  
                dm = utility.discernibility_metric(anonymized, params.quasi_identifiers)
                metrics["discernibility_metric"] = float(dm)
                
                # Global Certainty Penalty - 0 = no info loss, 1 = total info loss
                gcp = utility.global_certainty_penalty(
                    original_df, anonymized, params.quasi_identifiers
                )
                metrics["global_certainty_penalty"] = float(gcp)
            except Exception:
                # Metrics may fail if columns were modified significantly
                pass
        
        return AnonymizationResult(
            original_rows=len(original_df),
            anonymized_rows=len(anonymized),
            dataframe=anonymized,
            metrics=metrics,
        )
