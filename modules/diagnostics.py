import numpy as np
from sklearn.ensemble import IsolationForest

def run_diagnostics(df):

    # Degradation Trend
    df["Time_Index"] = range(len(df))
    trend_coeff = np.polyfit(df["Time_Index"], df["COP"], 1)[0]

    if trend_coeff < -0.0005:
        degradation_status = "Degrading"
    else:
        degradation_status = "Stable"

    # Anomaly Detection
    anomaly_model = IsolationForest(contamination=0.02, random_state=42)
    df["Anomaly"] = anomaly_model.fit_predict(
        df[["kWh", "Ambient_Temp", "Humidity", "Occupancy", "iKW_TR"]]
    )
    anomalies = df[df["Anomaly"] == -1]

    # Root Cause Analysis
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

    # Maintenance Priority
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

    return {
        "df": df,
        "anomalies": anomalies,
        "degradation_status": degradation_status,
        "root_cause": root_cause,
        "maintenance_priority": maintenance_priority
    }