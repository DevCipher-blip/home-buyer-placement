import pytest

from home_buyer_placement import HomeBuyer, InputError, Neighborhood, parse_lines


def test_parses_neighborhoods_and_buyers_in_input_order():
    problem = parse_lines(
        [
            "N N0 E:7 W:7 R:10",
            "N N1 E:2 W:1 R:1",
            "H H0 E:3 W:9 R:2 N1>N0",
        ]
    )
    assert problem.neighborhoods == (
        Neighborhood("N0", (7, 7, 10)),
        Neighborhood("N1", (2, 1, 1)),
    )
    assert problem.buyers == (HomeBuyer("H0", (3, 9, 2), ("N1", "N0")),)


def test_attribute_order_does_not_matter():
    problem = parse_lines(["N N0 R:3 E:1 W:2", "H H0 W:5 R:6 E:4 N0"])
    assert problem.neighborhoods[0].attributes == (1, 2, 3)
    assert problem.buyers[0].goals == (4, 5, 6)


def test_blank_lines_and_trailing_newlines_are_ignored():
    problem = parse_lines(["\n", "N N0 E:1 W:1 R:1\n", "   \n", "H H0 E:1 W:1 R:1 N0\n", "\n"])
    assert [n.name for n in problem.neighborhoods] == ["N0"]
    assert [b.name for b in problem.buyers] == ["H0"]


def test_buyers_may_reference_neighborhoods_declared_later():
    problem = parse_lines(["H H0 E:1 W:1 R:1 N0", "N N0 E:1 W:1 R:1"])
    assert problem.buyers[0].preferences == ("N0",)


def test_empty_input_parses_to_an_empty_problem():
    problem = parse_lines([])
    assert problem.neighborhoods == ()
    assert problem.buyers == ()


@pytest.mark.parametrize(
    ("line", "message"),
    [
        ("X N1 E:1 W:1 R:1", "must start with N or H"),
        ("N N1 E:1 W:1", "needs 5 fields"),
        ("N N1 E:1 W:1 R:1 extra", "needs 5 fields"),
        ("H H0 E:1 W:1 R:1", "needs 6 fields"),
        ("N N1 E:1 W:1 X:1", "expected an attribute like E:5"),
        ("N N1 E1 W:1 R:1", "expected an attribute like E:5"),
        ("N N1 E:1 E:2 W:1", "attribute E given twice"),
        ("N N1 E:one W:1 R:1", "must be an integer"),
        ("N N1 E: W:1 R:1", "must be an integer"),
        ("H H0 E:1 W:1 R:1 N0>>N0", "malformed preference list"),
        ("H H0 E:1 W:1 R:1 N0>", "malformed preference list"),
        ("H H0 E:1 W:1 R:1 N0>N0", "repeats a neighborhood"),
    ],
)
def test_malformed_lines_report_their_line_number(line, message):
    with pytest.raises(InputError, match=message) as excinfo:
        parse_lines(["N N0 E:1 W:1 R:1", line])
    assert excinfo.value.line_number == 2
    assert str(excinfo.value).startswith("line 2: ")


def test_unknown_preference_points_at_the_buyer_line():
    with pytest.raises(InputError, match="H0 prefers unknown neighborhood\\(s\\): N9") as excinfo:
        parse_lines(["N N0 E:1 W:1 R:1", "", "H H0 E:1 W:1 R:1 N0>N9"])
    assert excinfo.value.line_number == 3


@pytest.mark.parametrize(
    "lines",
    [
        ["N N0 E:1 W:1 R:1", "N N0 E:2 W:2 R:2"],
        ["N N0 E:1 W:1 R:1", "H H0 E:1 W:1 R:1 N0", "H H0 E:1 W:1 R:1 N0"],
        ["N X E:1 W:1 R:1", "H X E:1 W:1 R:1 X"],
    ],
)
def test_duplicate_names_are_rejected(lines):
    with pytest.raises(InputError, match="used more than once"):
        parse_lines(lines)
