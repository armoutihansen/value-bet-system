"""De-vig: remove the bookmaker overround to recover market-implied probabilities.

V1 uses proportional (multiplicative) normalization (ADR, CONTEXT.md). For a
balanced two-way market like O/U 2.5 this is indistinguishable from Shin/power,
and it makes no claim to recover a "true" probability — it assumes the margin is
applied in proportion to each side's implied probability.
"""

from __future__ import annotations


def devig_two_way(over_odds: float, under_odds: float) -> tuple[float, float]:
    """Return (p_over, p_under), de-vigged and summing to 1."""
    inv_over, inv_under = 1.0 / over_odds, 1.0 / under_odds
    total = inv_over + inv_under
    return inv_over / total, inv_under / total


def overround(over_odds: float, under_odds: float) -> float:
    """The market's overround (sum of raw implied probabilities minus 1)."""
    return 1.0 / over_odds + 1.0 / under_odds - 1.0
