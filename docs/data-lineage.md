# GoalLine — Data Lineage

Per-source provenance, point-in-time handling, and the legal/reproducibility posture. Decisions recorded in **ADR-0003** and **ADR-0004**.

## Sources

| Source | Provides | Access | Point-in-time handling | Legal / repro |
|---|---|---|---|---|
| **openfootball** | Fixtures, final scores | CC0 static files in git | Fixtures published ahead; results appended. Git history = built-in as-of audit trail | **Only source committable to the repo** |
| **football-data.co.uk** | Results, shots/cards/corners, multi-book odds incl. **Pinnacle closing** (`PSCH/PSCD/PSCA`), O/U 2.5 | CSV fetch (cache locally) | Pre-match (`B365H`) vs **closing** (`*C*`) columns are explicit. Match-stat columns are post-match — never use as features | No formal license; **fetch at build, attribute, do not commit raw CSVs** |
| **ClubElo** | Team Elo ratings | `api.clubelo.com/<date>` | **PIT-safe by construction** — dated `From`/`To` validity gives the exact rating known the day before kickoff | Public API; credit the site |
| **Understat** | xG / shot-level | scrape (`understat`, `soccerdata`) | **xG is post-match and silently revised** → snapshot once, freeze with a scrape date, use **lagged** only | Informal non-commercial nod only; **ship scraper + cache, never bulk-redistribute** |

## Cross-cutting rules

- **Fetch-at-build, not commit.** Only openfootball ships in the repo. Everything else is pulled at build/CI time into a local cache; the cache is git-ignored. This keeps the repo legal and reproducible-by-instruction.
- **Freeze revised sources.** Understat (and any future xG) is snapshotted with a scrape date; the training window is never re-scraped, or a model retrain silently rewrites history.
- **Preserve availability timestamps.** Every ingested record keeps `ingested_at`; corrections are new rows (see `data-model.md`).
- **Caching is mandatory.** These are scrapers and *will* break (the audit found exactly this pattern). Cache aggressively; pin a `soccerdata` version.

## Leakage-prone features — ranked (avoid or strictly timestamp)

1. **Current-match xG / any same-match stat** — doesn't exist until after kickoff. Direct target leakage. Use prior matches only.
2. **Re-stated historical xG** (Understat model updates) — even *prior* xG can change under your feet. *Reproducibility* hazard #1: snapshot & freeze.
3. **Season-aggregate / standings joined as current-state** — encodes post-fixture (often end-of-season) information. Recompute causally as-of kickoff.
4. **Hindsight-computed ratings** — an Elo column built in one backward pass over the season leaks results. Use ClubElo's dated snapshot or compute causally.
5. **Lineups / injuries without a verified publish timestamp** — defer in V1.
6. **Manager-change dates** — imprecise, misattributed; low-confidence.
7. **"Closing" odds used as model input** — legitimately pre-KO, but embed late team-news; fine as *benchmark*, deliberate if used as a feature.
8. **Backfilled context** (weather, attendance, market values) — often restated; exclude in V1.

## V1 safe-feature starting set (Phase 1.5)

Pre-match odds-implied probabilities (football-data.co.uk) · ClubElo rating & differential (as-of) · causally-computed rolling form (prior-N matches) · lagged rolling xG-for/against (frozen Understat) · rest days / congestion / home-away (from openfootball dates).
