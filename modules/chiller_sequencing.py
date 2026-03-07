def run_chiller_sequencing(predicted_peak, predicted_avg, scenario="normal"):
    # Scenario overrides
    forced_min = {
        "maintenance_mode": 2,  # one offline, so min 2 of remaining
        "heatwave": 2,
        "equipment_fault": 2,
    }
    forced_max = {
        "night_mode": 1,
        "solar_boost": 1,
    }

    chiller_capacity = 800  # kWh per chiller

    # Base calculation
    if predicted_peak < chiller_capacity * 0.55:
        chillers_required = 1
    elif predicted_peak < chiller_capacity * 1.15:
        chillers_required = 2
    else:
        chillers_required = 3

    # Apply scenario constraints
    if scenario in forced_min:
        chillers_required = max(chillers_required, forced_min[scenario])
    if scenario in forced_max:
        chillers_required = min(chillers_required, forced_max[scenario])

    load_per_chiller = round(predicted_peak / chillers_required, 2)
    loading_ratio = round((load_per_chiller / chiller_capacity) * 100, 1)

    # COP degrades with load
    base_cop = 5.5
    cop_degradation = (loading_ratio / 100) * 1.4
    optimized_cop = round(max(base_cop - cop_degradation, 2.8), 2)

    if loading_ratio > 85:
        load_status = "🔴 High Load — consider standby chiller"
    elif loading_ratio > 60:
        load_status = "🟡 Moderate Load — optimal sequencing active"
    else:
        load_status = "🟢 Low Load — single chiller sufficient"

    return {
        "chillers_required": chillers_required,
        "optimized_cop": optimized_cop,
        "load_per_chiller": load_per_chiller,
        "loading_ratio": loading_ratio,
        "load_status": load_status,
    }