"""Streamlit entry point for the Privacy Sandbox."""

from __future__ import annotations

from pathlib import Path

import pandas as pd
import streamlit as st

from app.core.config import settings
from app.core.logging import setup_logging
from app.privacy.algorithms.base import AlgorithmParams
from app.services.anonymization_service import AnonymizationService
from app.services.dataset_service import DatasetService
from app.ui.components.forms import dataset_overview, role_selector

setup_logging()
dataset_service = DatasetService()
anonymization_service = AnonymizationService()


def _load_dataframe(file) -> pd.DataFrame:
    suffix = Path(file.name).suffix.lower()
    if suffix == ".xlsx":
        return pd.read_excel(file)
    sep = "," if suffix == ".csv" else "\t"
    return pd.read_csv(file, sep=sep)


def main() -> None:
    st.set_page_config(
        page_title=settings.app.name,
        layout="wide",
        initial_sidebar_state="expanded",
    )
    st.title(settings.app.name)
    st.caption("Local sandbox for privacy-preserving data transformations.")

    uploaded_df: pd.DataFrame | None = st.session_state.get("uploaded_df")

    with st.sidebar:
        st.header("Upload dataset")
        uploaded_file = st.file_uploader(
            "CSV / TSV / XLSX",
            type=["csv", "tsv", "xlsx"],
            help=f"Max size {settings.app.max_file_size_mb} MB",
        )
        if uploaded_file is not None:
            if uploaded_file.size > settings.app.max_file_size_mb * 1024 * 1024:
                st.error("File too large.")
            else:
                uploaded_df = _load_dataframe(uploaded_file)
                st.session_state["uploaded_df"] = uploaded_df
                st.success(f"Loaded {uploaded_df.shape[0]} rows.")

        if st.button("Load example dataset"):
            example_path = Path(settings.data.examples_dir) / "people.csv"
            uploaded_df = dataset_service.load(example_path)
            st.session_state["uploaded_df"] = uploaded_df
            st.success("Example dataset loaded.")

    if uploaded_df is None:
        st.info("Upload a dataset to begin.")
        return

    validation_result = dataset_service.validate_dataset(uploaded_df)
    if validation_result.errors:
        st.error("Dataset validation failed:")
        for err in validation_result.errors:
            st.write(f"- {err}")
        return

    if validation_result.warnings:
        st.warning("Dataset warnings:")
        for warn in validation_result.warnings:
            st.write(f"- {warn}")

    dataset_overview(validation_result.column_summaries or [])

    qi_cols, sa_cols, id_cols = role_selector(uploaded_df)
    roles_result = dataset_service.validate_roles(uploaded_df, qi_cols, sa_cols, id_cols)

    if roles_result.errors:
        st.error("Role validation errors:")
        for err in roles_result.errors:
            st.write(f"- {err}")
        st.stop()
    if roles_result.warnings:
        st.warning("Role warnings:")
        for warn in roles_result.warnings:
            st.write(f"- {warn}")

    st.subheader("Algorithms")
    
    from app.ui.components.algorithm_tabs import render_algorithm_tabs
    
    tab_params = render_algorithm_tabs(uploaded_df)
    
    if tab_params.run_clicked:
        params = AlgorithmParams(
            quasi_identifiers=qi_cols,
            sensitive_attributes=sa_cols,
            identifiers=id_cols,
            k=tab_params.k,
            l=tab_params.l,
            t=tab_params.t,
            epsilon=tab_params.epsilon,
            query_type=tab_params.query_type,
            target_column=tab_params.target_column,
        )
        try:
            with st.spinner("Running algorithm..."):
                result = anonymization_service.run_pipeline(
                    uploaded_df, [tab_params.algorithm], params
                )
                # Store result in session state so it persists
                st.session_state["anonymization_result"] = result
                
                # For suggestion algorithm, store selected algorithm name and params
                if tab_params.algorithm == "suggestion":
                    algo = anonymization_service.registry.get("suggestion")
                    selected_name, utility, params_str = algo.get_selection_info()
                    st.session_state["suggestion_selected_algorithm"] = selected_name
                    st.session_state["suggestion_utility"] = utility
                    st.session_state["suggestion_params"] = params_str
        except ValueError as exc:
            st.error(f"Anonymization failed: {exc}")
            st.session_state.pop("anonymization_result", None)
            st.stop()

    # Display result if available (persists across reruns)
    if "anonymization_result" in st.session_state:
        result = st.session_state["anonymization_result"]
        
        # Check if this is a DP query result
        is_dp_query = result.metrics.get("is_dp_query", 0) == 1.0
        is_suggestion = result.metrics.get("is_suggestion", 0) == 1.0
        
        if is_dp_query:
            # Display DP query result as metrics
            st.subheader("Query Results")
            
            # Extract values from the result dataframe
            row = result.dataframe.iloc[0]
            true_value = row["True Value"]
            dp_value = row["DP Value (with noise)"]
            noise = row["Noise Added"]
            epsilon = row["Epsilon (ε)"]
            
            # Display as two metrics side by side
            col1, col2 = st.columns(2)
            with col1:
                st.metric("True Value", f"{true_value:.4f}")
            with col2:
                st.metric("DP Value", f"{dp_value:.4f}", delta=f"Noise: {noise:.4f}")
            
            st.caption(f"Applied Laplace mechanism with ε={epsilon}")
        elif is_suggestion:
            # Display suggestion algorithm result
            selected_algo = st.session_state.get("suggestion_selected_algorithm", "unknown")
            algo_params = st.session_state.get("suggestion_params", "")
            
            # Build message with algorithm details
            params_text = f" with **{algo_params}**" if algo_params else ""
            st.info(f"📊 The algorithm analyzed your data and selected **{selected_algo}**{params_text} as the best technique for maximum utility while preserving privacy.")
            
            # Display metrics in columns
            metric_cols = st.columns(3)
            with metric_cols[0]:
                if "avg_equivalence_class_size" in result.metrics:
                    st.metric(
                        "Avg. Equivalence Class Size", 
                        f"{result.metrics['avg_equivalence_class_size']:.2f}",
                        help="Closer to 1.0 = better (minimal over-generalization)."
                    )
            with metric_cols[1]:
                if "global_certainty_penalty" in result.metrics:
                    st.metric(
                        "Information Loss", 
                        f"{result.metrics['global_certainty_penalty']:.2%}",
                        help="0% = no info loss, 100% = total info loss."
                    )
            with metric_cols[2]:
                if "discernibility_metric" in result.metrics:
                    st.metric(
                        "Discernibility", 
                        f"{result.metrics['discernibility_metric']:,.0f}",
                        help="Quality loss metric. Lower = better utility."
                    )
            
            st.dataframe(result.dataframe.head(100), use_container_width=True)
            st.download_button(
                "Download anonymized CSV",
                data=result.dataframe.to_csv(index=False).encode("utf-8"),
                file_name="anonymized.csv",
                mime="text/csv",
            )
        else:
            # Display anonymization result
            st.success(f"Anonymization finished. Rows: {result.anonymized_rows}/{result.original_rows}")
            
            # Display metrics in columns
            metric_cols = st.columns(3)
            with metric_cols[0]:
                if "avg_equivalence_class_size" in result.metrics:
                    st.metric(
                        "Avg. Equivalence Class Size", 
                        f"{result.metrics['avg_equivalence_class_size']:.2f}",
                        help="Closer to 1.0 = better (minimal over-generalization)."
                    )
            with metric_cols[1]:
                if "global_certainty_penalty" in result.metrics:
                    st.metric(
                        "Information Loss", 
                        f"{result.metrics['global_certainty_penalty']:.2%}",
                        help="0% = no info loss, 100% = total info loss."
                    )
            with metric_cols[2]:
                if "discernibility_metric" in result.metrics:
                    st.metric(
                        "Discernibility", 
                        f"{result.metrics['discernibility_metric']:,.0f}",
                        help="Quality loss metric. Lower = better utility."
                    )
            
            st.dataframe(result.dataframe.head(100), use_container_width=True)
            st.download_button(
                "Download anonymized CSV",
                data=result.dataframe.to_csv(index=False).encode("utf-8"),
                file_name="anonymized.csv",
                mime="text/csv",
            )


if __name__ == "__main__":
    main()

