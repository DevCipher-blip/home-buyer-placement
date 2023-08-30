import random
from pathlib import Path

import pytest

from home_buyer_placement import (
    InputError,
    capacity,
    fit_score,
    format_placements,
    parse_file,
    parse_lines,
    place_buyers,
)

SAMPLE = Path(__file__).resolve().parent.parent / "examples" / "input.txt"


def place(*lines):
    return place_buyers(parse_lines(lines))


def assignment(placements):
    return {buyer: n for n, assigned in placements.items() for buyer, _ in assigned}


def test_sample_placement():
    assert place_buyers(parse_file(SAMPLE)) == {
        "N0": [("H5", 161), ("H11", 154), ("H2", 128), ("H4", 122)],
        "N1": [("H9", 23), ("H8", 21), ("H7", 20), ("H1", 18)],
        "N2": [("H6", 128), ("H3", 120), ("H10", 86), ("H0", 83)],
    }


def test_capacity_is_buyers_per_neighborhood():
    problem = parse_file(SAMPLE)
    assert capacity(problem) == 4


def test_buyers_that_do_not_divide_evenly_are_rejected():
    with pytest.raises(InputError, match="3 buyers cannot be split evenly across 2"):
        place(
            "N A E:1 W:0 R:0",
            "N B E:0 W:1 R:0",
            "H X E:1 W:1 R:1 A",
            "H Y E:1 W:1 R:1 A",
            "H Z E:1 W:1 R:1 A",
        )


def test_input_without_neighborhoods_is_rejected():
    with pytest.raises(InputError, match="no neighborhoods"):
        place()


def test_neighborhoods_without_buyers_stay_empty():
    assert place("N A E:1 W:1 R:1", "N B E:1 W:1 R:1") == {"A": [], "B": []}


def test_higher_score_takes_the_contested_neighborhood():
    result = place(
        "N A E:1 W:0 R:0",
        "N B E:0 W:1 R:0",
        "H Weak E:1 W:0 R:0 A>B",
        "H Strong E:5 W:0 R:0 A>B",
    )
    assert assignment(result) == {"Strong": "A", "Weak": "B"}


def test_a_bumped_buyer_can_still_reach_a_neighborhood_listed_before_the_bumper():
    # A is processed first, but Low is only bumped out of C later and must
    # still be able to fall back to A.
    result = place(
        "N A E:1 W:0 R:0",
        "N B E:0 W:1 R:0",
        "N C E:0 W:0 R:1",
        "H Low E:1 W:0 R:1 C>A>B",
        "H High E:0 W:0 R:9 C>B>A",
        "H Other E:0 W:1 R:0 B>A>C",
    )
    assert assignment(result) == {"High": "C", "Low": "A", "Other": "B"}


def test_equal_scores_go_to_the_buyer_listed_first():
    neighborhoods = ("N A E:1 W:0 R:0", "N B E:0 W:1 R:0")
    first = place(*neighborhoods, "H X E:2 W:0 R:0 A>B", "H Y E:2 W:0 R:0 A>B")
    swapped = place(*neighborhoods, "H Y E:2 W:0 R:0 A>B", "H X E:2 W:0 R:0 A>B")
    assert assignment(first) == {"X": "A", "Y": "B"}
    assert assignment(swapped) == {"Y": "A", "X": "B"}


def test_buyers_with_equal_scores_are_listed_in_input_order():
    result = place("N A E:1 W:1 R:1", "H X E:1 W:0 R:0 A", "H Y E:0 W:1 R:0 A")
    assert result == {"A": [("X", 1), ("Y", 1)]}


def test_buyers_past_their_stated_preferences_take_the_best_scoring_neighborhood_left():
    result = place(
        "N A E:1 W:0 R:0",
        "N B E:0 W:1 R:0",
        "N C E:0 W:0 R:1",
        "H Strong E:9 W:0 R:0 A",
        "H Short E:1 W:2 R:3 A",
        "H Rival E:0 W:9 R:0 B",
    )
    # Short only listed A and loses it; of B and C it scores higher in C (3 vs 2),
    # and C still has room.
    assert assignment(result) == {"Strong": "A", "Short": "C", "Rival": "B"}


def test_fallback_still_respects_capacity():
    result = place(
        "N A E:1 W:0 R:0",
        "N B E:0 W:1 R:0",
        "H Strong E:9 W:0 R:0 A",
        "H Short E:1 W:0 R:0 A",
    )
    assert assignment(result) == {"Strong": "A", "Short": "B"}


def test_format_lists_neighborhoods_in_input_order():
    text = format_placements(place("N Z E:1 W:0 R:0", "N A E:0 W:1 R:0"))
    assert text == "Z: \nA: \n"


def random_lines(rng, neighborhoods, per_neighborhood):
    names = [f"N{i}" for i in range(neighborhoods)]
    lines = [
        f"N {n} E:{rng.randint(0, 10)} W:{rng.randint(0, 10)} R:{rng.randint(0, 10)}" for n in names
    ]
    for h in range(neighborhoods * per_neighborhood):
        prefs = rng.sample(names, rng.randint(1, neighborhoods))
        lines.append(
            f"H H{h} E:{rng.randint(0, 10)} W:{rng.randint(0, 10)} R:{rng.randint(0, 10)} "
            + ">".join(prefs)
        )
    return lines


@pytest.mark.parametrize("seed", range(200))
def test_random_inputs_fill_every_neighborhood_with_a_stable_assignment(seed):
    rng = random.Random(seed)
    problem = parse_lines(random_lines(rng, rng.randint(1, 5), rng.randint(1, 5)))
    result = place_buyers(problem)
    limit = capacity(problem)

    placed = [buyer for assigned in result.values() for buyer, _ in assigned]
    assert sorted(placed) == sorted(b.name for b in problem.buyers)
    assert all(len(assigned) == limit for assigned in result.values())

    order = {b.name: i for i, b in enumerate(problem.buyers)}
    by_name = {n.name: n for n in problem.neighborhoods}
    where = assignment(result)
    for buyer in problem.buyers:
        ranking = [*buyer.preferences]
        ranking += sorted(
            (n for n in by_name if n not in ranking),
            key=lambda n: -fit_score(buyer, by_name[n]),
        )
        # No neighborhood the buyer ranks higher would rather have them than
        # someone it currently holds.
        for preferred in ranking[: ranking.index(where[buyer.name])]:
            key = (-fit_score(buyer, by_name[preferred]), order[buyer.name])
            assert all((-score, order[held]) < key for held, score in result[preferred]), (
                f"{buyer.name} would displace someone in {preferred}"
            )


def test_placement_is_deterministic():
    lines = random_lines(random.Random(7), 4, 6)
    results = {format_placements(place(*lines)) for _ in range(20)}
    assert len(results) == 1
