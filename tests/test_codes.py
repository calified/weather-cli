from weather_cli.codes import describe


def test_known_code():
    assert describe(0) == "Clear sky"


def test_unknown_code():
    assert describe(12345) == "Unknown"