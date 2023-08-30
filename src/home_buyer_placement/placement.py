"""Score buyers against neighborhoods and assign them with deferred acceptance."""

from __future__ import annotations

from collections import deque

from .parsing import HomeBuyer, InputError, Neighborhood, Problem

Placements = dict[str, list[tuple[str, int]]]


def fit_score(buyer: HomeBuyer, neighborhood: Neighborhood) -> int:
    """Dot product of the buyer's goals and the neighborhood's attributes."""
    return sum(
        goal * value for goal, value in zip(buyer.goals, neighborhood.attributes, strict=True)
    )


def capacity(problem: Problem) -> int:
    if not problem.neighborhoods:
        raise InputError("the input has no neighborhoods")
    per_neighborhood, remainder = divmod(len(problem.buyers), len(problem.neighborhoods))
    if remainder:
        raise InputError(
            f"{len(problem.buyers)} buyers cannot be split evenly across "
            f"{len(problem.neighborhoods)} neighborhoods"
        )
    return per_neighborhood


def place_buyers(problem: Problem) -> Placements:
    """Assign every buyer to exactly one neighborhood.

    Buyers apply to neighborhoods in their stated order, then to the remaining
    neighborhoods by descending score. A neighborhood holds its best applicants
    up to capacity and bumps the weakest, who apply to their next choice. Equal
    scores are won by the buyer who appears first in the input, so the result
    does not depend on processing order.

    Returns neighborhood name -> [(buyer name, score)], in input order of
    neighborhoods and descending score within each.
    """
    limit = capacity(problem)
    names = [n.name for n in problem.neighborhoods]
    input_order = {b.name: i for i, b in enumerate(problem.buyers)}
    score = {
        (b.name, n.name): fit_score(b, n) for b in problem.buyers for n in problem.neighborhoods
    }

    choices: dict[str, list[str]] = {}
    for buyer in problem.buyers:
        rest = [n for n in names if n not in buyer.preferences]
        rest.sort(key=lambda n: -score[buyer.name, n])
        choices[buyer.name] = [*buyer.preferences, *rest]

    held: dict[str, list[str]] = {n: [] for n in names}
    next_choice = dict.fromkeys(input_order, 0)
    unplaced = deque(b.name for b in problem.buyers)

    while unplaced:
        buyer = unplaced.popleft()
        neighborhood = choices[buyer][next_choice[buyer]]
        next_choice[buyer] += 1

        applicants = held[neighborhood]
        applicants.append(buyer)
        applicants.sort(key=lambda b: (-score[b, neighborhood], input_order[b]))
        if len(applicants) > limit:
            unplaced.append(applicants.pop())

    return {n: [(b, score[b, n]) for b in held[n]] for n in names}


def format_placements(placements: Placements) -> str:
    return "".join(
        f"{neighborhood}: {' '.join(f'{buyer}({score})' for buyer, score in assigned)}\n"
        for neighborhood, assigned in placements.items()
    )
