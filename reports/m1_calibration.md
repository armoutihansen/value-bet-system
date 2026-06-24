# Milestone 1 — calibration-layer A/B (derived; safe to commit)

Online calibration, point-in-time within the walk-forward, compared on the 3670 calibration-active predictions.

| series    |   log_loss |   brier |    ece |
|:----------|-----------:|--------:|-------:|
| raw model |    0.6814  | 0.24347 | 0.0561 |
| isotonic  |    0.6871  | 0.2419  | 0.0174 |
| platt     |    0.67416 | 0.24059 | 0.0174 |
| close     |    0.66382 | 0.23571 | 0.0129 |

- log-loss gap vs close — raw **-0.01758**, isotonic **-0.02328**, platt **-0.01035** (Platt 95% CI [-0.01432, -0.00640])
- Platt closes **+41.1%** of the raw log-loss gap.

## Finding

Isotonic improves ECE and Brier but **worsens log-loss**: as a step function it emits values at exactly 0/1 in flat regions, and the tail-sensitive log-loss punishes the occasional out-of-sample miss there. **Platt** (smooth, parametric) improves all three metrics and closes a meaningful part of the gap. The model still does not beat the close (gap CI excludes 0), but the calibrated floor is much closer. ECE/Brier and log-loss can disagree — pick the calibrator on the headline metric.
