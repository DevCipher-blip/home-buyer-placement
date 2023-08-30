"""Read the line-based input format.

    N <name> E:<int> W:<int> R:<int>
    H <name> E:<int> W:<int> R:<int> <neighborhood>[><neighborhood>...]

Blank lines are ignored. Attribute tokens may appear in any order.
"""

from __future__ import annotations

from collections.abc import Iterable
from dataclasses import dataclass
from pathlib import Path

ATTRIBUTES = ("E", "W", "R")


class InputError(ValueError):
    """The input text does not follow the expected format."""

    def __init__(self, message: str, line_number: int | None = None) -> None:
        self.line_number = line_number
        super().__init__(f"line {line_number}: {message}" if line_number else message)


@dataclass(frozen=True)
class Neighborhood:
    name: str
    attributes: tuple[int, int, int]


@dataclass(frozen=True)
class HomeBuyer:
    name: str
    goals: tuple[int, int, int]
    preferences: tuple[str, ...]


@dataclass(frozen=True)
class Problem:
    neighborhoods: tuple[Neighborhood, ...]
    buyers: tuple[HomeBuyer, ...]


def _parse_attributes(tokens: list[str], line_number: int) -> tuple[int, int, int]:
    values: dict[str, int] = {}
    for token in tokens:
        key, sep, raw = token.partition(":")
        if not sep or key not in ATTRIBUTES:
            raise InputError(f"expected an attribute like E:5, got {token!r}", line_number)
        if key in values:
            raise InputError(f"attribute {key} given twice", line_number)
        try:
            values[key] = int(raw)
        except ValueError:
            raise InputError(
                f"attribute {key} must be an integer, got {raw!r}", line_number
            ) from None
    missing = [key for key in ATTRIBUTES if key not in values]
    if missing:
        raise InputError(f"missing attribute(s): {', '.join(missing)}", line_number)
    return values["E"], values["W"], values["R"]


def _parse_preferences(token: str, line_number: int) -> tuple[str, ...]:
    names = tuple(token.split(">"))
    if any(not name for name in names):
        raise InputError(f"malformed preference list {token!r}", line_number)
    if len(set(names)) != len(names):
        raise InputError(f"preference list {token!r} repeats a neighborhood", line_number)
    return names


def parse_lines(lines: Iterable[str]) -> Problem:
    neighborhoods: list[Neighborhood] = []
    buyers: list[HomeBuyer] = []
    seen: set[str] = set()
    buyer_lines: dict[str, int] = {}

    for line_number, line in enumerate(lines, start=1):
        parts = line.split()
        if not parts:
            continue
        kind = parts[0]
        if kind not in ("N", "H"):
            raise InputError(f"line must start with N or H, got {kind!r}", line_number)
        expected_tokens = 5 if kind == "N" else 6
        if len(parts) != expected_tokens:
            raise InputError(
                f"{kind} line needs {expected_tokens} fields, got {len(parts)}", line_number
            )
        name = parts[1]
        if name in seen:
            raise InputError(f"name {name!r} is used more than once", line_number)
        seen.add(name)

        attributes = _parse_attributes(parts[2:5], line_number)
        if kind == "N":
            neighborhoods.append(Neighborhood(name, attributes))
        else:
            buyers.append(HomeBuyer(name, attributes, _parse_preferences(parts[5], line_number)))
            buyer_lines[name] = line_number

    known = {n.name for n in neighborhoods}
    for buyer in buyers:
        unknown = [name for name in buyer.preferences if name not in known]
        if unknown:
            raise InputError(
                f"{buyer.name} prefers unknown neighborhood(s): {', '.join(unknown)}",
                buyer_lines[buyer.name],
            )

    return Problem(tuple(neighborhoods), tuple(buyers))


def parse_file(path: str | Path) -> Problem:
    with open(path, encoding="utf-8") as handle:
        return parse_lines(handle)
