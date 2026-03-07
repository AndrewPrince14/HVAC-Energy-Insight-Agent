def apply_scenario(df, scenario="normal"):
    df = df.copy()
    eff_col = "iKW-TR" if "iKW-TR" in df.columns else "iKW_TR" if "iKW_TR" in df.columns else None

    if scenario == "heatwave":
        df["Ambient_Temp"] += 5
        df["Humidity"] *= 1.10
        df["kWh"] *= 1.15
        if eff_col: df[eff_col] *= 1.08

    elif scenario == "high_occupancy":
        df["Occupancy"] = (df["Occupancy"] * 1.3).clip(upper=500)
        df["kWh"] *= 1.10

    elif scenario == "equipment_fault":
        if eff_col: df[eff_col] *= 1.25
        df["kWh"] *= 1.12

    elif scenario == "solar_boost":
        df["kWh"] *= 0.85
        if eff_col: df[eff_col] *= 0.92

    elif scenario == "night_mode":
        df["Occupancy"] = (df["Occupancy"] * 0.15).clip(lower=5)
        df["kWh"] *= 0.55
        df["Ambient_Temp"] -= 4
        if eff_col: df[eff_col] *= 0.88

    elif scenario == "monsoon":
        df["Humidity"] = (df["Humidity"] * 1.35).clip(upper=98)
        df["Ambient_Temp"] -= 2
        df["kWh"] *= 1.08
        if eff_col: df[eff_col] *= 1.12

    elif scenario == "maintenance_mode":
        df["kWh"] *= 1.20
        if eff_col: df[eff_col] *= 1.35
        df["Occupancy"] = (df["Occupancy"] * 0.7).clip(lower=10)

    # Recalculate WBT after scenario modifies Ambient_Temp / Humidity
    if "Ambient_Temp" in df.columns and "Humidity" in df.columns:
        from modules.data_loader import calculate_wbt
        df["WBT"] = calculate_wbt(df["Ambient_Temp"], df["Humidity"])

    return df


SCENARIO_DESCRIPTIONS = {
    "normal": "Standard operating conditions. All systems nominal.",
    "heatwave": "Extreme outdoor heat (+5°C). Cooling load elevated. Efficiency degraded.",
    "equipment_fault": "Chiller performance degraded. iKW-TR elevated by 25%.",
    "solar_boost": "Rooftop solar active. Grid load reduced by 15%. Efficiency improved.",
    "night_mode": "Low occupancy night operation. Reduced load. Single chiller optimal.",
    "monsoon": "High humidity stress. Cooling tower performance reduced. Load elevated.",
    "maintenance_mode": "One chiller offline. Remaining units at high load. Critical monitoring.",
}