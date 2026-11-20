# HarvestStat Africa v1.2 — Nigeria preparation

## Current scope
- Input: `hvstat_africa_data_v1.2.csv`
- Filter: `country_code == "NG"`
- Nigeria records retained: 9,636 across 20 crops and 1999–2023.
- The processing script retains every Nigerian observation and all original fields. It adds period strings and diagnostic flags; it does not impute, convert units, or delete outliers.

## Outputs
- `harveststat_nigeria_cleaned.csv` — all Nigerian rows plus diagnostic columns.
- `nigeria_crop_frequency_summary.csv` — per-crop record counts, valid yield counts, harvest-year span/count and admin_1 coverage.
- `nigeria_observation_review_flags.csv` — observations flagged by crop-wise 1.5×IQR review rules.
- `data_dictionary.csv` — short field guide.
- `qa_summary.json` — reproducible QA counts.
- `process_harveststat_nigeria.py` — reproducible processing script.
- `investigation_report.docx` — findings and limitations.

## Source documentation follow-up
Official HarvestStat documentation confirms `area` is in hectares (ha), `production` in metric tonnes (mt), and `yield` in metric tonnes per hectare (mt/ha). It defines `qc_flag` as 0 = no flag, 1 = outlier, and 2 = low variance. See `OUTSTANDING_WORK_UPDATE.md` for the source links and GROW-Africa assessment.

The GROW-Africa v2.0 documentation describes an Africa-wide source containing regional statistics, household surveys, and point observations. Its regional data partly incorporate HarvestStat, so do not append regional GROW-Africa rows to this file without source-level deduplication. Exact Nigerian incremental coverage and overlap have not yet been counted.

## QA decisions
- Exact duplicate rows: none.
- Duplicate composite observations (FNID, crop, season, planting/harvest year and month, crop production system): none.
- Missing area: 525; missing production: 90; missing yield: 615.
- Negative or zero area/production/yield values: none.
- Yield formula check: all 9,021 rows with complete yield, production and nonzero area satisfy yield = production / area within floating-point tolerance. This is an arithmetic consistency check only, not a unit confirmation.
- Tukey 1.5×IQR review flags are crop-specific statistical prompts, not deletion rules: yield 311, area 331, production 424. These can reflect genuine crop/region/year differences and should be reviewed with domain context.
- `qc_flag` counts are 0: 9,020; 1: 18; 2: 598. Codes are preserved verbatim and not interpreted because their official definitions were not available.

## Climate integration notes
- Nigeria has 37 distinct `admin_1` values. `admin_2` is `none` for all 9,636 records, so this extract does not support sub-state matching.
- `planting_month` is 3 (March) for all Nigerian rows; `harvest_month` is 10 (October) for all rows. Official HarvestStat documentation says these standardized crop-calendar fields do not represent actual phenological timing. `planting_year` and `harvest_year` match row-by-row in this extract.
- `season_name`: Wet 7,478; Annual 2,158.
- `planting_period` and `harvest_period` are derived YYYY-MM labels, with no day imputed. Monthly climate data can be aligned to these periods, but the season definitions and crop calendars should be verified before interpreting exposure windows.
- A spatial crosswalk from `admin_1`/`fnid` to the climate dataset's spatial units is still required.
