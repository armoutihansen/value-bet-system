"""Phase 1.5: does ClubElo (as a Poisson covariate) close more of the gap?

    uv run python -m goalline.eval.run_features

Attaches point-in-time ClubElo, runs the walk-forward with elo_diff as a Poisson
covariate, applies Platt calibration to both baseline and Elo models, and A/Bs
baseline-calibrated vs Elo-calibrated vs the close. Writes reports/m1_features.md.
"""

from __future__ import annotations

import argparse
from pathlib import Path

import pandas as pd

from ..data.clubelo import attach_elo
from . import metrics
from .calibrate import online_calibrate
from .run_m1 import EVAL_SEASONS
from .walkforward import walk_forward


def _block(df: pd.DataFrame) -> pd.Series:
    return df["league"].astype(str) + "|" + df["week"].astype(str)


def _metric_row(name: str, y, p) -> dict:
    return {
        "series": name,
        "log_loss": round(metrics.log_loss(y, p), 5),
        "brier": round(metrics.brier(y, p), 5),
        "ece": round(metrics.ece(y, p), 4),
    }


def main() -> int:
    ap = argparse.ArgumentParser(description="M1 ClubElo-feature A/B.")
    ap.add_argument("--data", type=Path, default=Path("data/processed/m1_dataset.parquet"))
    ap.add_argument("--cache", type=Path, default=Path("data/clubelo"))
    ap.add_argument("--report", type=Path, default=Path("reports/m1_features.md"))
    ap.add_argument("--half-life", type=float, default=180.0)
    args = ap.parse_args()

    dataset = attach_elo(pd.read_parquet(args.data), args.cache, fetch=False)
    dataset["elo_diff_scaled"] = dataset["elo_diff"] / 400.0

    print("Walk-forward: baseline & baseline+elo ...")
    base_raw = walk_forward(dataset, EVAL_SEASONS, half_life_days=args.half_life)
    elo_raw = walk_forward(
        dataset, EVAL_SEASONS, half_life_days=args.half_life, covariate_col="elo_diff_scaled"
    )
    base = online_calibrate(base_raw, method="platt")
    elo = online_calibrate(elo_raw, method="platt")
    mask = base["calibrated"].to_numpy()
    bc, ec = base[mask].copy(), elo[mask].copy()
    y = bc["outcome"]
    print(f"{len(bc)} calibration-active predictions.")

    table = pd.DataFrame(
        [
            _metric_row("baseline (platt)", y, bc["model_prob_cal"]),
            _metric_row("baseline+elo (platt)", y, ec["model_prob_cal"]),
            _metric_row("close", y, bc["market_prob"]),
        ]
    )
    ll_close = metrics.log_loss(y, bc["market_prob"])
    gap_base = ll_close - metrics.log_loss(y, bc["model_prob_cal"])
    gap_elo = ll_close - metrics.log_loss(y, ec["model_prob_cal"])
    # Does Elo beat the baseline? gap = LL_baseline - LL_elo (positive => Elo better).
    lo, hi = metrics.block_bootstrap_gap_ci(
        y, ec["model_prob_cal"], bc["model_prob_cal"], _block(bc)
    )

    print("\n" + table.to_string(index=False))
    gain = gap_elo - gap_base
    print(f"\ngap vs close:  baseline {gap_base:+.5f}   baseline+elo {gap_elo:+.5f}")
    print(f"Elo vs baseline log-loss gain: {gain:+.5f}  95% CI [{lo:+.5f}, {hi:+.5f}]")
    verdict = "Elo helps" if lo > 0 else ("Elo hurts" if hi < 0 else "Elo: no significant effect")
    print(f"Verdict: {verdict}")

    _write_report(args.report, table, gap_base, gap_elo, (lo, hi), verdict, len(bc))
    print(f"Wrote {args.report}")
    return 0


def _write_report(path, table, gap_base, gap_elo, ci, verdict, n) -> None:
    lo, hi = ci
    gain = gap_elo - gap_base
    path.parent.mkdir(parents=True, exist_ok=True)
    md = [
        "# Milestone 1 — ClubElo feature A/B (derived; safe to commit)",
        "",
        f"Elo difference as a Poisson covariate, both models Platt-calibrated, "
        f"compared on the {n} calibration-active predictions.",
        "",
        table.to_markdown(index=False),
        "",
        f"- log-loss gap vs close — baseline **{gap_base:+.5f}**, baseline+elo **{gap_elo:+.5f}**",
        f"- Elo vs baseline log-loss gain **{gain:+.5f}** (95% CI [{lo:+.5f}, {hi:+.5f}])",
        f"- **Verdict: {verdict}.**",
        "",
        "Elo encodes cross-league / European form the within-league attack/defense "
        "cannot see; whether that adds information beyond the model's own team "
        "strengths is exactly what this A/B tests.",
    ]
    path.write_text("\n".join(md) + "\n")


if __name__ == "__main__":
    raise SystemExit(main())
