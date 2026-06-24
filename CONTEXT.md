# GoalLine

A paper-trading research system that detects **value bets** in football betting markets from point-in-time data and tracks how a simulated bankroll would evolve under a portfolio staking rule. The emphasis is on *evidence that detected value is real* (calibration and closing-line value), not on raw simulated profit.

## Language

### Pricing & evaluation

**Value bet**:
A selection whose model-estimated probability implies a fair price longer than the price actually available, i.e. positive expected value after the bookmaker margin is removed.
_Avoid_: tip, pick

**Edge**:
The proportional advantage of a bet, `model_probability × decimal_odds − 1`. The expected return per unit staked.
_Avoid_: value (as a number — "value" is the qualitative property, "edge" is the quantity)

**Expected value (EV)**:
Synonym for edge expressed as expected profit per unit stake. Used interchangeably with edge.

**Implied probability**:
The probability a price corresponds to, `1 / decimal_odds`, before removing margin.

**Overround**:
The amount by which a market's raw implied probabilities sum above 1.0 — the bookmaker's built-in margin.
_Avoid_: vig, juice, margin, overround percentage

**De-vig**:
The operation that removes the overround from a market's raw prices to estimate the market's implied probabilities for each selection.
_Avoid_: margin removal, normalisation

**Fair odds**:
The odds implied by an estimated probability with no margin, `1 / probability`. The model's fair odds are what it would price the selection at.

**Closing line**:
The final price available for a selection immediately before the market closes at kickoff. Treated as the most informationally efficient public estimate of the true probability.
_Avoid_: closing odds (use "closing line" for the concept, "closing price" for a specific number)

**Closing line value (CLV)**:
The improvement between the price taken at bet time and the closing price for the same selection. Positive CLV means a better price than the closing market — the leading, lower-variance evidence that a value bet was genuinely mispriced.
_Avoid_: line value, beat-the-close

**Calibration**:
The property that selections assigned probability *p* occur about *p* of the time. The necessary condition for any value claim: if probabilities are not calibrated, edge and stake are computed from wrong numbers.
_Avoid_: reliability (use "calibration"; "reliability diagram" is fine as the name of the plot)

**Sharp book / soft book**:
A *sharp* book (e.g. Pinnacle) or exchange (e.g. Betfair) moves its line efficiently and is the benchmark for CLV; a *soft* book shades and moves slowly. Beating a sharp close is strong evidence; beating a soft close is weak.

### Data & backtest

**Point-in-time** (adj.), also **as-of**:
The principle that a feature value used for a forecast must be the value that was *known before the decision time*. Using later-revised or future values is leakage.
_Avoid_: historical (ambiguous), snapshot (use for the stored artifact, not the principle)

**Model-vs-close**:
The free historical edge test — whether the model's probabilities are systematically more accurate than the sharp closing line. Stands in for true CLV when controlled-timestamp historical prices are unavailable.

**Decision time**:
The fixed pre-kickoff timestamp at which a forecast is generated and a simulated bet is priced. Everything used to make the bet must be point-in-time as of this moment.
_Avoid_: bet time, forecast time (use "decision time" for the canonical moment)

### Modelling

**Score-distribution model**:
A generative model that estimates each team's scoring rate for a match and produces the full joint probability distribution over scorelines, from which every goal-based market price (O/U, BTTS, 1X2, correct score) is derived coherently.
_Avoid_: goals model (acceptable informally), Poisson model (that names one instance, not the family)

**Scoring rate (λ)**:
The expected number of goals for a team in a match — `λ_home`, `λ_away` — the core latent quantities the score-distribution baseline estimates.
_Avoid_: expected goals, xG (reserve **xG** for the Understat shot-based metric; λ is the model's fitted rate, not xG)

