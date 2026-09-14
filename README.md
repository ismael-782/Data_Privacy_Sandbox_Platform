# Privacy Sandbox

A local sandbox for privacy-preserving data transformations. Upload a dataset, mark which columns are quasi-identifiers and sensitive attributes, apply a privacy method (k-anonymity, l-diversity, t-closeness, or differential privacy), and inspect the trade-off between privacy and data utility before exporting the result.

---

## How It Works

1. **Data Upload & Selection** — Upload a CSV/TSV/XLSX dataset (or load the example dataset) and select which columns are quasi-identifiers and which are sensitive attributes.
2. **Method Selection & Configuration** — Choose a privacy method (k-anonymity, l-diversity, t-closeness, or differential privacy) and configure its parameters (e.g. the *k* value, *l* value, or epsilon).
3. **Processing & Calculation** — The selected algorithm anonymizes the data, and utility metrics comparing the original and anonymized data are calculated.
4. **Results & Export** — Trade-offs are shown through interactive dashboards, and the anonymized dataset and analysis reports can be exported.

---

## Screenshots

### 1. Landing page (empty state)

The app opens with a prompt to upload a dataset or load the built-in example dataset. No processing happens until a file is provided.

![Landing page empty state](screenshots/01-landing-empty-state.png)

### 2. Dataset loaded — column profile & warnings

Once a dataset is loaded, the app profiles every column (type, uniqueness, uniqueness ratio, missing values) and flags columns that look like identifiers, so the user knows what to exclude or mark before configuring privacy settings.

![Dataset loaded with column warnings](screenshots/02-dataset-loaded-warnings.png)

### 3. Column roles & algorithm selection

The user assigns each column a role, quasi-identifier, sensitive attribute, or identifier (identifiers are dropped before processing), and picks one or more privacy algorithms to apply. The app also raises role-level warnings, e.g. flagging a quasi-identifier that is too unique and should probably be reclassified.

![Column roles and algorithm selection](screenshots/03-column-roles-algorithms.png)

### 4. Anonymization results

After processing, the app reports the suppression ratio and shows the anonymized dataset (quasi-identifiers generalized into ranges, sensitive/identifier columns handled per the configuration), with a button to download the anonymized CSV.

![Anonymization results](screenshots/04-anonymization-results.png)

---

## Privacy Methods

| Method | Description |
|---|---|
| **k-Anonymity** | Groups records by quasi-identifiers and generalizes or suppresses records so that every group has at least *k* indistinguishable members. |
| **l-Diversity** | Builds on k-anonymity; requires each equivalence class to contain at least *l* distinct values for the sensitive attribute. |
| **t-Closeness** | Builds on l-diversity; requires the sensitive attribute's distribution within each equivalence class to stay within distance *t* of the overall dataset distribution (measured with Earth Mover's Distance). |
| **Differential Privacy** | Adds calibrated Laplace or Gaussian noise to numeric/categorical values, with a tracked privacy budget (epsilon). |

---

## Tech Stack

| Category | Libraries | Purpose |
|---|---|---|
| Anonymization algorithms | `anonymity-api`, `ANJANA` | Apply k/l/t-privacy transformations |
| Differential privacy | `OpenDP`, `PyDP`, `diffprivlib`, `PETINA` | Industry-grade DP mechanisms and wrappers |
| Anonymity evaluation | `PYCANON` | Evaluate anonymity levels in a dataset |
| Data processing | `pandas`, `numpy`, `scipy`, `dask`, `modin` | Core data cleaning, transformation, manipulation |
| Visualization | `plotly`, `matplotlib`, `seaborn`, `bokeh` | Graphs, heatmaps, interactive dashboards |
| Frontend/Web | `streamlit` | Main web application framework |
| Synthetic data | `sdv`, `faker` | Generate synthetic datasets for testing |
| Validation/quality | `great_expectations`, `pandas-profiling` | Validate data correctness and consistency |
| Utility metrics | `scikit-learn` | Utility metric calculations (e.g. classification accuracy) |

---

## Project Structure

```
privacy-sandbox/
├── app.py                          # Main Streamlit app, session state, navigation
├── privacy_methods/
│   ├── k_anonymity.py              # k-anonymity generalization/suppression
│   ├── l_diversity.py              # l-diversity on top of k-anonymity
│   ├── differential_privacy.py     # Laplace/Gaussian noise, epsilon tracking
│   └── t_closeness.py              # t-closeness (EMD-based) on top of l-diversity
├── utils/
│   ├── data_handler.py             # CSV loading, type detection, cleaning, export
│   ├── validators.py                # Parameter and column validation
│   └── synthetic_generator.py       # Synthetic sample datasets (SDV/Faker)
├── ui/
│   ├── upload_section.py           # Upload, preview, column selection
│   ├── config_section.py           # Method selection and parameter controls
│   ├── results_section.py          # Original vs. anonymized comparison, export
│   └── visualization.py            # Distribution plots, trade-off dashboards
└── metrics/
    ├── utility_metrics.py          # Information loss, correlation, query accuracy
    └── privacy_metrics.py          # Re-identification/disclosure risk, privacy score
```

---

## Getting Started

```bash
pip install -r requirements.txt
streamlit run app.py
```

Then open the local URL Streamlit prints in the terminal, and either upload a CSV/TSV/XLSX dataset or click **Load example dataset** to try it out.

---

## Team & Roles

| Developer | Primary Role | Tasks | Effort |
|---|---|---|---|
| Developer 1 | Privacy Algorithms | k-anonymity, l-diversity, differential privacy, t-closeness algorithms and related code review | 20% |
| Developer 2 | Frontend | Frontend and design for all pages, Figma design, frontend API endpoints, frontend functionality | 20% |
| Developer 3 | Data Management & Utilities | Uploaded-data handling, validation, processing, privacy vs. utility evaluation and other metrics | 20% |
| Developer 4 | Backend | API routes, user authentication, data authentication, database | 20% |
| Developer 5 | Visualization & Metrics | Dashboards, charts, utility metrics, visualization/graph logic and data display | 20% |

---

## Developer Implementation Guide

### Developer 1 — Privacy Algorithms: k-Anonymity & l-Diversity

**Libraries**: `pandas`, `numpy`, `copy`, `itertools`, `anonymity-api`

**`privacy_methods/k_anonymity.py`** — group records by quasi-identifiers, generalize groups smaller than *k* (e.g. `25-30`, `123**`), and suppress records if generalization can't reach *k*-anonymity.

| Function | Purpose |
|---|---|
| `generalize_numeric(df, column, levels=5)` | Generalize numeric columns into ranges |
| `generalize_categorical(df, column, hierarchy)` | Generalize categorical data using a hierarchy |
| `suppress_records(df, quasi_identifiers, k)` | Remove records that can't achieve k-anonymity |
| `apply_k_anonymity(df, k, quasi_identifiers)` | Main function to apply k-anonymity |
| `verify_k_anonymity(df, k, quasi_identifiers)` | Verify a dataset satisfies k-anonymity |

**`privacy_methods/l_diversity.py`** — for each equivalence class, check that at least *l* distinct sensitive-attribute values exist; merge classes or suppress records if not.

| Function | Purpose |
|---|---|
| `calculate_entropy_diversity(group, sensitive_column)` | Calculate entropy-based l-diversity |
| `calculate_distinct_diversity(group, sensitive_column)` | Calculate distinct l-diversity (simplest form) |
| `merge_groups(df, quasi_identifiers, sensitive_attribute, l)` | Merge equivalence classes to achieve l-diversity |
| `apply_l_diversity(df, l, quasi_identifiers, sensitive_attribute, k=None)` | Main function to apply l-diversity |
| `verify_l_diversity(df, l, quasi_identifiers, sensitive_attribute)` | Verify a dataset satisfies l-diversity |

### Developer 2 — Privacy Algorithms: Differential Privacy & t-Closeness

**Libraries**: `diffprivlib`, `python-dp` (PyDP), `pandas`, `numpy`, `scipy`

**`privacy_methods/differential_privacy.py`** — wrap `diffprivlib` to apply Laplace/Gaussian noise to numeric and categorical columns, and track cumulative epsilon spend.

| Function | Purpose |
|---|---|
| `apply_laplace_noise(value, epsilon, sensitivity)` | Add Laplace noise to a single value |
| `apply_gaussian_noise(value, epsilon, delta, sensitivity)` | Add Gaussian noise for (ε, δ)-DP |
| `privatize_numeric_column(df, column, epsilon, bounds)` | Add DP noise to an entire numeric column |
| `privatize_categorical_column(df, column, epsilon)` | Randomized response for categorical data |
| `apply_differential_privacy(df, epsilon, columns_config)` | Main function to apply DP to a dataset |
| `calculate_privacy_loss(operations)` | Track total epsilon spent across operations |

**`privacy_methods/t_closeness.py`** — for each equivalence class, compare the sensitive attribute distribution against the overall dataset distribution (Earth Mover's Distance); generalize/merge further if EMD exceeds *t*.

| Function | Purpose |
|---|---|
| `calculate_emd(distribution1, distribution2)` | Calculate Earth Mover's Distance between distributions |
| `calculate_distribution(group, sensitive_column)` | Get the probability distribution of a sensitive attribute |
| `check_t_closeness(group_dist, global_dist, t)` | Check if the t-closeness constraint is satisfied |
| `apply_t_closeness(df, t, quasi_identifiers, sensitive_attribute)` | Main function to apply t-closeness |
| `verify_t_closeness(df, t, quasi_identifiers, sensitive_attribute)` | Verify a dataset satisfies t-closeness |

### Developer 3 — Data Management & Utilities

**Libraries**: `pandas`, `numpy`, `sdv`, `faker`, `csv`

**`utils/data_handler.py`** — CSV loading, column type detection, missing-value handling, summary statistics, export.

| Function | Purpose |
|---|---|
| `load_csv(file_path, encoding='utf-8')` | Load a CSV with error handling |
| `detect_column_types(df)` | Automatically detect numeric vs. categorical columns |
| `clean_data(df, strategy='drop')` | Handle missing values and basic cleaning |
| `export_to_csv(df, filename, include_metadata=True)` | Export the anonymized data to CSV |
| `get_data_summary(df)` | Generate a statistical summary of the dataset |
| `identify_quasi_identifiers(df)` | Suggest potential quasi-identifiers |

**`utils/validators.py`** — validate privacy parameters (k, l, t, epsilon), column selections, and dataset size for the chosen method.

| Function | Purpose |
|---|---|
| `validate_k_value(k, dataset_size)` | Ensure k is valid (2 ≤ k ≤ dataset_size / 2) |
| `validate_epsilon(epsilon)` | Ensure epsilon is positive and reasonable (0.01–10) |
| `validate_columns(df, quasi_identifiers, sensitive_attribute)` | Check specified columns exist and are valid |
| `validate_dataset_size(df, method, k=None)` | Ensure the dataset is large enough for the method |
| `validate_input(df, method, parameters)` | Main validation entry point |

**`utils/synthetic_generator.py`** — generate realistic synthetic datasets for testing with SDV and Faker.

| Function | Purpose |
|---|---|
| `generate_student_data(num_records=1000)` | Generate a synthetic student dataset |
| `generate_customer_data(num_records=1000)` | Generate a synthetic customer dataset |
| `generate_health_data(num_records=1000)` | Generate a synthetic patient/health dataset |
| `generate_custom_data(schema, num_records)` | Generate data from a user-defined schema |
| `save_sample_datasets()` | Pre-generate and save sample datasets |

### Developer 4 — Frontend Interface

**Libraries**: `streamlit`, `pandas`

**`app.py`** — main Streamlit app: layout, sidebar navigation, header, session-state management.

| Function | Purpose |
|---|---|
| `main()` | Main Streamlit application function |
| `initialize_session_state()` | Initialize all session variables |
| `render_header()` | Render the page header (title and info) |
| `render_sidebar()` | Render the navigation sidebar |

**`ui/upload_section.py`** — upload, data preview, statistics, quasi-identifier/sensitive-attribute selection.

| Function | Purpose |
|---|---|
| `render_upload_section()` | Main upload interface (`st.file_uploader`) |
| `display_data_preview(df, num_rows=10)` | Show the data table with formatting |
| `render_column_selector(df)` | UI for selecting quasi-identifiers and sensitive attributes |
| `display_data_statistics(df)` | Show dataset statistics |
| `render_sample_dataset_loader()` | Allow loading pre-made sample datasets |

**`ui/config_section.py`** — method dropdown, dynamic parameter controls, "Apply Privacy Method" action with progress.

| Function | Purpose |
|---|---|
| `render_config_section(df)` | Main configuration interface |
| `render_method_selector()` | Dropdown to select the privacy method |
| `render_k_anonymity_config()` | Parameter controls for k-anonymity |
| `render_l_diversity_config()` | Parameter controls for l-diversity |
| `render_dp_config()` | Parameter controls for differential privacy |
| `render_t_closeness_config()` | Parameter controls for t-closeness |
| `apply_privacy_method(df, method, params)` | Execute the selected privacy method with a progress bar |

**`ui/results_section.py`** — original vs. anonymized comparison, metric cards, export.

| Function | Purpose |
|---|---|
| `render_results_section(original_df, anonymized_df, metrics)` | Main results display |
| `display_data_comparison(original_df, anonymized_df)` | Side-by-side comparison of datasets |
| `display_metrics_cards(metrics)` | Show privacy and utility metrics in cards |
| `render_export_button(df, filename)` | Download button for the anonymized data |
| `display_transformation_summary(transformations)` | Show what changed in the data |

### Developer 5 — Visualization & Metrics

**Libraries**: `plotly`, `matplotlib`, `seaborn`, `pandas`, `scikit-learn`

**`metrics/utility_metrics.py`** — information loss, correlation preservation, statistical similarity, query accuracy.

| Function | Purpose |
|---|---|
| `calculate_information_loss(original_df, anonymized_df)` | Calculate the percentage of information lost |
| `measure_correlation_preservation(original_df, anonymized_df, columns)` | Compare correlation matrices |
| `measure_statistical_similarity(original_df, anonymized_df)` | Compare means, standard deviations, distributions |
| `test_query_accuracy(original_df, anonymized_df, queries)` | Test the accuracy of aggregate queries |
| `calculate_classification_accuracy(original_df, anonymized_df, target)` | Train a classifier on both datasets and compare accuracy |
| `generate_utility_report(original_df, anonymized_df)` | Comprehensive utility metrics report |

**`metrics/privacy_metrics.py`** — privacy property verification, re-identification/disclosure risk, overall score.

| Function | Purpose |
|---|---|
| `calculate_reidentification_risk(df, quasi_identifiers)` | Estimate the risk of re-identifying individuals |
| `calculate_disclosure_risk(df, sensitive_attribute)` | Measure the risk of sensitive data disclosure |
| `verify_privacy_guarantee(df, method, parameters)` | Check whether the privacy property is satisfied |
| `calculate_privacy_score(df, method, parameters)` | Overall privacy score (0–100) |
| `generate_privacy_report(df, method, parameters)` | Comprehensive privacy assessment |

**`ui/visualization.py`** — interactive visualizations and trade-off analysis.

| Function | Purpose |
|---|---|
| `plot_distribution_comparison(original_df, anonymized_df, column)` | Side-by-side histogram comparison |
| `plot_privacy_utility_tradeoff(results_list)` | Scatter plot of privacy vs. utility across parameters |
| `plot_correlation_heatmap(df, title)` | Interactive correlation heatmap |
| `plot_metrics_radar(metrics_dict)` | Radar chart of multiple metrics |
| `create_interactive_dashboard(original_df, anonymized_df, metrics)` | Comprehensive visualization dashboard |
| `plot_parameter_sensitivity(parameter_range, privacy_scores, utility_scores)` | Show how changing parameters affects privacy and utility |
| `run_parameter_sweep(df, method, parameter_range, quasi_identifiers, sensitive_attr)` | Test multiple parameter values automatically |
| `compare_methods(df, methods_list, quasi_identifiers, sensitive_attr)` | Compare different privacy methods on the same dataset |
| `find_optimal_parameters(tradeoff_results, privacy_threshold, utility_threshold)` | Suggest the best parameters for given requirements |
| `plot_method_comparison(comparison_results)` | Bar chart comparing multiple methods |
| `generate_recommendation_report(analysis_results)` | Provide recommendations based on analysis |
