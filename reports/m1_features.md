# Milestone 1 — ClubElo feature A/B (derived; safe to commit)

Elo difference as a Poisson covariate, both models Platt-calibrated, compared on the 3670 calibration-active predictions.

| series               |   log_loss |   brier |    ece |
|:---------------------|-----------:|--------:|-------:|
| baseline (platt)     |    0.67416 | 0.24059 | 0.0174 |
| baseline+elo (platt) |    0.67406 | 0.24055 | 0.018  |
| close                |    0.66382 | 0.23571 | 0.0129 |

- log-loss gap vs close — baseline **-0.01035**, baseline+elo **-0.01025**
- Elo vs baseline log-loss gain **+0.00010** (95% CI [-0.00021, +0.00042])
- **Verdict: Elo: no significant effect.**

Elo encodes cross-league / European form the within-league attack/defense cannot see; whether that adds information beyond the model's own team strengths is exactly what this A/B tests.
