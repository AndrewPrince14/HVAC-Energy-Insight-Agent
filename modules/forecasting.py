import requests
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_absolute_error


def run_forecasting(df, latitude=13.0827, longitude=80.2707):

    # -------------------------
    # MODEL TRAINING
    # -------------------------
    features = ["Ambient_Temp", "Humidity", "Occupancy"]
    target = "kWh"

    X = df[features]
    y = df[target]

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42
    )

    model = RandomForestRegressor(n_estimators=100, random_state=42)
    model.fit(X_train, y_train)

    predictions = model.predict(X_test)
    mae = mean_absolute_error(y_test, predictions)

    # -------------------------
    # WEATHER API
    # -------------------------
    weather_url = (
        f"https://api.open-meteo.com/v1/forecast?"
        f"latitude={latitude}&longitude={longitude}"
        f"&hourly=temperature_2m,relativehumidity_2m"
        f"&forecast_days=7"
    )

    response = requests.get(weather_url)
    weather_data = response.json()

    temps = weather_data["hourly"]["temperature_2m"][:168]
    humidity_forecast = weather_data["hourly"]["relativehumidity_2m"][:168]

    avg_occupancy = df["Occupancy"].mean()
    forecast_hours = len(temps)

    future_input = pd.DataFrame({
        "Ambient_Temp": temps,
        "Humidity": humidity_forecast,
        "Occupancy": [avg_occupancy] * forecast_hours
    })

    future_prediction = model.predict(future_input)

    historical_peak = df["kWh"].max()
    predicted_peak = max(future_prediction)

    peak_increase_percent = (
        (predicted_peak - historical_peak) / historical_peak
    ) * 100

    if peak_increase_percent > 5:
        peak_risk = "High"
    else:
        peak_risk = "Normal"

    return {
        "mae": mae,
        "future_prediction": future_prediction,
        "forecast_hours": forecast_hours,
        "predicted_peak": predicted_peak,
        "historical_peak": historical_peak,
        "peak_risk": peak_risk
    }