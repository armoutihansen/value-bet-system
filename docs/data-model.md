# GoalLine — Data Model (later-phase schema outline)

> **Milestone 1 does not need a database.** It runs off cached CSV/Parquet. This schema is the Phase 3 target, designed around one non-negotiable: **point-in-time correctness must be enforced by the data model, not just by convention.**

## The core idea: two time axes (bitemporal)

Every fact carries *when it was true* and *when we learned it*:

- **`valid_at`** — the time the fact pertains to (kickoff, the moment a price was live).
- **`ingested_at`** — the time our system recorded it (transaction time).

A point-in-time query for a forecast at decision time `D` selects rows where `valid_at ≤ D` **and** `ingested_at ≤ D`. The second clause is what stops backfilled data (a revised xG, a late-corrected result) from leaking into a historical forecast. Raw tables are **append-only**; corrections are new rows, never updates.

## Tables (outline)

```sql
-- Immutable raw odds snapshots (append-only; never UPDATE/DELETE)
odds_snapshot(
  odds_snapshot_id PK,
  fixture_id FK,
  source, bookmaker,
  market, line, selection,           -- e.g. totals, 2.5, over
  decimal_odds,
  captured_at,                       -- valid_at: when the price was live
  source_timestamp,                  -- as reported by the source
  ingested_at,                       -- transaction time
  raw_payload JSONB                  -- preserve the original, un-normalized
)

fixture(
  fixture_id PK, league, season,
  home_team_id, away_team_id,
  kickoff_at,
  final_home_goals, final_away_goals, status,
  result_ingested_at,                -- when the score became known to us
  source_timestamp, ingested_at
)

team(team_id PK, canonical_name, league, aliases JSONB)  -- cross-source ID resolution

-- Point-in-time feature snapshot used for a specific forecast
feature_snapshot(
  feature_snapshot_id PK, fixture_id FK,
  feature_version,
  as_of,                             -- decision time the features respect
  features JSONB, built_at
)

-- One row per generated forecast/decision (the audit trail; mirrors the brief)
forecast(
  forecast_id PK, fixture_id FK,
  generated_at, kickoff_at,
  feature_snapshot_time, odds_snapshot_time, decision_time,
  market, line, selection,
  model_probability, fair_odds,
  market_probability_raw, market_probability_devigged,
  best_available_odds,
  expected_value_raw, expected_value_uncertainty_adjusted,
  decision, decision_reason,
  model_version, feature_version, data_quality_status
)

-- Closing snapshot + CLV, captured at kickoff
closing_line(fixture_id FK, market, line, selection,
             closing_odds, closing_devigged_probability, captured_at)

-- Settlement of simulated bets (Phase 6)
settlement(forecast_id FK, outcome, stake, pnl, clv, settled_at)
```

## Rules the schema enforces

- **Raw is immutable.** `odds_snapshot` and the raw side of `fixture` are append-only. Re-pulls insert new rows with a new `ingested_at`.
- **Preserve the original payload.** `raw_payload JSONB` keeps the un-normalized source record so normalization bugs are recoverable and audits are possible.
- **Forecasts are frozen.** A `forecast` row records the exact model/feature/odds versions and timestamps used — it is never recomputed in place.
- **No "best odds" lookahead.** `best_available_odds` is selected only from snapshots with `captured_at ≤ decision_time`.
- See `data-lineage.md` for per-source as-of handling and `backtesting-protocol.md` for the leakage tests that guard these invariants.
