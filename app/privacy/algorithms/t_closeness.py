"""Placeholder t-closeness implementation."""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np
import pandas as pd

from .base import AlgorithmParams, PrivacyAlgorithm


@dataclass
class TCloseness(PrivacyAlgorithm):
    name: str = "t-closeness"

    def run(self, df: pd.DataFrame, params: AlgorithmParams) -> pd.DataFrame:
        if not params.quasi_identifiers or not params.sensitive_attributes:
            raise ValueError("t-closeness requires QI and sensitive attributes.")

        t = params.t or 0.2
        grouped = df.groupby(params.quasi_identifiers, dropna=False)
        global_distributions = {
            column: df[column].value_counts(normalize=True) for column in params.sensitive_attributes
        }

        for _, group in grouped:
            for column in params.sensitive_attributes:
                class_dist = group[column].value_counts(normalize=True)
                distance = _total_variation_distance(class_dist, global_distributions[column])
                if distance > t:
                    raise ValueError(
                        f"Equivalence class violates t-closeness for '{column}' (distance {distance:.2f})."
                    )
        return df.copy()


def _total_variation_distance(class_dist: pd.Series, global_dist: pd.Series) -> float:
    combined_index = class_dist.index.union(global_dist.index)
    class_probs = class_dist.reindex(combined_index, fill_value=0.0)
    global_probs = global_dist.reindex(combined_index, fill_value=0.0)
    return 0.5 * np.abs(class_probs - global_probs).sum()

