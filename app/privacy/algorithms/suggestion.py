"""Suggestion algorithm using anonymity-api library."""

from __future__ import annotations

import io
import re
import sys
from dataclasses import dataclass

import pandas as pd
from anonymity_api import anonymity

from .base import AlgorithmParams, PrivacyAlgorithm


@dataclass
class SuggestionAlgorithm(PrivacyAlgorithm):
    """
    Automatic anonymization suggestion using anonymity-api library.
    
    This algorithm analyzes the data distribution and automatically suggests
    and applies the best anonymization technique (k-anonymity, l-diversity, etc.)
    to maximize utility while preserving privacy.
    """

    name: str = "suggestion"
    
    # Store the last result for UI access
    last_selected_algorithm: str = ""
    last_utility: float = 0.0

    def run(self, df: pd.DataFrame, params: AlgorithmParams) -> pd.DataFrame:
        """
        Analyze data and apply the best suggested anonymization.
        
        Args:
            df: Input DataFrame to anonymize.
            params: Algorithm parameters including quasi_identifiers and sensitive_attributes.
            
        Returns:
            Anonymized DataFrame using the best suggested technique.
            
        Raises:
            ValueError: If no quasi-identifiers are specified.
        """
        if not params.quasi_identifiers:
            raise ValueError("Suggestion algorithm requires at least one quasi-identifier.")
        
        # The suggestion algorithm requires sensitive attributes for full analysis
        sens_attrs = params.sensitive_attributes or []
        
        # Capture stdout to parse which algorithm was selected
        captured = io.StringIO()
        old_stdout = sys.stdout
        sys.stdout = captured
        
        try:
            # Pass a copy because the library modifies data in-place when testing algorithms
            anonymized = anonymity.suggest_anonymity(
                data=df.copy(),
                quasi_idents=params.quasi_identifiers,
                sens=sens_attrs,
                idents=params.identifiers or [],
            )
        finally:
            sys.stdout = old_stdout
        
        # Parse the output to find which algorithm was selected
        output = captured.getvalue()
        self._parse_selection(output)
        
        return anonymized
    
    def _parse_selection(self, output: str) -> None:
        """Parse stdout output to extract selected algorithm, parameters, and utility."""
        # First find the algorithm parameters from lines like:
        # "K-anonymization with k = 2.000000"
        # "Distinct l-diversity with l = 2"
        algorithm_params = {}
        for line in output.split('\n'):
            if 'K-anonymization with k =' in line:
                match = re.search(r'k = ([\d.]+)', line)
                if match:
                    algorithm_params['k-anonymity'] = f"k={int(float(match.group(1)))}"
            elif 'Distinct l-diversity with l =' in line:
                match = re.search(r'l = ([\d.]+)', line)
                if match:
                    algorithm_params['distinct l-diversity'] = f"l={int(float(match.group(1)))}"
            elif 'Entropy l-diversity with l =' in line:
                match = re.search(r'l = ([\d.]+)', line)
                if match:
                    algorithm_params['entropy l-diversity'] = f"l={float(match.group(1)):.2f}"
            elif 'Recursive (c,l)-diversity with c =' in line:
                match = re.search(r'c = (\d+) and l = (\d+)', line)
                if match:
                    algorithm_params['recursive (c,l)-diversity'] = f"c={match.group(1)}, l={match.group(2)}"
        
        # Find which algorithm was selected
        for line in output.split('\n'):
            if 'Returning the result from' in line:
                match = re.search(r'Returning the result from ([^,]+), with utility of ([\d.]+)', line)
                if match:
                    self.last_selected_algorithm = match.group(1).strip()
                    utility_str = match.group(2).rstrip('.')
                    self.last_utility = float(utility_str)
                    # Get the parameters for the selected algorithm
                    self.last_parameters = algorithm_params.get(self.last_selected_algorithm, "")
                break
    
    def get_selection_info(self) -> tuple[str, float, str]:
        """Get info about the last selected algorithm."""
        return self.last_selected_algorithm, self.last_utility, getattr(self, 'last_parameters', "")
