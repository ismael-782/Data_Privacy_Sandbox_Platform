"""T-Closeness implementation using anonymity-api library."""

from __future__ import annotations

from dataclasses import dataclass

import pandas as pd
from anonymity_api import anonymity

from .base import AlgorithmParams, PrivacyAlgorithm


@dataclass
class TCloseness(PrivacyAlgorithm):
    """T-Closeness algorithm using anonymity-api library."""

    name: str = "t-closeness"

    def run(self, df: pd.DataFrame, params: AlgorithmParams) -> pd.DataFrame:
        """
        Apply t-closeness to the dataset.
        
        Ensures the distribution of sensitive attributes within each
        equivalence class is close to their distribution in the overall dataset.
        
        Args:
            df: Input DataFrame to anonymize.
            params: Algorithm parameters including quasi_identifiers, 
                    sensitive_attributes, and t threshold.
            
        Returns:
            Anonymized DataFrame satisfying t-closeness.
            
        Raises:
            ValueError: If quasi-identifiers or sensitive attributes are not specified.
        """
        if not params.quasi_identifiers:
            raise ValueError("t-closeness requires at least one quasi-identifier.")
        if not params.sensitive_attributes:
            raise ValueError("t-closeness requires at least one sensitive attribute.")
        
        t_value = params.t or 0.2
        
        anonymized = anonymity.t_closeness(
            data=df,
            quasi_idents=params.quasi_identifiers,
            sens_atts=params.sensitive_attributes,
            t=t_value,
            idents=params.identifiers or [],
        )
        
        return anonymized
