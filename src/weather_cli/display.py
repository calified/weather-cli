from .codes import describe

LABELS = {
    "metric": ("°C", "km/h"),
    "imperial": ("°F", "mph"),
}


def render(place: str, w: dict, units: str = "metric") -> str:
    t, spd = LABELS[units]
    cur, d = w["current"], w["daily"]
    lines = [
        f"\n{place}",
        f'Now: {describe(cur["weather_code"])}, {cur["temperature_2m"]:.0f}{t} '
        f'(feels {cur["apparent_temperature"]:.0f}{t}), wind {cur["wind_speed_10m"]:.0f} {spd}\n',
    ]
    for i, day in enumerate(d["time"]):
        lines.append(
            f'{day}  {describe(d["weather_code"][i]):<18} '
            f'{d["temperature_2m_min"][i]:.0f}–{d["temperature_2m_max"][i]:.0f}{t}  '
            f'rain {d["precipitation_probability_max"][i]}%'
        )
    return "\n".join(lines) + "\n"