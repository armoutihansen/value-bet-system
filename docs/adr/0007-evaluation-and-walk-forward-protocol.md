# 0007 — Evaluation and walk-forward backtest protocol

Milestone 1 and all offline evaluation must avoid the leakage and small-sample traps that make betting backtests worthless. This ADR fixes the methodology; it is the project's credibility spine.

**Decision.**

- **Walk-forward, expanding window.** For each matchweek *t*, fit only on matches with kickoff strictly before *t*; predict matchweek *t*. No random train/test splits, ever.
- **Point-in-time features only.** Everything is as-of the decision time (ADR refs: [[point-in-time]]). Rolling features are recomputed causally from prior matches; revised sources (Understat xG) are frozen by scrape date and used only lagged.
- **Benchmark = de-vigged Pinnacle closing line**, using **proportional (multiplicative) de-vig**. Shin is implemented only as a tested-and-shown-negligible comparison (<0.5pp on O/U 2.5).
- **Primary metrics:**
  - *Gate:* calibration — reliability diagram + ECE, with confidence bands.
  - *Accuracy:* log loss and Brier (both strictly proper). Brier reported via its Murphy decomposition (reliability / resolution / uncertainty).
  - *Headline:* **log-loss difference vs the de-vigged close** — which equals, in expectation, the Kelly log-growth rate of betting the model against the market (`KL(p‖m) − KL(p‖q)`), i.e. the information-theoretic form of CLV. Also reported as Brier/log-loss skill score.
- **Excluded from offline evaluation:** accuracy / F1 (threshold-dependent, improper), AUC (calibration-invariant — contradicts the gate), ROI / Kelly bankroll (high-variance; deferred to the live phase per ADR-0001).
- **Segmentation discipline.** Slices (league, season, scoring environment) are **pre-registered before viewing results**. Any slice that beats the close is a **hypothesis**, confirmed only on a later, untouched walk-forward window — never concluded from the slice that generated it.
- **Uncertainty.** Block bootstrap (by matchweek/season) for confidence intervals on every metric and on the model-vs-close gap; a naive per-match bootstrap understates variance because matches share team parameters and cluster in time.

**Why.** Walk-forward is the only structure that mirrors deployment and blocks temporal leakage. Proper scoring rules are the theoretically correct objective for probability estimation (uniquely minimized by the true probabilities). Benchmark-relative log loss is the low-variance, information-theoretic version of edge. Pre-registered slices plus out-of-sample confirmation defuse the multiple-testing / selection-bias trap. Block bootstrap respects the data's dependence structure.

**Consequences.** Milestone 1 needs none of the platform (no FastAPI/Postgres/MLflow/Docker/frontend) — just Python, the free data, a walk-forward harness, and an evaluation notebook. This protocol is binding on every later evaluation phase.
