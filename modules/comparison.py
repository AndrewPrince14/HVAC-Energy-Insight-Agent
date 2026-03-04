import pandas as pd
import os

def generate_comparison_report(result):

    file_path = "reports/scenario_results.csv"

    # Convert result to DataFrame
    df_new = pd.DataFrame([result])

    # If file exists, append
    if os.path.exists(file_path):
        df_existing = pd.read_csv(file_path)
        df_all = pd.concat([df_existing, df_new], ignore_index=True)
    else:
        df_all = df_new

    # Save updated results
    df_all.to_csv(file_path, index=False)

    # Generate HTML comparison
    html = """
<html>
<head>
<title>Scenario Comparison Report</title>

<style>
body {
font-family: Arial;
margin: 40px;
background-color: #f4f6f9;
}

h1 {
color: #1B4F72;
}

table {
width: 100%;
border-collapse: collapse;
background: white;
box-shadow: 0px 2px 6px rgba(0,0,0,0.1);
}

th, td {
padding: 12px;
border: 1px solid #ddd;
text-align: center;
}

th {
background-color: #2E86C1;
color: white;
}
</style>
</head>

<body>

<h1>HVAC Scenario Comparison</h1>

<table>
<tr>
<th>Scenario</th>
<th>Predicted Avg Demand (kWh)</th>
<th>Predicted Peak (kWh)</th>
<th>Energy Impact (kWh)</th>
<th>Cost Impact (₹)</th>
<th>CO₂ Impact (kg)</th>
</tr>
"""

    for _, r in df_all.iterrows():

        html += f"""
<tr>
<td>{r['scenario']}</td>
<td>{round(r['avg'],2)}</td>
<td>{round(r['peak'],2)}</td>
<td>{round(r['energy'],2)}</td>
<td>{round(r['cost'],2)}</td>
<td>{round(r['co2'],2)}</td>
</tr>
"""

    html += """
</table>
</body>
</html>
"""

    with open("reports/scenario_comparison.html", "w", encoding="utf-8") as f:
        f.write(html)

    print("Scenario comparison report saved to reports/scenario_comparison.html")