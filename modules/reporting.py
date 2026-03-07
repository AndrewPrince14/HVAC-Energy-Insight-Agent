def generate_report(
    scenario,
    df,
    anomalies,
    predicted_avg,
    mae,
    forecast_hours,
    projected_energy_change,
    projected_cost_change,
    projected_co2_change,
    historical_peak,
    predicted_peak,
    peak_risk,
    root_cause,
    maintenance_priority,
    total_solar_generated
):

    eff_col = "iKW-TR" if "iKW-TR" in df.columns else "iKW_TR"
    avg_ikwtr = round(df[eff_col].mean(), 3)

    report_content = f"""
<html>
<head>
<title>HVAC Energy Insight Technical Report</title>

<style>

body {{
font-family: Arial, sans-serif;
margin: 40px;
background-color: #f4f6f9;
}}

h1 {{
color: #1B4F72;
}}

h2 {{
color: #2E86C1;
border-bottom: 2px solid #ddd;
padding-bottom: 6px;
}}

.section {{
background: white;
padding: 20px;
margin-bottom: 25px;
border-radius: 8px;
box-shadow: 0px 2px 6px rgba(0,0,0,0.08);
}}

.metric {{
font-weight: bold;
}}

</style>
</head>

<body>

<h1>HVAC Energy Insight Decision Report</h1>

<div class="section">
<h2>Simulation Scenario</h2>
<p>Active Scenario: <span class="metric">{scenario}</span></p>
</div>

<div class="section">
<h2>System Overview</h2>
<p>Total Records Analysed: <span class="metric">{len(df)}</span></p>
<p>Average Energy Consumption: <span class="metric">{round(df["kWh"].mean(),2)} kWh</span></p>
<p>Average iKW-TR: <span class="metric">{avg_ikwtr}</span></p>
</div>

<div class="section">
<h2>Forecast Analysis</h2>
<p>Forecast Horizon: <span class="metric">{forecast_hours} hours</span></p>
<p>Predicted Average Demand: <span class="metric">{round(predicted_avg,2)} kWh</span></p>
<p>Forecast Model MAE: <span class="metric">{round(mae,2)} kWh</span></p>
</div>
<div class="section">
<h2>Environmental Conditions</h2>
<p>Average Temperature: <span class="metric">{round(df["Ambient_Temp"].mean(),2)} °C</span></p>
<p>Average Humidity: <span class="metric">{round(df["Humidity"].mean(),2)} %</span></p>
<p>Average Wet Bulb Temperature: <span class="metric">{round(df["WBT"].mean(),2)} °C</span></p>
</div>

<div class="section">
<h2>Peak Demand Risk</h2>
<p>Historical Peak Load: <span class="metric">{round(historical_peak,2)} kWh</span></p>
<p>Predicted Peak Load: <span class="metric">{round(predicted_peak,2)} kWh</span></p>
<p>Risk Level: <span class="metric">{peak_risk}</span></p>
</div>

<div class="section">
<h2>Diagnostic Intelligence</h2>
<p>Anomalies Detected: <span class="metric">{len(anomalies)}</span></p>
<p>Root Cause Assessment: <span class="metric">{root_cause}</span></p>
<p>Maintenance Priority: <span class="metric">{maintenance_priority}</span></p>
</div>

<div class="section">
<h2>Optimization Strategy</h2>
<p>Chiller Sequencing Optimization Applied</p>
<p>Energy Efficiency Optimization Evaluated</p>
</div>

<div class="section">
<h2>Renewable Energy Integration</h2>
<p>Total Solar Contribution: <span class="metric">{round(total_solar_generated,2)} kWh</span></p>
</div>

<div class="section">
<h2>Impact Quantification</h2>
<p>Total Grid Energy Reduction: <span class="metric">{round(abs(projected_energy_change),2)} kWh</span></p>
<p>Estimated Cost Impact: <span class="metric">₹ {round(abs(projected_cost_change),2)}</span></p>
<p>Estimated CO₂ Impact: <span class="metric">{round(abs(projected_co2_change),2)} kg</span></p>
</div>

<div class="section">
<h2>Final Engineering Recommendations</h2>
<p>• Monitor system efficiency trends continuously.</p>
<p>• Investigate anomaly patterns for potential operational issues.</p>
<p>• Maintain optimized chiller sequencing during peak demand periods.</p>
<p>• Utilize renewable energy offsets where possible to reduce grid dependency.</p>
</div>

</body>
</html>
"""

    filename = f"reports/{scenario}_report.html"

    with open(filename, "w", encoding="utf-8") as f:
        f.write(report_content)

    print(f"Report saved to {filename}")