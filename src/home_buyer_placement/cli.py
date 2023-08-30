"""Command-line entry point."""

from __future__ import annotations

import argparse
import sys
from collections.abc import Sequence

from .parsing import InputError, parse_file
from .placement import format_placements, place_buyers


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="home-buyer-placement",
        description=(
            "Place home buyers into neighborhoods. Each buyer's fit for a neighborhood "
            "is the dot product of their E/W/R goals and its E/W/R scores; buyers are "
            "assigned by deferred acceptance over their stated preferences, with every "
            "neighborhood taking the same number of buyers."
        ),
    )
    parser.add_argument("input", help="input file with N (neighborhood) and H (home buyer) lines")
    parser.add_argument(
        "-o",
        "--output",
        metavar="FILE",
        help="write the placements to FILE instead of standard output",
    )
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        report = format_placements(place_buyers(parse_file(args.input)))
    except InputError as error:
        print(f"home-buyer-placement: {args.input}: {error}", file=sys.stderr)
        return 1
    except OSError as error:
        print(f"home-buyer-placement: {error}", file=sys.stderr)
        return 1

    if args.output:
        with open(args.output, "w", encoding="utf-8") as handle:
            handle.write(report)
    else:
        sys.stdout.write(report)
    return 0
