from pathlib import Path
import re
import numpy as np
import pandas as pd
import rasterio

PROJECT_ROOT = Path(__file__).resolve().parent.parent
POWER_CLEAN_PATH = PROJECT_ROOT / "data" / "interim" / "nasa_power_clean.parquet"
RAW_CHIRPS_DIR = PROJECT_ROOT / "data" / "raw" / "chirps"
CHIRPS_OUT_PATH = PROJECT_ROOT / "data" / "interim" / "chirps_clean.parquet"
MERGED_OUT_PATH = (
    PROJECT_ROOT / "data" / "processed" / "nigeria_climate_1999_2023.parquet"
)


def parse_date_from_name(filepath: Path):
  name = filepath.name
  m = re.search(
      r"(?<!\d)(\d{4})[._-]?(\d{2})(?:[._-]?(\d{2}))?(?!\d)", name
  )
  if not m:
    return None
  year, month, day = int(m.group(1)), int(m.group(2)), m.group(3)
  if not (1 <= month <= 12):
    return None
  if day:
    d = int(day)
    if not (1 <= d <= 31):
      return None
    return pd.Timestamp(year=year, month=month, day=d).to_period("M").to_timestamp()
  return pd.Timestamp(year=year, month=month, day=1)


def normalize_keys(df: pd.DataFrame) -> pd.DataFrame:
  out = df.copy()
  out["lat"] = pd.to_numeric(out["lat"], errors="coerce").round(4)
  out["lon"] = pd.to_numeric(out["lon"], errors="coerce").round(4)
  out["date"] = pd.to_datetime(out["date"]).dt.to_period("M").dt.to_timestamp()
  return out


def main() -> None:
  if not POWER_CLEAN_PATH.exists():
    raise FileNotFoundError(
        f"Missing {POWER_CLEAN_PATH}. Run 01_clean_nasa_power.py first."
    )

  df_power = normalize_keys(pd.read_parquet(POWER_CLEAN_PATH))
  val_cols = [c for c in ["tmean_c", "tmax_c", "tmin_c"] if c in df_power.columns]
  df_power = (
      df_power.groupby(["lat", "lon", "date"], as_index=False)[val_cols]
      .first()
      .sort_values(["lat", "lon", "date"])
  )

  grid_pts = df_power[["lat", "lon"]].drop_duplicates().reset_index(drop=True)
  coords = list(zip(grid_pts["lon"], grid_pts["lat"]))

  chirps_files = sorted(RAW_CHIRPS_DIR.rglob("*.tif"))
  if not chirps_files:
    raise FileNotFoundError(f"No .tif files found in {RAW_CHIRPS_DIR}")

  records = []
  skipped = 0

  for path in chirps_files:
    date_val = parse_date_from_name(path)
    if date_val is None:
      skipped += 1
      continue

    with rasterio.open(path) as src:
      nodata = src.nodata
      sampled = [v[0] for v in src.sample(coords)]

    for (lat, lon), val in zip(coords, sampled):
      if (
          val is None
          or np.isnan(val)
          or val < 0
          or (nodata is not None and np.isclose(val, nodata))
      ):
        val = np.nan
      records.append({
          "lat": lat,
          "lon": lon,
          "date": date_val,
          "precip_mm": float(val) if pd.notna(val) else np.nan,
      })

  df_chirps = pd.DataFrame(records)
  if df_chirps.empty:
    raise ValueError(
        f"Found {len(chirps_files)} .tif files, but could not parse dates from filenames. "
        f"Example filename: {chirps_files[0].name}"
    )

  df_chirps = normalize_keys(df_chirps)
  df_chirps = (
      df_chirps.groupby(["lat", "lon", "date"], as_index=False)["precip_mm"]
      .mean()
      .sort_values(["lat", "lon", "date"])
  )

  CHIRPS_OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
  df_chirps.to_parquet(CHIRPS_OUT_PATH, index=False)

  df_merged = pd.merge(
      df_power, df_chirps, on=["lat", "lon", "date"], how="inner"
  ).sort_values(["lat", "lon", "date"])

  MERGED_OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
  df_merged.to_parquet(MERGED_OUT_PATH, index=False)

  print(f"Processed {len(chirps_files) - skipped} .tif files (skipped {skipped})")
  print(f"Saved CHIRPS rows: {len(df_chirps)} -> {CHIRPS_OUT_PATH}")
  print(f"Saved merged rows: {len(df_merged)} -> {MERGED_OUT_PATH}")
  print("Missing values per column:")
  print(df_merged.isna().sum())


if __name__ == "__main__":
  main()