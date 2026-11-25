# Project Assessment: Climate-Based Crop Yield Analysis in Nigeria

## Executive summary

The project has progressed from setup to an end-to-end research prototype. It includes a Nigeria HarvestStat extract, aligned administrative boundaries, CHIRPS rainfall and NASA POWER temperature inputs, exploratory notebooks, a time-aware model comparison, saved results, and a Streamlit interface.

The central result is cautious: a Random Forest using crop, state, and three-year prior annual climate averages did not improve overall prediction accuracy over a crop-median baseline in the recorded comparisons. The interface appropriately displays both estimates and warns users about the climate model's limitations. The project should now prioritize reproducibility, evaluation discipline, and better-defined climate features before extending claims or practical use.

## Project question and current method

The question is whether crop and state identifiers plus climate information available before planting can help estimate the recorded yield for a crop-state-year. The latest pipeline in notebook 04 uses the average annual rainfall and annual mean temperature for years t−1, t−2, and t−3. The model uses one-hot encoded crop and state identifiers plus those two numeric values, with a Random Forest of 300 trees and minimum leaf size 5.

The supervised target is HarvestStat yield. The evaluation excludes production and area from the predictors because yield is derived from these quantities, and excludes the QC flag from predictors. QC-0-only comparisons are sensitivity analyses. The documented units are area in hectares, production in metric tonnes, and yield in metric tonnes per hectare. The documented QC codes are 0 (no flag), 1 (outlier), and 2 (low variance).

## Data inventory and preparation

The processed agricultural extract has 9,636 rows, 16 columns, 20 crops, 37 first-level regions, and reported years from 1999 through 2023. The eight modeled crops are Cassava, Cowpea, Groundnuts (In Shell), Maize, Millet, Rice, Sorghum, and Yams. The exploration notebook reports 615 missing yield records, 525 missing areas, and 90 missing production values. It reports no exact or composite duplicates, no nonpositive values, and no yield arithmetic mismatch among 9,021 complete rows. These are notebook findings and should be regenerated from the source as part of a reproducible pipeline.

Climate outputs include 11,100 state-month rows in CHIRPS rainfall, NASA POWER temperature, and merged monthly tables, plus 925 annual state-year rows. The processed monthly series spans 1999–2023. The boundary notebook records a match between the 37 Nigeria admin-1 boundary identifiers and the agricultural extract. CHIRPS missing raster cells marked −9999 are treated as missing, not as zero rainfall.

One important artifact mismatch remains: `nigeria_preplant_candidate.csv` and `nigeria_preplant_model_table.csv` carry prior-year climate features, whereas the latest evaluation and app compute prior-three-year means. These files should be renamed, regenerated, or clearly marked as earlier experimental outputs so they are not mistaken for the current modeling table.

## Model results

The checked-in comparison table reports the following overall results. MAE and RMSE are in metric tonnes per hectare.

| Evaluation period | Records | Method | MAE | RMSE | R² |
| --- | ---: | --- | ---: | ---: | ---: |
| 2019–2020 validation, all eligible records | 483 | Crop-median baseline | 1.164 | 2.278 | 0.513 |
| 2019–2020 validation, all eligible records | 483 | Crop, state, and prior-three-year climate | 1.205 | 2.726 | 0.302 |
| 2019–2020 validation, QC-0 only | 381 | Crop-median baseline | 0.892 | 1.877 | 0.677 |
| 2019–2020 validation, QC-0 only | 381 | Crop, state, and prior-three-year climate | 0.873 | 1.974 | 0.643 |
| 2021–2023 previously examined period, all eligible records | 726 | Crop-median baseline | 1.106 | 2.175 | 0.609 |
| 2021–2023 previously examined period, all eligible records | 726 | Crop, state, and prior-three-year climate | 1.146 | 2.623 | 0.431 |
| 2021–2023 previously examined period, QC-0 only | 679 | Crop-median baseline | 1.023 | 2.060 | 0.651 |
| 2021–2023 previously examined period, QC-0 only | 679 | Crop, state, and prior-three-year climate | 1.040 | 2.361 | 0.541 |

The baseline is better on all three pooled metrics for the complete validation data and the previously examined 2021–2023 data. On QC-0 validation, climate has a slightly lower MAE but higher RMSE and lower R². Crop-specific scores are mixed. Pooled errors also combine crops with different typical yield scales, so crop-wise metrics and sample counts are essential context.

The 2021–2023 period appears in earlier notebook experimentation and in the later pipeline as a reproduction. It is not a new, untouched test set. A separate narrative in notebook 03 still calls this period an untouched final evaluation; that language is now stale and must not be used to characterize the evidence.

## Strengths

- The notebooks inspect crop, season, region, and year coverage rather than treating the agricultural table as a uniform panel.
- Yield outliers are reviewed in context instead of being removed automatically.
- Climate features in the current pipeline use only years before planting, and the join checks for one climate row per state-year.
- The model comparison uses chronological periods and includes a simple baseline.
- Area, production, and QC flags are excluded as model predictors, reducing direct leakage and inappropriate reliance on quality labels.
- The app shows the baseline beside the climate estimate and describes the state-level and experimental limitations.

## Limitations and open issues

- Overall accuracy is not better than the crop-median baseline in the reported comparisons.
- The most recent evaluation years have already been examined; changing the model based on them would make them unsuitable as independent final evidence.
- Annual state averages discard within-season timing, extremes, dry spells, and local variation that may matter to crop response.
- State-level climate and state-level agricultural statistics cannot support farm-specific claims.
- Crop reporting varies by season and coverage. Sparse crop-state-year records and changes in reporting coverage can affect apparent trends and model errors.
- The current files include competing one-year and three-year feature tables. Their names and documentation do not yet make the distinction sufficiently prominent.
- Existing `src/train.py`, `src/evaluate.py`, and `src/preprocessing.py` are empty, so the reusable pipeline currently lives primarily in notebooks and app code.
- The requirements file pins a broad notebook environment rather than a minimal application/research dependency set; an environment lock and installation check would improve reproducibility.
- The latest climate records end in 2023. With a complete three-year history and training labels through 2023, the prototype presently supports 2024 as its only later planting year.

## Conclusions

This is a credible exploratory analysis and prototype with a useful evidence trail. The tested climate model has not demonstrated a stable overall advantage over the crop-median reference. The most defensible next milestone is a reproducible, clearly versioned evaluation workflow, followed by predeclared tests of seasonal climate features and fresh future-year evidence when new labels are available. Until then, app results should remain clearly labeled as state-level planning references.
