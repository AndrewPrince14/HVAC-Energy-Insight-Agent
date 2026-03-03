import pandas as pd

def load_data(path="data/hvac_dataset.csv"):
    df = pd.read_csv(path)
    df["Timestamp"] = pd.to_datetime(df["Timestamp"])
    df["COP"] = 3.517 / df["iKW_TR"]
    return df