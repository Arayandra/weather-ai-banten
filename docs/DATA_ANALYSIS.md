# Weather Data Analysis — Banten

This repository includes a reproducible exploratory data analysis notebook at [notebooks/Weather_Data_Analysis.ipynb](../notebooks/Weather_Data_Analysis.ipynb).

## Scope

The notebook reads `data/dataset_banten_clean.csv` and performs:
- Dataset structure, date coverage, city coverage, missing-value, and duplicate checks.
- Data type normalization and conversion of date/numeric fields.
- Descriptive statistics and distributions for temperature, precipitation, and wind speed.
- Monthly weather profiles and city-level comparisons.
- Pearson correlation analysis and IQR-based outlier flags.
- Export of quality and summary tables to `analysis_outputs/`.

## Run the notebook

From the repository root on a supported Python environment:

```bash
python -m pip install -r requirements-analysis.txt
python -m jupyter lab notebooks/Weather_Data_Analysis.ipynb
```

The notebook locates the dataset relative to the repository root or the `notebooks/` folder. The generated `analysis_outputs/` folder is reproducible and intentionally excluded from version control.

## Variables and interpretation

The application code uses the following main fields: `city`, `date`, `temperature_2m_mean`, `precipitation_sum`, `windspeed_10m_max`, `cape_proxy_radiation`, `lat`, and `lon`. The notebook analyzes the fields that are present in the CSV. Confirm the upstream dataset's data dictionary for exact definitions, units, and source provenance before interpreting results.

`cape_proxy_radiation` is treated cautiously as a proxy feature because of its name in the application code; it should not be described as a validated direct measurement of CAPE or solar radiation without supporting metadata.

The notebook's exploratory wet-day threshold (>0.1 mm) is a configurable analysis rule, not an assertion that it is an official meteorological category.

## Important distinction

This notebook demonstrates data preparation and descriptive analytics. It does not retrain or independently validate the CNN-LSTM model included in `data/model.keras`. Model performance claims require a separate chronological holdout evaluation using data that was not used during training.
