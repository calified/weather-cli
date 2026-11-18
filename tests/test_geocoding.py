import pytest

from weather_cli import geocoding
from weather_cli.geocoding import Location, LocationError


def place(city, region, country, code, pop=0):
    return Location(
        lat=0.0, lon=0.0, name=f"{city}, {country}",
        city=city, region=region, country=country,
        country_code=code, population=pop,
    )


PARIS = [
    place("Paris", "Île-de-France", "France", "FR", 2_100_000),
    place("Paris", "Texas", "United States", "US", 25_000),
    place("Paris", "Ontario", "Canada", "CA", 12_000),
]

SPRINGFIELD = [
    place("Springfield", "Illinois", "United States", "US", 114_000),
    place("Springfield", "Missouri", "United States", "US", 169_000),
    place("Springfield", "Massachusetts", "United States", "US", 155_000),
]

MANCHESTER = [
    place("Manchester", "England", "United Kingdom", "GB", 510_000),
    place("Manchester", "New Hampshire", "United States", "US", 115_000),
]


def fake(monkeypatch, results):
    monkeypatch.setattr(geocoding, "search", lambda name, count=20: results)


def test_clear_winner_is_picked_without_asking(monkeypatch):
    fake(monkeypatch, PARIS)
    options, exact, needs_choice = geocoding.find("Paris")
    assert exact and not needs_choice
    assert options[0].country == "France"
    assert options[0].name == "Paris, France"


def test_similar_sizes_need_a_choice(monkeypatch):
    fake(monkeypatch, SPRINGFIELD)
    options, exact, needs_choice = geocoding.find("Springfield")
    assert exact and needs_choice
    assert len(options) == 3


def test_population_ratio_edge(monkeypatch):
    fake(monkeypatch, MANCHESTER)
    assert geocoding.find("Manchester")[2] is True


def test_missing_population_needs_a_choice(monkeypatch):
    fake(monkeypatch, [place("Foo", "A", "X", "XX"), place("Foo", "B", "Y", "YY")])
    assert geocoding.find("Foo")[2] is True


def test_region_qualifier_picks_directly(monkeypatch):
    fake(monkeypatch, PARIS)
    options, exact, needs_choice = geocoding.find("Paris, Texas")
    assert not needs_choice
    assert options[0].region == "Texas"
    assert options[0].name == "Paris, Texas, United States"


def test_country_qualifier_and_alias(monkeypatch):
    fake(monkeypatch, MANCHESTER)
    assert geocoding.find("Manchester, UK")[0][0].country == "United Kingdom"
    assert geocoding.find("Manchester, us")[0][0].region == "New Hampshire"
    assert geocoding.find("Manchester, new hamp")[0][0].region == "New Hampshire"


def test_qualifier_with_no_match_is_an_error(monkeypatch):
    fake(monkeypatch, PARIS)
    with pytest.raises(LocationError, match="in 'Narnia'"):
        geocoding.find("Paris, Narnia")


def test_typo_asks_did_you_mean(monkeypatch):
    fake(monkeypatch, MANCHESTER)
    options, exact, needs_choice = geocoding.find("Mancehster")
    assert not exact and needs_choice


def test_accents_and_case_are_ignored(monkeypatch):
    fake(monkeypatch, [place("Zürich", "Zurich", "Switzerland", "CH", 400_000)])
    options, exact, needs_choice = geocoding.find("zurich")
    assert exact and not needs_choice


def test_no_results(monkeypatch):
    fake(monkeypatch, [])
    with pytest.raises(LocationError, match="Couldn't find a place called 'Nowhere'"):
        geocoding.find("Nowhere")


def test_at_most_five_options(monkeypatch):
    many = [place("Springfield", f"State{i}", "United States", "US", 100_000) for i in range(9)]
    fake(monkeypatch, many)
    assert len(geocoding.find("Springfield")[0]) == 5


def test_full_label_skips_repeats():
    assert place("Singapore", "Singapore", "Singapore", "SG").full_label == "Singapore"