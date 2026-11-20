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

The official GROW-Africa v2.0 record describes 535,844 georeferenced crop-yield observations covering 25 crops and 1960–2023. Its database includes LSMS crop-cut records, LSMS farmer surveys, other point observations, and regional statistics. The regional series are compiled in part from HarvestStat, as well as FAO/Agro-MAPS and ReSAKSS Country eAtlases.

Compared with this Nigeria HarvestStat extract (20 crops, 1999–2023, 37 first-level regions, and no usable `admin_2` values), GROW-Africa is a promising complement for point- or plot-level observations and potentially finer geographic detail. Its Africa-wide crop list also includes crops beyond the 20 observed here. However, the catalog-level metadata does not establish that those extra crops, earlier years, or finer spatial units are actually present in its Nigerian records. The regional GROW-Africa file also partly reuses HarvestStat, so combining its regional records with this extract without source-level deduplication could double-count observations.

**Assessment:** GROW-Africa may add useful Nigerian survey/point evidence and possibly finer geography, but additional Nigerian coverage has not been demonstrated at the record level yet. Treat the two datasets as separate sources for now. Before merging, filter GROW-Africa to Nigeria, summarize valid records by crop/year/geographic level/source, identify HarvestStat-derived regional rows, harmonize units and crop labels, and quantify overlap. The published dataset README identifies the required source tables and geographic lookup tables.

## Evidence and sources

- HarvestStat Africa v1.2 repository and release documentation: <https://github.com/HarvestStat/HarvestStat-Africa>
- HarvestStat Africa data paper: <https://pmc.ncbi.nlm.nih.gov/articles/PMC12022251/>
- GROW-Africa v2.0 record and files: <https://zenodo.org/records/16544448>
- GROW-Africa README: <https://zenodo.org/records/16544448/files/readme.txt?download=1>
- GROW-Africa data paper: <https://www.nature.com/articles/s41597-025-05257-5>

## Remaining publication and integration items

- The original project request does not identify Fahd's assigned branch in the repository. The previously suggested name `feature/yield-data` was not present on the remote when checked; this work is prepared on that branch locally for review.
- A Nigeria-specific record-level GROW-Africa coverage/overlap table still needs to be generated before claiming exact incremental counts.
- The climate-data spatial crosswalk and final crop-calendar interpretation remain integration tasks.
