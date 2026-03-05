import numpy as np
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_absolute_error


def run_forecasting(df, forecast_hours=168):

    # -------------------------
    # FEATURE SELECTION
    # -------------------------

    features = [
        "Ambient_Temp",
        "Humidity",
        "WBT",
        "Occupancy",
        "iKW_TR"
    ]

    X = df[features]
    y = df["kWh"]

    # -------------------------
    # TRAIN TEST SPLIT
    # -------------------------

    X_train, X_test, y_train, y_test = train_test_split(
        X,
        y,
        test_size=0.2,
        random_state=42
    )

    # -------------------------
    # MODEL
    # -------------------------

    model = RandomForestRegressor(
        n_estimators=200,
        random_state=42
    )

    model.fit(X_train, y_train)

    # -------------------------
    # EVALUATION
    # -------------------------

    y_pred = model.predict(X_test)

    mae = mean_absolute_error(y_test, y_pred)

    # -------------------------
    # FUTURE PREDICTION
    # -------------------------

    last_values = X.iloc[-forecast_hours:]

    future_prediction = model.predict(last_values)

    predicted_peak = np.max(future_prediction)

    historical_peak = df["kWh"].max()

    peak_risk = "Normal"

    if predicted_peak > historical_peak:

        peak_risk = "High"

    return {

        "future_prediction": future_prediction,
        "forecast_hours": forecast_hours,
        "mae": mae,
        "predicted_peak": predicted_peak,
        "historical_peak": historical_peak,
        "peak_risk": peak_risk
    }