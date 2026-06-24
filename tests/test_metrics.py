"""Scoring-rule and calibration metric tests."""

from __future__ import annotations

from goalline.eval import metrics


def test_log_loss_rewards_confident_correct_predictions():
    y = [1, 0, 1, 0]
    confident = metrics.log_loss(y, [0.9, 0.1, 0.9, 0.1])
    timid = metrics.log_loss(y, [0.6, 0.4, 0.6, 0.4])
    assert confident < timid


def test_brier_known_value():
    assert abs(metrics.brier([1, 0], [0.75, 0.25]) - 0.0625) < 1e-12


def test_ece_is_zero_when_perfectly_calibrated():
    y = [1, 0] * 50  # 50% positive
    p = [0.5] * 100
    assert metrics.ece(y, p) < 1e-9


def test_skill_scores_positive_when_model_beats_reference():
    y = [1, 0, 1, 0]
    better = [0.9, 0.1, 0.9, 0.1]
    worse = [0.6, 0.4, 0.6, 0.4]
    assert metrics.log_loss_skill(y, better, worse) > 0
    assert metrics.brier_skill(y, better, worse) > 0
