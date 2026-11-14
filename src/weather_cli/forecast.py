import urllib.parse

from .geocoding import Location
from .http import get_json


def fetch(loc: Location, days: int = 3, units: str = "metric", past: int = 0) -> dict:
    params = {
        "latitude": loc.lat,
        "longitude": loc.lon,
        "current": "temperature_2m,apparent_temperature,weather_code,wind_speed_10m",
        "daily": (
            "weather_code,temperature_2m_max,temperature_2m_min,"
            "precipitation_probability_max,precipitation_sum"
        ),
        "timezone": "auto",
        "forecast_days": days,
    }
    if past:
        params["past_days"] = past
    if units == "imperial":
        params["temperature_unit"] = "fahrenheit"
        params["wind_speed_unit"] = "mph"
        params["precipitation_unit"] = "inch"
    query = urllib.parse.urlencode(params)
    return get_json(f"https://api.open-meteo.com/v1/forecast?{query}")