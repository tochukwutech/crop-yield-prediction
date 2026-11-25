"""Notebook entry points for the shared pre-plant workflow."""

from __future__ import annotations

from pathlib import Path

import pandas as pd

from .preprocessing import build_model_data
from .train import fit_climate_model


def load_project_data(project_root: Path):
    project_root = Path(project_root)
    harvest = pd.read_csv(project_root / "data" / "processed" / "harveststat_nigeria.csv")
    climate = pd.read_csv(
        project_root / "data" / "processed" / "climate" / "nigeria_state_annual_climate.csv"
    )
    return harvest, climate


def prepare_and_fit(project_root: Path):
    harvest, annual_climate = load_project_data(project_root)
    model_data = build_model_data(harvest, annual_climate)
    model = fit_climate_model(model_data)
    return model_data, annual_climate, model
