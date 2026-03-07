def run_optimization(predicted_avg, historical_avg, predicted_peak, historical_peak,
                     peak_risk, maintenance_priority, df, forecast_hours=168):

    recs = []
    demand_increase_pct = ((predicted_avg - historical_avg) / historical_avg) * 100
    peak_ratio = predicted_peak / historical_peak
    avg_wbt = df["WBT"].mean() if "WBT" in df.columns else 22.0

    eff_col = "iKW-TR" if "iKW-TR" in df.columns else "iKW_TR" if "iKW_TR" in df.columns else None
    avg_eff = df[eff_col].mean() if eff_col else 0.7

    # Horizon label
    if forecast_hours <= 24:
        urgency = "🔴 IMMEDIATE"
        timeframe = "within the next hour"
    elif forecast_hours <= 48:
        urgency = "🟡 SHORT-TERM"
        timeframe = "within 48 hours"
    elif forecast_hours <= 72:
        urgency = "🟡 SHORT-TERM"
        timeframe = "within 3 days"
    else:
        urgency = "🟢 WEEKLY STRATEGY"
        timeframe = "this week"

    # Peak demand
    if peak_risk == "High" or demand_increase_pct > 10:
        if forecast_hours <= 24:
            recs.append(f"{urgency} — Demand elevated {demand_increase_pct:.1f}%. Increase setpoint by 1–2°C now to shed load.")
        elif forecast_hours <= 72:
            recs.append(f"{urgency} — Peak demand risk detected. Pre-cool facility during off-peak hours {timeframe}.")
        else:
            recs.append(f"{urgency} — Weekly peak risk. Schedule demand response strategy and pre-cooling windows {timeframe}.")
    else:
        recs.append(f"✅ Demand within normal range. No setpoint adjustment needed {timeframe}.")

    # Efficiency
    if avg_eff > 0.75:
        if forecast_hours <= 24:
            recs.append(f"{urgency} — iKW-TR at {avg_eff:.3f} (above 0.75 threshold). Inspect refrigerant and heat exchanger now.")
        else:
            recs.append(f"⚠️ iKW-TR at {avg_eff:.3f}. Schedule chiller inspection and refrigerant check {timeframe}.")
    elif avg_eff > 0.65:
        recs.append(f"⚠️ iKW-TR at {avg_eff:.3f} — approaching threshold. Plan preventive maintenance {timeframe}.")
    else:
        recs.append(f"✅ System efficiency healthy at {avg_eff:.3f} iKW-TR.")

    # Chiller load
    if peak_ratio > 1.05:
        recs.append(f"⚠️ Peak load {peak_ratio:.2f}x historical. Distribute load across all available chillers {timeframe}.")
    else:
        recs.append("✅ Chiller load distribution stable.")

    # WBT advisory
    if avg_wbt > 24:
        recs.append(f"⚠️ WBT at {avg_wbt:.1f}°C — elevated. Check condenser water temps and cooling tower performance.")

    # Maintenance
    if maintenance_priority == "High":
        recs.append(f"🔴 HIGH maintenance priority. Immediate inspection before next peak cycle.")
    elif maintenance_priority == "Moderate":
        recs.append(f"🟡 Moderate priority. Schedule review {timeframe}.")

    return recs