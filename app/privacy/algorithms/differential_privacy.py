"""Differential Privacy implementation using diffprivlib."""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np
import pandas as pd
from diffprivlib.tools import mean as dp_mean, sum as dp_sum

from .base import AlgorithmParams, PrivacyAlgorithm


@dataclass
class DPResult:
    """Result from a differential privacy query."""
    query_type: str
    column: str
    epsilon: float
    true_value: float
    dp_value: float
    noise_added: float


@dataclass
class DifferentialPrivacy(PrivacyAlgorithm):
    """
    Differential Privacy algorithm using IBM's diffprivlib.
    
    Unlike k-anonymity/l-diversity/t-closeness which return anonymized datasets,
    DP returns noisy aggregate query results (mean or sum) that provide
    mathematical privacy guarantees.
    """

    name: str = "differential-privacy"

    def run(self, df: pd.DataFrame, params: AlgorithmParams) -> pd.DataFrame:
        """
        Apply differential privacy to compute a noisy aggregate.
        
        Args:
            df: Input DataFrame.
            params: Must include query_type, target_column, and epsilon.
            
        Returns:
            DataFrame with a single row containing the DP result.
            
        Raises:
            ValueError: If required parameters are missing or invalid.
        """
        if not params.target_column:
            raise ValueError("Differential privacy requires a target column.")
        if params.target_column not in df.columns:
            raise ValueError(f"Column '{params.target_column}' not found in dataset.")
        if not params.query_type:
            raise ValueError("Differential privacy requires a query type (Mean or Sum).")
        if not params.epsilon or params.epsilon <= 0:
            raise ValueError("Epsilon must be a positive value.")
        
        # Get the column data
        column_data = df[params.target_column].dropna().values
        
        if len(column_data) == 0:
            raise ValueError(f"Column '{params.target_column}' has no valid numeric values.")
        
        # Calculate bounds for the data (required by diffprivlib)
        data_min = float(np.min(column_data))
        data_max = float(np.max(column_data))
        bounds = (data_min, data_max)
        
        # Apply DP query
        if params.query_type.lower() == "mean":
            true_value = float(np.mean(column_data))
            dp_value = float(dp_mean(column_data, epsilon=params.epsilon, bounds=bounds))
        elif params.query_type.lower() == "sum":
            true_value = float(np.sum(column_data))
            dp_value = float(dp_sum(column_data, epsilon=params.epsilon, bounds=bounds))
        else:
            raise ValueError(f"Unknown query type: {params.query_type}")
        
        noise_added = dp_value - true_value
        
        # Return result as a DataFrame
        result_df = pd.DataFrame([{
            "Query Type": params.query_type,
            "Column": params.target_column,
            "Epsilon (ε)": params.epsilon,
            "True Value": round(true_value, 4),
            "DP Value (with noise)": round(dp_value, 4),
            "Noise Added": round(noise_added, 4),
            "Data Range": f"{data_min:.2f} - {data_max:.2f}",
            "Records Used": len(column_data),
        }])
        
        return result_df
