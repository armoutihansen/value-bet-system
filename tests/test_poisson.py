"""Time-weighted Poisson tests (ADR-0006), on synthetic data."""

from __future__ import annotations

import numpy as np
import pandas as pd

from goalline.model.poisson import fit_poisson


def _simulate(seed: int = 0) -> tuple[pd.DataFrame, dict[str, float], float]:
    rng = np.random.default_rng(seed)
    teams = [f"T{i}" for i in range(8)]
    true_att = dict(zip(teams, np.linspace(0.4, -0.4, 8), strict=True))
    true_def = dict(zip(teams, np.linspace(-0.3, 0.3, 8), strict=True))
    mu, home_adv = 0.2, 0.25
    base = pd.Timestamp("2022-01-01")
    rows = []
    for _ in range(20):
        for h in teams:
            for a in teams:
                if h == a:
                    continue
                lam_h = np.exp(mu + home_adv + true_att[h] - true_def[a])
                lam_a = np.exp(mu + true_att[a] - true_def[h])
                day = base + pd.Timedelta(days=len(rows))
                rows.append((day, h, a, rng.poisson(lam_h), rng.poisson(lam_a)))
    df = pd.DataFrame(rows, columns=["date", "home_team", "away_team", "home_goals", "away_goals"])
    return df, true_att, home_adv


def test_fit_recovers_attack_ordering_and_home_advantage():
    df, true_att, true_home_adv = _simulate()
    fit = fit_poisson(df, as_of=df["date"].max() + pd.Timedelta(days=1), half_life_days=100_000)
    teams = list(true_att)
    recovered = [fit.attack[t] for t in teams]
    truth = [true_att[t] for t in teams]
    assert np.corrcoef(recovered, truth)[0, 1] > 0.9
    assert 0.1 < fit.home_adv < 0.45  # true 0.25


def test_unseen_team_defaults_to_average_strength():
    df, _, _ = _simulate()
    fit = fit_poisson(df, as_of=df["date"].max() + pd.Timedelta(days=1))
    assert "Newcomer" not in fit.attack
    lam_home, lam_away = fit.lambdas("T0", "Newcomer")  # must not raise
    assert lam_home > 0 and lam_away > 0


def test_fit_ignores_matches_on_or_after_as_of():
    base = pd.Timestamp("2022-01-01")
    df = pd.DataFrame(
        [(base + pd.Timedelta(days=i), "A", "B", 1, 1) for i in range(12)],
        columns=["date", "home_team", "away_team", "home_goals", "away_goals"],
    )
    as_of = base + pd.Timedelta(days=12)
    baseline = fit_poisson(df, as_of, half_life_days=100_000)
    absurd_future = pd.DataFrame(
        [(as_of + pd.Timedelta(days=1), "A", "B", 50, 0)], columns=df.columns
    )
    with_future = fit_poisson(pd.concat([df, absurd_future]), as_of, half_life_days=100_000)
    assert baseline.lambdas("A", "B") == with_future.lambdas("A", "B")


def test_no_covariate_gives_zero_coefficient():
    df, _, _ = _simulate()
    fit = fit_poisson(df, as_of=df["date"].max() + pd.Timedelta(days=1))
    assert fit.covariate_coef == 0.0


def test_fit_recovers_positive_covariate_effect():
    rng = np.random.default_rng(2)
    teams = [f"T{i}" for i in range(6)]
    base = pd.Timestamp("2022-01-01")
    true_theta = 0.5
    rows = []
    for _ in range(40):
        for h in teams:
            for a in teams:
                if h == a:
                    continue
                x = float(rng.normal())
                lam_h = np.exp(0.2 + 0.2 + true_theta * x)
                lam_a = np.exp(0.2 - true_theta * x)
                day = base + pd.Timedelta(days=len(rows))
                rows.append((day, h, a, rng.poisson(lam_h), rng.poisson(lam_a), x))
    cols = ["date", "home_team", "away_team", "home_goals", "away_goals", "cov"]
    df = pd.DataFrame(rows, columns=cols)
    as_of = df["date"].max() + pd.Timedelta(days=1)
    fit = fit_poisson(df, as_of=as_of, half_life_days=100_000, covariate_col="cov")
    assert fit.covariate_coef > 0.2  # true effect 0.5, recovered with the right sign
