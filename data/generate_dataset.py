import pandas as pd
import numpy as np
from datetime import datetime, timedelta

# Set random seed for consistency
np.random.seed(42)

# Generate 30 days of hourly data
start_date = datetime(2025, 1, 1)
hours = 24 * 30
timestamps = [start_date + timedelta(hours=i) for i in range(hours)]

data = []

for ts in timestamps:
    hour = ts.hour
    
    # Simulate daily temperature pattern (hot afternoon, cooler night)
    ambient_temp = 28 + 6 * np.sin((hour / 24) * 2 * np.pi) + np.random.normal(0, 1)
    
    # Simulate humidity
    humidity = 60 + 10 * np.sin((hour / 24) * 2 * np.pi) + np.random.normal(0, 3)
    
    # Simulate occupancy (higher during working hours)
    if 8 <= hour <= 18:
        occupancy = np.random.randint(200, 500)
    else:
        occupancy = np.random.randint(20, 100)
    
    # Energy consumption depends on temp + occupancy
    kwh = (
        500
        + (ambient_temp * 10)
        + (occupancy * 0.5)
        + np.random.normal(0, 50)
    )
    
    # Efficiency (iKW-TR) slightly worsens at high temp
    ikw_tr = 0.7 + (ambient_temp - 28) * 0.01 + np.random.normal(0, 0.02)
    
    data.append([ts, round(kwh, 2), round(ikw_tr, 3), round(ambient_temp, 2), round(humidity, 2), occupancy])

df = pd.DataFrame(data, columns=[
    "Timestamp",
    "kWh",
    "iKW_TR",
    "Ambient_Temp",
    "Humidity",
    "Occupancy"
])

df.to_csv("data/hvac_dataset.csv", index=False)

print("Dataset generated successfully!")