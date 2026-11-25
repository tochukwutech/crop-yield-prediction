from pathlib import Path

import pandas as pd
import streamlit as st

from src.preprocessing import CORE_CROPS, build_model_data
from src.train import MODEL_FEATURES, fit_climate_model

ROOT = Path(__file__).resolve().parent
HARVEST_PATH = ROOT / "data" / "processed" / "harveststat_nigeria.csv"
CLIMATE_PATH = ROOT / "data" / "processed" / "climate" / "nigeria_state_annual_climate.csv"
@st.cache_resource
def load_data_and_fit_model():
    """Build pre-plant training rows and fit the fixed project Random Forest."""
    harvest = pd.read_csv(HARVEST_PATH)
    climate = pd.read_csv(CLIMATE_PATH)

    model_data = build_model_data(harvest, climate)
    climate_model = fit_climate_model(model_data)
    return model_data, climate, climate_model


def make_prediction_climate_row(climate, fnid, planting_year):
    required_years = list(range(planting_year - 3, planting_year))
    history = climate.loc[
        (climate["fnid"] == fnid) & climate["year"].isin(required_years)
    ].sort_values("year")
    if history["year"].tolist() != required_years:
        raise ValueError(
            f"Climate data are incomplete for {planting_year}; expected prior years {required_years}."
        )
    return {
        "prior3y_mean_rainfall": float(history["annual_rainfall_mm"].mean()),
        "prior3y_mean_T2M": float(history["T2M_annual_mean"].mean()),
    }


st.set_page_config(page_title="Climate-informed crop yield estimate", page_icon="🌾", layout="centered")
st.title("Climate-informed crop yield estimate")
st.write(
    "Choose a crop, state, and planting year to compare a pre-plant climate estimate "
    "with the crop-median reference."
)
st.warning(
    "The climate model is experimental: it did not improve overall accuracy over the "
    "crop-median baseline in the project evaluation. The app shows both estimates so "
    "the comparison stays visible."
)

try:
    model_data, annual_climate, climate_model = load_data_and_fit_model()
except Exception as exc:
    st.error(f"Could not load or prepare project data: {exc}")
    st.stop()

max_training_year = int(model_data["planting_year"].max())
max_climate_year = int(annual_climate["year"].max())

# Permit only genuinely later planting years; avoid presenting in-sample predictions as forecasts.
prediction_years = []
for year in range(max_training_year + 1, max_climate_year + 2):
    needed = set(range(year - 3, year))
    if needed.issubset(set(annual_climate["year"].unique())):
        prediction_years.append(year)

if not prediction_years:
    st.error(
        f"No future planting year is supported. Yield training data run through {max_training_year}, "
        f"and climate data run through {max_climate_year}. Add newer climate data before forecasting."
    )
    st.stop()

state_table = annual_climate[["fnid", "admin_1"]].drop_duplicates().sort_values("admin_1")
state_labels = dict(zip(state_table["admin_1"], state_table["fnid"]))
available_crops = [crop for crop in CORE_CROPS if crop in set(model_data["product"])]

with st.form("yield_estimate_form"):
    crop = st.selectbox("Crop", available_crops)
    state = st.selectbox("State", list(state_labels))
    planting_year = st.selectbox("Planting year", prediction_years)
    farm_area = st.number_input(
        "Farm area planted to this crop (hectares)",
        min_value=0.01,
        value=1.0,
        step=0.1,
        help="Used after yield prediction to estimate total harvest; it is not a model predictor.",
    )
    submitted = st.form_submit_button("Estimate yield", type="primary")

st.caption(
    f"This project’s climate records currently run through {max_climate_year}; "
    f"yield training records run through {max_training_year}. Supported future planting years: "
    + ", ".join(map(str, prediction_years))
    + ". Refresh the climate data before using the app for a later planting year."
)

if submitted:
    selected_fnid = state_labels[state]
    try:
        climate_values = make_prediction_climate_row(annual_climate, selected_fnid, int(planting_year))
    except ValueError as exc:
        st.error(str(exc))
        st.stop()

    prediction_row = pd.DataFrame([{
        "product": crop,
        "fnid": selected_fnid,
        **climate_values,
    }])
    climate_yield = float(climate_model.predict(prediction_row[MODEL_FEATURES])[0])

    crop_history = model_data.loc[model_data["product"] == crop, "yield"]
    baseline_yield = float(crop_history.median())
    state_history = model_data.loc[
        (model_data["product"] == crop) & (model_data["admin_1"] == state), "yield"
    ]

    st.subheader(f"Yield estimates for {crop} in {state}, planting year {planting_year}")
    col1, col2 = st.columns(2)
    col1.metric("Climate-informed estimate", f"{climate_yield:.2f} mt/ha")
    col1.caption(f"Approximate harvest for {farm_area:.2f} ha: {climate_yield * farm_area:.2f} metric tonnes")
    col2.metric("Crop-median reference", f"{baseline_yield:.2f} mt/ha")
    col2.caption(f"Approximate harvest for {farm_area:.2f} ha: {baseline_yield * farm_area:.2f} metric tonnes")

    st.markdown("**Climate values used**")
    st.write(
        f"Prior-three-year average rainfall: {climate_values['prior3y_mean_rainfall']:.1f} mm/year; "
        f"prior-three-year average annual mean temperature: {climate_values['prior3y_mean_T2M']:.2f} °C."
    )

    if len(state_history) >= 5:
        state_median = float(state_history.median())
        state_low, state_high = state_history.quantile([0.10, 0.90]).tolist()
        st.caption(
            f"Historical context for {crop} in {state}: {len(state_history)} eligible records, "
            f"median {state_median:.2f} mt/ha, 10th–90th percentile spread {state_low:.2f}–{state_high:.2f} mt/ha. "
            "This is historical variation, not a prediction interval."
        )
    else:
        st.caption(f"Only {len(state_history)} eligible {crop} records were found for {state}; local history is limited.")

    st.info(
        "The climate-informed estimate uses state-level historical averages, not measurements from your farm. "
        "Actual yields also depend on soil, seed, rainfall distribution, pests, inputs, and farm management. "
        "Treat both figures as planning references, not guaranteed harvests or advice on which crop to plant."
    )

with st.expander("How this estimate is made"):
    st.markdown(
        "- The climate model uses crop, state, and average annual rainfall and mean temperature from the three complete years before planting.\n"
        "- The crop-median reference uses the median yield for that crop in the eligible training records.\n"
        "- Yield is measured in metric tonnes per hectare (mt/ha), as defined by HarvestStat Africa v1.2.\n"
        "- Farm area is used only after predicting yield to estimate total harvest. It is not a model input.\n"
        "- The previous 2021–2023 evaluation was examined earlier; it is not a fresh, untouched test."
    )
st.markdown(
    "Source definitions: [HarvestStat Africa v1.2 documentation](https://github.com/HarvestStat/HarvestStat-Africa/releases)."
)
