# GoalLine — Roadmap

**Phasing principle:** spend-gated (ADR-0004) and measurability-first (ADR-0002). Each phase has a gate. The betting layer and the platform are **not built until Milestone 1 proves the model can match the closing line.** If M1 says the market is efficient here, most later phases are correctly never built — that is a successful outcome, not a failure (ADR-0001).

---

## Phase 0 — Feasibility & data audit ✅ done

Audited free/legal/reproducible data sources (June 2026). Key findings recorded in **ADR-0003** (FBref xG removed Jan 2026 → Understat is the only free top-5 xG source; football-data.co.uk is the free backtest spine with Pinnacle closing odds) and **ADR-0004** (no controlled-timestamp historical odds for free → true CLV is forward-only).

## Phase 1 — Milestone 1: offline walk-forward — establish the baseline floor ✅ done

- **Scope:** Premier League + Bundesliga, market = Over/Under 2.5. **Walk-forward evaluation on 2019/20–2024/25** (~4,116 matches — the seasons that actually carry a Pinnacle *closing* O/U 2.5 line, verified in `reports/m1_data_coverage.md`); **2014/15–2018/19 serve as goals-only warm-up** for the expanding-window fit. (The earlier seasons carry O/U only as Betbrain aggregates — usable for fitting, not as a sharp-close benchmark.)
- **Model:** time-weighted independent Poisson (ADR-0006), *pure* — no extra features. Establish the floor.
- **Protocol:** ADR-0007 — expanding-window walk-forward, de-vigged Pinnacle close benchmark, calibration + log-loss + Brier, sliced and block-bootstrapped.
- **Needs none of the platform** — Python, the data, a walk-forward harness, an evaluation notebook.
- **Result (`reports/m1_results.md`):** the pure Poisson sits **~2.6% behind** the de-vigged Pinnacle close in log-loss (model 0.678 vs 0.661; gap −0.017, 95% CI [−0.024, −0.011]), consistently across all six seasons and both leagues — but **beats the base rate** (~0.691), so the floor is informative and the harness is validated.
- **This is the expected floor, not a decision point.** A featureless Poisson never beats a sharp close; the floor exists to launch from. The genuine *edge gate* — does the **built-out** model beat the close anywhere, justifying paid data or a live layer — lives after Phase 1.5 (below), not here.

## Phase 1.5 — build the model out ⟵ NEXT

Add a **calibration layer** (isotonic / Platt — the floor is overconfident in the tails: ECE 0.052 vs the close's 0.014), then features (ClubElo ratings, lagged Understat xG), the Dixon-Coles τ-correction test, and the challenger (Bayesian hierarchical dynamic Poisson; gradient-boosting). **Every change is A/B'd against the M1 Poisson floor** — report how much each closes the gap; adopt only what demonstrably improves calibration / model-vs-close.

- **🚦 EDGE GATE (after the refinements):** does the built-out model beat the de-vigged close in any pre-registered slice with a bootstrap CI excluding zero? **Go** → consider paying for controlled-timestamp data (ADR-0004) and building the live layer. **No** → the honest "efficient market" result stands; the portfolio finding is the rigorous floor-to-built-out gap analysis.

## Phase 2 — point-in-time ingestion + signal generation *(only past the gate)*

Live odds capture (Odds API free tier; optional Betfair delayed key) to begin accruing **forward CLV**. First real **decision policy** and **uncertainty quantification**. Paper signals generated at a fixed live decision time.

## Phase 3 — FastAPI + Postgres + MLflow

Persist the data model (see `data-model.md`), serve signals via API, put the model behind an MLflow registry with controlled promotion.

## Phase 4 — TypeScript / Next.js frontend

The decision console (market scan, match detail, signal review queue, monitoring) — a quantitative tool, not a tips site.

## Phase 5 — workflows, monitoring, CI/CD

Prefect orchestration of the ingestion/forecast/settlement loops; Prometheus/Grafana operational + model + decision-quality monitoring; GitHub Actions CI/CD.

## Phase 6 — paper-trading live evaluation

The live loop runs: forward CLV accrues, the simulated Kelly bankroll is tracked as the *lagging, secondary* demonstration (ADR-0001).

---

## Deferred decisions, parked at their phase

Re-grill these when their phase arrives — not before (spend-gate):

| Decision | Phase | Notes |
|---|---|---|
| Decision policy & states (NO_BET / WATCHLIST / …) | 2 | The eligibility rule + reason strings |
| Uncertainty: parametric bootstrap vs Bayesian posterior | 1.5 / 2 | Bootstrap is the cheap interim (ADR-0006) |
| Kelly form: fractional / capped + exposure caps | 2 / 6 | Demoted; core challenge is probability quality |
| Point-in-time feature store realization | 2 | As-of join discipline; see `data-lineage.md` |
| Bitemporal DB schema | 3 | Outlined in `data-model.md`; M1 uses files |
| Live decision time (24h vs 12h) | 2 | Moot for M1 (prior-match features only) |
| Stack sequencing / Docker services | 3–5 | Justified only once there's a signal to serve |
