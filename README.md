# weather-cli

A small command-line weather tool for macOS. Check the forecast for your current location (or any city) straight from the terminal, with colour-coded output.

Built with Python's standard library only. Weather data comes from [Open-Meteo](https://open-meteo.com) (no API key needed).

## Features

- Detects your location from your IP address, or pass any city name
- Current conditions plus a 1 to 7 day forecast
- Metric (°C, km/h) or imperial (°F, mph) units
- Colour-coded temperatures, conditions, rain chance and wind
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
```

### Options

| Flag | Description | Values |
|---|---|---|
| `-d`, `--days` | Number of forecast days | 1 to 7 (default 3) |
| `-u`, `--units` | Unit system | `metric` or `imperial` (default `metric`) |
| `-h`, `--help` | Show help | |

### Examples

```bash
weather -d 1                      # just today
weather London -d 7               # a week in London
weather -u imperial               # detected location in °F and mph
weather Tokyo -u imperial -d 5    # flags can be combined in any order
```

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
│       ├── forecast.py     # coordinates -> weather data
│       ├── display.py      # weather data -> formatted text
│       ├── codes.py        # weather code -> description
│       └── http.py         # shared JSON fetch helper
└── tests/
```

### How it works

1. `colours.py` is the entry point (`weather = "weather_cli.colours:main"` in `pyproject.toml`). It runs `cli.main()`, captures the printed text, and adds colour.
2. `cli.py` parses arguments and asks `geocoding.py` for coordinates.
3. `forecast.py` fetches the weather from Open-Meteo.
4. `display.py` formats the result as plain text.

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
