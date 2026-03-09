import pandas as pd
import numpy as np


def calculate_wbt(temp, humidity):
    """
    Approximate Wet Bulb Temperature using Stull's formula.
    """
    return (
        temp * np.arctan(0.151977 * (humidity + 8.313659)**0.5)
        + np.arctan(temp + humidity)
        - np.arctan(humidity - 1.676331)
        + 0.00391838 * humidity**1.5 * np.arctan(0.023101 * humidity)
        - 4.686035
    )


def load_data(path="data/hvac_dataset.csv"):
    df = pd.read_csv(path)
    df["Timestamp"] = pd.to_datetime(df["Timestamp"])

    # Efficiency calculation
    df["COP"] = 3.517 / df["iKW-TR"]

    # Add Wet Bulb Temperature
    if "WBT" not in df.columns:
        df["WBT"] = calculate_wbt(df["Ambient_Temp"], df["Humidity"])

    return df