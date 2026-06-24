# GoalLine

A paper-trading research system that detects **value bets** in football betting markets from point-in-time data, and measures — honestly — whether a public-data model can beat the closing line.

> **Status: design phase.** The architecture and methodology are specified; Milestone 1 (an offline walk-forward evaluation) is the next build. No betting layer or platform is built until M1 proves the model can match the close.

## The question this answers

Not *"who will win?"* but:

> At a fixed pre-kickoff decision time, is a market price materially mispriced relative to a calibrated model estimate — after margin, model uncertainty, and realistic timing — and can that be demonstrated with evidence that isn't just luck?

## How it judges itself (the part that matters)

Realized profit is the *noisiest* possible evidence, so it is **not** the headline. The evidence hierarchy (see [ADR-0001](docs/adr/0001-evaluation-hierarchy.md)):

1. **Calibration** — are the probabilities true? *(the gate)*
2. **Closing-line value vs a sharp close** — is the model beating the best public price? *(primary proof; equivalently, beating the close in log-loss = the information-theoretic form of CLV)*
3. **Simulated Kelly bankroll** — what it would have paid *(secondary, high-variance demonstration)*

A rigorous **"the market is efficient here"** result is a success, not a failure.

## What it is / isn't

- ✅ A point-in-time, leakage-controlled decisioning and evaluation system; a portfolio piece in ML engineering + applied statistics.
- ❌ Not financial advice, not a tips service, not a promise of profit, never real-money or automated. See [limitations](docs/limitations.md).

## V1 scope

Premier League + Bundesliga · Over/Under 2.5 goals · ~10 seasons · time-weighted Poisson baseline · free public data. Rationale: [ADR-0002](docs/adr/0002-v1-targets-efficient-core.md) (efficient = measurable), [ADR-0005](docs/adr/0005-generative-score-distribution-baseline.md), [ADR-0006](docs/adr/0006-baseline-time-weighted-poisson-not-dixon-coles.md).

## Data

football-data.co.uk (odds + Pinnacle close) · ClubElo (ratings) · Understat (xG) · openfootball (fixtures). **Only openfootball is committed**; everything else is fetched at build time with attribution and never redistributed. See [data-lineage](docs/data-lineage.md) and [ADR-0003](docs/adr/0003-v1-data-sources.md).

## Reading the design

- [`CONTEXT.md`](CONTEXT.md) — domain glossary
- [`docs/adr/`](docs/adr/) — the 7 architectural decisions and their rationale
- [`docs/roadmap.md`](docs/roadmap.md) — phases 0–6 and the spend-gate
- [`docs/architecture.md`](docs/architecture.md) — target system + Mermaid diagrams
- [`docs/backtesting-protocol.md`](docs/backtesting-protocol.md) — the evaluation methodology
- [`docs/data-model.md`](docs/data-model.md) — bitemporal schema (later phases)
- [`docs/limitations.md`](docs/limitations.md) — the honest caveats

## Tech (eventual)

Python · PostgreSQL · FastAPI · MLflow · Prefect · TypeScript/Next.js · Docker Compose · Prometheus/Grafana · GitHub Actions — introduced phase by phase ([roadmap](docs/roadmap.md)), not up front.
