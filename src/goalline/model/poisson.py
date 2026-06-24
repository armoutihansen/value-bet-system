"""Time-weighted independent Poisson — the M1 baseline (ADR-0006).

For a match between home team h and away team a:

    lambda_home = exp(mu + home_adv + attack[h] - defense[a])
    lambda_away = exp(mu          + attack[a] - defense[h])

Parameters are fit by maximum likelihood on past matches, each weighted by an
exponential time-decay (recent matches count more). The attack/defense vectors
are unidentified up to a constant, so a small ridge penalty pins them and they
are reported mean-centered (mu absorbs the shift — predictions are unchanged).
An analytic gradient keeps the many walk-forward refits fast.
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np
import pandas as pd
from scipy.optimize import minimize


@dataclass(frozen=True)
class FittedPoisson:
    """A fitted model. Unseen teams (e.g. just-promoted) default to league-average
    strength (attack = defense = 0)."""

    mu: float
    home_adv: float
    attack: dict[str, float]
    defense: dict[str, float]

    def lambdas(self, home_team: str, away_team: str) -> tuple[float, float]:
        a_h, d_h = self.attack.get(home_team, 0.0), self.defense.get(home_team, 0.0)
        a_a, d_a = self.attack.get(away_team, 0.0), self.defense.get(away_team, 0.0)
        lam_home = np.exp(self.mu + self.home_adv + a_h - d_a)
        lam_away = np.exp(self.mu + a_a - d_h)
        return float(lam_home), float(lam_away)


def time_weights(dates: pd.Series, as_of: pd.Timestamp, half_life_days: float) -> np.ndarray:
    age_days = (as_of - dates).dt.days.to_numpy(dtype=float)
    return 0.5 ** (age_days / half_life_days)


def fit_poisson(
    matches: pd.DataFrame,
    as_of: pd.Timestamp,
    *,
    half_life_days: float = 180.0,
    ridge: float = 1e-4,
) -> FittedPoisson:
    """Fit on matches strictly before ``as_of`` (leakage-safe by construction).

    ``matches`` needs columns: date, home_team, away_team, home_goals, away_goals.
    """
    df = matches[matches["date"] < as_of].dropna(
        subset=["home_team", "away_team", "home_goals", "away_goals", "date"]
    )
    if df.empty:
        raise ValueError("no training matches before as_of")

    teams = sorted(set(df["home_team"]) | set(df["away_team"]))
    index = {t: i for i, t in enumerate(teams)}
    n = len(teams)

    hi = df["home_team"].map(index).to_numpy()
    ai = df["away_team"].map(index).to_numpy()
    gh = df["home_goals"].to_numpy(dtype=float)
    ga = df["away_goals"].to_numpy(dtype=float)
    w = time_weights(df["date"], as_of, half_life_days)

    def objective(theta: np.ndarray) -> tuple[float, np.ndarray]:
        mu, home_adv = theta[0], theta[1]
        att, dfn = theta[2 : 2 + n], theta[2 + n : 2 + 2 * n]
        eta_h = mu + home_adv + att[hi] - dfn[ai]
        eta_a = mu + att[ai] - dfn[hi]
        lam_h, lam_a = np.exp(eta_h), np.exp(eta_a)

        ll = np.sum(w * (gh * eta_h - lam_h) + w * (ga * eta_a - lam_a))
        nll = -ll + ridge * np.sum(theta[2:] ** 2)

        rh = w * (gh - lam_h)  # d(ll)/d(eta_home)
        ra = w * (ga - lam_a)  # d(ll)/d(eta_away)
        g_att = np.zeros(n)
        g_def = np.zeros(n)
        np.add.at(g_att, hi, rh)
        np.add.at(g_att, ai, ra)
        np.add.at(g_def, ai, -rh)
        np.add.at(g_def, hi, -ra)
        grad_ll = np.concatenate([[rh.sum() + ra.sum(), rh.sum()], g_att, g_def])
        grad = -grad_ll
        grad[2:] += 2 * ridge * theta[2:]
        return nll, grad

    res = minimize(objective, np.zeros(2 + 2 * n), jac=True, method="L-BFGS-B")
    mu, home_adv = float(res.x[0]), float(res.x[1])
    att, dfn = res.x[2 : 2 + n], res.x[2 + n : 2 + 2 * n]

    # Mean-center attack/defense (mu absorbs the shift; lambdas unchanged).
    a_mean, d_mean = float(att.mean()), float(dfn.mean())
    mu_centered = mu + a_mean - d_mean
    attack = {t: float(att[index[t]] - a_mean) for t in teams}
    defense = {t: float(dfn[index[t]] - d_mean) for t in teams}
    return FittedPoisson(mu=mu_centered, home_adv=home_adv, attack=attack, defense=defense)
