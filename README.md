## Privacy Sandbox

Local-first playground for experimenting with anonymisation techniques such as k-anonymity, l-diversity, t-closeness, and differential privacy.

### What works today
- Upload CSV/TSV/XLSX files into `data/uploads`
- Automatic dataset validation pipeline (schema, column typing, rule checks)
- Modular privacy engine hooks for future algorithms
- Streamlit UI scaffold at `streamlit_app.py`

### Quick start
1. Create a Python 3.11 virtual environment.
2. Install dependencies:
   ```
   pip install -r requirements.txt
   ```
3. Launch Streamlit:
   ```
   streamlit run streamlit_app.py
   ```

### Repository layout
- `app/core`: shared configuration, logging, file helpers.
- `app/privacy`: validation logic and privacy algorithm adapters.
- `app/services`: orchestration services for uploads, metrics, and reports.
- `app/ui`: view helpers for Streamlit pages/components.
- `data/uploads`: local-only storage for user datasets.
- `data/examples`: sample datasets for demos/tests.
- `reports`: generated reports combining metrics and artifacts.
- `tests`: pytest-based regression and unit tests.

### Next steps
- Flesh out algorithm implementations in `app/privacy/algorithms`.
- Connect UI controls to services for end-to-end anonymisation.
- Add persistence (session cache) for uploaded datasets/metrics.
- Expand test suite to cover validators and algorithms.


