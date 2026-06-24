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
