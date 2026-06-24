"""Data-quality check tests on synthetic normalized frames."""

from __future__ import annotations

import pandas as pd

from goalline.data.quality import check_dataset


def _clean() -> pd.DataFrame:
    return pd.DataFrame(
        {
            "season": ["2024/25"] * 3,
            "league": ["Premier League"] * 3,
            "division": ["E0"] * 3,
            "date": pd.to_datetime(["2024-08-15", "2024-08-16", "2024-08-17"]),
            "home_team": ["A", "B", "C"],
            "away_team": ["X", "Y", "Z"],
            "home_goals": [2, 1, 0],
            "away_goals": [2, 0, 0],
            "result": ["D", "H", "D"],
            "total_goals": [4, 1, 0],
            "over_2_5": [True, False, False],
            "over_odds": [1.90, 2.10, 2.50],
            "under_odds": [1.95, 1.80, 1.55],
            "ou_source": ["pinnacle_closing"] * 3,
            "home_odds": [1.5, 1.8, 1.6],
            "draw_odds": [4.0, 3.5, 4.2],
            "away_odds": [6.0, 4.0, 5.0],
            "x12_source": ["pinnacle_closing"] * 3,
        }
    )


def _status(df: pd.DataFrame) -> dict[str, bool]:
    return {name: passed for name, passed, _ in check_dataset(df).checks}


def test_clean_dataset_passes():
    assert check_dataset(_clean()).ok


def test_duplicate_fixture_is_caught():
    df = pd.concat([_clean(), _clean().iloc[[0]]], ignore_index=True)
    assert _status(df)["no_duplicate_fixtures"] is False


def test_invalid_decimal_odds_is_caught():
    df = _clean()
    df.loc[0, "over_odds"] = 0.90  # decimal odds must exceed 1.0
    assert _status(df)["over_odds_valid_decimal"] is False


def test_inconsistent_target_is_caught():
    df = _clean()
    df.loc[1, "over_2_5"] = True  # total is 1, cannot be Over 2.5
    assert _status(df)["over_2_5_consistent"] is False
