"""Proper scoring rules and calibration metrics (ADR-0007).

All operate on a binary outcome y in {0,1} and a probability p in (0,1). Skill
scores are relative to a reference probability (the de-vigged close): positive
means the model beats the reference.
"""

from __future__ import annotations

import numpy as np
import pandas as pd

_EPS = 1e-12


def _arrays(y, p) -> tuple[np.ndarray, np.ndarray]:
    return np.asarray(y, dtype=float), np.clip(np.asarray(p, dtype=float), _EPS, 1 - _EPS)


def log_loss(y, p) -> float:
    y, p = _arrays(y, p)
    return float(-np.mean(y * np.log(p) + (1 - y) * np.log(1 - p)))


def brier(y, p) -> float:
    y, p = _arrays(y, p)
    return float(np.mean((p - y) ** 2))


def ece(y, p, n_bins: int = 10) -> float:
    """Expected calibration error (equal-width bins)."""
    y, p = _arrays(y, p)
    edges = np.linspace(0.0, 1.0, n_bins + 1)
    bin_idx = np.clip(np.digitize(p, edges) - 1, 0, n_bins - 1)
    error = 0.0
    for b in range(n_bins):
        mask = bin_idx == b
        if mask.any():
            error += abs(p[mask].mean() - y[mask].mean()) * mask.mean()
    return float(error)


def reliability_table(y, p, n_bins: int = 10) -> pd.DataFrame:
    y, p = _arrays(y, p)
    edges = np.linspace(0.0, 1.0, n_bins + 1)
    bin_idx = np.clip(np.digitize(p, edges) - 1, 0, n_bins - 1)
    rows = []
    for b in range(n_bins):
        mask = bin_idx == b
        if mask.any():
            rows.append(
                {"bin": f"[{edges[b]:.1f},{edges[b + 1]:.1f})",
                 "n": int(mask.sum()),
                 "mean_pred": round(float(p[mask].mean()), 4),
                 "mean_obs": round(float(y[mask].mean()), 4)}
            )
    return pd.DataFrame(rows)


def log_loss_skill(y, p_model, p_ref) -> float:
    """1 - LL_model / LL_ref. Positive => model beats the reference."""
    return 1.0 - log_loss(y, p_model) / log_loss(y, p_ref)


def brier_skill(y, p_model, p_ref) -> float:
    return 1.0 - brier(y, p_model) / brier(y, p_ref)


def row_log_loss(y, p) -> np.ndarray:
    """Per-row log loss, for bootstrap aggregation."""
    y, p = _arrays(y, p)
    return -(y * np.log(p) + (1 - y) * np.log(1 - p))


def block_bootstrap_gap_ci(
    outcome, model_prob, ref_prob, blocks, *, n_boot: int = 2000, seed: int = 0
):
    """95% CI for gap = LL_ref - LL_model (positive => model beats ref).

    Resamples whole blocks (e.g. league x ISO week) with replacement to respect
    the data's dependence structure (ADR-0007).
    """
    frame = pd.DataFrame(
        {
            "block": np.asarray(blocks),
            "lm": row_log_loss(outcome, model_prob),
            "lr": row_log_loss(outcome, ref_prob),
        }
    )
    agg = frame.groupby("block").agg(sm=("lm", "sum"), sr=("lr", "sum"), n=("lm", "size"))
    sm, sr, nn = agg["sm"].to_numpy(), agg["sr"].to_numpy(), agg["n"].to_numpy()
    n_blocks = len(agg)
    rng = np.random.default_rng(seed)
    gaps = np.empty(n_boot)
    for i in range(n_boot):
        idx = rng.integers(0, n_blocks, n_blocks)
        total = nn[idx].sum()
        gaps[i] = sr[idx].sum() / total - sm[idx].sum() / total
    return float(np.percentile(gaps, 2.5)), float(np.percentile(gaps, 97.5))
