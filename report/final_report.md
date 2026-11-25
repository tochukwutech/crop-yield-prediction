# Climate-Based Crop Yield Estimation in Nigeria

## Abstract

This study examines whether prior climate summaries improve estimates of crop yield for selected crops in Nigeria. HarvestStat Africa v1.2 yield observations were matched to state-level annual rainfall and temperature summaries from CHIRPS and NASA POWER. The evaluated Random Forest uses crop, state, and the mean annual rainfall and mean annual temperature over the three years before planting. It is compared with a crop-median baseline using chronological training and validation periods. On 2019–2020 validation data, the baseline had lower pooled MAE and RMSE and higher R² than the climate model. The 2021–2023 comparison was examined earlier in project experimentation and is reported as a historical reproduction, not an untouched final test. The results do not establish an overall predictive advantage for the climate features tested. They support continued exploratory work and careful validation rather than farm-level deployment claims.

## 1. Introduction

Crop yields respond to weather alongside soil, seed variety, pests, inputs, and management. Understanding whether available climate records improve yield estimates can support agricultural analysis, but the value of a model depends on the quality and scale of both the agricultural observations and climate predictors. This project studies historical Nigerian crop yields at state level and compares a simple reference estimate with a climate-informed model.

The research question is: **Do crop and state identifiers plus climate summaries observed before planting improve estimates of recorded yield for selected Nigerian crops?** The work is predictive and observational. It does not estimate the causal effect of climate on yield.

## 2. Data

### 2.1 Agricultural observations

The project uses the Nigeria extract from HarvestStat Africa v1.2. The processed file contains 9,636 records across 20 crops and 37 first-level administrative areas, spanning 1999–2023. The modeling subset contains Cassava, Cowpea, Groundnuts (In Shell), Maize, Millet, Rice, Sorghum, and Yams. HarvestStat v1.2 defines area in hectares, production in metric tonnes, and yield in metric tonnes per hectare (mt/ha). The stated QC codes are 0 (no flag), 1 (outlier), and 2 (low variance). QC flags are excluded from predictors; QC-0-only results are sensitivity analyses.

Notebook 01 reports 615 missing yields, 525 missing area values, and 90 missing production values in the extract. It also reports no exact or composite duplicates, no nonpositive values, and no mismatch in yield arithmetic among complete cases. These checks describe the processed extract and should be regenerated from source inputs when the data pipeline is rerun.

### 2.2 Climate observations

Monthly rainfall is derived from CHIRPS raster inputs and summarized by state using HarvestStat administrative boundaries. Monthly temperature (T2M, T2M_MAX, T2M_MIN) comes from NASA POWER state-point series. Processed outputs include 11,100 state-month records and 925 state-year records, with climate data through 2023. The climate notebook treats raster value −9999 as missing rather than zero and notes that NASA POWER values are point estimates while CHIRPS values are state-area summaries. This difference in spatial support is a limitation.

### 2.3 Integration and eligibility

The current feature pipeline matches eligible yield records to state annual climate by FNID, state, and planting year. It calculates prior-three-year means using years t−1, t−2, and t−3 only. A state-year climate key must be unique, and incomplete prior climate rows are excluded. The target is yield; area and production are excluded as predictors because yield is derived from those values. Planting year defines chronological periods, while the QC flag is retained for sensitivity analysis only.

## 3. Methods

The baseline predicts the crop median calculated from training records only. The climate model is a scikit-learn pipeline with one-hot encoded crop and state plus two numeric climate features. It uses a Random Forest with 300 trees, minimum leaf size 5, and random seed 42. Both methods are scored on the same eligible records using mean absolute error (MAE), root mean squared error (RMSE), and coefficient of determination (R²). Lower MAE/RMSE and higher R² indicate better fit for the evaluated records.

The chronological development comparison trains on planting years 2000–2018 and validates on 2019–2020. A QC-0-only sensitivity analysis repeats the comparison on records carrying flag 0. The 2021–2023 comparison trains through 2020 and reproduces a period already examined during project experimentation. It is not independent final test evidence and must not be used for additional feature or model selection.

## 4. Results

| Evaluation period | Records | Model | MAE (mt/ha) | RMSE (mt/ha) | R² |
| --- | ---: | --- | ---: | ---: | ---: |
| Validation 2019–2020, all eligible | 483 | Crop-median baseline | 1.164 | 2.278 | 0.513 |
| Validation 2019–2020, all eligible | 483 | Crop, state, and prior-three-year climate | 1.205 | 2.726 | 0.302 |
| Validation 2019–2020, QC-0 only | 381 | Crop-median baseline | 0.892 | 1.877 | 0.677 |
| Validation 2019–2020, QC-0 only | 381 | Crop, state, and prior-three-year climate | 0.873 | 1.974 | 0.643 |
| Previously examined 2021–2023, all eligible | 726 | Crop-median baseline | 1.106 | 2.175 | 0.609 |
| Previously examined 2021–2023, all eligible | 726 | Crop, state, and prior-three-year climate | 1.146 | 2.623 | 0.431 |
| Previously examined 2021–2023, QC-0 only | 679 | Crop-median baseline | 1.023 | 2.060 | 0.651 |
| Previously examined 2021–2023, QC-0 only | 679 | Crop, state, and prior-three-year climate | 1.040 | 2.361 | 0.541 |

For the complete 2019–2020 validation set, the crop-median baseline outperforms the climate model on all three pooled metrics. Within QC-0 validation records, climate has slightly lower MAE but higher RMSE and lower R². In the previously examined 2021–2023 period, the crop-median baseline again has lower pooled MAE and RMSE and higher R², both overall and for QC-0 records. Crop-specific scores are mixed. Since crops have very different yield scales, pooled metrics should be interpreted alongside crop-specific scores and sample counts.

## 5. Discussion

The tested prior annual climate summaries did not produce a stable overall improvement over the crop-median baseline. This does not show that climate is unrelated to yield. It shows that these two annual summaries, combined with crop and state identifiers in this model and dataset, did not yield better overall predictions in the reported comparisons. Possible next features include predeclared crop-season rainfall and temperature summaries, variability, and extremes, provided they are defined using only information available at the prediction date.

Several limitations constrain interpretation. Crop reporting coverage varies by year and state; missing yields reduce eligible rows. State-level predictors and targets cannot describe within-state or farm-level variation. Annual means obscure crop-season timing and weather extremes. NASA POWER point temperatures and CHIRPS state-area rainfall have different spatial supports. QC-0 means no assigned flag, not independently verified accuracy. Finally, 2021–2023 has already been examined and therefore cannot serve as a fresh untouched test for future experiments.

## 6. Conclusion and recommendations

The project assembled and explored relevant agricultural and climate data, built a pre-plant prediction comparison, and implemented an explanatory local prototype. In the evaluated comparisons, the crop-median baseline is the stronger pooled reference. The climate model should remain experimental until a prespecified feature set shows stable gains across development folds and a genuinely new later period.

Recommended work is to make data preparation and evaluation reproducible from shared code, reconcile earlier one-year and current three-year tables, validate seasonal climate aggregation, report crop-level error and uncertainty, and reserve future observations for prospective testing. The Streamlit app should continue to present estimates as state-level planning references, not farm-specific guarantees.

## References

1. Lee, D., Anderson, W., Chen, X., et al. (2024). *HarvestStat Africa: Harmonized subnational crop statistics for Sub-Saharan Africa* [Dataset, version 1.2]. Dryad. https://doi.org/10.5061/dryad.vq83bk42w
2. Funk, C., Peterson, P., Landsfeld, M., et al. (2015). The climate hazards infrared precipitation with stations—a new environmental record for monitoring extremes. *Scientific Data, 2*, 150066. https://doi.org/10.1038/sdata.2015.66
3. NASA Langley Research Center. (n.d.). *Prediction Of Worldwide Energy Resources (POWER)*. https://power.larc.nasa.gov/
4. Climate Hazards Center, UC Santa Barbara. (n.d.). *CHIRPS precipitation data*. https://chc.ucsb.edu/data/chirps/
5. Climate Hazards Center. (n.d.). *CHIRPS version 3 data record*. https://doi.org/10.15780/G2JQ0P

## Reproducibility note

The checked-in raw HarvestStat file is version 1.2 and the processed monthly climate files span 1999–2023. The notebook documents CHIRPS v3 and NASA POWER, but exact download dates and NASA POWER API request metadata are not consistently recorded in the files; retrieve dates cannot be established from the current project artifacts. The statistics below are therefore tied to the checked-in files, not a claimed new data refresh. Metric values are generated into `results/tables/preplant_model_comparison.csv` by `python -m src.run_pipeline` from the repository root after installing `requirements.txt`. A local reproduction in the current environment yielded small differences in the last decimal places from the previously saved results. Notebook 04 documents the detailed analysis. The 2021–2023 values are explicitly historical reproductions, not fresh test evidence.
