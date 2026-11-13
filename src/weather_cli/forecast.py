import urllib.parse

from .geocoding import Location
from .http import get_json


def fetch(loc: Location, days: int = 3, units: str = "metric") -> dict:
    params = {
        "latitude": loc.lat,
        "longitude": loc.lon,
        "current": "temperature_2m,apparent_temperature,weather_code,wind_speed_10m",
        "daily": "weather_code,temperature_2m_max,temperature_2m_min,precipitation_probability_max",
        "timezone": "auto",
        "forecast_days": days,
    }
    if units == "imperial":
        params["temperature_unit"] = "fahrenheit"
        params["wind_speed_unit"] = "mph"
    query = urllib.parse.urlencode(params)
    return get_json(f"https://api.open-meteo.com/v1/forecast?{query}")