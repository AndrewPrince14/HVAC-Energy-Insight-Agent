def run_optimization(
    predicted_avg,
    historical_avg,
    predicted_peak,
    historical_peak,
    peak_risk,
    maintenance_priority,
    df
):

    recommendations = []

    demand_increase_percent = (
        (predicted_avg - historical_avg) / historical_avg
    ) * 100

    peak_ratio = predicted_peak / historical_peak

    avg_wbt = df["WBT"].mean()

    # Setpoint Optimization
    if peak_risk == "High" or demand_increase_percent > 10:
        recommendations.append(
            "Consider increasing HVAC temperature setpoint by 1-2°C during peak hours to reduce system load."
        )
    else:
        recommendations.append(
            "No immediate setpoint adjustment required."
        )

    # Chiller Load Balancing
    if peak_ratio > 1.05:
        recommendations.append(
            "Distribute cooling load evenly across chillers to prevent overloading a single unit."
        )
    else:
        recommendations.append(
            "Current chiller load distribution appears stable."
        )

    # Maintenance Link
    if maintenance_priority in ["High", "Moderate"]:
        recommendations.append(
            f"Maintenance priority is {maintenance_priority}. Review chiller performance."
        )

    return recommendations