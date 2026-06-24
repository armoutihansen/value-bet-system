# 0001 — Evaluation hierarchy: calibration and CLV over realized ROI

The system detects value bets and tracks a simulated Kelly bankroll. The obvious success metric is realized simulated ROI — but over a few hundred bets in efficient football markets, ROI is dominated by outcome variance and is easily inflated by leakage, so it is weak evidence that detected value is real.

**Decision.** Three-tier evidence hierarchy:

1. **Calibration is the gate.** Value may only be claimed where the model's probabilities are demonstrably calibrated *in that segment*. Miscalibrated probabilities make edge and stake fiction.
2. **CLV against a sharp closing line is the primary proof of edge.** It is low-variance and available at kickoff, giving a trustworthy read on edge in hundreds of bets rather than thousands.
3. **The simulated Kelly bankroll is the headline demonstration, but secondary, high-variance evidence.** It is reported, never used as proof or as a model-promotion gate.

**Why.** Kelly staking assumes calibrated probabilities — miscalibration causes systematic overbetting and simulated ruin — so calibration is a prerequisite, not a nicety. CLV is the industry-standard fingerprint of genuine skill and discriminates edge from luck far faster than ROI. This framing also reads as credible rather than naïve to the quant / ML-engineer / applied-scientist audience the project targets.

**Considered and rejected.** Realized simulated ROI / bankroll growth as the primary metric — too noisy and too easily inflated by leakage to constitute proof.

**Consequences.** Evaluation, monitoring, and model-promotion gates are organised around calibration and CLV first; ROI is shown but is never the headline. A "no exploitable edge" finding, backed by calibrated CLV evidence, is a valid and publishable result.
