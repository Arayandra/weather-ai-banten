# Weather AI Banten — Data Analytics Findings

This report records the descriptive results produced from the cleaned dataset and exported summary CSVs. It is a reproducible snapshot, not a live weather report. Re-run the notebook after replacing or updating the dataset to refresh these figures.

**Analysis period:** 3 January 2019 – 31 December 2025  
**Locations:** 7  
**City-day records:** 17,885 (2,555 records for each listed location)  
**Variables in the data-quality report:** 22

## Executive summary

- The average temperature across all city-day records is **26.49 °C**.
- The average precipitation is **6.73 mm per city-day record**. This is not a province-wide accumulated rainfall total.
- **February** has the highest monthly average precipitation (**10.65 mm**); **August** has the lowest (**2.92 mm**).
- **Tangerang Selatan** has the highest city-level average precipitation (**7.61 mm**), while **Kota Serang** has the lowest (**5.31 mm**).
- **Kota Serang** has the highest city-level average temperature (**27.15 °C**); **Kab. Pandeglang** has the lowest (**25.36 °C**).
- The exported data-quality report records **zero missing values across the 22 listed columns**. This does not by itself establish measurement accuracy or prove that every city-date key is unique.

## 1. Dataset coverage

The exported city summary contains the following locations:

| Location | Records | Mean temperature (°C) | Mean precipitation (mm) | Wet-day records (%) |
| --- | ---: | ---: | ---: | ---: |
| Kab. Pandeglang | 2,555 | 25.36 | 6.53 | 91.94 |
| Kota Cilegon | 2,555 | 26.56 | 6.54 | 91.51 |
| Kota Serang | 2,555 | 27.15 | 5.31 | 89.55 |
| Kota Tangerang | 2,555 | 26.73 | 7.37 | 90.29 |
| Provinsi Banten (Titik Tengah) | 2,555 | 26.32 | 6.62 | 87.28 |
| Rangkasbitung (Lebak) | 2,555 | 26.49 | 7.10 | 86.69 |
| Tangerang Selatan | 2,555 | 26.81 | 7.61 | 88.45 |

Each location contributes 2,555 records, totaling 17,885 city-day records. The period shown by the notebook output is 3 January 2019 through 31 December 2025.

## 2. Monthly weather profile

Monthly values below are averages per city-day record grouped by calendar month.

| Month | Mean temperature (°C) | Mean precipitation (mm) | Mean maximum wind speed* |
| --- | ---: | ---: | ---: |
| Jan | 25.89 | 10.41 | 14.29 |
| Feb | 25.86 | 10.65 | 13.39 |
| Mar | 26.14 | 9.08 | 13.38 |
| Apr | 26.47 | 7.25 | 12.12 |
| May | 26.77 | 6.16 | 10.90 |
| Jun | 26.32 | 5.04 | 10.60 |
| Jul | 26.46 | 3.18 | 11.71 |
| Aug | 26.83 | 2.92 | 12.54 |
| Sep | 27.01 | 4.09 | 13.16 |
| Oct | 27.22 | 5.19 | 13.67 |
| Nov | 26.66 | 7.54 | 14.42 |
| Dec | 26.20 | 9.47 | 14.75 |

*The wind-speed field is `windspeed_10m_max`; confirm the source data dictionary for its unit.

**Interpretation:** the monthly average precipitation is highest in February and lowest in August. The monthly average temperature reaches its maximum in October and its minimum in February. These are patterns in this dataset, not a causal explanation or a forecast.

## 3. City comparison

- Tangerang Selatan has the highest average precipitation at **7.61 mm per city-day record**.
- Kota Serang has the lowest average precipitation at **5.31 mm per city-day record**.
- Kota Serang has the highest average temperature at **27.15 °C**.
- Kab. Pandeglang has the lowest average temperature at **25.36 °C**.
- Using the notebook's exploratory wet-day rule (>0.1 mm), Kab. Pandeglang has the largest wet-day percentage (**91.94%**) and Rangkasbitung (Lebak) the smallest (**86.69%**).

The wet-day threshold is an analysis convention used in this notebook. It is not presented as an official rainfall classification.

## 4. Data quality

The supplied `data_quality_report.csv` contains 22 columns, all with **0 missing values (0.0%)** in the cleaned data represented by that report.

This result addresses missingness only. It does not confirm:

- whether the original measurements are accurate;
- whether units are consistent with the intended interpretation;
- whether repeated city-date keys exist with differing values;
- whether the source data are suitable for operational decisions.

The expanded notebook now adds a separate city-date coverage and duplicate-key check. Re-run the notebook to generate `city_day_coverage_report.csv` and inspect that result before claiming full temporal completeness.

## 5. IQR outlier screening

The supplied global IQR report flags the following values for review:

| Variable | Lower IQR bound | Upper IQR bound | Flagged values | Flagged (%) |
| --- | ---: | ---: | ---: | ---: |
| `temperature_2m_mean` | 23.85 | 29.05 | 351 | 1.96 |
| `precipitation_sum` | -11.90 | 22.50 | 961 | 5.37 |
| `windspeed_10m_max` | 2.05 | 23.25 | 295 | 1.65 |
| `cape_proxy_radiation` | 9.47 | 27.87 | 634 | 3.54 |

IQR is a screening technique, not a data-error detector. A high rainfall value may represent a real weather event. The mathematically calculated lower precipitation bound is negative; precipitation itself should not be negative, so the meaningful side of this IQR flag range should be reviewed against the actual observations and source conventions. Do not delete flagged records automatically.

The name `cape_proxy_radiation` is treated as a proxy label from the dataset. Its physical meaning and unit require confirmation from a data dictionary.

## 6. Further analysis added to the notebook

The notebook has been extended to produce:

- per-city calendar coverage and duplicate city-date checks;
- annual average profiles for temperature, rainfall, and wind;
- a city-by-month precipitation heatmap;
- rainfall quantiles and wet-day frequency by city;
- Spearman correlation alongside Pearson correlation;
- city-specific IQR outlier screening;
- additional CSV exports in `analysis_outputs/`.

Run all notebook cells to generate these new outputs locally. The analysis notebook does not retrain or validate the CNN-LSTM model; model evaluation must be performed separately with a chronological holdout set.

## Reproducibility

From the repository root on Windows CMD:

```cmd
python -m venv .venv-analysis
.venv-analysis\Scripts\activate
python -m pip install --upgrade pip
python -m pip install -r requirements-analysis.txt
python -m jupyter lab notebooks/Weather_Data_Analysis.ipynb
```

The optional analysis environment is separate from the Django/TensorFlow application environment. Generated CSVs are written to `analysis_outputs/` and are not committed by default.


## 7. Extended analysis results (notebook run)

The extended notebook was run against the same 17,885-row cleaned dataset. The following results come from the generated CSV files in `analysis_outputs/`.

### City-date coverage

All seven locations have 2,555 unique dates out of 2,555 expected dates in the dataset interval. Every location therefore has 100% date coverage for **3 January 2019 – 31 December 2025**. The coverage report records zero missing dates and zero duplicate city-date rows for each location.

This result confirms date-key completeness within the dataset's stated interval; it does not independently verify the provenance or accuracy of the underlying weather measurements.

### Annual averages

| Year | Mean temperature (°C) | Mean precipitation (mm per city-day record) | Mean maximum wind speed* |
| --- | ---: | ---: | ---: |
| 2019 | 26.79 | 4.81 | 12.65 |
| 2020 | 26.39 | 8.04 | 12.40 |
| 2021 | 26.16 | 6.95 | 12.23 |
| 2022 | 26.02 | 7.24 | 13.04 |
| 2023 | 26.81 | 5.09 | 13.51 |
| 2024 | 26.90 | 7.01 | 13.10 |
| 2025 | 26.37 | 7.93 | 13.44 |

The highest annual mean temperature in this dataset occurs in 2024 (26.90 °C), while the lowest occurs in 2022 (26.02 °C). The highest annual mean precipitation occurs in 2020 (8.04 mm per city-day record), and the lowest occurs in 2019 (4.81 mm per city-day record). These annual values are descriptive summaries, not evidence of a long-term climate trend.

*The unit for `windspeed_10m_max` must be confirmed in the source data dictionary.

### Rainfall distribution

The generated rainfall quantiles are:

| Percentile | Precipitation (mm) |
| ---: | ---: |
| 25th | 1.0 |
| 50th (median) | 3.6 |
| 75th | 9.6 |
| 90th | 17.3 |
| 95th | 23.2 |
| 99th | 37.3 |
| Maximum | 200.3 |

The distribution is right-skewed: a relatively small number of high-rainfall observations extend the upper tail. The maximum value should be checked against source records and meteorological context rather than removed automatically.

### Pearson and Spearman correlation

Selected coefficients from the generated matrices:

| Variable pair | Pearson | Spearman |
| --- | ---: | ---: |
| Temperature and precipitation | -0.442 | -0.522 |
| Temperature and `cape_proxy_radiation` | +0.640 | +0.624 |
| Precipitation and `cape_proxy_radiation` | -0.504 | -0.552 |
| Wind speed and precipitation | -0.026 | -0.078 |

The negative coefficients for temperature versus precipitation describe an inverse association in the pooled records. The proxy variable's meaning remains subject to source metadata. City and seasonal effects may influence pooled correlations, so these coefficients should not be interpreted as causal or as isolated within-city relationships.

### City-level outlier screening

For precipitation, the city-specific IQR screening flags the following share of records:

| Location | Flagged values | Flagged (%) |
| --- | ---: | ---: |
| Kab. Pandeglang | 150 | 5.87 |
| Kota Cilegon | 152 | 5.95 |
| Kota Serang | 176 | 6.89 |
| Kota Tangerang | 97 | 3.80 |
| Provinsi Banten (Titik Tengah) | 171 | 6.69 |
| Rangkasbitung (Lebak) | 120 | 4.70 |
| Tangerang Selatan | 104 | 4.07 |

These observations are review candidates, not confirmed errors. A high rainfall amount may be a real event.

### Reproducibility note

The extended notebook generated the following additional outputs: `city_day_coverage_report.csv`, `annual_weather_profile.csv`, `monthly_city_precipitation.csv`, `rainfall_quantiles.csv`, `rainfall_by_city.csv`, `weather_correlation_pearson.csv`, `weather_correlation_spearman.csv`, and `city_outlier_report.csv`. These files remain local generated outputs under `analysis_outputs/`; rerun the notebook to regenerate them.
