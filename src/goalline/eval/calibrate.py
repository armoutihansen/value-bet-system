"""Online (point-in-time) probability calibration within the walk-forward.

For each ISO week of predictions, fit a calibrator on every *earlier* prediction
(strictly before the week's first match) and transform that week's raw
probabilities. Leakage-safe: the calibrator never sees the week it transforms.
The first `min_history` predictions pass through uncalibrated (warm-up).
"""

from __future__ import annotations

import numpy as np
import pandas as pd

from ..model.calibration import fit_calibrator


def online_calibrate(
    preds: pd.DataFrame, *, method: str = "isotonic", min_history: int = 380
) -> pd.DataFrame:
    df = preds.sort_values("date").reset_index(drop=True)
    dates = df["date"].to_numpy()
    weeks = df["week"].to_numpy()
    probs = df["model_prob"].to_numpy(dtype=float)
    outcomes = df["outcome"].to_numpy(dtype=float)

    calibrated_prob = probs.copy()
    is_calibrated = np.zeros(len(df), dtype=bool)
    for week in pd.unique(weeks):  # chronological, since df is sorted by date
        wk_idx = np.flatnonzero(weeks == week)
        history = np.flatnonzero(dates < dates[wk_idx].min())
        if len(history) >= min_history:
            calibrator = fit_calibrator(probs[history], outcomes[history], method=method)
            calibrated_prob[wk_idx] = calibrator(probs[wk_idx])
            is_calibrated[wk_idx] = True

    out = df.copy()
    out["model_prob_cal"] = np.clip(calibrated_prob, 1e-9, 1 - 1e-9)
    out["calibrated"] = is_calibrated
    return out
