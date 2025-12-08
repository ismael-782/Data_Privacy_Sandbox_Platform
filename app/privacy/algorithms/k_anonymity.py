"""K-Anonymity implementation using anonymity-api library."""

from __future__ import annotations

from dataclasses import dataclass

import pandas as pd
from anonymity_api import anonymity

from .base import AlgorithmParams, PrivacyAlgorithm


@dataclass
class KAnonymity(PrivacyAlgorithm):
    """K-Anonymity algorithm using anonymity-api library."""

    name: str = "k-anonymity"

    def run(self, df: pd.DataFrame, params: AlgorithmParams) -> pd.DataFrame:
        """
        Apply k-anonymity to the dataset.
        
        Each record will be indistinguishable from at least k-1 other records
        with respect to the quasi-identifying attributes.
        
        Args:
            df: Input DataFrame to anonymize.
            params: Algorithm parameters including quasi_identifiers and k value.
            
        Returns:
            Anonymized DataFrame satisfying k-anonymity.
            
        Raises:
            ValueError: If no quasi-identifiers are specified.
        """
        if not params.quasi_identifiers:
            raise ValueError("k-anonymity requires at least one quasi-identifier.")
        
        k = params.k or 5
        
        anonymized = anonymity.k_anonymity(
            data=df,
            quasi_idents=params.quasi_identifiers,
            k=k,
            idents=params.identifiers or [],
        )
        
        return anonymized
