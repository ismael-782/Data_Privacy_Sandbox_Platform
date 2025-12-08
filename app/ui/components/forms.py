"""Reusable Streamlit form components."""

from __future__ import annotations

from typing import Sequence

import pandas as pd
import streamlit as st

from app.privacy.validators.dataset_validator import ColumnSummary


def dataset_overview(columns: Sequence[ColumnSummary]) -> None:
    """Render a compact table of column summaries."""
    if not columns:
        st.info("No column summaries available yet.")
        return
    data = [
        {
            "Column": col.name,
            "Type": col.semantic_type.value,
            "Uniq": col.unique_values,
            "Uniq %": col.uniqueness_ratio,
            "Missing": "yes" if col.has_missing else "no",
        }
        for col in columns
    ]
    st.dataframe(data, use_container_width=True, hide_index=True)


def role_selector(df: pd.DataFrame) -> tuple[list[str], list[str], list[str]]:
    """
    Let the user mark QI, SA, and identifier columns.
    
    Columns are mutually exclusive - selecting a column in one dropdown
    removes it from the options in other dropdowns.
    """
    st.subheader("Column Roles")
    all_columns = list(df.columns)
    
    # Initialize session state for selections if not present
    if "role_qi" not in st.session_state:
        st.session_state["role_qi"] = []
    if "role_sa" not in st.session_state:
        st.session_state["role_sa"] = []
    if "role_id" not in st.session_state:
        st.session_state["role_id"] = []
    
    # Get current selections from session state
    current_qi = st.session_state["role_qi"]
    current_sa = st.session_state["role_sa"]
    current_id = st.session_state["role_id"]
    
    # Calculate available columns for each dropdown
    # Each dropdown excludes columns selected in the OTHER dropdowns
    available_for_qi = [c for c in all_columns if c not in current_sa and c not in current_id]
    available_for_sa = [c for c in all_columns if c not in current_qi and c not in current_id]
    available_for_id = [c for c in all_columns if c not in current_qi and c not in current_sa]
    
    # Ensure current selections are valid (in case columns were removed)
    valid_qi = [c for c in current_qi if c in available_for_qi]
    valid_sa = [c for c in current_sa if c in available_for_sa]
    valid_id = [c for c in current_id if c in available_for_id]
    
    # Render multiselects with filtered options
    quasi_identifiers = st.multiselect(
        "Quasi-identifiers",
        options=available_for_qi,
        default=valid_qi,
        key="qi_selector",
    )
    
    sensitive_attributes = st.multiselect(
        "Sensitive attributes",
        options=available_for_sa,
        default=valid_sa,
        help="Required for l-diversity and t-closeness.",
        key="sa_selector",
    )
    
    identifiers = st.multiselect(
        "Identifiers (will be dropped before processing)",
        options=available_for_id,
        default=valid_id,
        key="id_selector",
    )
    
    # Update session state with new selections
    st.session_state["role_qi"] = quasi_identifiers
    st.session_state["role_sa"] = sensitive_attributes
    st.session_state["role_id"] = identifiers
    
    return quasi_identifiers, sensitive_attributes, identifiers
