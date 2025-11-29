"""Differential privacy helpers using diffprivlib."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Callable

import numpy as np
import pandas as pd
from diffprivlib.mechanisms import LaplaceBoundedDomain

from .base import AlgorithmParams, PrivacyAlgorithm


AggregateFunc = Callable[[pd.DataFrame], float]


@dataclass
class DifferentialPrivacy(PrivacyAlgorithm):
    name: str = "differential-privacy"

    def run(self, df: pd.DataFrame, params: AlgorithmParams) -> pd.DataFrame:
        """Stub: returning df until DP workflow is wired in."""
        return df.copy()

    def dp_query(
        self,
        df: pd.DataFrame,
        query: AggregateFunc,
        epsilon: float,
        lower: float,
        upper: float,
    ) -> float:
        """Apply Laplace noise to a numeric aggregate."""
        true_value = query(df)
        mech = LaplaceBoundedDomain(epsilon=epsilon, delta=0.0, lower=lower, upper=upper)
        return mech.randomise(true_value)

