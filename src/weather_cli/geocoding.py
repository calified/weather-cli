import urllib.parse
from dataclasses import dataclass

from .http import get_json

@dataclass
class Location:
    lat: float
    lon: float
    name: str
    
class LocationError(Exception):
    pass
    
def from_ip() -> Location:
    data = get_json("https://ipinfo.io/json")
    lat, lon = data["loc"].split(",")
    return Location(float(lat), float(lon), f'{data["city"]}, {data["country"]}')
    
def from_name(name: str) -> Location:
    query = urllib.parse.urlencode({"name": name, "count": 1})
    data = get_json(f"https://geocoding-api.open-meteo.com/v1/search?{query}")
    if "results" not in data:
        raise LocationError(f"Couldn't find a place called '{name}'.")
    r = data["results"][0]
    return Location(r["latitude"], r["longitude"], f'{r["name"]}, {r.get("country", "")}')