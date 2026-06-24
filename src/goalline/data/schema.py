"""Column mapping for football-data.co.uk and the normalized M1 schema.

football-data.co.uk changed its odds columns at 2019/20: closing columns
("...C...") and per-book Pinnacle O/U (P>2.5) appear only from then; earlier
seasons carry O/U only as Betbrain aggregates (BbAv/BbMx). We therefore detect
columns defensively and record which one was used (provenance), rather than
assume a fixed layout. Verified empirically — see reports/m1_data_coverage.md.
"""

from __future__ import annotations

# Core match columns, present in every season.
CORE: dict[str, str] = {
    "Date": "date",
    "HomeTeam": "home_team",
    "AwayTeam": "away_team",
    "FTHG": "home_goals",
    "FTAG": "away_goals",
    "FTR": "result",
}

TIME_COL = "Time"  # kickoff time; present only from ~2019/20

# Over/Under 2.5 benchmark candidates, sharpest + closing first.
# (over_column, under_column, provenance). The first pair whose BOTH columns are
# present in the file wins (presence only — per-row fill can still vary, which is
# why coverage.py reports fill-rates and quality.py validates the values).
OU_2_5_CANDIDATES: list[tuple[str, str, str]] = [
    ("PC>2.5", "PC<2.5", "pinnacle_closing"),
    ("P>2.5", "P<2.5", "pinnacle_prematch"),
    ("AvgC>2.5", "AvgC<2.5", "market_avg_closing"),
    ("BbAv>2.5", "BbAv<2.5", "betbrain_avg_prematch"),
]

# Pinnacle 1X2, closing preferred. Present across all M1 seasons. Captured for
# later use / sanity, not required by the O/U 2.5 model.
ONE_X_TWO_CANDIDATES: list[tuple[tuple[str, str, str], str]] = [
    (("PSCH", "PSCD", "PSCA"), "pinnacle_closing"),
    (("PSH", "PSD", "PSA"), "pinnacle_prematch"),
]

# The canonical sharp-closing O/U columns, for coverage reporting.
PINNACLE_CLOSING_OU = ("PC>2.5", "PC<2.5")
PINNACLE_PREMATCH_OU = ("P>2.5", "P<2.5")
BETBRAIN_OU = ("BbAv>2.5", "BbAv<2.5")

NORMALIZED_COLUMNS: list[str] = [
    "season", "league", "division", "date",
    "home_team", "away_team",
    "home_goals", "away_goals", "result", "total_goals", "over_2_5",
    "over_odds", "under_odds", "ou_source",
    "home_odds", "draw_odds", "away_odds", "x12_source",
]
