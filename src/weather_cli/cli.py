import argparse
import os
import sys
import time

from . import forecast, geocoding, picker
from .display import render


def past_days(value):
    try:
        n = int(value)
    except ValueError:
        raise argparse.ArgumentTypeError(f"'{value}' is not a number (use 1 to 7)")
    if not 1 <= n <= 7:
        raise argparse.ArgumentTypeError("must be between 1 and 7")
    return n


def minutes(value):
    try:
        n = int(value)
    except ValueError:
        raise argparse.ArgumentTypeError(f"'{value}' is not a number of minutes")
    if not 1 <= n <= 1440:
        raise argparse.ArgumentTypeError("must be between 1 and 1440")
    return n


def parse_args(argv=None):
    p = argparse.ArgumentParser(prog="weather", description="Check the weather.")
    p.add_argument(
        "place", nargs="*",
        help="City name, optionally with a region: 'Paris, Texas' (default: detect from IP)",
    )
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
    p.add_argument(
        "-w", "--watch", action="store_true",
        help="keep running and refresh the weather until you press Ctrl+C",
    )
    p.add_argument(
        "-e", "--every",
        type=minutes, default=None, metavar="MIN",
        help="minutes between refreshes in --watch mode (1-1440, default 15)",
    )
    args = p.parse_args(argv)
    if args.every is not None and not args.watch:
        p.error("--every only works together with --watch")
    if args.every is None:
        args.every = 15
    return args


def resolve_location(place_words):
    if not place_words:
        return geocoding.from_ip()

    text = " ".join(place_words)
    options, exact, needs_choice = geocoding.find(text)
    if not needs_choice:
        return options[0]
    if picker.can_ask():
        return picker.choose(options, text, exact)

    best = geocoding.with_region(options[0])
    if exact:
        note = (f"several places match '{text}'; using {best.name}. "
                "Add a region to choose another, e.g. 'Paris, Texas'.")
    else:
        note = f"no exact match for '{text}'; using {best.name}."
    print(f"Note: {note}", file=sys.stderr)
    return best


def build_report(loc, args):
    data = forecast.fetch(loc, args.days, args.units, args.past)
    return render(loc.name, data, args.units, args.past)


def clear_screen():
    os.system("cls" if os.name == "nt" else "clear")


def watch(loc, args, out):
    wait = args.every * 60
    last = None
    while True:
        error = None
        try:
            last = build_report(loc, args)
        except Exception as e:
            if last is None:
                sys.exit(f"Error: {e}")
            error = " ".join(str(e).split())

        stamp = time.strftime("%H:%M:%S")
        if error:
            footer = (f"Update failed at {stamp} ({error}). Showing older data, "
                      f"retrying in {args.every} min. Ctrl+C to quit.")
        else:
            footer = (f"Updated {stamp}, refreshing every {args.every} min. "
                      "Ctrl+C to quit.")

        clear_screen()
        out(last + "\n" + footer)
        time.sleep(wait)


def main(argv=None, out=print):
    args = parse_args(argv)
    try:
        if args.watch and not sys.stdout.isatty():
            sys.exit("Error: --watch needs an interactive terminal, not piped output.")
        loc = resolve_location(args.place)
        if args.watch:
            watch(loc, args, out)
        else:
            out(build_report(loc, args))
    except KeyboardInterrupt:
        print(file=sys.stderr)
        sys.exit(130)
    except Exception as e:
        sys.exit(f"Error: {e}")