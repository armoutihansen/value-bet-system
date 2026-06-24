"""De-vig tests."""

from __future__ import annotations

from goalline.eval.devig import devig_two_way, overround


def test_devig_sums_to_one_and_symmetric():
    p_over, p_under = devig_two_way(1.9, 1.9)
    assert abs(p_over + p_under - 1.0) < 1e-12
    assert abs(p_over - 0.5) < 1e-12


def test_devig_lower_odds_gives_higher_probability():
    p_over, p_under = devig_two_way(1.5, 2.7)
    assert p_over > p_under
    assert abs(p_over + p_under - 1.0) < 1e-12


def test_overround_positive_with_margin_zero_without():
    assert overround(1.9, 1.9) > 0
    assert abs(overround(2.0, 2.0)) < 1e-12
