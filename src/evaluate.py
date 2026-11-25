"""Time-based evaluation against a crop-median baseline."""

from __future__ import annotations

import numpy as np
import pandas as pd
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score

from .preprocessing import CLIMATE_FEATURES
from .train import MODEL_FEATURES, make_climate_model


def score_predictions(actual, predicted) -> dict:
    actual = np.asarray(actual, dtype=float)
    predicted = np.asarray(predicted, dtype=float)
    return {
        "records": int(len(actual)),
        "MAE": float(mean_absolute_error(actual, predicted)),
        "RMSE": float(np.sqrt(mean_squared_error(actual, predicted))),
        "R2": float(r2_score(actual, predicted)) if len(actual) > 1 else float("nan"),
    }


def evaluate_period(train_rows: pd.DataFrame, evaluation_rows: pd.DataFrame,
                    evaluation_period: str) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Fit on earlier rows; score crop median and climate methods on shared rows."""
    if train_rows.empty or evaluation_rows.empty:
        raise ValueError("Training and evaluation rows must both be non-empty.")

    crop_medians = train_rows.groupby("product")["yield"].median()
    fallback = float(train_rows["yield"].median())
    baseline = evaluation_rows["product"].map(crop_medians).fillna(fallback).to_numpy()

    model = make_climate_model()
    model.fit(train_rows[MODEL_FEATURES], train_rows["yield"])
    climate_predictions = model.predict(evaluation_rows[MODEL_FEATURES])

    predictions = evaluation_rows[
        ["fnid", "admin_1", "product", "planting_year", "yield", "qc_flag"]
    ].copy()
    predictions = predictions.rename(columns={"yield": "actual_yield"})
    predictions["evaluation_period"] = evaluation_period
    predictions["crop_median_prediction"] = baseline
    predictions["climate_model_prediction"] = climate_predictions

    rows = []
    for group_name, subset in [("Overall", predictions), *list(predictions.groupby("product"))]:
        for method, column in [
            ("Crop median baseline", "crop_median_prediction"),
            ("Crop, state, and prior-three-year climate", "climate_model_prediction"),
        ]:
            rows.append({
                "evaluation_period": evaluation_period,
                "group": group_name,
                "model": method,
                **score_predictions(subset["actual_yield"], subset[column]),
            })
    return pd.DataFrame(rows), predictions


def evaluate_with_qc_sensitivity(model_data: pd.DataFrame, train_mask,
                                 evaluation_mask, evaluation_period: str):
    """Return full and QC-0-only comparisons without using QC as a predictor."""
    scores, predictions = evaluate_period(
        model_data.loc[train_mask], model_data.loc[evaluation_mask], evaluation_period
    )
    qc_train = train_mask & model_data["qc_flag"].eq(0)
    qc_eval = evaluation_mask & model_data["qc_flag"].eq(0)
    qc_scores, qc_predictions = evaluate_period(
        model_data.loc[qc_train], model_data.loc[qc_eval],
        f"{evaluation_period}, QC-0 only",
    )
    return (pd.concat([scores, qc_scores], ignore_index=True),
            pd.concat([predictions, qc_predictions], ignore_index=True))
