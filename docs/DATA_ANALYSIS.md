# Weather Data Analysis — Banten

The repository includes a reproducible exploratory data analysis notebook:
[notebooks/Weather_Data_Analysis.ipynb](../notebooks/Weather_Data_Analysis.ipynb).

For a snapshot of the results produced from the current cleaned dataset, see
[ANALYSIS_FINDINGS.md](ANALYSIS_FINDINGS.md).

## Scope

The notebook performs:

- Dataset structure, date coverage, city coverage, missing-value, duplicate-row, and city-date coverage checks.
- Data type normalization and conversion of date and numeric fields.
- Descriptive statistics and distributions for temperature, precipitation, wind speed, and the available proxy feature.
- Monthly and annual weather profiles.
- City-level comparisons and a city-by-month precipitation heatmap.
- Wet-day frequency and rainfall quantiles using a clearly stated exploratory threshold.
- Pearson and Spearman correlation analysis on the main weather variables.
- Global and per-city IQR outlier flags, without automatically deleting flagged observations.
- Export of reproducible CSV tables to `analysis_outputs/`.

## Run the notebook

Use a dedicated virtual environment so the optional analysis packages do not interfere with the Django/TensorFlow application environment.

### Windows CMD

From the repository root:

```cmd
python -m venv .venv-analysis
.venv-analysis\Scripts\activate
python -m pip install --upgrade pip
python -m pip install -r requirements-analysis.txt
python -m jupyter lab notebooks/Weather_Data_Analysis.ipynb
```

The requirements file selects compatible Pandas and NumPy ranges according to the Python version. Python 3.14 uses the Pandas 3.x / NumPy 2.x dependency range. The main Django/TensorFlow application has its own runtime constraints; keep its environment separate from `.venv-analysis`.

### macOS / Linux

```bash
python3 -m venv .venv-analysis
source .venv-analysis/bin/activate
python -m pip install --upgrade pip
python -m pip install -r requirements-analysis.txt
python -m jupyter lab notebooks/Weather_Data_Analysis.ipynb
```

The notebook locates `data/dataset_banten_clean.csv` relative to the repository root or the `notebooks/` directory. Generated tables are written to `analysis_outputs/`, which is intentionally excluded from version control so results can be reproduced locally.

## Generated outputs

The notebook generates the following CSV files when the required columns are available:

| File | Description |
| --- | --- |
| `data_quality_report.csv` | Data types, missing-value counts, and unique-value counts |
| `city_weather_summary.csv` | City-level weather averages and wet-day percentage |
| `monthly_weather_profile.csv` | Monthly averages for temperature, rainfall, and wind |
| `outlier_iqr_report.csv` | Global IQR outlier flags |
| `city_day_coverage_report.csv` | Number of observed and missing dates per city |
| `annual_weather_profile.csv` | Annual averages for main weather variables |
| `monthly_city_precipitation.csv` | Average rainfall for each city and calendar month |
| `rainfall_quantiles.csv` | Rainfall distribution quantiles |
| `rainfall_by_city.csv` | Mean, median, and wet-day frequency by city |
| `weather_correlation_pearson.csv` | Pearson correlation matrix |
| `weather_correlation_spearman.csv` | Spearman correlation matrix |
| `city_outlier_report.csv` | IQR outlier flags calculated separately per city |

## Variables and interpretation

The main weather fields are `city`, `date`, `temperature_2m_mean`, `precipitation_sum`, `windspeed_10m_max`, `cape_proxy_radiation`, `lat`, and `lon`. The notebook also encounters engineered time-series fields such as lag, rolling, difference, and seasonal encoding columns.

Confirm the upstream data dictionary for exact definitions, units, and source provenance before interpreting results. `cape_proxy_radiation` is treated cautiously as a proxy feature; it must not be described as a validated direct measurement of CAPE or solar radiation without supporting metadata.

The exploratory wet-day threshold (>0.1 mm) is a configurable analysis rule, not an assertion that it is an official meteorological category.

## Important distinctions and limitations

- The reported averages are calculated per city-day record, not a total rainfall accumulation for the whole province.
- Missing-value checks do not by themselves prove that records are accurate, complete, or free of duplicate city-date keys. Use the coverage report for the latter checks.
- IQR flags identify values for review; they are not proof of data errors. Extreme rainfall may be meteorologically valid.
- Pearson and Spearman correlations are descriptive and do not establish causality.
- This notebook demonstrates data preparation and descriptive analytics. It does not retrain or independently validate the CNN-LSTM model in `data/model.keras`.
- Model performance claims require a separate chronological holdout evaluation using observations not used during training. Avoid randomly splitting time-series rows because that can cause temporal leakage.
