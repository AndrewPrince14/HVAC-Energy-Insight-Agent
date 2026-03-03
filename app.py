import requests
import pandas as pd
from modules.reporting import generate_report
from modules.forecasting import run_forecasting
from modules.diagnostics import run_diagnostics
from modules.data_loader import load_data
from sklearn.ensemble import IsolationForest, RandomForestRegressor
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_absolute_error
import numpy as np

# -------------------------
# LOAD DATA
# -------------------------
df = load_data()
diagnostics_results = run_diagnostics(df)

df = diagnostics_results["df"]
anomalies = diagnostics_results["anomalies"]
degradation_status = diagnostics_results["degradation_status"]
root_cause = diagnostics_results["root_cause"]
maintenance_priority = diagnostics_results["maintenance_priority"]

print("\n--- Degradation Trend Analysis ---")
if degradation_status == "Degrading":
    print("⚠ Efficiency degradation trend detected.")
else:
    print("✅ No significant efficiency degradation trend.")

print("\n--- Anomaly Detection ---")
print("Number of detected anomalies:", len(anomalies))

print("\n--- Root Cause Analysis ---")
print("Root Cause Assessment:", root_cause)

print("\n--- Maintenance Priority Assessment ---")
print("Maintenance Priority Level:", maintenance_priority)

forecast_results = run_forecasting(df)

mae = forecast_results["mae"]
future_prediction = forecast_results["future_prediction"]
predicted_avg = np.mean(future_prediction)
forecast_hours = forecast_results["forecast_hours"]
predicted_peak = forecast_results["predicted_peak"]
historical_peak = forecast_results["historical_peak"]
peak_risk = forecast_results["peak_risk"]

print("\n--- Load Forecasting ---")
print("Model Mean Absolute Error (kWh):", round(mae, 2))

print("\n--- Peak Demand Analysis ---")
print("Historical Peak Load:", round(historical_peak, 2), "kWh")
print("Predicted Peak Load (168h):", round(predicted_peak, 2), "kWh")

if peak_risk == "High":
    print("⚠ Risk of exceeding historical peak. Potential demand penalty.")
else:
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

print("\nGenerating HTML decision report...")

generate_report(
    df,
    anomalies,
    predicted_avg,
    mae,
    forecast_hours,
    projected_energy_change,
    projected_cost_change,
    projected_co2_change
)

print("Report saved to reports/decision_report.html")