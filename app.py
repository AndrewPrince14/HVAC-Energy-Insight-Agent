import sys
import numpy as np
import pandas as pd

from modules.weather_api import get_weather
from modules.data_loader import load_data
from modules.scenario_engine import apply_scenario
from modules.diagnostics import run_diagnostics
from modules.forecasting import run_forecasting
from modules.chiller_sequencing import run_chiller_sequencing
from modules.renewable import apply_renewable_offset
from modules.optimization import run_optimization
from modules.reporting import generate_report
from modules.comparison import generate_comparison_report


# -------------------------
# SCENARIO SELECTION
# -------------------------
scenario = "normal"

if len(sys.argv) > 1:
    scenario = sys.argv[1]

print("\n--- Scenario Simulation ---")
print("Active Scenario:", scenario)


# -------------------------
# LOAD DATA
# -------------------------
df = load_data()

# Apply scenario effects
df = apply_scenario(df, scenario)


# -------------------------
# DIAGNOSTICS
# -------------------------
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


# -------------------------
# FORECASTING
# -------------------------
forecast_results = run_forecasting(df)

mae = forecast_results["mae"]
future_prediction = forecast_results["future_prediction"]
forecast_hours = forecast_results["forecast_hours"]
predicted_peak = forecast_results["predicted_peak"]
historical_peak = forecast_results["historical_peak"]
peak_risk = forecast_results["peak_risk"]

predicted_avg = np.mean(future_prediction)

print("\n--- Load Forecasting ---")
print("Model Mean Absolute Error (kWh):", round(mae, 2))


# -------------------------
# CHILLER SEQUENCING
# -------------------------
sequencing_results = run_chiller_sequencing(
    predicted_peak,
    predicted_avg
)

chillers_required = sequencing_results["chillers_required"]
optimized_cop = sequencing_results["optimized_cop"]

print("\n--- Chiller Sequencing Plan ---")
print("Predicted Cooling Load Peak:", round(predicted_peak,2), "kWh")
print("Chillers Required:", chillers_required)
print("Estimated Optimized COP:", optimized_cop)


# -------------------------
# RENEWABLE INTEGRATION
# -------------------------
future_prediction, total_solar_generated = apply_renewable_offset(
    future_prediction,
    forecast_hours
)

predicted_peak = max(future_prediction)
predicted_avg = future_prediction.mean()


# -------------------------
# PEAK DEMAND ANALYSIS
# -------------------------
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

optimization_recommendations = run_optimization(
    predicted_avg,
    historical_avg,
    predicted_peak,
    historical_peak,
    peak_risk,
    maintenance_priority,
    df
)

increase_percent = ((predicted_avg - historical_avg) / historical_avg) * 100

print("Root Cause:", root_cause)
print("Maintenance Priority:", maintenance_priority)
print("Peak Risk Level:", peak_risk)

print("\n--- Optimization Recommendations ---")

for rec in optimization_recommendations:
    print("-", rec)

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

grid_avg_before_solar = historical_avg
grid_avg_after_solar = predicted_avg

grid_difference = grid_avg_after_solar - grid_avg_before_solar

operational_energy_change = grid_difference * forecast_hours
solar_contribution = total_solar_generated

total_grid_reduction = abs(operational_energy_change) + solar_contribution

estimated_cost_impact = total_grid_reduction * tariff_per_kwh
estimated_co2_impact = total_grid_reduction * emission_factor

print("Operational energy change (168h):", round(operational_energy_change, 2), "kWh")
print("Renewable solar contribution (168h):", round(solar_contribution, 2), "kWh")
print("Total grid energy reduction:", round(total_grid_reduction, 2), "kWh")
print("Estimated cost impact: ₹", round(estimated_cost_impact, 2))
print("Estimated CO2 impact:", round(estimated_co2_impact, 2), "kg")


# -------------------------
# GENERATE SCENARIO REPORT
# -------------------------
print("\nGenerating HTML decision report...")

generate_report(
    scenario,
    df,
    anomalies,
    predicted_avg,
    mae,
    forecast_hours,
    operational_energy_change,
    estimated_cost_impact,
    estimated_co2_impact,
    historical_peak,
    predicted_peak,
    peak_risk,
    root_cause,
    maintenance_priority,
    total_solar_generated
)


# -------------------------
# SCENARIO COMPARISON DATA
# -------------------------
comparison_result = {
    "scenario": scenario,
    "avg": predicted_avg,
    "peak": predicted_peak,
    "energy": operational_energy_change,
    "cost": estimated_cost_impact,
    "co2": estimated_co2_impact
}

generate_comparison_report(comparison_result)