def generate_report(
    df,
    anomalies,
    predicted_avg,
    mae,
    forecast_hours,
    projected_energy_change,
    projected_cost_change,
    projected_co2_change
):

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

    <div class="section">
    <h2>System Summary</h2>
    <p>Total Records: {len(df)}</p>
    <p>Average Energy Consumption: {round(df["kWh"].mean(),2)} kWh</p>
    <p>Average COP: {round(df["COP"].mean(),2)}</p>
    </div>

    <div class="section">
    <h2>Forecasting</h2>
    <p>Predicted {forecast_hours}-hour Average Demand: {round(predicted_avg,2)} kWh</p>
    <p>Model MAE: {round(mae,2)} kWh</p>
    </div>

    <div class="section">
    <h2>Anomaly Detection</h2>
    <p>Number of Detected Anomalies: {len(anomalies)}</p>
    </div>

    <div class="section">
    <h2>Impact Analysis</h2>
    <p>Projected Energy Change ({forecast_hours}h): {round(projected_energy_change,2)} kWh</p>
    <p>Estimated Cost Impact: ₹ {round(projected_cost_change,2)}</p>
    <p>Estimated CO₂ Impact: {round(projected_co2_change,2)} kg</p>
    </div>

    </body>
    </html>
    """

    with open("reports/decision_report.html", "w", encoding="utf-8") as f:
        f.write(report_content)