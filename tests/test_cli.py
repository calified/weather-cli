import sys

import pytest

from weather_cli import cli, geocoding
from weather_cli.geocoding import Location


def place(city, region, country, code, pop=0):
    return Location(
        lat=0.0, lon=0.0, name=f"{city}, {country}",
        city=city, region=region, country=country,
        country_code=code, population=pop,
    )


def test_every_needs_watch():
    with pytest.raises(SystemExit) as e:
        cli.parse_args(["London", "--every", "5"])
    assert e.value.code == 2


def test_defaults():
    args = cli.parse_args(["London"])
    assert args.watch is False and args.every == 15


@pytest.mark.parametrize("bad", ["0", "1441", "abc"])
def test_every_range(bad):
    with pytest.raises(SystemExit):
        cli.parse_args(["--watch", "--every", bad])


def test_watch_flag_before_city_is_fine():
    args = cli.parse_args(["--watch", "New", "York", "-e", "30"])
    assert args.place == ["New", "York"] and args.every == 30


def test_watch_refuses_piped_output(monkeypatch, capsys):
    monkeypatch.setattr(sys.stdout, "isatty", lambda: False, raising=False)
    with pytest.raises(SystemExit) as e:
        cli.main(["London", "--watch"])
    assert "interactive terminal" in str(e.value)


def run_watch(monkeypatch, capsys, reports, loops):
    monkeypatch.setattr(sys.stdout, "isatty", lambda: True, raising=False)
    monkeypatch.setattr(cli, "resolve_location", lambda words: place("X", "", "Y", "YY"))
    monkeypatch.setattr(cli, "clear_screen", lambda: print("<CLEAR>"))
    seq = iter(reports)

    def fake_report(loc, args):
        item = next(seq)
        if isinstance(item, Exception):
            raise item
        return item

    monkeypatch.setattr(cli, "build_report", fake_report)
    sleeps = []

    def fake_sleep(seconds):
        sleeps.append(seconds)
        if len(sleeps) >= loops:
            raise KeyboardInterrupt

    monkeypatch.setattr(cli.time, "sleep", fake_sleep)
    with pytest.raises(SystemExit) as e:
        cli.main(["X", "--watch", "--every", "2"])
    return capsys.readouterr(), sleeps, e.value.code


def test_watch_refreshes_and_clears(monkeypatch, capsys):
    cap, sleeps, code = run_watch(monkeypatch, capsys, ["one\n", "two\n"], loops=2)
    assert cap.out.count("<CLEAR>") == 2
    assert "one" in cap.out and "two" in cap.out
    assert "Updated " in cap.out and "refreshing every 2 min" in cap.out
    assert sleeps == [120, 120]
    assert code == 130


def test_watch_keeps_old_data_when_a_refresh_fails(monkeypatch, capsys):
    cap, _, _ = run_watch(
        monkeypatch, capsys, ["good report\n", OSError("network down")], loops=2
    )
    last_screen = cap.out.split("<CLEAR>")[-1]
    assert "good report" in last_screen
    assert "Update failed" in last_screen and "network down" in last_screen


def test_watch_first_failure_exits_with_error(monkeypatch, capsys):
    monkeypatch.setattr(sys.stdout, "isatty", lambda: True, raising=False)
    monkeypatch.setattr(cli, "resolve_location", lambda words: place("X", "", "Y", "YY"))
    monkeypatch.setattr(cli, "build_report", lambda l, a: (_ for _ in ()).throw(OSError("offline")))
    with pytest.raises(SystemExit) as e:
        cli.main(["X", "--watch"])
    assert str(e.value) == "Error: offline"


def test_ambiguous_but_not_interactive_uses_first_and_notes(monkeypatch, capsys):
    options = [
        place("Springfield", "Illinois", "United States", "US", 114_000),
        place("Springfield", "Missouri", "United States", "US", 169_000),
    ]
    monkeypatch.setattr(geocoding, "search", lambda name, count=20: options)
    monkeypatch.setattr(cli.picker, "can_ask", lambda: False)
    loc = cli.resolve_location(["Springfield"])
    assert loc.name == "Springfield, Illinois, United States"
    err = capsys.readouterr().err
    assert "several places match 'Springfield'" in err and "Paris, Texas" in err


def test_typo_not_interactive_notes_no_exact_match(monkeypatch, capsys):
    options = [place("Manchester", "England", "United Kingdom", "GB", 510_000)]
    monkeypatch.setattr(geocoding, "search", lambda name, count=20: options)
    monkeypatch.setattr(cli.picker, "can_ask", lambda: False)
    loc = cli.resolve_location(["Mancehster"])
    assert loc.name == "Manchester, England, United Kingdom"
    assert "no exact match for 'Mancehster'" in capsys.readouterr().err


def test_plain_city_is_unchanged(monkeypatch):
    options = [
        place("London", "England", "United Kingdom", "GB", 8_900_000),
        place("London", "Ontario", "Canada", "CA", 400_000),
    ]
    monkeypatch.setattr(geocoding, "search", lambda name, count=20: options)
    assert cli.resolve_location(["London"]).name == "London, United Kingdom"