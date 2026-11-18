import unicodedata
import urllib.parse
from dataclasses import dataclass, replace

from .http import get_json


@dataclass
class Location:
    lat: float
    lon: float
    name: str
    city: str = ""
    region: str = ""
    country: str = ""
    country_code: str = ""
    population: int = 0

    @property
    def full_label(self) -> str:
        parts = []
        for part in (self.city, self.region, self.country):
            if part and part not in parts:
                parts.append(part)
        return ", ".join(parts)


class LocationError(Exception):
    pass


def from_ip() -> Location:
    data = get_json("https://ipinfo.io/json")
    lat, lon = data["loc"].split(",")
    return Location(float(lat), float(lon), f'{data["city"]}, {data["country"]}')


def with_region(loc: Location) -> Location:
    return replace(loc, name=loc.full_label)


def _plain(text: str) -> str:
    decomposed = unicodedata.normalize("NFKD", text)
    stripped = "".join(c for c in decomposed if not unicodedata.combining(c))
    return stripped.casefold().strip()


def split_query(text: str):
    name, _, qualifier = text.partition(",")
    return name.strip(), qualifier.strip()


def search(name: str, count: int = 20) -> list:
    query = urllib.parse.urlencode({"name": name, "count": count, "language": "en"})
    data = get_json(f"https://geocoding-api.open-meteo.com/v1/search?{query}")
    results = []
    for r in data.get("results", []):
        city = r.get("name", "")
        country = r.get("country", "")
        short = ", ".join(p for p in (city, country) if p)
        results.append(Location(
            lat=r["latitude"],
            lon=r["longitude"],
            name=short,
            city=city,
            region=r.get("admin1", ""),
            country=country,
            country_code=r.get("country_code", ""),
            population=r.get("population") or 0,
        ))
    return results


_ALIASES = {"uk": "gb", "usa": "us"}


def _matches(loc: Location, qualifier: str) -> bool:
    q = _plain(qualifier)
    q = _ALIASES.get(q, q)
    if not q:
        return True
    if len(q) == 2 and q == loc.country_code.casefold():
        return True
    return q in _plain(loc.region) or q in _plain(loc.country)


def _dominant(options: list, ratio: int = 10) -> bool:
    top, rest = options[0], options[1:]
    if not top.population:
        return False
    return top.population >= ratio * max(o.population for o in rest)


def find(text: str, count: int = 20):
    name, qualifier = split_query(text)
    if not name:
        raise LocationError("No place name given.")

    results = search(name, count)
    if qualifier:
        results = [r for r in results if _matches(r, qualifier)]
    if not results:
        where = f" in '{qualifier}'" if qualifier else ""
        raise LocationError(f"Couldn't find a place called '{name}'{where}.")

    top = results[0]
    exact = _plain(top.city) == _plain(name)
    if exact:
        options = [r for r in results if _plain(r.city) == _plain(top.city)]
    else:
        options = results
    options = options[:5]

    if exact and qualifier:
        return [with_region(options[0])], True, False
    if exact:
        needs_choice = len(options) > 1 and not _dominant(options)
    else:
        needs_choice = True
    return options, exact, needs_choice