import ee
import numpy as np
import pandas as pd
import requests
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score

# ==========================================
# 1. NASA POWER API FETCH (Temperature/Met)
# ==========================================


def fetch_nasa_power_data(lat, lon, start_date, end_date):
  """Fetch daily agricultural meteorological data from NASA POWER API.

  Dates format: 'YYYYMMDD' (e.g., '20200101')
  """
  url = (
      "https://power.larc.nasa.gov/api/temporal/daily/point?"
      f"parameters=T2M,T2M_MAX,T2M_MIN,RH2M,RAIN&community=AG&"
      f"start={start_date}&end={end_date}&latitude={lat}&longitude={lon}&format=JSON"
  )

  print(f"Querying NASA POWER for Lat: {lat}, Lon: {lon}...")
  response = requests.get(url)

  if response.status_code == 200:
    data = response.json()
    properties = data["properties"]["parameter"]

    df = pd.DataFrame(properties)
    df.index = pd.to_datetime(df.index, format="%Y%m%d")
    df.index.name = "Date"
    return df
  else:
    raise Exception(
        f"Failed to fetch NASA POWER data: {response.status_code}"
    )


# ==========================================
# 2. CHIRPS FETCH (Rainfall via GEE)
# ==========================================


def fetch_chirps_rainfall(lat, lon, start_date, end_date):
  """Extract daily CHIRPS rainfall data for a specific point from Google Earth Engine.

  Dates format: 'YYYY-MM-DD' (e.g., '2020-01-01')
  """
  try:
    ee.Initialize()
  except Exception:
    ee.Authenticate()
    ee.Initialize()

  point = ee.Geometry.Point([lon, lat])

  chirps = (
      ee.ImageCollection("UCSB-CHG/CHIRPS/DAILY")
      .filterBounds(point)
      .filterDate(start_date, end_date)
      .select("precipitation")
  )

  def extract_data(image):
    date = ee.Date(image.get("system:time_start")).format("YYYY-MM-dd")
    val = image.reduceRegion(
        reducer=ee.Reducer.mean(), geometry=point, scale=5000
    ).get("precipitation")
    return ee.Feature(None, {"date": date, "precipitation": val})

  print(f"Extracting CHIRPS rainfall for Lat: {lat}, Lon: {lon}...")
  features = chirps.map(extract_data).filter(ee.Filter.notNull(["precipitation"]))
  features_list = features.getInfo()["features"]

  dates = [pd.to_datetime(f["properties"]["date"]) for f in features_list]
  precip = [f["properties"]["precipitation"] for f in features_list]

  df = pd.DataFrame({"Precipitation_mm": precip}, index=dates)
  df.index.name = "Date"
  return df


# ==========================================
# 3. GROWING SEASON AGGREGATION
# ==========================================


def aggregate_growing_season(weather_df, rain_df, planting_month, harvest_month):
  """Merges datasets and aggregates daily metrics over the crop's growing season

  (Filtering by specified planting and harvesting months).
  """
  # Merge both dataframes on Date index
  combined_df = weather_df.join(rain_df, how="inner")

  # Filter months for the growing season (handles standard intra-year seasons)
  season_mask = combined_df.index.month.isin(
      range(planting_month, harvest_month + 1)
  )
  growing_season_data = combined_df[season_mask]

  # Compute aggregated features per year (or season)
  aggregated_features = {
      "Total_Rainfall_mm": growing_season_data["Precipitation_mm"].sum(),
      "Mean_Temp": growing_season_data["T2M"].mean(),
      "Max_Temp": growing_season_data["T2M_MAX"].max(),
      "Min_Temp": growing_season_data["T2M_MIN"].min(),
      "Mean_Humidity": growing_season_data["RH2M"].mean(),
  }

  return pd.Series(aggregated_features)


# ==========================================
# 4. RANDOM FOREST MODELLING WORKSTREAM
# ==========================================


def train_evaluate_random_forest(X_train, y_train, X_test, y_test):
  """Trains and evaluates the Random Forest Regressor using shared splits."""
  print("Training Random Forest Regressor...")

  rf_model = RandomForestRegressor(n_estimators=100, random_state=42)
  rf_model.fit(X_train, y_train)

  y_pred = rf_model.predict(X_test)

  mae = mean_absolute_error(y_test, y_pred)
  rmse = mean_squared_error(y_test, y_pred, squared=False)
  r2 = r2_score(y_test, y_pred)

  metrics = {"MAE": mae, "RMSE": rmse, "R2": r2}
  print("Evaluation Metrics:", metrics)
  return rf_model, y_pred, metrics


# ==========================================
# SCRIPT EXECUTION WORKFLOW
# ==========================================
if __name__ == "__main__":
  # Placeholders - update with real data from Fahd and David later
  lat, lon = 9.05, 7.49  # Example: Abuja, Nigeria
  nasa_start, nasa_end = "20200101", "20201231"
  chirps_start, chirps_end = "2020-01-01", "2020-12-31"

  # 1. Fetch data
  # weather_df = fetch_nasa_power_data(lat, lon, nasa_start, nasa_end)
  # rain_df = fetch_chirps_rainfall(lat, lon, chirps_start, chirps_end)

  # 2. Aggregate (e.g., May to September growing season)
  # season_features = aggregate_growing_season(weather_df, rain_df, planting_month=5, harvest_month=9)
  # print(season_features)

  print(
      "Climate pipeline template ready. Plug in final coordinates and dates"
      " once team confirms."
  )