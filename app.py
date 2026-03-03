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

# -------------------------
# DEGRADATION TREND ANALYSIS
# -------------------------
df["Time_Index"] = range(len(df))
trend_coeff = np.polyfit(df["Time_Index"], df["COP"], 1)[0]

print("\n--- Degradation Trend Analysis ---")

if trend_coeff < -0.0005:
    degradation_status = "Degrading"
    print("⚠ Efficiency degradation trend detected.")
else:
    degradation_status = "Stable"
    print("✅ No significant efficiency degradation trend.")

# -------------------------
# SYSTEM SUMMARY
# -------------------------
print("\n--- HVAC System Summary ---\n")
print("Total Records:", len(df))
print("Average Energy Consumption (kWh):", round(df["kWh"].mean(), 2))
print("Average COP:", round(df["COP"].mean(), 2))

# -------------------------
# ANOMALY DETECTION
# -------------------------
anomaly_model = IsolationForest(contamination=0.02, random_state=42)
df["Anomaly"] = anomaly_model.fit_predict(
    df[["kWh", "Ambient_Temp", "Humidity", "Occupancy", "iKW_TR"]]
)
anomalies = df[df["Anomaly"] == -1]

print("\n--- Anomaly Detection ---")
print("Number of detected anomalies:", len(anomalies))

# -------------------------
# ROOT CAUSE ANALYSIS
# -------------------------
print("\n--- Root Cause Analysis ---")

equipment_count = 0
behavioral_count = 0

for _, row in anomalies.iterrows():
    if row["COP"] < df["COP"].mean() * 0.9:
        equipment_count += 1
    elif row["Occupancy"] > df["Occupancy"].mean() * 1.2:
        behavioral_count += 1

if equipment_count > behavioral_count:
    root_cause = "Equipment inefficiency likely"
elif behavioral_count > equipment_count:
    root_cause = "Behavioral / occupancy-driven load surge likely"
else:
    root_cause = "Mixed or inconclusive pattern"

print("Root Cause Assessment:", root_cause)

# -------------------------
# MAINTENANCE PRIORITY SCORING
# -------------------------
print("\n--- Maintenance Priority Assessment ---")

priority_score = 0

if len(anomalies) > 20:
    priority_score += 2
elif len(anomalies) > 10:
    priority_score += 1

if degradation_status == "Degrading":
    priority_score += 2

if root_cause == "Equipment inefficiency likely":
    priority_score += 2

if priority_score >= 4:
    maintenance_priority = "High"
elif priority_score >= 2:
    maintenance_priority = "Moderate"
else:
    maintenance_priority = "Low"

print("Maintenance Priority Level:", maintenance_priority)

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

# -------------------------
# WEATHER-ADJUSTED FORECAST (168h)
# -------------------------
print("\nFetching live weather forecast...")

latitude = 13.0827
longitude = 80.2707

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

future_prediction = forecast_model.predict(future_input)
predicted_avg = np.mean(future_prediction)

print("\nPredicted next 168-hour average demand (weather-adjusted):",
      round(predicted_avg, 2), "kWh")

# -------------------------
# PEAK DEMAND ANALYSIS
# -------------------------
historical_peak = df["kWh"].max()
predicted_peak = max(future_prediction)

print("\n--- Peak Demand Analysis ---")
print("Historical Peak Load:", round(historical_peak, 2), "kWh")
print("Predicted Peak Load (168h):", round(predicted_peak, 2), "kWh")

peak_increase_percent = ((predicted_peak - historical_peak) / historical_peak) * 100

if peak_increase_percent > 5:
    peak_risk = "High"
    print("⚠ Risk of exceeding historical peak. Potential demand penalty.")
else:
    peak_risk = "Normal"
    print("✅ No significant peak demand escalation expected.")

# -------------------------
# DECISION RECOMMENDATIONS
# -------------------------
print("\n--- Decision Recommendations ---")

historical_avg = df["kWh"].mean()
increase_percent = ((predicted_avg - historical_avg) / historical_avg) * 100

print("Root Cause:", root_cause)
print("Maintenance Priority:", maintenance_priority)
print("Peak Risk Level:", peak_risk)

if increase_percent > 10:
    print("⚠ Forecasted demand significantly higher than normal.")
else:
    print("✅ No significant average demand risk detected.")

if df["COP"].mean() < 4.5:
    print("⚠ Efficiency below optimal range.")
else:
    print("✅ Efficiency within healthy operating range.")

if len(anomalies) > 10:
    print("⚠ Frequent anomalies detected.")
else:
    print("✅ Anomaly frequency within expected range.")

# -------------------------
# IMPACT QUANTIFICATION
# -------------------------
print("\n--- Impact Quantification ---")

tariff_per_kwh = 8.0
emission_factor = 0.82

difference_kwh = predicted_avg - historical_avg
projected_energy_change = difference_kwh * forecast_hours
projected_cost_change = projected_energy_change * tariff_per_kwh
projected_co2_change = projected_energy_change * emission_factor

if difference_kwh > 0:
    print(f"Projected additional energy ({forecast_hours}h): {round(projected_energy_change,2)} kWh")
    print(f"Estimated additional electricity cost: ₹ {round(projected_cost_change,2)}")
    print(f"Estimated additional CO2 emissions: {round(projected_co2_change,2)} kg")
elif difference_kwh < 0:
    print(f"Projected energy savings ({forecast_hours}h): {round(abs(projected_energy_change),2)} kWh")
    print(f"Estimated cost savings: ₹ {round(abs(projected_cost_change),2)}")
    print(f"Estimated CO2 reduction: {round(abs(projected_co2_change),2)} kg")
else:
    print("No significant energy impact expected.")

# -------------------------
# HTML REPORT GENERATION
# -------------------------
print("\nGenerating HTML decision report...")

report_content = f"""
<html>
<head>
    <title>HVAC Energy Insight Report</title>
    <style>
        body {{ font-family: Arial; padding: 20px; }}
        h1 {{ color: #2E86C1; }}
        h2 {{ color: #1B4F72; }}
        .section {{ margin-bottom: 20px; }}
    </style>
</head>
<body>

<h1>HVAC Energy Insight Technical Report</h1>

<h2>System Summary</h2>
<p>Total Records: {len(df)}</p>
<p>Average Energy Consumption: {round(df["kWh"].mean(),2)} kWh</p>
<p>Average COP: {round(df["COP"].mean(),2)}</p>

<h2>Forecasting (168h)</h2>
<p>Predicted Average Demand: {round(predicted_avg,2)} kWh</p>
<p>Model MAE: {round(mae,2)} kWh</p>

<h2>Peak Analysis</h2>
<p>Historical Peak: {round(historical_peak,2)} kWh</p>
<p>Predicted Peak: {round(predicted_peak,2)} kWh</p>
<p>Peak Risk: {peak_risk}</p>

<h2>Diagnostics</h2>
<p>Anomalies Detected: {len(anomalies)}</p>
<p>Root Cause: {root_cause}</p>
<p>Maintenance Priority: {maintenance_priority}</p>

<h2>Impact Analysis</h2>
<p>Energy Change ({forecast_hours}h): {round(projected_energy_change,2)} kWh</p>
<p>Cost Impact: ₹ {round(projected_cost_change,2)}</p>
<p>CO₂ Impact: {round(projected_co2_change,2)} kg</p>

</body>
</html>
"""

with open("reports/decision_report.html", "w", encoding="utf-8") as f:
    f.write(report_content)

print("Report saved to reports/decision_report.html")