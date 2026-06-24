"""Probability calibration (Phase 1.5).

A calibrator maps a raw model probability to a calibrated one, learned from past
(raw_prob, outcome) pairs. Used online in the walk-forward (eval/calibrate.py),
so it only ever sees data before the decision time.
"""

from __future__ import annotations

from collections.abc import Callable

import numpy as np
from sklearn.isotonic import IsotonicRegression
from sklearn.linear_model import LogisticRegression


def fit_calibrator(
    probs, outcomes, *, method: str = "isotonic"
) -> Callable[[np.ndarray], np.ndarray]:
    """Fit a calibrator and return a transform: raw probability -> calibrated."""
    p = np.asarray(probs, dtype=float)
    y = np.asarray(outcomes, dtype=float)
    if method == "isotonic":
        model = IsotonicRegression(out_of_bounds="clip", y_min=0.0, y_max=1.0)
        model.fit(p, y)
        return lambda x: model.predict(np.asarray(x, dtype=float))
    if method == "platt":
        model = LogisticRegression()
        model.fit(p.reshape(-1, 1), y)
        return lambda x: model.predict_proba(np.asarray(x, dtype=float).reshape(-1, 1))[:, 1]
    raise ValueError(f"unknown calibration method: {method!r}")
