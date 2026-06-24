# 0005 — Generative score-distribution baseline; O/U 2.5 primary market

V1 must price Over/Under 2.5 goals. Two modelling paradigms were available: a **generative** score-distribution model (Poisson family) or a **discriminative** binary classifier for `P(Over 2.5)` directly.

**Decision.** The V1 **baseline is a generative score-distribution model**: estimate each team's scoring rate (`λ_home`, `λ_away`), produce the full joint distribution over scorelines, and derive all goal-based market prices from it. The **primary evaluation market is O/U 2.5** (the only free, deep totals line with Pinnacle closing odds — ADR-0003 — and clean ground truth every match). A **discriminative model (gradient boosting) is deferred to the challenger.**

**Why.**

- **Coherence by construction.** Satisfies the "no logically contradictory prices across Over 2.5 / Under 2.5 / BTTS / exact score" requirement automatically, and makes it a hard unit test (monotone Over lines, probabilities sum to 1). A per-market classifier can violate this.
- **Data efficiency.** Learns from the full scoreline of every match rather than one thresholded over/under bit — decisive with only a few seasons per league.
- **Interpretability + monitoring.** `λ_home`/`λ_away` are inspectable; the model-monitoring plan (drift in λ) only exists because the model has a λ.
- **Credibility.** Poisson-family is the literature-standard baseline for totals (Maher 1982, Dixon-Coles 1997).

The discriminative model's one real advantage — flexible use of rich features — is precisely the **challenger's** job, giving a fair baseline-vs-challenger test of whether ML features beat the parametric model.

**Consequences.** The goals model yields 1X2 / BTTS / correct-score coherently as by-products (1X2 is not foregone by choosing O/U 2.5). The coherence properties become mandatory unit tests.
