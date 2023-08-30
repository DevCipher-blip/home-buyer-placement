import pytest

from home_buyer_placement import HomeBuyer, Neighborhood, fit_score


@pytest.mark.parametrize(
    ("goals", "attributes", "expected"),
    [
        ((6, 7, 7), (7, 7, 10), 161),  # H5 in N0 from the sample
        ((8, 2, 3), (2, 1, 1), 21),  # H8 in N1 from the sample
        ((0, 0, 0), (9, 9, 9), 0),
        ((1, 0, 0), (5, 6, 7), 5),
        ((0, 1, 0), (5, 6, 7), 6),
        ((0, 0, 1), (5, 6, 7), 7),
        ((-2, 3, 1), (4, 1, 2), -3),
    ],
)
def test_fit_score_is_the_dot_product_of_goals_and_attributes(goals, attributes, expected):
    buyer = HomeBuyer("H", goals, ("N",))
    assert fit_score(buyer, Neighborhood("N", attributes)) == expected
