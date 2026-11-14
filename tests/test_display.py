from weather_cli.display import render

SAMPLE = {
    "current": {
        "weather_code": 3, "temperature_2m": 10.2,
        "apparent_temperature": 8.0, "wind_speed_10m": 12.0,
    },
    "daily": {
        "time": ["2026-11-13", "2026-11-14", "2026-11-15"],
        "weather_code": [61, 3, 0],
        "temperature_2m_max": [11, 10, 9],
        "temperature_2m_min": [5, 4, 3],
        "precipitation_probability_max": [None, 20, 5],
        "precipitation_sum": [3.2, 0.0, 0.0],
    },
}

def test_no_past_has_no_headings():
    out = render("Test", SAMPLE, "metric", 0)
    assert "Past" not in out
    assert "Forecast" not in out


def test_past_section_is_labelled():
    out = render("Test", SAMPLE, "metric", 1)
    assert "Past 1 day (recorded, not forecast)" in out
    assert "rain 3.2 mm" in out
    assert "Forecast" in out