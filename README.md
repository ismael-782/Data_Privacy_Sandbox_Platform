# Privacy Sandbox

A local-first playground for experimenting with data anonymization techniques including **K-Anonymity**, **L-Diversity**, **T-Closeness**, **Differential Privacy**, and **Auto-Suggest**.

## Features

### Anonymization Algorithms
- **K-Anonymity**: Ensures each record is indistinguishable from at least k-1 others based on quasi-identifiers
- **L-Diversity**: Extends k-anonymity by requiring diversity in sensitive attribute values
- **T-Closeness**: Limits the distance between class and global distributions of sensitive attributes
- **Auto-Suggest**: Automatically analyzes your data and selects the best anonymization technique for maximum utility
- **Differential Privacy**: Adds calibrated noise to aggregate queries (Mean/Sum) with mathematical privacy guarantees

### Application Features
- Upload CSV, TSV, or XLSX files for anonymization
- Interactive tabbed UI for selecting and configuring algorithms
- Mutually exclusive column role selection (Quasi-identifiers, Sensitive attributes, Identifiers)
- Real-time utility metrics (AECS, Information Loss, Discernibility)
- Download anonymized datasets as CSV

## Quick Start

1. Create a Python 3.11+ virtual environment:
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Launch the application:
   ```bash
   streamlit run streamlit_app.py
   ```

## Dependencies

| Library | Purpose |
|---------|---------|
| `anonymity-api` | K-Anonymity, L-Diversity, T-Closeness, Auto-Suggest algorithms and utility metrics |
| `diffprivlib` | Differential Privacy mechanisms (IBM) |
| `streamlit` | Web UI framework |
| `pandas` | Data manipulation |

## Repository Layout

```
├── app/
│   ├── core/           # Configuration and logging
│   ├── privacy/
│   │   ├── algorithms/ # K-Anonymity, L-Diversity, T-Closeness, DP, Auto-Suggest
│   │   └── validators/ # Dataset validation logic
│   ├── services/       # Anonymization service orchestration
│   └── ui/
│       └── components/ # Streamlit UI components (forms, tabs)
├── config/             # Application settings (YAML)
├── data/               # Sample datasets
├── streamlit_app.py    # Main Streamlit application
└── requirements.txt    # Python dependencies
```

## Usage

1. **Upload a dataset** (CSV, TSV, or XLSX)
2. **Assign column roles**:
   - Quasi-identifiers: Columns that could partially identify individuals
   - Sensitive attributes: Private information to protect
   - Identifiers: Direct identifiers to remove (e.g., names, SSN)
3. **Select an algorithm** and configure parameters (or use Auto-Suggest)
4. **Run** and view results with utility metrics
5. **Download** the anonymized dataset

## Utility Metrics

| Metric | Description | Interpretation |
|--------|-------------|----------------|
| Avg. Equivalence Class Size | Ratio of records per equivalence class | Closer to 1.0 = better |
| Information Loss | Global certainty penalty | 0% = no loss, 100% = total loss |
| Discernibility | Quality loss based on class sizes | Lower = better utility |

## License

MIT
