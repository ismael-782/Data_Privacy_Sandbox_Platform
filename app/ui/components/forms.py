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


def _sync_qi():
    """Callback to sync QI selection to session state."""
    st.session_state["role_qi"] = st.session_state["qi_widget"]

def _sync_sa():
    """Callback to sync SA selection to session state."""
    st.session_state["role_sa"] = st.session_state["sa_widget"]

def _sync_id():
    """Callback to sync ID selection to session state."""
    st.session_state["role_id"] = st.session_state["id_widget"]


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
    
    # Filter out any columns that are no longer in the dataframe
    current_qi = [c for c in current_qi if c in all_columns]
    current_sa = [c for c in current_sa if c in all_columns]
    current_id = [c for c in current_id if c in all_columns]
    
    # Calculate available columns for each dropdown
    # Each dropdown excludes columns selected in the OTHER dropdowns
    available_for_qi = [c for c in all_columns if c not in current_sa and c not in current_id]
    available_for_sa = [c for c in all_columns if c not in current_qi and c not in current_id]
    available_for_id = [c for c in all_columns if c not in current_qi and c not in current_sa]
    
    # Ensure current selections are valid options
    valid_qi = [c for c in current_qi if c in available_for_qi]
    valid_sa = [c for c in current_sa if c in available_for_sa]
    valid_id = [c for c in current_id if c in available_for_id]
    
    # Initialize widget states if not present (first run)
    if "qi_widget" not in st.session_state:
        st.session_state["qi_widget"] = valid_qi
    if "sa_widget" not in st.session_state:
        st.session_state["sa_widget"] = valid_sa
    if "id_widget" not in st.session_state:
        st.session_state["id_widget"] = valid_id
    
    # Render multiselects with on_change callbacks
    quasi_identifiers = st.multiselect(
        "Quasi-identifiers",
        options=available_for_qi,
        default=valid_qi,
        key="qi_widget",
        on_change=_sync_qi,
    )
    
    sensitive_attributes = st.multiselect(
        "Sensitive attributes",
        options=available_for_sa,
        default=valid_sa,
        help="Required for l-diversity and t-closeness.",
        key="sa_widget",
        on_change=_sync_sa,
    )
    
    identifiers = st.multiselect(
        "Identifiers (will be dropped before processing)",
        options=available_for_id,
        default=valid_id,
        key="id_widget",
        on_change=_sync_id,
    )
    
    # Also sync on initial render (for cases where callback hasn't fired yet)
    st.session_state["role_qi"] = quasi_identifiers
    st.session_state["role_sa"] = sensitive_attributes
    st.session_state["role_id"] = identifiers
    
    return quasi_identifiers, sensitive_attributes, identifiers
