from pathlib import Path
import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
POWER_PATH = ROOT / "data" / "interim" / "nasa_power_clean.parquet"
CHIRPS_PATH = ROOT / "data" / "interim" / "chirps_clean.parquet"
MERGED_OUT = ROOT / "data" / "processed" / "nigeria_climate_monthly_1999_2023.parquet"
SEASONAL_OUT = ROOT / "data" / "processed" / "nigeria_climate_annual_season_1999_2023.parquet"


def prep(df: pd.DataFrame) -> pd.DataFrame:
  out = df.copy()
  out["lat"] = pd.to_numeric(out["lat"], errors="coerce").round(3)
  out["lon"] = pd.to_numeric(out["lon"], errors="coerce").round(3)
  out["date"] = pd.to_datetime(out["date"]).dt.to_period("M").dt.to_timestamp()
  return out


def main() -> None:
  p = prep(pd.read_parquet(POWER_PATH))
  c = prep(pd.read_parquet(CHIRPS_PATH))

  # Average any duplicate keys cleanly, then left-join CHIRPS onto POWER
  p_cols = [col for col in ["tmean_c", "tmax_c", "tmin_c"] if col in p.columns]
  p = p.groupby(["lat", "lon", "date"], as_index=False, dropna=False)[p_cols].first()
  c = c.groupby(["lat", "lon", "date"], as_index=False, dropna=False)["precip_mm"].mean()

  merged = pd.merge(p, c, on=["lat", "lon", "date"], how="left").sort_values(["lat", "lon", "date"])
  MERGED_OUT.parent.mkdir(parents=True, exist_ok=True)
  merged.to_parquet(MERGED_OUT, index=False)

  # Annual + Main Growing Season (Apr-Sep) aggregation per grid cell & year
  merged["year"] = merged["date"].dt.year
  merged["month"] = merged["date"].dt.month
  merged["is_main_season"] = merged["month"].between(4, 9)

  annual = merged.groupby(["lat", "lon", "year"], as_index=False).agg(
      annual_precip_mm=("precip_mm", "sum"),
      annual_tmean_c=("tmean_c", "mean"),
      annual_tmax_max_c=("tmax_c", "max"),
  )

  season = (
      merged[merged["is_main_season"]]
      .groupby(["lat", "lon", "year"], as_index=False)
      .agg(
          season_precip_mm=("precip_mm", "sum"),
          season_tmean_c=("tmean_c", "mean"),
          season_tmax_max_c=("tmax_c", "max"),
      )
  )

  summary = pd.merge(annual, season, on=["lat", "lon", "year"], how="left")
  summary.to_parquet(SEASONAL_OUT, index=False)

  print("Monthly rows:", len(merged))
  print("Annual/Season rows:", len(summary))
  print("Missing counts:\n", merged.isna().sum())


if __name__ == "__main__":
  main()