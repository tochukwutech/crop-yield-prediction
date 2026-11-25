# Next Steps: Implementation Plan

## Priority 1: Set a single source of truth

1. Use the three-year pre-plant feature definition in notebook 04 as the current experiment, unless the team explicitly selects another definition.
2. Regenerate the current modeling table from raw/processed source inputs and save the exact feature names, source versions, date range, row counts, crop list, and split definitions in metadata.
3. Label one-year candidate tables as historical experiments or move them to an archive directory; do not leave ambiguous outputs alongside current results.
4. Refactor the feature construction, model creation, and scoring logic into `src/` functions. Have the notebook and Streamlit app call those shared functions so there is one implementation.
5. Add a small command-line entry point that rebuilds tables and scores from existing local inputs without network access. Keep downloading/updating source data as a separate explicit step.

## Priority 2: Lock down input quality and source definitions

1. Preserve raw inputs and record source URLs, release/version, retrieval date, and file checksums in a data manifest.
2. Validate expected columns, units, missing-value codes, duplicate keys, year continuity, boundary identifiers, and climate coverage before building features.
3. Reconcile every unit and QC statement with the cited HarvestStat v1.2 source documentation and keep the same definitions in README, notebooks, metadata, and the app.
4. Treat the QC-0 subset as a sensitivity analysis. Keep all eligible values in the primary analysis unless a documented, predeclared data-quality rule supports exclusion.
5. Investigate crop-season and crop-state coverage gaps and document which observations are dropped at each join or eligibility step.

## Priority 3: Establish evaluation discipline

1. Keep 2019–2020 as development validation and label 2021–2023 as previously examined in every artifact.
2. Do not tune or select new features, hyperparameters, or crop filters against the existing 2021–2023 results.
3. Compare proposed features using rolling-origin validation inside years that can be considered development data; report fold years and eligible sample counts.
4. Pre-register the modeling choices before any new evaluation. If fresh yield records beyond 2023 become available, reserve those later years as the untouched prospective test.
5. Report MAE, RMSE, and R² overall and per crop, plus a distribution of absolute errors and a clear sample count. Consider normalized or crop-relative metrics alongside mt/ha because crop scales differ substantially.
6. Compare every candidate against at least the crop-median baseline. Retain a more complex model only if gains are stable across folds and useful for the intended decision.

## Priority 4: Test more relevant climate features

1. Keep the current three-year annual summary as the reference experiment.
2. Define crop-season windows before calculating monthly climate features. Use planting month/season information where reliable, and keep all input dates strictly before the prediction date.
3. Evaluate rainfall totals, temperature summaries, variability, and dry-spell or extreme indicators only when source coverage and definitions are defensible.
4. Consider state-specific historical yield baselines or hierarchical/mixed-effect approaches as candidates, with safeguards for sparse state-crop histories.
5. Document climate aggregation choices (area weighting, boundary rasterization, grid-cell treatment, missingness, and point sampling) and test whether they materially change the resulting features.

## Priority 5: Clarify prototype boundaries

1. Keep the baseline and climate estimate side by side, with the evaluation limitation visible.
2. Label both results as state-level estimates in mt/ha and explain that multiplying by farm area is arithmetic, not an improvement in prediction precision.
3. Show the historical number of eligible records and a historical spread separately from any model uncertainty; do not present the historical range as a prediction interval.
4. Refuse unsupported planting years until the climate inputs cover the required history and report the latest climate and yield years used.
5. Avoid crop-choice recommendations or farm-specific guarantees based on the current model.

## Priority 6: Package the research for handoff

1. Update notebooks 01–04 so their narrative agrees on the target, units, QC codes, features, and status of evaluation years.
2. Replace notebook 03's stale “untouched final test” language for 2021–2023 with “previously examined period.”
3. Add a short data dictionary and a reproducibility section with environment setup, notebook order, data refresh steps, and commands to rebuild results.
4. Split dependencies into a manageable requirements file and record a tested Python version/environment lock.
5. Refresh the report and result tables whenever the analysis changes; retain prior results with version/date labels rather than silently overwriting their meaning.

## Suggested completion criteria for the next milestone

- One command rebuilds the current feature table and evaluation tables from versioned local inputs.
- The notebook, app, and metadata agree on features, units, target, crop list, and supported years.
- Join/coverage checks produce a short auditable summary, including dropped-row counts.
- Validation results are reported per crop and overall against the baseline.
- No already examined years are described as an untouched test set.
- The app clearly reports the evidence limits and refuses unsupported forecast years.
