# 0004 — Free-first, spend-gated, forward-only CLV

True CLV needs two controlled-timestamp prices: a bet-time decision price at a fixed pre-kickoff offset, and a sharp closing price. Free historical data has **no** controlled-timestamp bet-time price (see ADR-0003). The only cheap source of controlled-timestamp historical odds — The Odds API historical (~$30/mo, 10× credit cost, back only to mid-2020) — is paid.

**Decision.** Start free.

- The **historical backtest** measures **calibration** and whether the model **beats Pinnacle's closing line** (the free proxy for edge).
- **True bet-time-vs-close CLV** is measured **going forward**, via self-captured snapshots (free Odds API live tier; optionally a free Betfair delayed app key for an exchange benchmark).
- Paid historical odds are **deferred** and revisited only if the free model-vs-close signal justifies the spend.

**Why.** Gate spend on evidence: if the model cannot beat the close for free, paid CLV data only confirms "no edge" at greater cost. Self-captured forward CLV is also a stronger live-paper-trading artifact than a paid historical reconstruction.

**Consequences.** The historical phase **cannot claim true CLV** — it claims calibration + model-vs-close edge. True CLV accrues slowly during the live phase. Revisit this ADR if the free signal is promising or if a controlled-timestamp historical feed becomes free.
