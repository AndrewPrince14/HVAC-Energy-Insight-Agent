from datetime import datetime
import requests

def get_weather():

    url = "https://api.open-meteo.com/v1/forecast"

    params = {
        "latitude": 13.0827,
        "longitude": 80.2707,
        "current_weather": True,
        "hourly": "relativehumidity_2m",
        "timezone": "auto"
    }

    response = requests.get(url, params=params)
    data = response.json()

    current_hour = min(datetime.now().hour, len(data["hourly"]["relativehumidity_2m"]) - 1)

    weather = {
        "temperature": data["current_weather"]["temperature"],
        "windspeed": data["current_weather"]["windspeed"],
        "humidity": data["hourly"]["relativehumidity_2m"][current_hour]
    }

    return weather