import numpy as np
import pandas as pd


def run_diagnostics(df):
    df = df.copy()
    df["Time_Index"] = range(len(df))

    if "iKW-TR" in df.columns:
        eff_col = "iKW-TR"
    elif "iKW_TR" in df.columns:
        eff_col = "iKW_TR"
    else:
        eff_col = None

    # ── Z-SCORE ANOMALY DETECTION (truly dynamic) ─────────────────────
    check_cols = ["kWh", "Ambient_Temp", "Humidity"]
    if eff_col:
        check_cols.append(eff_col)

    z_scores = pd.DataFrame()
    for col in check_cols:
        mean = float(df[col].mean())
        std = float(df[col].std())
        z_scores[col] = (df[col] - mean) / std if std > 0 else 0

    df["max_z"] = z_scores.abs().max(axis=1)
    df["anomaly_col"] = z_scores.abs().idxmax(axis=1)
    df["Anomaly"] = df["max_z"].apply(lambda z: -1 if z > 2.5 else 1)

    anomalies = df[df["Anomaly"] == -1].copy()
    anomaly_ratio = round(len(anomalies) / len(df) * 100, 1)

    if len(anomalies) > 0:
        worst = anomalies.loc[anomalies["max_z"].idxmax()]
        worst_z = round(worst["max_z"], 2)
        anomaly_description = f"{worst_z}σ deviation in {worst['anomaly_col']}"
    else:
        anomaly_description = "No significant anomalies"

    # ── DEGRADATION TREND ─────────────────────────────────────────────
    if eff_col:
        trend_coeff = np.polyfit(df["Time_Index"], df[eff_col], 1)[0]
        eff_std = df[eff_col].std()
        if trend_coeff > eff_std * 0.0002:
            degradation_status = "Degrading"
        elif trend_coeff > eff_std * 0.00005:
            degradation_status = "Marginal"
        else:
            degradation_status = "Stable"
    else:
        degradation_status = "Unknown"

    # ── ROOT CAUSE ────────────────────────────────────────────────────
    equipment_count = behavioral_count = thermal_count = 0
    eff_mean = df[eff_col].mean() if eff_col else 0

    for _, row in anomalies.iterrows():
        if eff_col and row[eff_col] > eff_mean * 1.05:
            equipment_count += 1
        if row["Occupancy"] > df["Occupancy"].mean() * 1.1:
            behavioral_count += 1
        if row["Ambient_Temp"] > df["Ambient_Temp"].mean() * 1.08:
            thermal_count += 1

    counts = {
        "Equipment inefficiency detected": equipment_count,
        "Thermal / environmental stress": thermal_count,
        "Behavioral / occupancy-driven surge": behavioral_count,
    }
    root_cause = max(counts, key=counts.get) if any(v > 0 for v in counts.values()) else "No dominant pattern"

    # ── PRIORITY SCORING ──────────────────────────────────────────────
    priority_score = 0
    if anomaly_ratio > 12: priority_score += 3
    elif anomaly_ratio > 7: priority_score += 2
    elif anomaly_ratio > 3: priority_score += 1

    if degradation_status == "Degrading": priority_score += 3
    elif degradation_status == "Marginal": priority_score += 1

    if eff_col:
        avg_eff = df[eff_col].mean()
        if avg_eff > 0.85: priority_score += 3
        elif avg_eff > 0.75: priority_score += 2
        elif avg_eff > 0.68: priority_score += 1

    if root_cause == "Equipment inefficiency detected": priority_score += 2
    elif root_cause == "Thermal / environmental stress": priority_score += 1

    kwh_spike = df["kWh"].max() / df["kWh"].mean()
    if kwh_spike > 2.0: priority_score += 2
    elif kwh_spike > 1.5: priority_score += 1

    if priority_score >= 7: maintenance_priority = "High"
    elif priority_score >= 4: maintenance_priority = "Moderate"
    else: maintenance_priority = "Low"

    return {
        "df": df,
        "anomalies": anomalies,
        "degradation_status": degradation_status,
        "root_cause": root_cause,
        "maintenance_priority": maintenance_priority,
        "priority_score": priority_score,
        "anomaly_ratio": anomaly_ratio,
        "anomaly_description": anomaly_description,
    }