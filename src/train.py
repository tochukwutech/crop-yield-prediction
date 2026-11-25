"""Model construction and fitting for pre-plant yield estimates."""

from __future__ import annotations

from sklearn.compose import ColumnTransformer
from sklearn.ensemble import RandomForestRegressor
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder

from .preprocessing import CLIMATE_FEATURES

CATEGORICAL_FEATURES = ["product", "fnid"]
MODEL_FEATURES = CATEGORICAL_FEATURES + CLIMATE_FEATURES


def make_climate_model() -> Pipeline:
    preprocessing = ColumnTransformer(
        transformers=[
            ("crop_and_state", OneHotEncoder(handle_unknown="ignore"), CATEGORICAL_FEATURES),
            ("prior_climate", "passthrough", CLIMATE_FEATURES),
        ],
        remainder="drop",
    )
    return Pipeline([
        ("preprocess", preprocessing),
        ("model", RandomForestRegressor(
            n_estimators=300,
            min_samples_leaf=5,
            random_state=42,
            n_jobs=-1,
        )),
    ])


def fit_climate_model(model_data):
    model = make_climate_model()
    model.fit(model_data[MODEL_FEATURES], model_data["yield"])
    return model
