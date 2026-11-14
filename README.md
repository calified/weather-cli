# weather-cli

A small command-line weather tool for macOS. Check the forecast for your current location (or any city) straight from the terminal, with colour-coded output and an optional look back at the past week.

Built with Python's standard library only. Weather data comes from [Open-Meteo](https://open-meteo.com) (no API key needed).

## Features

- Detects your location from your IP address, or pass any city name
- Current conditions plus a 1 to 7 day forecast
- Optional look back at the past 1 to 7 days, clearly labelled as past data
- Metric (°C, km/h, mm) or imperial (°F, mph, in) units
- Colour-coded temperatures, conditions, rain and wind
- Colour switches off automatically when piped or when `NO_COLOR` is set
- No third-party dependencies

## Requirements

- macOS
- Python 3.9 or newer
- [pipx](https://pipx.pypa.io) (for installing the command system-wide)

## Installation

```bash
# 1. Install pipx (once)
brew install pipx
pipx ensurepath

# 2. Restart Terminal (or run: source ~/.zshrc)

# 3. From the project folder, install the command
cd path/to/weather-cli
pipx install -e .
```

The `-e` flag installs in editable mode, so changes to the code apply immediately without reinstalling.

Check it works from any folder:

```bash
cd ~
weather
```

## Usage

```bash
weather                     # your location, 3-day forecast
weather Manchester          # a specific city
weather New York            # multi-word cities work without quotes
weather Manchester -p       # forecast plus the past 3 days
```

### Options

| Flag | Description | Values |
|---|---|---|
| `-d`, `--days` | Number of forecast days | 1 to 7 (default 3) |
| `-u`, `--units` | Unit system | `metric` or `imperial` (default `metric`) |
| `-p`, `--past [N]` | Also show the past N days | 1 to 7 (3 if no number is given) |
| `-h`, `--help` | Show help | |

### Examples

```bash
weather -d 1                      # just today
weather London -d 7               # a week in London
weather -u imperial               # detected location in °F and mph
weather Tokyo -u imperial -d 5    # flags can be combined in any order
weather -p                        # past 3 days plus forecast
weather -p 7                      # past week plus forecast
weather London -p 2 -d 1          # past 2 days, then today only
```

### Past days

With `-p`, the output is split into two labelled sections:

```
Past 3 days (recorded, not forecast)
2026-11-11  Rain               5–9°C  rain 3.2 mm
...

Forecast
2026-11-14  Overcast           4–10°C  rain 20%
...
```

Past days show the total rainfall that fell (mm or inches), because a rain *probability* only exists for future days. The limit is 7 days back.

If you give a city and `-p` together, put the city first (`weather London -p 3`). Writing `weather -p London` makes the tool try to read "London" as the number of days.

## Configuration

### Default units

Set a default in `~/.zshrc`, then run `source ~/.zshrc`:

```bash
export WEATHER_UNITS=imperial
```

An explicit `-u` flag always overrides this.

### Colour

```bash
NO_COLOR=1 weather                # disable colour for one run
weather | cat                     # colour is off automatically when piped
```

### Optional aliases

```bash
alias wi='weather -u imperial'
alias wt='weather -d 1'
alias wp='weather -p'
```

## Project structure

```
weather-cli/
├── pyproject.toml
├── README.md
├── .gitignore
├── src/
│   └── weather_cli/
│       ├── __init__.py
│       ├── __main__.py
│       ├── cli.py          # argument parsing, ties everything together
│       ├── colours.py      # colours the output (the installed entry point)
│       ├── geocoding.py    # place name / IP -> coordinates
│       ├── forecast.py     # coordinates -> weather data (past + forecast)
│       ├── display.py      # weather data -> formatted text
│       ├── codes.py        # weather code -> description
│       └── http.py         # shared JSON fetch helper
└── tests/
    ├── test_codes.py
    └── test_display.py
```

### How it works

1. `colours.py` is the entry point (`weather = "weather_cli.colours:main"` in `pyproject.toml`). It runs `cli.main()`, captures the printed text, and adds colour.
2. `cli.py` parses arguments and asks `geocoding.py` for coordinates.
3. `forecast.py` fetches the weather from Open-Meteo in a single request. When `-p` is used, it adds Open-Meteo's `past_days` parameter, so the past days come back at the start of the same daily data.
4. `display.py` formats the result as plain text, splitting the past days from the forecast.

## Updating and uninstalling

```bash
pipx list                         # confirm it's installed
pipx install -e . --force         # reinstall (needed after editing pyproject.toml)
pipx uninstall weather-cli        # remove the command
```

Do not move or delete the project folder after installing, since the editable install points at it. If you move it, uninstall and reinstall from the new location.

## Troubleshooting

| Problem | Fix |
|---|---|
| `weather: command not found` | Run `pipx ensurepath`, then restart Terminal or run `source ~/.zshrc` |
| `SyntaxError` or `ImportError` on run | Check the named file and line in the traceback, or run `python3 -m compileall src` to find all syntax errors at once |
| No colours | Check `echo $NO_COLOR` is empty and `pyproject.toml` points to `weather_cli.colours:main`, then reinstall with `--force` |
| Wrong location detected | IP lookup can be off (or affected by a VPN). Pass a city name instead |
| `Couldn't find a place called ...` | Try a different spelling or add a country, e.g. `weather Paris France` |
| `argument -p/--past: must be between 1 and 7` | `-p` only accepts 1 to 7 |
| `argument -p/--past: 'London' is not a number` | Put the city before `-p`: `weather London -p` |
| `rain n/a` on a day | Open-Meteo had no rain figure for that day |

## Running tests

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
pytest
```

## Credits

- Weather and geocoding: [Open-Meteo](https://open-meteo.com)
- IP-based location: [ipinfo.io](https://ipinfo.io)