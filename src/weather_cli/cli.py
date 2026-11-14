import argparse
import os
import sys

from . import forecast, geocoding
from .display import render

def past_days(value):
    try:
        n = int(value)
    except ValueError:
        raise argparse.ArgumentTypeError(f"'{value}' is not a number (use 1 to 7)")
    if not 1 <= n <= 7:
        raise argparse.ArgumentTypeError("must be between 1 and 7")
    return n


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
    p.add_argument(
        "-p", "--past",
        nargs="?", const=3, default=0, type=past_days, metavar="N",
        help="also show the past N days (1-7, default 3 if no number given)",
    )
    return p.parse_args(argv)


def main(argv=None):
    args = parse_args(argv)
    try:
        if args.place:
            loc = geocoding.from_name(" ".join(args.place))
        else:
            loc = geocoding.from_ip()
        data = forecast.fetch(loc, args.days, args.units, args.past)
    except Exception as e:
        sys.exit(f"Error: {e}")
    print(render(loc.name, data, args.units, args.past))