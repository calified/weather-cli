import io
import os
import re
import sys
from contextlib import redirect_stdout

from .cli import main as run

RESET = "\033[0m"

# Condition names that the display shows.
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
        return "94"   # BrightBlue
    if t < 10:
        return "36"   # Cyan
    if t < 18:
        return "32"   # Green
    if t < 25:
        return "33"   # Yellow
    return "31"       # Red


def rain_code(p):
    if p >= 60:
        return "94"   # BrightBlue
    if p >= 30:
        return "36"   # Cyan
    return "2"        # Dim (dry)


def amount_code(value, unit):
    mm = value * 25.4 if unit == "in" else value
    if mm >= 5:
        return "94"   # BrightBlue
    if mm > 0:
        return "36"   # Cyan
    return "2"        # Dim (dry)


def cond_code(desc):
    d = desc.lower()
    if "thunder" in d:
        return "35"   # Magenta
    if "snow" in d:
        return "97"   # BrightWhite
    if "rain" in d or "drizzle" in d or "shower" in d:
        return "94"   # BrightBlue
    if "fog" in d:
        return "90"   # Grey
    if "cloud" in d or "overcast" in d:
        return "37"   # White
    if "clear" in d:
        return "93"   # BrightYellow
    return "0"


# Longest names first so 'light rain' wins over 'rain'.
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
            lines[i] = paint(line, "1;96")   # Bold bright cyan place name
            header_done = True
        elif line.startswith("Past "):
            lines[i] = paint(line, "1;33")   # Bold yellow: past section heading
        elif line == "Forecast":
            lines[i] = paint(line, "1;92")   # Bold bright green: forecast heading
        else:
            lines[i] = PATTERN.sub(_sub, line)
    return "\n".join(lines)


def _enable_windows_ansi():
    """Turn on ANSI colour support in the Windows console.

    Returns True if colours can be used. Always True on macOS/Linux.
    """
    if os.name != "nt":
        return True
    try:
        import ctypes

        kernel32 = ctypes.windll.kernel32
        handle = kernel32.GetStdHandle(-11)
        mode = ctypes.c_ulong()
        if not kernel32.GetConsoleMode(handle, ctypes.byref(mode)):
            return False
        # Terminal processing: 0x0004 = ENABLE_VIRTUAL_TERMINAL_PROCESSING
        return bool(kernel32.SetConsoleMode(handle, mode.value | 0x0004))
    except Exception:
        return False


def _safe_stdout():
    """Keep the console's own encoding, but never crash on a character it can't show."""
    try:
        sys.stdout.reconfigure(errors="replace")
    except Exception:
        pass


def main(argv=None):
    _safe_stdout()

    # Plain output when piped, when NO_COLOR is set, or if the terminal can't do colour.
    if (
        not sys.stdout.isatty()
        or "NO_COLOR" in os.environ
        or not _enable_windows_ansi()
    ):
        run(argv)
        return

    buf = io.StringIO()
    try:
        with redirect_stdout(buf):
            run(argv)
    finally:
        sys.stdout.write(colourise(buf.getvalue()))