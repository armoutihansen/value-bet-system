# 0006 — Baseline is time-weighted Poisson, not Dixon-Coles

Within the generative family (ADR-0005), the obvious default baseline is the famous Dixon-Coles (1997) model. We are deliberately *not* starting there.

**Decision.** The V1 baseline is an **independent Poisson** model with attack / defense / home-advantage parameters and **exponential time-decay weighting** of past matches, fit by weighted maximum likelihood. The **Dixon-Coles low-score `τ` correction is a measured refinement** — added later and A/B-tested on O/U 2.5, not assumed. The **Bayesian hierarchical dynamic Poisson is the challenger.**

**Why.** Dixon-Coles' headline contribution, the `τ` correction, only reshuffles probability among the 0-0 / 1-0 / 0-1 / 1-1 scorelines — all of which sit *inside* "Under 3 goals." It therefore materially moves the **draw and correct-score prices** but barely moves the **O/U 2.5 line**. DC was designed for 1X2, not totals; for this market it is close to a no-op. Starting with the simpler model reaches the headline result (calibration + model-vs-close) fastest, and demonstrating *"I tested whether DC helps for totals and it doesn't"* is a stronger portfolio result than implementing it on reputation. The Bayesian model's complexity is justified only where it pays off — posterior uncertainty for the decision layer — which is the challenger's role.

**Consequences.** Exponential time decay (half-life ≈ one season) is in from the start; team strength drifts and a static fit leaks nothing but ages badly. Until the Bayesian challenger exists, uncertainty-about-probabilities for the decision layer comes from a **parametric bootstrap** over the fitted Poisson parameters.
