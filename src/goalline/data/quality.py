"""Data-quality checks on the normalized M1 dataset.

These are the cheap, high-value invariants from the testing strategy: no
duplicate fixtures, valid goals, consistent derived target, valid decimal odds,
and no implausible (future) dates. Leakage-specific tests arrive with features
in Phase 1.5.
"""

from __future__ import annotations

from dataclasses import dataclass, field

import pandas as pd


@dataclass
class QualityReport:
    checks: list[tuple[str, bool, str]] = field(default_factory=list)

    def add(self, name: str, passed: bool, detail: str = "") -> None:
        self.checks.append((name, passed, detail))

    @property
    def ok(self) -> bool:
        return all(passed for _, passed, _ in self.checks)


def check_dataset(df: pd.DataFrame) -> QualityReport:
    r = QualityReport()

    key = ["season", "division", "home_team", "away_team"]
    dups = int(df.duplicated(subset=key).sum())
    r.add("no_duplicate_fixtures", dups == 0, f"{dups} duplicate (season, teams) rows")

    bad_goals = int(((df["home_goals"] < 0) | (df["away_goals"] < 0)).sum())
    r.add("goals_non_negative", bad_goals == 0, f"{bad_goals} negative-goal rows")

    inconsistent = int((df["over_2_5"] != (df["total_goals"] > 2.5)).sum())
    r.add("over_2_5_consistent", inconsistent == 0, f"{inconsistent} inconsistent rows")

    for col in ("over_odds", "under_odds", "home_odds", "draw_odds", "away_odds"):
        present = df[col].notna()
        numeric = pd.to_numeric(df[col], errors="coerce")
        # Present but non-numeric (coerced to NaN) is invalid too, not only <= 1.0.
        bad = int((present & (numeric.isna() | (numeric <= 1.0))).sum())
        r.add(
            f"{col}_valid_decimal",
            bad == 0,
            f"{bad} of {int(present.sum())} present are non-numeric or <= 1.0",
        )

    future = int((df["date"] > pd.Timestamp.now()).sum())
    r.add("no_future_dates", future == 0, f"{future} rows dated in the future")

    return r
