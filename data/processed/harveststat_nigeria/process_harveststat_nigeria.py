"""Prepare and audit Nigeria records from HarvestStat Africa v1.2.

Usage:
  python process_harveststat_nigeria.py input.csv output_directory

No observations are dropped or overwritten. Original columns are retained;
additional columns are diagnostic flags for review and climate matching.
"""
from pathlib import Path
import sys
import pandas as pd
import numpy as np

REQUIRED = [
    "country_code", "country", "admin_1", "admin_2", "product",
    "season_name", "planting_year", "planting_month", "harvest_year",
    "harvest_month", "qc_flag", "area", "production", "yield"
]

def main(input_csv: str, output_dir: str) -> None:
    out = Path(output_dir)
    out.mkdir(parents=True, exist_ok=True)
    raw = pd.read_csv(input_csv, low_memory=False)
    missing_cols = [c for c in REQUIRED if c not in raw.columns]
    if missing_cols:
        raise ValueError(f"Missing required columns: {missing_cols}")

    ng = raw.loc[raw["country_code"].astype(str).str.upper().eq("NG")].copy()
    # Retain every Nigeria row and every original column. Do not impute units or values.
    ng["planting_period"] = (
        ng["planting_year"].astype("Int64").astype(str) + "-" +
        ng["planting_month"].astype("Int64").astype(str).str.zfill(2)
    )
    ng["harvest_period"] = (
        ng["harvest_year"].astype("Int64").astype(str) + "-" +
        ng["harvest_month"].astype("Int64").astype(str).str.zfill(2)
    )
    for col in ["area", "production", "yield"]:
        ng[f"missing_{col}"] = ng[col].isna()
        ng[f"nonpositive_{col}"] = ng[col].notna() & ng[col].le(0)

    # The CSV's own arithmetic establishes yield = production / area numerically;
    # unit semantics remain unconfirmed until the data documentation is checked.
    valid = ng["area"].notna() & ng["production"].notna() & ng["yield"].notna() & ng["area"].ne(0)
    ng["yield_calculated_production_over_area"] = np.where(
        ng["area"].notna() & ng["production"].notna() & ng["area"].ne(0),
        ng["production"] / ng["area"], np.nan
    )
    ng["yield_arithmetic_mismatch"] = False
    ng.loc[valid, "yield_arithmetic_mismatch"] = ~np.isclose(
        ng.loc[valid, "yield"], ng.loc[valid, "yield_calculated_production_over_area"],
        rtol=1e-5, atol=1e-8
    )

    # Flag crop-wise Tukey 1.5*IQR observations for human review, not deletion.
    for col in ["yield", "area", "production"]:
        flag = pd.Series(False, index=ng.index)
        for _, idx in ng.groupby("product").groups.items():
            vals = ng.loc[idx, col].dropna()
            if len(vals) < 4:
                continue
            q1, q3 = vals.quantile([0.25, 0.75])
            iqr = q3 - q1
            lo, hi = q1 - 1.5 * iqr, q3 + 1.5 * iqr
            flag.loc[idx] = ng.loc[idx, col].notna() & (ng.loc[idx, col].lt(lo) | ng.loc[idx, col].gt(hi))
        ng[f"{col}_iqr_outlier_review"] = flag

    # Preserve unknown QC codes verbatim; do not invent meanings.
    ng["qc_flag_interpretation"] = ng["qc_flag"].map({0: "code_0_meaning_unverified", 1: "code_1_meaning_unverified", 2: "code_2_meaning_unverified"}).fillna("unmapped_code_meaning_unverified")

    ng.to_csv(out / "harveststat_nigeria_cleaned.csv", index=False)

    rows = []
    for crop, g in ng.groupby("product", dropna=False):
        years = sorted(g["harvest_year"].dropna().astype(int).unique().tolist())
        regions = sorted(g["admin_1"].dropna().astype(str).unique().tolist())
        rows.append({
            "crop": crop,
            "total_records": len(g),
            "valid_yield_records": int(g["yield"].notna().sum()),
            "years_covered": f"{years[0]}-{years[-1]}" if years else "",
            "number_of_harvest_years": len(years),
            "number_of_geographical_regions": len(regions),
            "geographical_regions": "; ".join(regions),
        })
    pd.DataFrame(rows).sort_values(["total_records", "crop"], ascending=[False, True]).to_csv(
        out / "nigeria_crop_frequency_summary.csv", index=False
    )

    # Row-level review register for outliers or structural issues.
    review_cols = ["fnid", "admin_1", "admin_2", "product", "season_name", "planting_year", "planting_month", "harvest_year", "harvest_month", "qc_flag", "area", "production", "yield", "area_iqr_outlier_review", "production_iqr_outlier_review", "yield_iqr_outlier_review", "yield_arithmetic_mismatch"]
    review = ng.loc[
        ng[["area_iqr_outlier_review", "production_iqr_outlier_review", "yield_iqr_outlier_review", "yield_arithmetic_mismatch"]].any(axis=1)
        | ng[["area", "production", "yield"]].le(0).any(axis=1), review_cols
    ]
    review.to_csv(out / "nigeria_observation_review_flags.csv", index=False)

    # Machine-readable field notes.
    dictionary = pd.DataFrame([
        ("product", "Crop name", "Original source field"),
        ("admin_1", "First-level administrative region; 37 observed values", "Original source field"),
        ("admin_2", "Second-level administrative field; all Nigeria rows are 'none'", "Original source field"),
        ("planting_year", "Planting year", "Original source field"),
        ("planting_month", "Planting month; all Nigeria rows are 3", "Original source field"),
        ("harvest_year", "Harvest year", "Original source field"),
        ("harvest_month", "Harvest month; all Nigeria rows are 10", "Original source field"),
        ("season_name", "Season label: Wet or Annual", "Original source field"),
        ("yield", "Yield; unit unconfirmed from CSV alone", "Original source field"),
        ("production", "Production; unit unconfirmed from CSV alone", "Original source field"),
        ("area", "Area; unit unconfirmed from CSV alone", "Original source field"),
        ("qc_flag", "QC code 0/1/2; meanings unconfirmed without documentation", "Original source field"),
        ("planting_period", "Derived YYYY-MM period; no day inferred", "Derived, for monthly climate joins"),
        ("harvest_period", "Derived YYYY-MM period; no day inferred", "Derived, for monthly climate joins"),
        ("*_iqr_outlier_review", "Crop-specific 1.5*IQR statistical review flag; not an error verdict", "Derived, review only"),
        ("yield_calculated_production_over_area", "Arithmetic ratio when area is present and nonzero", "Derived, not unit confirmation"),
    ], columns=["field", "description", "origin_or_note"])
    dictionary.to_csv(out / "data_dictionary.csv", index=False)

    # concise machine-readable QA summary
    qa = {
        "source_file": Path(input_csv).name,
        "nigeria_records": int(len(ng)),
        "crops": int(ng["product"].nunique()),
        "harvest_year_min": int(ng.harvest_year.min()),
        "harvest_year_max": int(ng.harvest_year.max()),
        "admin_1_regions": int(ng.admin_1.nunique()),
        "admin_2_distinct_values": ng.admin_2.dropna().astype(str).unique().tolist(),
        "missing_area": int(ng.area.isna().sum()),
        "missing_production": int(ng.production.isna().sum()),
        "missing_yield": int(ng["yield"].isna().sum()),
        "exact_duplicate_rows": int(ng.duplicated().sum()),
        "composite_duplicate_rows": int(ng.duplicated(["fnid","product","season_name","planting_year","planting_month","harvest_year","harvest_month","crop_production_system"]).sum()),
        "qc_flag_counts": {str(k): int(v) for k,v in ng.qc_flag.value_counts().sort_index().items()},
        "planting_month_values": sorted(ng.planting_month.dropna().unique().astype(int).tolist()),
        "harvest_month_values": sorted(ng.harvest_month.dropna().unique().astype(int).tolist()),
        "season_counts": {str(k): int(v) for k,v in ng.season_name.value_counts(dropna=False).items()},
        "negative_values": {c: int(ng[c].lt(0).sum()) for c in ["area","production","yield"]},
        "zero_values": {c: int(ng[c].eq(0).sum()) for c in ["area","production","yield"]},
        "yield_iqr_review_count": int(ng.yield_iqr_outlier_review.sum()),
        "area_iqr_review_count": int(ng.area_iqr_outlier_review.sum()),
        "production_iqr_review_count": int(ng.production_iqr_outlier_review.sum()),
        "yield_arithmetic_mismatch_count": int(ng.yield_arithmetic_mismatch.sum()),
        "yield_formula_check_rows": int(valid.sum()),
    }
    (out / "qa_summary.json").write_text(pd.Series(qa).to_json(indent=2), encoding="utf-8")

if __name__ == "__main__":
    if len(sys.argv) != 3:
        raise SystemExit("Usage: python process_harveststat_nigeria.py input.csv output_directory")
    main(sys.argv[1], sys.argv[2])
