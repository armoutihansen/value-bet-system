"""Derive market prices from a fitted score distribution (ADR-0005).

Under independent Poisson goals, the *total* is Poisson(lambda_home + lambda_away),
so Over/Under prices follow exactly from the total-goals distribution — no
score-matrix truncation needed. The full score matrix is provided for coherence
tests and other markets.
"""

from __future__ import annotations

import numpy as np
from scipy.stats import poisson


def prob_over(lam_home: float, lam_away: float, line: float = 2.5) -> float:
    """P(total goals > line). For a .5 line (e.g. 2.5) this is P(total >= ceil)."""
    lam_total = lam_home + lam_away
    k = int(np.floor(line))  # line 2.5 -> k=2 -> P(total > 2) = 1 - cdf(2)
    return float(1.0 - poisson.cdf(k, lam_total))


def prob_under(lam_home: float, lam_away: float, line: float = 2.5) -> float:
    return 1.0 - prob_over(lam_home, lam_away, line)


def score_matrix(lam_home: float, lam_away: float, max_goals: int = 15) -> np.ndarray:
    """Joint P(home=i, away=j) under independence, i,j in 0..max_goals."""
    goals = np.arange(max_goals + 1)
    return np.outer(poisson.pmf(goals, lam_home), poisson.pmf(goals, lam_away))


def fair_odds(probability: float) -> float:
    """Fair decimal odds for a probability (no margin)."""
    return float("inf") if probability <= 0 else 1.0 / probability
