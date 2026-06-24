"""Phase 1.5: does an online calibration layer close part of the floor's gap?

    uv run python -m goalline.eval.run_calibration

Runs the baseline walk-forward, applies online isotonic and Platt calibration
(point-in-time, leakage-safe), and reports raw vs both calibrators vs the close
on the calibration-active subset. Writes reports/m1_calibration.md.

Finding: isotonic improves ECE/Brier but *worsens* log-loss (it emits 0/1 in
flat regions, which the tail-sensitive log-loss punishes out-of-sample); Platt,
being smooth, improves all three and closes a meaningful part of the gap.
"""

from __future__ import annotations

import argparse
from pathlib import Path

import pandas as pd

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
    ap = argparse.ArgumentParser(description="M1 calibration-layer A/B.")
    ap.add_argument("--data", type=Path, default=Path("data/processed/m1_dataset.parquet"))
    ap.add_argument("--report", type=Path, default=Path("reports/m1_calibration.md"))
    ap.add_argument("--half-life", type=float, default=180.0)
    args = ap.parse_args()

    dataset = pd.read_parquet(args.data)
    print("Running walk-forward + online calibration (isotonic & platt) ...")
    preds = walk_forward(dataset, EVAL_SEASONS, half_life_days=args.half_life)
    base = online_calibrate(preds, method="isotonic").rename(columns={"model_prob_cal": "iso_cal"})
    base["platt_cal"] = online_calibrate(preds, method="platt")["model_prob_cal"].to_numpy()

    active = base[base["calibrated"]].copy()
    y = active["outcome"]
    print(f"{len(active)} calibration-active predictions (of {len(base)}).")

    table = pd.DataFrame(
        [
            _metric_row("raw model", y, active["model_prob"]),
            _metric_row("isotonic", y, active["iso_cal"]),
            _metric_row("platt", y, active["platt_cal"]),
            _metric_row("close", y, active["market_prob"]),
        ]
    )
    ll_close = metrics.log_loss(y, active["market_prob"])
    gaps = {
        "raw": ll_close - metrics.log_loss(y, active["model_prob"]),
        "isotonic": ll_close - metrics.log_loss(y, active["iso_cal"]),
        "platt": ll_close - metrics.log_loss(y, active["platt_cal"]),
    }
    lo, hi = metrics.block_bootstrap_gap_ci(
        y, active["platt_cal"], active["market_prob"], _block(active)
    )
    closed = (gaps["platt"] - gaps["raw"]) / abs(gaps["raw"]) * 100

    print("\n" + table.to_string(index=False))
    print(f"\nlog-loss gap vs close:  raw {gaps['raw']:+.5f}   "
          f"isotonic {gaps['isotonic']:+.5f}   platt {gaps['platt']:+.5f}")
    print(f"Platt 95% CI [{lo:+.5f}, {hi:+.5f}] — closes {closed:+.1f}% of the raw gap.")

    _write_report(args.report, table, gaps, (lo, hi), closed, len(active))
    print(f"Wrote {args.report}")
    return 0


def _write_report(path, table, gaps, ci, closed, n) -> None:
    lo, hi = ci
    path.parent.mkdir(parents=True, exist_ok=True)
    md = [
        "# Milestone 1 — calibration-layer A/B (derived; safe to commit)",
        "",
        f"Online calibration, point-in-time within the walk-forward, compared on the "
        f"{n} calibration-active predictions.",
        "",
        table.to_markdown(index=False),
        "",
        f"- log-loss gap vs close — raw **{gaps['raw']:+.5f}**, "
        f"isotonic **{gaps['isotonic']:+.5f}**, platt **{gaps['platt']:+.5f}** "
        f"(Platt 95% CI [{lo:+.5f}, {hi:+.5f}])",
        f"- Platt closes **{closed:+.1f}%** of the raw log-loss gap.",
        "",
        "## Finding",
        "",
        "Isotonic improves ECE and Brier but **worsens log-loss**: as a step function it "
        "emits values at exactly 0/1 in flat regions, and the tail-sensitive log-loss "
        "punishes the occasional out-of-sample miss there. **Platt** (smooth, parametric) "
        "improves all three metrics and closes a meaningful part of the gap. The model "
        "still does not beat the close (gap CI excludes 0), but the calibrated floor is "
        "much closer. ECE/Brier and log-loss can disagree — pick the calibrator on the "
        "headline metric.",
    ]
    path.write_text("\n".join(md) + "\n")


if __name__ == "__main__":
    raise SystemExit(main())
