# GoalLine — Backtesting Protocol

The operational expansion of **ADR-0007**. This protocol is binding on every offline evaluation. Violating any clause — a random split, a post-hoc slice, a raw-odds benchmark, an ROI headline — invalidates the result.

## Objective

Answer one question per evaluation: **is the model calibrated, and does it match or beat the de-vigged closing line?** Not "is it profitable" (ADR-0001).

## Walk-forward mechanic

- **Expanding window.** For each matchweek *t*, fit on all matches with `kickoff < t_first_kickoff(t)`; predict matchweek *t*. Advance. No random splits, no k-fold.
- **What is frozen at each decision point *t*:** the training set (strictly prior matches), the feature values (as-of *t*), the hyperparameters (time-decay half-life, any priors), and the odds used for the benchmark (the closing line of matchweek *t*, never of any earlier-captured price for entry). Nothing from ≥ *t* touches the fit or the features.
- **Minimum history.** Skip the first ~1–2 seasons as warm-up; a team needs enough prior matches for stable attack/defense estimates.

## As-of feature rules

- Only prior-match information. Rolling stats recomputed causally; never join a season-aggregate or standings snapshot (it encodes the future).
- Revised sources (Understat xG) are snapshot-frozen by scrape date and used **lagged** (prior matches only). See `data-lineage.md`.
- For M1 the model is feature-free (pure Poisson), so leakage surface is minimal; these rules bind from Phase 1.5 on.

## De-vig

Proportional (multiplicative) normalization of the Pinnacle closing line; Shin computed only as a tested-negligible comparison (ADR-0007). All model-vs-market comparisons are on **de-vigged** probabilities — the vig is margin, not information.

## Metrics

- **Gate — calibration:** reliability diagram + ECE, with confidence bands. Sliced by edge bucket once features exist (tail calibration is where fake value hides).
- **Proper scoring rules:** log loss and Brier (both strictly proper). Brier reported via its Murphy decomposition (reliability / resolution / uncertainty) to separate *calibrated* from *informative*.
- **Headline — log-loss vs the de-vigged close.** `LL_close − LL_model = KL(p‖m) − KL(p‖q)`, which equals the expected Kelly log-growth of betting the model against the market — the information-theoretic form of CLV. Also reported as Brier / log-loss **skill score** (`1 − metric_model/metric_close`).
- **Diagnostic (not headline):** predicted-vs-realized total-goals histogram — catches gross score-distribution misfit.
- **Excluded:** accuracy / F1 (improper, threshold-dependent), AUC (calibration-invariant), ROI / Kelly bankroll (deferred to live phase).

## Baselines to compare against

| Baseline | Purpose | Applies |
|---|---|---|
| Follow the de-vigged close | The null you must beat | M1 |
| Static Poisson (no time decay) | Does recency weighting earn its place? | M1 |
| League base rate (always ~52% Over) | Calibration-without-resolution floor | M1 |
| Random / no-bet | Sanity floors for the betting layer | Phase 2 |
| Naive "bet whenever raw EV > 0" | Does the decision policy add value? | Phase 2 |
| Threshold-only (no uncertainty adj.) | Does uncertainty adjustment add value? | Phase 2 |

Each system component must justify itself by beating the baseline that isolates it.

## Slicing discipline

- **Pre-register** the slices (league, season, scoring environment) before viewing results.
- Any slice that beats the close is a **hypothesis**, confirmed only on a later, untouched walk-forward window — never concluded from its generating slice.
- Report how many slices were examined (multiple-testing transparency).

## Uncertainty

Block bootstrap by matchweek/season for CIs on every metric and on the model-vs-close gap. Naive per-match resampling understates variance (shared team parameters, temporal clustering).

## Leakage checklist (must all be FALSE)

- [ ] Uses post-match xG or any same-match statistic
- [ ] Uses a season aggregate updated after the fixture
- [ ] Uses the closing line as the *entry* price (closing is benchmark only)
- [ ] Uses lineup / injury info without a verified pre-decision timestamp
- [ ] Selects "best" historical odds captured after the decision time
- [ ] Mixes time zones / compares naive timestamps
- [ ] Backfills a source without preserving its `ingested_at`

## Reporting template

Each run produces: scope (leagues/seasons/market), model + feature + protocol versions, the metric table (model vs each baseline, with bootstrap CIs), reliability diagrams (overall + per pre-registered slice), the multiple-testing count, and an explicit go/no-go verdict against the gate.
