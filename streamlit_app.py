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
    selected_algorithms = st.multiselect(
        "Select privacy methods",
        anonymization_service.available_algorithms(),
        default=["k-anonymity"],
    )

    col_a, col_b, col_c, col_d = st.columns(4)
    with col_a:
        k_value = st.number_input("k (k-anonymity)", min_value=2, value=settings.privacy.default_k)
    with col_b:
        l_value = st.number_input("l (l-diversity)", min_value=2, value=settings.privacy.default_l)
    with col_c:
        t_value = st.number_input(
            "t (t-closeness)", min_value=0.0, max_value=1.0, value=settings.privacy.default_t, step=0.05
        )
    with col_d:
        epsilon_value = st.number_input(
            "ε (differential privacy)", min_value=0.01, value=settings.privacy.default_epsilon, step=0.1
        )

    if st.button("Run anonymization", type="primary", disabled=not selected_algorithms):
        params = AlgorithmParams(
            quasi_identifiers=qi_cols,
            sensitive_attributes=sa_cols,
            k=int(k_value),
            l=int(l_value),
            t=float(t_value),
            epsilon=float(epsilon_value),
        )
        try:
            with st.spinner("Running algorithms..."):
                result = anonymization_service.run_pipeline(
                    uploaded_df, selected_algorithms, params
                )
        except ValueError as exc:
            st.error(f"Anonymization failed: {exc}")
            st.stop()

        st.success(f"Anonymization finished. Rows: {result.anonymized_rows}/{result.original_rows}")
        st.metric("Suppression ratio", f"{result.metrics['suppression_ratio']:.2%}")
        st.dataframe(result.dataframe.head(100), use_container_width=True)
        st.download_button(
            "Download anonymized CSV",
            data=result.dataframe.to_csv(index=False).encode("utf-8"),
            file_name="anonymized.csv",
            mime="text/csv",
        )


if __name__ == "__main__":
    main()

