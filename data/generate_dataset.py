import pandas as pd
import numpy as np
from datetime import datetime, timedelta

np.random.seed(42)
n_hours = 720

timestamps = [datetime(2024, 1, 1) + timedelta(hours=i) for i in range(n_hours)]
ambient_temp = np.random.normal(32, 4, n_hours).clip(24, 42)
humidity = np.random.normal(65, 10, n_hours).clip(40, 90)
wbt = ambient_temp - ((100 - humidity) / 5)
occupancy = np.where((np.array([t.hour for t in timestamps]) >= 8) & 
                     (np.array([t.hour for t in timestamps]) <= 18), 
                     np.random.randint(50, 200, n_hours), 
                     np.random.randint(0, 30, n_hours))
ikw_tr = np.random.normal(0.68, 0.08, n_hours).clip(0.50, 0.95)
kwh = (ambient_temp * 2.1 + occupancy * 0.8 + ikw_tr * 150 + np.random.normal(0, 15, n_hours)).clip(200, 1200)

df = pd.DataFrame({
    "Timestamp": timestamps,
    "kWh": kwh.round(2),
    "iKW-TR": ikw_tr.round(4),
    "Ambient_Temp": ambient_temp.round(1),
    "Humidity": humidity.round(1),
    "WBT": wbt.round(2),
    "Occupancy": occupancy
})

df.to_csv("data/hvac_dataset.csv", index=False)
print(f"Dataset generated: {len(df)} rows")