from .codes import describe

LABELS = {
    "metric": {"temp": "°C", "wind": "km/h", "rain": "mm", "dp": 1},
    "imperial": {"temp": "°F", "wind": "mph", "rain": "in", "dp": 2},
}


def _row(d: dict, i: int, u: dict, is_past: bool) -> str:
    t = u["temp"]
    if is_past:
        amount = d["precipitation_sum"][i]
        rain = "rain n/a" if amount is None else f'rain {amount:.{u["dp"]}f} {u["rain"]}'
    else:
        prob = d["precipitation_probability_max"][i]
        rain = "rain n/a" if prob is None else f"rain {prob}%"
    return (
        f'{d["time"][i]}  {describe(d["weather_code"][i]):<18} '
        f'{d["temperature_2m_min"][i]:.0f}–{d["temperature_2m_max"][i]:.0f}{t}  '
        f"{rain}"
    )


def render(place: str, w: dict, units: str = "metric", past: int = 0) -> str:
    u = LABELS[units]
    t, spd = u["temp"], u["wind"]
    cur, d = w["current"], w["daily"]
    lines = [
        f"\n{place}",
        f'Now: {describe(cur["weather_code"])}, {cur["temperature_2m"]:.0f}{t} '
        f'(feels {cur["apparent_temperature"]:.0f}{t}), wind {cur["wind_speed_10m"]:.0f} {spd}\n',
    ]

    if past:
        s = "" if past == 1 else "s"
        lines.append(f"Past {past} day{s} (recorded, not forecast)")
        lines += [_row(d, i, u, True) for i in range(past)]
        lines.append("")
        lines.append("Forecast")

    lines += [_row(d, i, u, False) for i in range(past, len(d["time"]))]
    return "\n".join(lines) + "\n"