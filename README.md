# Forecasting Requested Hours for OTD

This repository provides a minimal, end-to-end example for preparing order
records and computing fulfillment-time quantiles. The goal is to demonstrate how
an analyst can transform raw data into a modeling-ready dataset and derive P10,
P50 and P90 statistics grouped by team and region.

## Quick start

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -U pip -r requirements.txt
python scripts/build_orders_modeling.py
python scripts/train_otd_quantiles.py
```

Running the scripts will produce:

- `data/orders_modeling.csv`: a feature engineered dataset derived from the raw
  order records found in `data/raw/orders.csv`.
- `data/orders_modeling_quantiles.csv`: the P10, P50 and P90 fulfillment-hour
  quantiles for each team/region combination.
- `models/otd_quantile_metadata.json`: metadata that documents the grouping
  columns, target column and summary statistics.

The project avoids third-party dependencies so it can run in restricted
execution environments. The repository also includes a small synthetic dataset
in `data/raw/orders.csv` to keep the example self-contained.
