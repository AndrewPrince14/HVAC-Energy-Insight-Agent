import requests
import pandas as pd
from sklearn.ensemble import IsolationForest, RandomForestRegressor
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_absolute_error
import numpy as np

# -------------------------
# LOAD DATA
# -------------------------
df = pd.read_csv("data/hvac_dataset.csv")
df["Timestamp"] = pd.to_datetime(df["Timestamp"])

# -------------------------
# CALCULATE COP
# -------------------------
df["COP"] = 3.517 / df["iKW_TR"]

print("\n--- HVAC System Summary ---\n")
print("Total Records:", len(df))
print("Average Energy Consumption (kWh):", round(df["kWh"].mean(), 2))
print("Average COP:", round(df["COP"].mean(), 2))

# -------------------------
# ANOMALY DETECTION
# -------------------------
anomaly_model = IsolationForest(contamination=0.02, random_state=42)
df["Anomaly"] = anomaly_model.fit_predict(df[["kWh"]])
anomalies = df[df["Anomaly"] == -1]

print("\n--- Anomaly Detection ---")
print("Number of detected anomalies:", len(anomalies))

# -------------------------
# LOAD FORECASTING
# -------------------------

features = ["Ambient_Temp", "Humidity", "Occupancy"]
target = "kWh"

X = df[features]
y = df[target]

X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42
)

forecast_model = RandomForestRegressor(n_estimators=100, random_state=42)
forecast_model.fit(X_train, y_train)

predictions = forecast_model.predict(X_test)

mae = mean_absolute_error(y_test, predictions)

print("\n--- Load Forecasting ---")
print("Model Mean Absolute Error (kWh):", round(mae, 2))

# Predict next 24 hours using last 24 rows
# -------------------------
# WEATHER-ADJUSTED FORECAST
# -------------------------

print("\nFetching live weather forecast...")

latitude = 13.0827
longitude = 80.2707

weather_url = (
    f"https://api.open-meteo.com/v1/forecast?"
    f"latitude={latitude}&longitude={longitude}"
    f"&hourly=temperature_2m,relativehumidity_2m"
    f"&forecast_days=1"
)

response = requests.get(weather_url)
weather_data = response.json()

temps = weather_data["hourly"]["temperature_2m"][:24]
humidity_forecast = weather_data["hourly"]["relativehumidity_2m"][:24]

avg_occupancy = df["Occupancy"].mean()

future_input = pd.DataFrame({
    "Ambient_Temp": temps,
    "Humidity": humidity_forecast,
    "Occupancy": [avg_occupancy] * 24
})

future_prediction = forecast_model.predict(future_input)

print("\nPredicted next 24-hour average demand (weather-adjusted):",
      round(np.mean(future_prediction), 2), "kWh")
# -------------------------
# RECOMMENDATION ENGINE
# -------------------------

print("\n--- Decision Recommendations ---")

historical_avg = df["kWh"].mean()
predicted_avg = np.mean(future_prediction)

increase_percent = ((predicted_avg - historical_avg) / historical_avg) * 100

# Demand Risk Check
if increase_percent > 10:
    print(f"⚠ Forecasted demand is {round(increase_percent,2)}% higher than normal.")
    print("   → Risk of peak demand penalty and equipment stress.")
    print("   → Recommend load balancing or pre-cooling strategy.")
else:
    print("✅ No significant peak demand risk detected.")

# Efficiency Check
if df["COP"].mean() < 4.5:
    print("⚠ Efficiency trend below optimal range.")
    print("   → Recommend preventive maintenance inspection.")
else:
    print("✅ Efficiency within healthy operating range.")

# Anomaly Check
if len(anomalies) > 10:
    print("⚠ Frequent anomalies detected.")
    print("   → Investigate potential operational irregularities.")
else:
    print("✅ Anomaly frequency within expected range.")