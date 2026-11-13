import argparse
import os
import sys

from . import forecast, geocoding
from .display import render


def parse_args(argv=None):
    p = argparse.ArgumentParser(prog="weather", description="Check the weather.")
    p.add_argument("place", nargs="*", help="City name (default: detect from IP)")
    p.add_argument("-d", "--days", type=int, default=3, choices=range(1, 8))
    p.add_argument(
        "-u", "--units",
        choices=["metric", "imperial"],
        default=os.environ.get("WEATHER_UNITS", "metric"),
        help="metric (°C, km/h) or imperial (°F, mph)",
    )
    return p.parse_args(argv)


def main(argv=None):
    args = parse_args(argv)
    try:
        if args.place:
            loc = geocoding.from_name(" ".join(args.place))
        else:
            loc = geocoding.from_ip()
        data = forecast.fetch(loc, args.days, args.units)
    except Exception as e:
        sys.exit(f"Error: {e}")
    print(render(loc.name, data, args.units))