# 0003 — V1 data sources

A Phase-0 data audit (June 2026) established the free, legal, reproducible options. Two findings drive this decision and are invisible in code:

- **FBref removed xG and all advanced stats in January 2026** — Opta/Stats Perform terminated the agreement and demanded deletion. FBref is dead as an xG source, and previously-scraped FBref xG has been formally clawed back (do not redistribute). **Understat is now effectively the only live, free xG source for the top-5 leagues.**
- **football-data.co.uk "opening" odds are a Friday/Tuesday-afternoon batch**, an uncontrolled 18–70h pre-kickoff offset — not a controlled timestamp. Its **closing** columns (Pinnacle `PSCH/PSCD/PSCA`, Bet365 `B365C*`) are genuine pre-match closing prices.

**Decision — V1 data stack:**

| Need | Source | Notes |
|---|---|---|
| Fixtures / results | **openfootball** (CC0) | The only dataset committable to the repo |
| Backtest odds + match facts + sharp closing line | **football-data.co.uk** | 1X2, **O/U 2.5 only**, Asian Handicap; Pinnacle + Bet365; back to 2000/01; fetch at build, attribute, do not commit |
| Ratings feature | **ClubElo** | Point-in-time-safe dated `From/To` snapshots |
| xG | **Understat** | Snapshot-frozen; lagged features only; post-FBref the only free top-5 source |

**Reproducibility / legal posture.** Commit only openfootball; fetch everything else at build time via cached scrapers with attribution; never redistribute Understat/FBref/StatsBomb/Sofascore/WhoScored bulk data; keep API keys out of the data path.

**Consequences.** Free historical odds cover **O/U 2.5 only** for totals (no BTTS, no alternative lines). Understat xG is revised/non-reproducible unless snapshot-frozen with a scrape date. Sources are scrapers and will break — caching is mandatory.
