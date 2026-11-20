from pathlib import Path
import numpy as np
import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parent.parent
RAW_POWER_DIR = PROJECT_ROOT / "data" / "raw" / "nasa_power"
OUT_PATH = PROJECT_ROOT / "data" / "interim" / "nasa_power_clean.parquet"

MONTH_MAP = {
    "JAN": 1, "FEB": 2, "MAR": 3, "APR": 4, "MAY": 5, "JUN": 6,
    "JUL": 7, "AUG": 8, "SEP": 9, "OCT": 10, "NOV": 11, "DEC": 12,
}

PARAM_RENAME = {
    "T2M": "tmean_c",
    "T2M_MAX": "tmax_c",
    "T2M_MIN": "tmin_c",
}


def load_power_csv(filepath: Path) -> pd.DataFrame:
  with open(filepath, "r", encoding="utf-8") as f:
    lines = f.readlines()

  header_idx = next(
      i for i, line in enumerate(lines) if "-END HEADER-" in line
  )
  df = pd.read_csv(filepath, skiprows=header_idx + 1)
  df.columns = [c.strip().upper() for c in df.columns]

  if "MO" in df.columns:
    df = df[df["MO"].between(1, 12)].copy()
    if "DY" in df.columns:
      df["date"] = pd.to_datetime(
          df[["YEAR", "MO", "DY"]].rename(
              columns={"YEAR": "year", "MO": "month", "DY": "day"}
          )
      )
    else:
      df["date"] = pd.to_datetime(
          df["YEAR"].astype(str) + "-" + df["MO"].astype(str).str.zfill(2) + "-01"
      )
    df = df.rename(columns={"LAT": "lat", "LON": "lon", **PARAM_RENAME})
    keep_cols = ["lat", "lon", "date"] + [
        c for c in ["tmean_c", "tmax_c", "tmin_c"] if c in df.columns
    ]
    out = df[keep_cols].copy()

  elif any(m in df.columns for m in MONTH_MAP):
    present_months = [m for m in MONTH_MAP if m in df.columns]
    id_vars = [c for c in ["PARAMETER", "LAT", "LON", "YEAR"] if c in df.columns]
    melted = df.melt(
        id_vars=id_vars,
        value_vars=present_months,
        var_name="MON_STR",
        value_name="val",
    )
    melted["month"] = melted["MON_STR"].map(MONTH_MAP)
    melted["date"] = pd.to_datetime(
        melted["YEAR"].astype(str)
        + "-"
        + melted["month"].astype(str).str.zfill(2)
        + "-01"
    )
    melted = melted.rename(columns={"LAT": "lat", "LON": "lon"})

    if "PARAMETER" in melted.columns:
      melted["param_clean"] = (
          melted["PARAMETER"].astype(str).str.strip().str.upper()
      )
      melted = melted[melted["param_clean"].isin(PARAM_RENAME)].copy()
      melted["param_clean"] = melted["param_clean"].map(PARAM_RENAME)
      out = melted.pivot_table(
          index=["lat", "lon", "date"],
          columns="param_clean",
          values="val",
          aggfunc="first",
      ).reset_index()
    else:
      out = melted[["lat", "lon", "date", "val"]].rename(
          columns={"val": "tmean_c"}
      )

  else:
    raise KeyError(
        f"No 'MO' or JAN..DEC columns in {filepath.name}. Columns:"
        f" {list(df.columns)}"
    )

  for col in ["tmean_c", "tmax_c", "tmin_c"]:
    if col in out.columns:
      out[col] = pd.to_numeric(out[col], errors="coerce").replace(
          [-999, -999.0], np.nan
      )

  return out


def main() -> None:
  power_files = sorted(RAW_POWER_DIR.glob("*.csv"))
  if not power_files:
    raise FileNotFoundError(f"No CSV files found in {RAW_POWER_DIR}")

  df_power = pd.concat(
      [load_power_csv(p) for p in power_files], ignore_index=True
  )

  val_cols = [
      c for c in ["tmean_c", "tmax_c", "tmin_c"] if c in df_power.columns
  ]
  df_power = (
        df_power.groupby(["lat", "lon", "date"], as_index=False, dropna=False)[
            val_cols
        ]
        .first()
        .sort_values(["lat", "lon", "date"])
    )

  OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
  df_power.to_parquet(OUT_PATH, index=False)
  print(
      f"Loaded {len(power_files)} CSV files -> saved {len(df_power)} rows to"
      f" {OUT_PATH}"
  )


if __name__ == "__main__":
  main()