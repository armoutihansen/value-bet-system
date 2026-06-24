"""Expanding-window walk-forward harness (ADR-0007).

For each league and each ISO week in the evaluation seasons, fit the Poisson on
every match *strictly before* that week's first match (warm-up + earlier eval
seasons all contribute their goals), then predict P(Over 2.5) for that week's
matches and compare against the de-vigged Pinnacle closing line. Refitting per
week (not per match) keeps the run fast; it is leakage-safe because training is
always strictly before the predicted matches.
"""

from __future__ import annotations

from collections.abc import Callable

import pandas as pd

from ..markets import prob_over
from ..model.poisson import fit_poisson
from .devig import devig_two_way


def walk_forward(
    dataset: pd.DataFrame,
    eval_seasons: list[str],
    *,
    line: float = 2.5,
    half_life_days: float = 180.0,
    min_train_matches: int = 200,
    benchmark_source: str = "pinnacle_closing",
    progress: Callable[[str, int], None] | None = None,
) -> pd.DataFrame:
    results = []
    for league, g in dataset.groupby("league"):
        g = g.sort_values("date").reset_index(drop=True)
        is_eval = (
            g["season"].isin(eval_seasons)
            & (g["ou_source"] == benchmark_source)
            & g["over_odds"].notna()
            & g["under_odds"].notna()
        )
        ev = g[is_eval].copy()
        ev["_week"] = ev["date"].dt.to_period("W")

        n_fits = 0
        for week, wk_matches in ev.groupby("_week", sort=True):
            as_of = wk_matches["date"].min()
            train = g[g["date"] < as_of]
            if len(train) < min_train_matches:
                continue
            fitted = fit_poisson(train, as_of=as_of, half_life_days=half_life_days)
            n_fits += 1
            for r in wk_matches.itertuples():
                lam_h, lam_a = fitted.lambdas(r.home_team, r.away_team)
                p_over_market, _ = devig_two_way(r.over_odds, r.under_odds)
                results.append(
                    {
                        "league": league,
                        "season": r.season,
                        "date": r.date,
                        "week": str(week),
                        "home_team": r.home_team,
                        "away_team": r.away_team,
                        "model_prob": prob_over(lam_h, lam_a, line),
                        "market_prob": p_over_market,
                        "outcome": int(r.over_2_5),
                        "over_odds": float(r.over_odds),
                        "lam_total": lam_h + lam_a,
                    }
                )
            if progress is not None:
                progress(league, n_fits)
    return pd.DataFrame(results)
