"""Market-pricing coherence tests (ADR-0005)."""

from __future__ import annotations

from scipy.stats import poisson

from goalline.markets import prob_over, prob_under, score_matrix


def test_over_under_are_complementary():
    assert abs(prob_over(1.4, 1.3, 2.5) + prob_under(1.4, 1.3, 2.5) - 1.0) < 1e-12


def test_over_is_monotone_decreasing_in_line():
    lam_home, lam_away = 1.5, 1.2
    assert prob_over(lam_home, lam_away, 1.5) > prob_over(lam_home, lam_away, 2.5)
    assert prob_over(lam_home, lam_away, 2.5) > prob_over(lam_home, lam_away, 3.5)


def test_prob_over_is_a_probability():
    p = prob_over(1.7, 1.1, 2.5)
    assert 0.0 < p < 1.0


def test_prob_over_equals_total_goals_poisson_survival():
    lam_home, lam_away = 1.7, 1.1
    expected = 1.0 - poisson.cdf(2, lam_home + lam_away)  # P(total >= 3)
    assert abs(prob_over(lam_home, lam_away, 2.5) - expected) < 1e-12


def test_score_matrix_sums_to_one():
    assert abs(score_matrix(1.6, 1.2, max_goals=15).sum() - 1.0) < 1e-6
