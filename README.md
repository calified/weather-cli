# weather-cli

> Check the weather from your terminal. Colour-coded, no API key, standard library only.

<p align="center">
  <img src="docs/images/default.png" alt="weather-cli showing a three-day forecast for London in colour" width="650">
</p>

A small command-line weather tool for macOS, Linux and Windows. Check the forecast for your current location (or any city) straight from the terminal, with colour-coded output, a live watch mode, and an optional look back at the past week.

Built with Python's standard library only. Weather data comes from [Open-Meteo](https://open-meteo.com) (no API key needed).

## Features

- Detects your location from your IP address, or pass any city name
- "Did you mean?" prompt when a name matches several places (Springfield, Paris, ...) or is misspelled
- Current conditions plus a 1 to 7 day forecast
- `--watch` mode that refreshes automatically, and keeps showing the last forecast if you go offline
- Optional look back at the past 1 to 7 days, clearly labelled as past data
- Metric (°C, km/h, mm) or imperial (°F, mph, in) units
- Colour-coded temperatures, conditions, rain and wind
- Colour switches off automatically when piped or when `NO_COLOR` is set
- Works on macOS, Linux and Windows
- No third-party dependencies

## Requirements

- macOS, Linux, or Windows 10 and newer
- Python 3.9 or newer
- [pipx](https://pipx.pypa.io) (installs the command so it works from any folder)

## Installation

### 1. Install pipx (once)

**macOS**

```bash
brew install pipx
pipx ensurepath
```

**Linux**

```bash
sudo apt install pipx          # Debian/Ubuntu
# sudo dnf install pipx        # Fedora
# sudo pacman -S python-pipx   # Arch
pipx ensurepath
```

**Windows (PowerShell)**

```powershell
py -m pip install --user pipx
py -m pipx ensurepath
```

Then **close and reopen your terminal** so the PATH change applies.

### 2. Install weather-cli

This works on every OS and needs no `git`:

```bash
pipx install https://github.com/calified/weather-cli/archive/refs/heads/main.zip
```

If you have `git` installed, this also works:

```bash
pipx install git+https://github.com/calified/weather-cli.git
```

To update later, run the same command again with `--force` added.

### 3. Try it

```bash
weather
```

### For development

```bash
git clone https://github.com/calified/weather-cli.git
cd weather-cli
pipx install -e .
```

The `-e` flag installs in editable mode, so code changes apply immediately without reinstalling.

## Usage

```bash
weather                     # your location, 3-day forecast
weather Manchester          # a specific city
weather New York            # multi-word cities work without quotes
weather Paris, Texas        # add a region or country after a comma
weather Manchester -p       # forecast plus the past 3 days
weather London --watch      # keep refreshing until you press Ctrl+C
```

### Options

| Flag | Description | Values |
|---|---|---|
| `-d`, `--days` | Number of forecast days | 1 to 7 (default 3) |
| `-u`, `--units` | Unit system | `metric` or `imperial` (default `metric`) |
| `-p`, `--past [N]` | Also show the past N days | 1 to 7 (3 if no number is given) |
| `-w`, `--watch` | Refresh the weather until you press Ctrl+C | |
| `-e`, `--every MIN` | Minutes between refreshes (needs `--watch`) | 1 to 1440 (default 15) |
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
weather London -w -e 5            # refresh every 5 minutes
```

### Ambiguous and misspelled places

Many names belong to more than one place. When the tool can't tell which you mean, it asks:

```
$ weather Springfield
"Springfield" matches several places. Which one did you mean?
  1) Springfield, Illinois, United States (pop. 114,000)
  2) Springfield, Missouri, United States (pop. 169,000)
  3) Springfield, Massachusetts, United States (pop. 155,000)
Pick 1-3 [1], or q to cancel:
```

Press Enter for the first, type a number to pick another, or `q` to cancel. A misspelled name (`weather Mancehster`) gets a "Did you mean...?" list in the same way.

- **Clear winners are not questioned.** `weather London` and `weather Paris` go straight to the big, obvious city. The prompt only appears when the best match is not far larger than the others.
- **Skip the question by adding a region or country after a comma:** `weather Paris, Texas`, `weather Manchester, UK`, `weather Springfield, Missouri`. Remember the comma.
- **In scripts and pipes** nobody can answer, so the best match is used and a note is printed to stderr.

### Watch mode

`--watch` clears the screen and redraws the forecast on a timer, with a footer showing when it last updated:

```
Updated 14:32:07, refreshing every 15 min. Ctrl+C to quit.
```

- Open-Meteo refreshes its current conditions roughly every 15 minutes, so shorter intervals mostly re-fetch the same numbers. Please keep the interval reasonable, since the API is free.
- If a refresh fails (for example your Wi-Fi drops), the last forecast stays on screen with a red warning, and it retries on schedule.
- Your location is looked up once at the start, and so is any "Did you mean?" choice.
- It needs an interactive terminal and will not run when the output is piped.
- Flags still combine: `weather London --watch -p 2 -u imperial`.

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

**macOS / Linux** (add to `~/.zshrc` or `~/.bashrc`, then restart the terminal):

```bash
export WEATHER_UNITS=imperial
```

**Windows (PowerShell)**

```powershell
setx WEATHER_UNITS imperial      # permanent, applies to new terminals
$env:WEATHER_UNITS = "imperial"  # this terminal only
```

An explicit `-u` flag always overrides this.

### Colour

Colour turns off automatically when output is piped or redirected.

| | macOS / Linux | PowerShell | Command Prompt |
|---|---|---|---|
| Disable for one run | `NO_COLOR=1 weather` | `$env:NO_COLOR=1; weather` | `set NO_COLOR=1 && weather` |

### Optional shortcuts

**macOS / Linux** (add to `~/.zshrc` or `~/.bashrc`):

```bash
alias wi='weather -u imperial'
alias wt='weather -d 1'
alias wp='weather -p'
alias ww='weather --watch'
```

**Windows (PowerShell)**: open your profile with `notepad $PROFILE` and add:

```powershell
function wi { weather -u imperial @args }
function wt { weather -d 1 @args }
function wp { weather -p @args }
function ww { weather --watch @args }
```

## Project structure

```
weather-cli/
├── pyproject.toml
├── README.md
├── .gitignore
├── docs/
│   └── images/
│       └── default.png     # screenshot used in this README
├── src/
│   └── weather_cli/
│       ├── __init__.py
│       ├── __main__.py
│       ├── cli.py          # argument parsing, watch loop, ties everything together
│       ├── colours.py      # colours the output (the installed entry point)
│       ├── geocoding.py    # place name / IP -> coordinates, ranks ambiguous matches
│       ├── picker.py       # the "Did you mean?" prompt
│       ├── forecast.py     # coordinates -> weather data (past + forecast)
│       ├── display.py      # weather data -> formatted text
│       ├── codes.py        # weather code -> description
│       └── http.py         # shared JSON fetch helper
└── tests/
    ├── test_cli.py
    ├── test_codes.py
    ├── test_display.py
    ├── test_geocoding.py
    └── test_picker.py
```

### How it works

1. `colours.py` is the entry point (`weather = "weather_cli.colours:main"` in `pyproject.toml`). It runs `cli.main()` and hands it a function that colours each screen of text before printing it. On Windows it first enables ANSI colour support in the console.
2. `cli.py` parses arguments and asks `geocoding.py` for matching places. If the match is ambiguous and a person is at the keyboard, `picker.py` asks which one they meant. Prompts go to stderr, so they never mix into piped output.
3. `forecast.py` fetches the weather from Open-Meteo in a single request. When `-p` is used, it adds Open-Meteo's `past_days` parameter, so the past days come back at the start of the same daily data.
4. `display.py` formats the result as plain text, splitting the past days from the forecast.
5. With `--watch`, `cli.py` repeats steps 3 and 4 on a timer, clearing the screen each time.

## Updating and uninstalling

```bash
pipx list                         # confirm it's installed
pipx uninstall weather-cli        # remove the command
pipx install -e . --force         # development install: reinstall after editing pyproject.toml
```

For an editable install, do not move or delete the project folder, since the install points at it. If you move it, uninstall and reinstall from the new location.

## Troubleshooting

| Problem | Fix |
|---|---|
| `weather: command not found` (macOS/Linux) | Run `pipx ensurepath`, then restart the terminal |
| `'weather' is not recognized` (Windows) | Run `py -m pipx ensurepath`, then close and reopen the terminal. `pipx ensurepath` also prints where the command lives |
| `py` is not recognized (Windows) | Install Python from python.org (tick "Add python.exe to PATH"), or use `python -m pip ...` instead of `py -m pip ...` |
| `pipx install git+...` fails with "git not found" | Install Git, or use the `.zip` install command instead |
| PowerShell blocks scripts when activating a venv | Run `Set-ExecutionPolicy -Scope CurrentUser RemoteSigned` once |
| Strange characters like `←[93m` instead of colour | Use Windows Terminal or PowerShell 7, or run with `NO_COLOR=1` to switch colour off |
| No colour in Git Bash on Windows | Expected on some setups. Output falls back to plain text. Windows Terminal or PowerShell shows colour |
| No colours (macOS/Linux) | Check `echo $NO_COLOR` is empty and `pyproject.toml` points to `weather_cli.colours:main`, then reinstall with `--force` |
| `SyntaxError` or `ImportError` on run | Check the named file and line in the traceback, or run `python3 -m compileall src` |
| Wrong location detected | IP lookup can be off (or affected by a VPN). Pass a city name instead |
| `Couldn't find a place called ...` | Check the spelling, or try a nearby larger town. Add a region after a comma, e.g. `weather Paris, France` |
| `Couldn't find a place called 'X' in 'Y'` | Nothing matching `X` was found in region or country `Y`. Check the part after the comma |
| Asked "Which one did you mean?" every time | Add a region: `weather Springfield, Missouri`. Or set a shell alias with the region included |
| `Note: several places match ...` | The tool could not ask (piped or scripted), so it used the best match. Add a region to choose another |
| `argument -p/--past: must be between 1 and 7` | `-p` only accepts 1 to 7 |
| `argument -p/--past: 'London' is not a number` | Put the city before `-p`: `weather London -p` |
| `--every only works together with --watch` | Add `--watch`: `weather London -w -e 5` |
| `--watch needs an interactive terminal` | Run it directly in a terminal, not through a pipe or redirect |
| `Update failed ... Showing older data` | The refresh could not reach Open-Meteo. The old forecast is kept and it retries automatically |
| `rain n/a` on a day | Open-Meteo had no rain figure for that day |

## Running tests

```bash
python3 -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\Activate.ps1
pip install -e ".[dev]"
pytest
```

## Credits

- Weather and geocoding: [Open-Meteo](https://open-meteo.com)
- IP-based location: [ipinfo.io](https://ipinfo.io)