import pandas as pd
import numpy as np
from datetime import datetime, timedelta

# Reproducibility
np.random.seed(42)

# Generate 30 days of hourly data
start_date = datetime(2025, 1, 1)
hours = 24 * 30
timestamps = [start_date + timedelta(hours=i) for i in range(hours)]

data = []

for ts in timestamps:
    hour = ts.hour

    # -----------------------------
    # Ambient Temperature Pattern
    # -----------------------------
    ambient_temp = 28 + 6 * np.sin((hour / 24) * 2 * np.pi) + np.random.normal(0, 1)

    # -----------------------------
    # Humidity Pattern
    # -----------------------------
    humidity = 60 + 10 * np.sin((hour / 24) * 2 * np.pi) + np.random.normal(0, 3)

    # -----------------------------
    # Wet Bulb Temperature Approx
    # -----------------------------
    wbt = (
        ambient_temp * np.arctan(0.151977 * np.sqrt(humidity + 8.313659))
        + np.arctan(ambient_temp + humidity)
        - np.arctan(humidity - 1.676331)
        + 0.00391838 * humidity ** 1.5 * np.arctan(0.023101 * humidity)
        - 4.686035
    )

    # -----------------------------
    # Occupancy Simulation
    # -----------------------------
    if 8 <= hour <= 18:
        occupancy = np.random.randint(200, 500)
    else:
        occupancy = np.random.randint(20, 100)

    # -----------------------------
    # Energy Consumption Model
    # -----------------------------
    kwh = (
        500
        + (ambient_temp * 10)
        + (occupancy * 0.5)
        + np.random.normal(0, 50)
    )

    # -----------------------------
    # Efficiency (iKW-TR)
    # -----------------------------
    ikw_tr = 0.7 + (ambient_temp - 28) * 0.01 + np.random.normal(0, 0.02)

    # -----------------------------
    # Rare anomaly spikes
    # -----------------------------
    if np.random.rand() < 0.01:
        kwh += np.random.randint(300, 600)

    data.append([
        ts,
        round(kwh, 2),
        round(ikw_tr, 3),
        round(ambient_temp, 2),
        round(humidity, 2),
        round(wbt, 2),
        occupancy
    ])

df = pd.DataFrame(
    data,
    columns=[
        "Timestamp",
        "kWh",
        "iKW_TR",
        "Ambient_Temp",
        "Humidity",
        "WBT",
        "Occupancy"
    ]
)

df.to_csv("data/hvac_dataset.csv", index=False)

print("Dataset generated successfully with WBT and anomaly events.")