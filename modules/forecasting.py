import numpy as np
import shap
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_absolute_error


def run_forecasting(df, forecast_hours=168):
    df = df.copy()
    eff_col = "iKW-TR" if "iKW-TR" in df.columns else "iKW_TR" if "iKW_TR" in df.columns else None

    features = ["Ambient_Temp", "Humidity", "Occupancy"]
    if "WBT" in df.columns: features.append("WBT")
    if eff_col: features.append(eff_col)

    X, y = df[features], df["kWh"]
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    model = RandomForestRegressor(n_estimators=200, random_state=42)
    model.fit(X_train, y_train)

    mae = mean_absolute_error(y_test, model.predict(X_test))
    accuracy_pct = round(100 - (mae / y.mean() * 100), 1)

    last_values = X.iloc[-forecast_hours:] if len(X) >= forecast_hours else X
    future_prediction = model.predict(last_values)

    tree_preds = np.array([tree.predict(last_values.values) for tree in model.estimators_])
    upper_band = np.percentile(tree_preds, 85, axis=0)
    lower_band = np.percentile(tree_preds, 15, axis=0)

    predicted_peak = float(np.max(future_prediction))
    historical_peak = float(df["kWh"].max())
    avg_eff = float(df[eff_col].mean()) if eff_col else 0.0

    if avg_eff > 0.75:
        peak_risk = "High"
    elif predicted_peak > historical_peak * 0.95:
        peak_risk = "High"
    elif avg_eff > 0.65 or predicted_peak > historical_peak * 0.85:
        peak_risk = "Moderate"
    else:
        peak_risk = "Normal"

    explainer = shap.TreeExplainer(model)
    shap_values = explainer.shap_values(X_test)
    mean_shap = np.abs(shap_values).mean(axis=0)
    total = mean_shap.sum()
    shap_importance = {
        features[i]: round(float(mean_shap[i] / total * 100), 1)
        for i in range(len(features))
    }
    shap_importance = dict(sorted(shap_importance.items(), key=lambda x: x[1], reverse=True))

    return {
        "future_prediction": future_prediction.tolist(),
        "upper_band": upper_band.tolist(),
        "lower_band": lower_band.tolist(),
        "forecast_hours": forecast_hours,
        "mae": mae,
        "accuracy_pct": accuracy_pct,
        "predicted_peak": predicted_peak,
        "historical_peak": historical_peak,
        "peak_risk": peak_risk,
        "avg_eff": avg_eff,
        "shap_importance": shap_importance,
    }