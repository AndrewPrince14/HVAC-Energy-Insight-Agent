import pandas as pd

def apply_scenario(df, scenario="normal"):
    """
    Modify dataset conditions to simulate operational scenarios
    """

    print("\n--- Scenario Simulation ---")
    print(f"Active Scenario: {scenario}")

    df = df.copy()

    if scenario == "heatwave":
        df["Ambient_Temp"] += 5
        df["kWh"] *= 1.15

    elif scenario == "high_occupancy":
        df["Occupancy"] *= 1.3
        df["kWh"] *= 1.10

    elif scenario == "equipment_fault":
        df["iKW_TR"] *= 1.25
        df["kWh"] *= 1.12

    elif scenario == "solar_boost":
        df["kWh"] *= 0.85

    elif scenario == "weekend_low_load":
        df["Occupancy"] *= 0.5
        df["kWh"] *= 0.75

    else:
        print("Normal operation scenario.")

    return df