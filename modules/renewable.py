import numpy as np

def apply_renewable_offset(future_prediction, forecast_hours):
    """
    Simulate rooftop solar generation during daytime hours.
    """

    solar_profile = []

    for hour in range(forecast_hours):
        # Assume daytime between 8 AM and 5 PM
        hour_of_day = hour % 24

        if 8 <= hour_of_day <= 17:
            # Simulate moderate solar production (kWh offset)
            solar_profile.append(120)
        else:
            solar_profile.append(0)

    solar_profile = np.array(solar_profile)

    adjusted_prediction = future_prediction - solar_profile

    # Prevent negative demand
    adjusted_prediction = np.maximum(adjusted_prediction, 0)

    total_solar_generated = np.sum(solar_profile)

    return adjusted_prediction, total_solar_generated