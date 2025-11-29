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
    """Let the user mark QI, SA, and identifier columns."""
    st.subheader("Column Roles")
    columns = list(df.columns)
    quasi_identifiers = st.multiselect("Quasi-identifiers", columns)
    sensitive_attributes = st.multiselect(
        "Sensitive attributes",
        columns,
        help="Required for l-diversity and t-closeness.",
    )
    identifiers = st.multiselect(
        "Identifiers (will be dropped before processing)",
        columns,
    )
    return quasi_identifiers, sensitive_attributes, identifiers

