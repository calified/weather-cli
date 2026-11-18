import sys

from .geocoding import with_region


def can_ask() -> bool:
    return sys.stdin.isatty() and sys.stderr.isatty()


def _say(text: str = "") -> None:
    print(text, file=sys.stderr)


def _ask(prompt: str) -> str:
    sys.stderr.write(prompt)
    sys.stderr.flush()
    try:
        return input().strip().lower()
    except EOFError:
        return "q"


def _line(number: int, loc) -> str:
    pop = f" (pop. {loc.population:,})" if loc.population else ""
    return f"  {number}) {loc.full_label}{pop}"


def choose(options: list, query: str, exact: bool):
    if len(options) == 1:
        _say(f'No exact match for "{query}".')
        answer = _ask(f"Did you mean {options[0].full_label}? [Y/n] ")
        if answer in ("", "y", "yes"):
            return with_region(options[0])
        sys.exit("Cancelled.")

    if exact:
        _say(f'"{query}" matches several places. Which one did you mean?')
    else:
        _say(f'No exact match for "{query}". Did you mean:')
    for number, loc in enumerate(options, 1):
        _say(_line(number, loc))

    while True:
        answer = _ask(f"Pick 1-{len(options)} [1], or q to cancel: ")
        if answer == "":
            return with_region(options[0])
        if answer in ("q", "quit", "n", "no"):
            sys.exit("Cancelled.")
        if answer.isdigit() and 1 <= int(answer) <= len(options):
            return with_region(options[int(answer) - 1])
        _say("Please enter a number from the list.")