"""Tabbed interface components for anonymization algorithms."""

from __future__ import annotations

from dataclasses import dataclass

import pandas as pd
import streamlit as st

from app.core.config import settings


@dataclass
class TabParams:
    """Parameters collected from the active algorithm tab."""
    algorithm: str | None = None
    k: int | None = None
    l: int | None = None
    t: float | None = None
    epsilon: float | None = None
    query_type: str | None = None
    target_column: str | None = None
    run_clicked: bool = False


def render_algorithm_tabs(df: pd.DataFrame) -> TabParams:
    """
    Render tabbed interface for algorithm selection and parameter input.
    Each tab has its own Run button that triggers the algorithm.
    
    Args:
        df: The uploaded DataFrame.
        
    Returns:
        TabParams with the selected algorithm and its parameters, 
        and run_clicked=True if a Run button was clicked.
    """
    tab_names = ["K-Anonymity", "L-Diversity", "T-Closeness", "Auto-Suggest", "Differential Privacy"]
    tabs = st.tabs(tab_names)
    
    # Track button clicks and params for each algorithm
    clicked = None
    params_dict = {}
    
    # K-Anonymity Tab
    with tabs[0]:
        st.markdown("**K-Anonymity** ensures each record is indistinguishable from at least k-1 others.")
        k = st.number_input(
            "k (minimum group size)",
            min_value=2,
            value=settings.privacy.default_k,
            help="Each record must be indistinguishable from at least k-1 other records.",
            key="k_anon_k",
        )
        params_dict["k-anonymity"] = {"k": int(k)}
        if st.button("Run K-Anonymity", key="btn_run_k_anon", type="primary"):
            clicked = "k-anonymity"
    
    # L-Diversity Tab
    with tabs[1]:
        st.markdown("**L-Diversity** extends k-anonymity by requiring diversity in sensitive attributes.")
        l_val = st.number_input(
            "l (diversity threshold)",
            min_value=2,
            value=settings.privacy.default_l,
            help="Each equivalence class must have at least l distinct sensitive values.",
            key="l_div_l",
        )
        params_dict["l-diversity"] = {"l": int(l_val)}
        if st.button("Run L-Diversity", key="btn_run_l_div", type="primary"):
            clicked = "l-diversity"
    
    # T-Closeness Tab
    with tabs[2]:
        st.markdown("**T-Closeness** limits the distance between class and global distributions.")
        t_val = st.number_input(
            "t (maximum distance)",
            min_value=0.0,
            max_value=1.0,
            value=settings.privacy.default_t,
            step=0.05,
            help="Maximum allowed distance between class and global distributions.",
            key="t_close_t",
        )
        params_dict["t-closeness"] = {"t": float(t_val)}
        if st.button("Run T-Closeness", key="btn_run_t_close", type="primary"):
            clicked = "t-closeness"
    
    # Auto-Suggest Tab
    with tabs[3]:
        st.markdown("**Auto-Suggest** analyzes your data and automatically applies the best anonymization technique.")
        st.info("💡 The algorithm evaluates multiple techniques and selects the one with the highest utility.")
        params_dict["suggestion"] = {}
        if st.button("Run Auto-Suggest", key="btn_run_suggest", type="primary"):
            clicked = "suggestion"
    
    # Differential Privacy Tab
    with tabs[4]:
        st.markdown("**Differential Privacy** adds calibrated noise to aggregate queries.")
        
        # Filter to only numeric columns
        numeric_cols = df.select_dtypes(include=["number"]).columns.tolist()
        
        if not numeric_cols:
            st.warning("No numeric columns available for differential privacy queries.")
            params_dict["differential-privacy"] = {"query_type": None, "target_column": None, "epsilon": None}
        else:
            query_type = st.radio(
                "Query type",
                options=["Mean", "Sum"],
                horizontal=True,
                help="The type of aggregate query to apply.",
                key="dp_query_type",
            )
            
            target_column = st.selectbox(
                "Column to apply query on",
                options=numeric_cols,
                help="Select the numeric column for the differential privacy query.",
                key="dp_target_column",
            )
            
            epsilon = st.number_input(
                "ε (epsilon)",
                min_value=0.01,
                value=settings.privacy.default_epsilon,
                step=0.1,
                help="Privacy budget. Lower values = more privacy, more noise.",
                key="dp_epsilon",
            )
            
            params_dict["differential-privacy"] = {
                "query_type": query_type,
                "target_column": target_column,
                "epsilon": float(epsilon),
            }
            
        if st.button("Run Differential Privacy", key="btn_run_dp", type="primary"):
            clicked = "differential-privacy"
    
    # Return params for clicked algorithm, or empty if none clicked
    if clicked:
        p = params_dict.get(clicked, {})
        return TabParams(
            algorithm=clicked,
            k=p.get("k"),
            l=p.get("l"),
            t=p.get("t"),
            epsilon=p.get("epsilon"),
            query_type=p.get("query_type"),
            target_column=p.get("target_column"),
            run_clicked=True,
        )
    
    return TabParams(run_clicked=False)
