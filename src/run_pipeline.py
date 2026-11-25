"""Rebuild model comparison tables from the checked-in processed CSV inputs."""

from __future__ import annotations

import argparse
from pathlib import Path

import pandas as pd

from .evaluate import evaluate_with_qc_sensitivity
from .preprocessing import build_model_data

ROOT = Path(__file__).resolve().parents[1]


def run(output_dir: Path = ROOT / "results" / "tables") -> tuple[pd.DataFrame, pd.DataFrame]:
    harvest = pd.read_csv(ROOT / "data" / "processed" / "harveststat_nigeria.csv")
    climate = pd.read_csv(
        ROOT / "data" / "processed" / "climate" / "nigeria_state_annual_climate.csv"
    )
    model_data = build_model_data(harvest, climate)

    validations, validation_predictions = evaluate_with_qc_sensitivity(
        model_data,
        model_data["planting_year"].between(2000, 2018),
        model_data["planting_year"].between(2019, 2020),
        "validation 2019-2020",
    )
    historical, historical_predictions = evaluate_with_qc_sensitivity(
        model_data,
        model_data["planting_year"].between(2000, 2020),
        model_data["planting_year"].between(2021, 2023),
        "previously examined period 2021-2023",
    )
    scores = pd.concat([validations, historical], ignore_index=True)
    predictions = pd.concat([validation_predictions, historical_predictions], ignore_index=True)

    output_dir.mkdir(parents=True, exist_ok=True)
    scores.to_csv(output_dir / "preplant_model_comparison.csv", index=False)
    predictions.to_csv(output_dir / "preplant_model_predictions.csv", index=False)
    (model_data.groupby("product")["yield"].median().rename("crop_median_yield")
     .reset_index().to_csv(output_dir / "preplant_crop_median_baseline.csv", index=False))
    model_data.to_csv(ROOT / "data" / "processed" / "climate" / "nigeria_preplant_three_year_model_table.csv", index=False)
    return scores, predictions


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-dir", type=Path, default=ROOT / "results" / "tables")
    args = parser.parse_args()
    scores, _ = run(args.output_dir)
    print(scores.loc[scores["group"].eq("Overall")].to_string(index=False))


if __name__ == "__main__":
    main()
