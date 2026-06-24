# GoalLine — Limitations & Failure Modes

This project is a probabilistic market-research and decisioning system. It is **not** financial advice and makes **no** promise of betting profit. Stated honestly up front because the credibility of the whole exercise rests on it (ADR-0001).

## The hard truths

- **Market efficiency.** Pre-match O/U 2.5 in the Premier League and Bundesliga is among the most efficient, most-modeled markets that exist. The closing line at a sharp book is, for practical purposes, the best public probability estimate available. The realistic prior is **no exploitable edge after margin and timing.** The system is built to *measure* that honestly, and a "no edge" finding is a valid result — not a failure to engineer away.

- **Backtest leakage is the largest technical risk.** A betting backtest that quietly uses post-match xG, season aggregates, closing odds as entry prices, or future lineup info will look brilliant and be worthless. The walk-forward protocol (`backtesting-protocol.md`) and the bitemporal data model (`data-model.md`) exist specifically to make leakage hard and testable. Assume any too-good result is leakage until proven otherwise.

- **Small-sample variance.** ROI over hundreds of bets is dominated by noise; a system can look profitable by chance. This is why ROI is demoted to a secondary, lagging metric and CLV + calibration are the headline (ADR-0001).

- **CLV is a proxy, not proof.** Positive closing-line value is strong evidence of market-quality information, but it is **not** proof of sustainable profit. And it only means something against a *sharp* close — beating a soft book proves little. The benchmark choice is load-bearing.

- **Model-vs-market information overlap.** The market already incorporates most of what a public-data model knows. Ensembling with a market prior tends to improve calibration while *reducing* apparent edge — the honest version of "the market is hard to beat."

- **Public-data ceiling.** Professional operations have faster, richer, licensed data and low-latency execution. This project explicitly does **not** claim professional-grade advantage. Free sources are scrapers that break, carry revision/reproducibility hazards (Understat xG), and shift under licensing changes (FBref's Jan-2026 xG removal — ADR-0003).

- **"Closing" must be defined precisely.** The closing price's source, timestamp, and de-vig method are documented (Pinnacle, last pre-kickoff snapshot, proportional de-vig) and must not drift silently.

- **Selection bias.** If only some bookmakers / markets / snapshots are available historically, results may not generalize. Free historical odds give one closing-ish snapshot per match, not the full picture.

## Scope honesty

- **Paper trading only.** No real money, no automated betting, ever.
- **True CLV is forward-only on free data** (ADR-0004) — the historical phase measures calibration + model-vs-close, not true bet-time-vs-close CLV.
- The frontend is a **research console**, not a tips product.
