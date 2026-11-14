import io
import os
import re
import sys
from contextlib import redirect_stdout

from .cli import main as run

RESET = "\033[0m"

# Condition names the display shows (kept here so this file is standalone)
CONDITIONS = [
    "Clear sky", "Mainly clear", "Partly cloudy", "Overcast",
    "Fog", "Freezing fog",
    "Light drizzle", "Drizzle", "Heavy drizzle",
    "Light rain", "Rain", "Heavy rain",
    "Light snow", "Snow", "Heavy snow",
    "Light showers", "Showers", "Heavy showers",
    "Thunderstorm, heavy hail", "Thunderstorm, hail", "Thunderstorm",
    "Unknown",
]


def paint(text, code):
    return f"\033[{code}m{text}{RESET}"


def to_c(value, unit):
    """Convert to Celsius so colour thresholds work for both units."""
    return (value - 32) * 5 / 9 if unit == "F" else value


def temp_code(t):
    if t <= 0:
        return "94"   # bright blue
    if t < 10:
        return "36"   # cyan
    if t < 18:
        return "32"   # green
    if t < 25:
        return "33"   # yellow
    return "31"       # red


def rain_code(p):
    if p >= 60:
        return "94"   # bright blue
    if p >= 30:
        return "36"   # cyan
    return "2"        # dim


def amount_code(value, unit):
    mm = value * 25.4 if unit == "in" else value
    if mm >= 5:
        return "94"   # bright blue
    if mm > 0:
        return "36"   # cyan
    return "2"        # dim (dry)


def cond_code(desc):
    d = desc.lower()
    if "thunder" in d:
        return "35"   # magenta
    if "snow" in d:
        return "97"   # bright white
    if "rain" in d or "drizzle" in d or "shower" in d:
        return "94"   # bright blue
    if "fog" in d:
        return "90"   # grey
    if "cloud" in d or "overcast" in d:
        return "37"   # white
    if "clear" in d:
        return "93"   # bright yellow
    return "0"


# Longest names first so "Light rain" wins over "Rain"
_conds = "|".join(re.escape(c) for c in sorted(CONDITIONS, key=len, reverse=True))

PATTERN = re.compile(
    r"(?P<range>(?P<lo>-?\d+)–(?P<hi>-?\d+)°(?P<ru>[CF]))"
    r"|(?P<temp>(?P<t>-?\d+)°(?P<tu>[CF]))"
    r"|(?P<rain>rain (?P<p>\d+)%)"
    r"|(?P<amt>rain (?P<a>\d+(?:\.\d+)?) (?P<au>mm|in))"
    r"|(?P<date>\d{4}-\d{2}-\d{2})"
    r"|(?P<wind>\d+ (?:km/h|mph))"
    r"|(?P<cond>" + _conds + r")"
)


def _sub(m):
    if m.group("range"):
        u = m.group("ru")
        lo, hi = int(m.group("lo")), int(m.group("hi"))
        return (f"{paint(lo, temp_code(to_c(lo, u)))}–"
                f"{paint(hi, temp_code(to_c(hi, u)))}°{u}")
    if m.group("temp"):
        u = m.group("tu")
        return paint(m.group("temp"), temp_code(to_c(int(m.group("t")), u)))
    if m.group("rain"):
        return paint(m.group("rain"), rain_code(int(m.group("p"))))
    if m.group("amt"):
        return paint(m.group("amt"), amount_code(float(m.group("a")), m.group("au")))
    if m.group("date"):
        return paint(m.group("date"), "2")
    if m.group("wind"):
        return paint(m.group("wind"), "35")
    return paint(m.group("cond"), cond_code(m.group("cond")))


def colourise(text):
    lines = text.split("\n")
    header_done = False
    for i, line in enumerate(lines):
        if not line.strip():
            continue
        if not header_done:
            lines[i] = paint(line, "1;96")   # bold bright cyan place name
            header_done = True
        elif line.startswith("Past "):
            lines[i] = paint(line, "1;33")   # bold yellow: past section heading
        elif line == "Forecast":
            lines[i] = paint(line, "1;92")   # bold bright green: forecast heading
        else:
            lines[i] = PATTERN.sub(_sub, line)
    return "\n".join(lines)


def main(argv=None):
    # Plain output when piped or when NO_COLOR is set
    if not sys.stdout.isatty() or "NO_COLOR" in os.environ:
        run(argv)
        return

    buf = io.StringIO()
    try:
        with redirect_stdout(buf):
            run(argv)
    finally:
        sys.stdout.write(colourise(buf.getvalue()))