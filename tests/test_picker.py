import pytest

from weather_cli import picker
from weather_cli.geocoding import Location


def place(city, region, country, code, pop=0):
    return Location(
        lat=0.0, lon=0.0, name=f"{city}, {country}",
        city=city, region=region, country=country,
        country_code=code, population=pop,
    )


SPRINGFIELD = [
    place("Springfield", "Illinois", "United States", "US", 114_000),
    place("Springfield", "Missouri", "United States", "US", 169_000),
    place("Springfield", "Massachusetts", "United States", "US", 155_000),
]

MANCHESTER = [
    place("Manchester", "England", "United Kingdom", "GB", 510_000),
    place("Manchester", "New Hampshire", "United States", "US", 115_000),
]


def answer_with(monkeypatch, *replies):
    it = iter(replies)
    monkeypatch.setattr("builtins.input", lambda: next(it))


def test_pick_by_number(monkeypatch, capsys):
    answer_with(monkeypatch, "2")
    loc = picker.choose(SPRINGFIELD, "Springfield", True)
    assert loc.region == "Missouri"
    assert loc.name == "Springfield, Missouri, United States"
    err = capsys.readouterr()
    assert err.out == ""
    assert "matches several places" in err.err
    assert "1) Springfield, Illinois, United States (pop. 114,000)" in err.err


def test_enter_takes_first(monkeypatch):
    answer_with(monkeypatch, "")
    assert picker.choose(SPRINGFIELD, "Springfield", True).region == "Illinois"


def test_bad_input_reprompts(monkeypatch, capsys):
    answer_with(monkeypatch, "9", "abc", "3")
    assert picker.choose(SPRINGFIELD, "Springfield", True).region == "Massachusetts"
    assert capsys.readouterr().err.count("Please enter a number") == 2


def test_quit_exits(monkeypatch):
    answer_with(monkeypatch, "q")
    with pytest.raises(SystemExit) as e:
        picker.choose(SPRINGFIELD, "Springfield", True)
    assert str(e.value) == "Cancelled."


def test_typo_wording(monkeypatch, capsys):
    answer_with(monkeypatch, "1")
    picker.choose(MANCHESTER, "Mancehster", False)
    assert 'No exact match for "Mancehster". Did you mean:' in capsys.readouterr().err


def test_single_suggestion_yes_no(monkeypatch):
    answer_with(monkeypatch, "y")
    assert picker.choose(MANCHESTER[:1], "Mancehster", False).region == "England"
    answer_with(monkeypatch, "n")
    with pytest.raises(SystemExit):
        picker.choose(MANCHESTER[:1], "Mancehster", False)