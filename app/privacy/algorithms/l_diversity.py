"""L-Diversity implementation using anonymity-api library."""

from __future__ import annotations

from dataclasses import dataclass

import pandas as pd
from anonymity_api import anonymity

from .base import AlgorithmParams, PrivacyAlgorithm


@dataclass
class LDiversity(PrivacyAlgorithm):
    """L-Diversity algorithm using anonymity-api library."""

    name: str = "l-diversity"

    def run(self, df: pd.DataFrame, params: AlgorithmParams) -> pd.DataFrame:
        """
        Apply l-diversity to the dataset.
        
        Ensures each equivalence class has at least l distinct values
        for each sensitive attribute.
        
        Args:
            df: Input DataFrame to anonymize.
            params: Algorithm parameters including quasi_identifiers, 
                    sensitive_attributes, and l value.
            
        Returns:
            Anonymized DataFrame satisfying l-diversity.
            
        Raises:
            ValueError: If quasi-identifiers or sensitive attributes are not specified.
        """
        if not params.quasi_identifiers:
            raise ValueError("l-diversity requires at least one quasi-identifier.")
        if not params.sensitive_attributes:
            raise ValueError("l-diversity requires at least one sensitive attribute.")
        
        l_value = params.l or 2
        
        anonymized = anonymity.distinct_l_diversity(
            data=df,
            quasi_idents=params.quasi_identifiers,
            sens_atts=params.sensitive_attributes,
            l=l_value,
            idents=params.identifiers or [],
        )
        
        return anonymized
