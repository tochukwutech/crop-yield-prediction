# HarvestStat Nigeria: outstanding work update

This update supplements `investigation_report.docx` and supersedes its statements that the HarvestStat measurement units and `qc_flag` meanings are unconfirmed, and that the GROW-Africa comparison has not begun.

## HarvestStat measurement units and QC flags

The official HarvestStat Africa documentation confirms:

| Field | Definition |
|---|---|
| `area` | Cropped area, hectares (ha) |
| `production` | Crop production, metric tonnes (mt) |
| `yield` | Crop yield, metric tonnes per hectare (mt/ha) |
| `qc_flag = 0` | No flag |
| `qc_flag = 1` | Outlier |
| `qc_flag = 2` | Low variance |

These definitions are documented in the HarvestStat Africa publication and the official v1.2 release notes/readme. The 9,636-row Nigeria extract contains 9,020 records with flag 0, 18 with flag 1, and 598 with flag 2. The prepared files retain every original row and QC code. Flag meanings are metadata; they do not on their own dictate whether observations should be excluded from the modelling dataset.

The official project documentation also clarifies that planting and harvest year/month fields reflect standardized FEWS NET crop-calendar metadata, not observed phenological dates. Do not interpret the Nigeria-wide March and October values as crop-specific planting and harvest dates without further source evidence.

## GROW-Africa comparison

The official GROW-Africa v2.0 record describes 535,844 georeferenced crop-yield observations covering 25 crops and 1960–2023. Its database includes LSMS crop-cut records, LSMS farmer surveys, other point observations, and regional statistics. The paper identifies Nigeria among the countries represented in the LSMS-ISA survey component. The World Bank lists Nigerian General Household Survey Panel waves in 2010–11, 2012–13, 2015–16, and 2018–19. GROW-Africa's regional series are compiled in part from HarvestStat, as well as FAO/Agro-MAPS and ReSAKSS Country eAtlases.

Compared with this Nigeria HarvestStat extract (20 crops, 1999–2023, 37 first-level regions, and no usable `admin_2` values), the clearest expected benefit is **different observation types and finer potential geography**: GROW-Africa includes survey/plot and point observations linked to coordinates and nested administrative IDs, while the HarvestStat Nigeria extract is aggregated to first-level regions. The cited Nigerian survey waves fall within HarvestStat's 1999–2023 time span, so the evidence reviewed does not establish a longer Nigerian time series. GROW-Africa's Africa-wide crop list is broader, but its documentation alone does not prove which of those additional crops occur in Nigeria. The regional GROW-Africa file partly reuses HarvestStat, so combining regional rows without source-level deduplication could double-count observations.

**Assessment:** GROW-Africa is a useful candidate complement for Nigerian plot/household observations and potentially finer spatial coverage, especially if the project benefits from those data types. It is not established as a source of additional Nigerian years or crop types from the documentation alone. Before merging, filter GROW-Africa to Nigeria, summarize valid records by crop/year/geographic level/source, identify HarvestStat-derived regional rows, harmonize units and crop labels, and quantify overlap. The published dataset README identifies the required source tables and geographic lookup tables.

## Evidence and sources

- HarvestStat Africa v1.2 repository and release documentation: <https://github.com/HarvestStat/HarvestStat-Africa>
- HarvestStat Africa data paper: <https://pmc.ncbi.nlm.nih.gov/articles/PMC12022251/>
- GROW-Africa v2.0 record and files: <https://zenodo.org/records/16544448>
- GROW-Africa README: <https://zenodo.org/records/16544448/files/readme.txt?download=1>
- GROW-Africa data paper: <https://www.nature.com/articles/s41597-025-05257-5>
- GROW-Africa data paper (PMC full text): <https://pmc.ncbi.nlm.nih.gov/articles/PMC12215972/>
- World Bank Nigeria LSMS-ISA survey waves: <https://www.worldbank.org/en/programs/lsms/initiatives/lsms-ISA>

## Remaining publication and integration items

- The original project request does not identify Fahd's assigned branch in the repository. The previously suggested name `feature/yield-data` was not present on the remote when checked; this work is prepared on that branch locally for review.
- A Nigeria-specific record-level GROW-Africa coverage/overlap table still needs to be generated before claiming exact incremental counts.
- The climate-data spatial crosswalk and final crop-calendar interpretation remain integration tasks.
