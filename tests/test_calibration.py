"""Calibration-layer tests (synthetic)."""

from __future__ import annotations

import numpy as np
import pandas as pd

from goalline.eval import metrics
from goalline.eval.calibrate import online_calibrate
from goalline.model.calibration import fit_calibrator


def test_isotonic_calibration_reduces_ece_on_overconfident_model():
    rng = np.random.default_rng(0)
    true_p = rng.uniform(0.2, 0.8, 4000)
    y = (rng.uniform(size=4000) < true_p).astype(float)
    # Overconfident model: push probabilities away from 0.5.
    raw = np.clip(0.5 + (true_p - 0.5) * 1.6, 0.01, 0.99)
    calibrate = fit_calibrator(raw, y, method="isotonic")
    assert metrics.ece(y, calibrate(raw)) < metrics.ece(y, raw)


def test_online_calibrate_warms_up_then_calibrates_and_passes_through_raw():
    base = pd.Timestamp("2020-01-01")
    rng = np.random.default_rng(1)
    rows = []
    for w in range(60):
        day = base + pd.Timedelta(weeks=w)
        for _ in range(10):
            mp = float(rng.uniform(0.2, 0.8))
            rows.append(
                {
                    "league": "L",
                    "week": str(day.to_period("W")),
                    "date": day,
                    "model_prob": mp,
                    "outcome": int(rng.uniform() < mp),
                    "market_prob": mp,
                }
            )
    out = online_calibrate(pd.DataFrame(rows), min_history=100)
    assert (~out["calibrated"]).any() and out["calibrated"].any()  # both warm-up and active exist
    passthrough = out[~out["calibrated"]]
    assert np.allclose(passthrough["model_prob_cal"], passthrough["model_prob"])
