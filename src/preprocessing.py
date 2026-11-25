"""Build pre-plant climate features and eligible crop-yield records."""

from __future__ import annotations

import pandas as pd

CORE_CROPS = [
    "Cassava", "Cowpea", "Groundnuts (In Shell)", "Maize",
    "Millet", "Rice", "Sorghum", "Yams",
]
CLIMATE_FEATURES = ["prior3y_mean_rainfall", "prior3y_mean_T2M"]


def build_model_data(harvest: pd.DataFrame, annual_climate: pd.DataFrame) -> pd.DataFrame:
    harvest_required = {
        "fnid", "admin_1", "product", "planting_year", "yield", "qc_flag",
    }
    climate_required = {
        "fnid", "admin_1", "year", "annual_rainfall_mm", "T2M_annual_mean",
    }
    missing_harvest = harvest_required - set(harvest.columns)
    missing_climate = climate_required - set(annual_climate.columns)
    if missing_harvest or missing_climate:
        raise ValueError(
            f"Missing HarvestStat columns: {sorted(missing_harvest)}; "
            f"missing climate columns: {sorted(missing_climate)}"
        )

    harvest = harvest.copy()
    climate = annual_climate.copy()
    for column in ("planting_year", "yield"):
        harvest[column] = pd.to_numeric(harvest[column], errors="coerce")
    for column in ("year", "annual_rainfall_mm", "T2M_annual_mean"):
        climate[column] = pd.to_numeric(climate[column], errors="coerce")

    harvest = harvest.loc[
        harvest["product"].isin(CORE_CROPS) & harvest["yield"].notna()
    ].dropna(subset=["fnid", "admin_1", "planting_year"]).copy()
    climate = climate.dropna(
        subset=["fnid", "admin_1", "year", "annual_rainfall_mm", "T2M_annual_mean"]
    ).copy()
    harvest["planting_year"] = harvest["planting_year"].astype(int)
    climate["year"] = climate["year"].astype(int)

    if climate.duplicated(["fnid", "year"]).any():
        raise ValueError("Annual climate file has duplicate state-year rows.")

    climate = climate.sort_values(["fnid", "year"]).copy()
    by_state = climate.groupby("fnid", sort=False)
    climate[CLIMATE_FEATURES[0]] = by_state["annual_rainfall_mm"].transform(
        lambda values: values.shift(1).rolling(3, min_periods=3).mean()
    )
    climate[CLIMATE_FEATURES[1]] = by_state["T2M_annual_mean"].transform(
        lambda values: values.shift(1).rolling(3, min_periods=3).mean()
    )

    model_data = harvest.merge(
        climate.rename(columns={"year": "planting_year"})[
            ["fnid", "admin_1", "planting_year", *CLIMATE_FEATURES]
        ],
        on=["fnid", "admin_1", "planting_year"],
        how="inner",
        validate="many_to_one",
    ).dropna(subset=[*CLIMATE_FEATURES, "yield"]).copy()
    if model_data.empty:
        raise ValueError("No eligible rows with complete prior-three-year climate were found.")
    return model_data
