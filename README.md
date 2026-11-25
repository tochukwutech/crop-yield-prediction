# Climate-Based Crop Yield Analysis in Nigeria

## Project status

This project has assembled and explored Nigeria crop-yield data, joined state-level rainfall and temperature summaries, compared a crop-median reference with a pre-plant climate model, and built a local Streamlit prototype. The current evidence does not show that the tested climate model improves overall predictive accuracy over the crop-median baseline. The prototype is therefore an exploratory planning aid, not a validated farm-level forecasting service.

## Research question

Can crop and state identifiers plus climate summaries available before planting improve estimates of recorded crop yield in Nigeria? The current model uses the mean state annual rainfall and mean temperature for the three complete years before planting. Its target is HarvestStat Africa v1.2 yield, in metric tonnes per hectare. The model excludes production, area, QC flags, and target-year climate from its predictors.

## Data

- `data/raw/hvstat_africa_data_v1.2.csv`: source HarvestStat Africa data.
- `data/processed/harveststat_nigeria.csv`: Nigeria extract, 9,636 records, 20 crops, 37 admin-1 areas, 1999–2023.
- `data/raw/boundaries/`: HarvestStat Africa v1.2 administrative boundaries used for climate aggregation.
- `data/raw/chirps/`: monthly CHIRPS raster inputs. `-9999` is treated as missing in the climate exploration workflow.
- `data/raw/nasa_power/`: state-point monthly NASA POWER source responses.
- `data/processed/climate/`: state-month and state-year climate tables, exploratory joins, and candidate modeling tables.

The modeling comparison focuses on Cassava, Cowpea, Groundnuts (In Shell), Maize, Millet, Rice, Sorghum, and Yams. The exploration notebooks document missing fields, crop and season coverage, yield distributions, unusual values, and climate coverage. Outlier checks are review prompts; they do not automatically alter source values. HarvestStat v1.2 defines area in hectares, production in metric tonnes, yield in metric tonnes per hectare, and QC flags as 0 (no flag), 1 (outlier), and 2 (low variance). A QC-0 record is not thereby guaranteed error-free.

## Modeling and evaluation

`notebooks/04_preplant_model_pipeline.ipynb` is the clearest current account of the three-year pre-plant experiment. The comparison trains through 2018 and validates on 2019–2020. The 2021–2023 comparison was examined previously and is a reproduction, not an untouched test set. It must not be used to select new features or tune models and then presented as independent final evidence.

The checked-in results show:

| Period and records | Crop-median baseline MAE / RMSE / R² | Crop-state-climate model MAE / RMSE / R² |
| --- | ---: | ---: |
| Validation 2019–2020, all records (483) | 1.164 / 2.278 / 0.513 | 1.205 / 2.726 / 0.302 |
| Validation 2019–2020, QC-0 (381) | 0.892 / 1.877 / 0.677 | 0.873 / 1.974 / 0.643 |
| Previously examined 2021–2023, all records (726) | 1.106 / 2.175 / 0.609 | 1.146 / 2.623 / 0.431 |
| Previously examined 2021–2023, QC-0 (679) | 1.023 / 2.060 / 0.651 | 1.040 / 2.361 / 0.541 |

MAE and RMSE are in mt/ha. Across the full validation set and previously examined period, the crop-median baseline has lower overall error. Crop-level results vary; no broad climate-model advantage is established. This is evidence about the specific data, features, and model tested, not evidence that climate has no relationship with yield.

## Notebooks and outputs

1. `notebooks/01_data_exploration.ipynb`: agricultural data coverage, QC, yield distributions, regional and year patterns.
2. `notebooks/02_climate_data_exploration.ipynb`: source coverage and preparation of state-level climate summaries.
3. `notebooks/03_preplant_model_preparation.ipynb`: candidate feature preparation and earlier experiments. Some statements describe 2021–2023 as an untouched final test; those statements are stale because the period has since been examined. Read the later clarification in notebook 04 and do not treat those historical scores as fresh test evidence.
4. `notebooks/04_preplant_model_pipeline.ipynb`: current three-year feature definition, validation, historical reproduction, results, and limitations.

Key tables are in `results/tables/`; model setup and evaluation-period notes are in `models/preplant_pipeline_metadata.json`. The `nigeria_preplant_candidate.csv` and `nigeria_preplant_model_table.csv` files retain earlier one-year climate features and are not interchangeable with notebook 04's three-year features. Check feature definitions before using either file.

## Local prototype

The Streamlit app in `app.py` rebuilds the three-year Random Forest from project CSV inputs and presents its estimate alongside a crop-median reference. Inputs are state-level, not farm-level. Its estimate should be interpreted as exploratory context; farm conditions, within-season weather, soils, varieties, inputs, and management are not represented.

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
python -m src.run_pipeline
streamlit run app.py
```

For the app only, install `requirements-app.txt` instead. To run notebook 04, start Jupyter from the repository root so the local `src` package is importable. Raw climate ingestion and raster preparation remain documented in notebook 02 and require the supplied raw files; the scoring command above rebuilds the modeling table and evaluation tables from the checked-in processed CSV inputs without network access.

The bundled climate data end in 2023. With yields through 2023, the present app can construct the three prior years for planting year 2024 only. Refresh and quality-check climate inputs before supporting a later year.

## Recommended work sequence

1. Reconcile the source documentation, code, metadata, and notebook language; keep unit and QC definitions consistent.
2. Establish one reproducible data-preparation and training entry point so the notebook, CSV outputs, metadata, and app share the same feature construction.
3. Review climate coverage and aggregation assumptions; compare predeclared seasonal rainfall and temperature summaries with the annual features, without using already examined years for model selection.
4. Evaluate candidate changes using rolling-origin validation within the historical training period, then reserve a genuinely later untouched period if new yield observations become available.
5. Report crop-specific metrics, sample counts, error distributions, and uncertainty alongside pooled scores. Keep the crop-median baseline as the benchmark unless a model demonstrates stable gains.
6. Refresh the README, results, and app’s supported forecast years whenever inputs or modeling choices change.

See `report/project_assessment.md` for the detailed findings and `report/next_steps.md` for the implementation sequence.
The formal project report is `report/final_report.md`.

## Team

- David Offor (Project Lead)
- Fahd Animashaun
- Faisal Farouk-Muazu
- Muhammed-Faiz Oyebanji
