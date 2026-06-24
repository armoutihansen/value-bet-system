"""Ingestion tests on synthetic fixtures (no real football-data.co.uk data)."""

from __future__ import annotations

import pandas as pd
import pytest

from goalline.data.ingest import normalize
from goalline.data.sources import SourceFile


def _raw_modern() -> pd.DataFrame:
    """Mimics a 2019/20+ file: Pinnacle closing + pre-match O/U, closing 1X2.
    Includes a postponed row (NaN goals) and an all-empty trailing row."""
    return pd.DataFrame(
        {
            "Date": ["15/08/24", "16/08/24", "17/08/24", "18/08/24", None],
            "HomeTeam": ["Arsenal", "Chelsea", "Liverpool", "Newcastle", None],
            "AwayTeam": ["Spurs", "Man City", "Everton", "Brighton", None],
            "FTHG": [2, 1, 0, None, None],
            "FTAG": [2, 0, 0, None, None],
            "FTR": ["D", "H", "D", None, None],
            "PC>2.5": [1.90, 2.10, 2.50, 2.0, None],
            "PC<2.5": [1.95, 1.80, 1.55, 1.85, None],
            "P>2.5": [1.88, 2.05, 2.45, 1.98, None],
            "P<2.5": [1.97, 1.82, 1.57, 1.87, None],
            "PSCH": [1.5, 1.8, 1.6, 2.2, None],
            "PSCD": [4.0, 3.5, 4.2, 3.3, None],
            "PSCA": [6.0, 4.0, 5.0, 3.1, None],
        }
    )


def test_normalize_drops_unplayed_and_empty_rows():
    out = normalize(_raw_modern(), SourceFile(season="2425", division="E0"))
    assert len(out) == 3  # postponed + all-empty rows dropped


def test_normalize_derives_target_and_metadata():
    out = normalize(_raw_modern(), SourceFile(season="2425", division="E0"))
    assert out["over_2_5"].tolist() == [True, False, False]  # totals 4, 1, 0
    assert out["total_goals"].tolist() == [4, 1, 0]
    assert out["season"].unique().tolist() == ["2024/25"]
    assert out["league"].unique().tolist() == ["Premier League"]


def test_normalize_prefers_pinnacle_closing_odds():
    out = normalize(_raw_modern(), SourceFile(season="2425", division="E0"))
    assert out["ou_source"].unique().tolist() == ["pinnacle_closing"]
    assert out["over_odds"].iloc[0] == 1.90  # the PC>2.5 value, not P>2.5
    assert out["x12_source"].unique().tolist() == ["pinnacle_closing"]


def test_normalize_falls_back_to_betbrain_and_prematch_1x2():
    """Pre-2019/20 file: only Betbrain O/U and pre-match Pinnacle 1X2."""
    raw = pd.DataFrame(
        {
            "Date": ["10/05/15", "11/05/15"],
            "HomeTeam": ["Bayern", "Dortmund"],
            "AwayTeam": ["Mainz", "Koln"],
            "FTHG": [3, 1],
            "FTAG": [0, 1],
            "FTR": ["H", "D"],
            "BbAv>2.5": [1.70, 2.00],
            "BbAv<2.5": [2.10, 1.80],
            "PSH": [1.20, 2.00],
            "PSD": [6.0, 3.4],
            "PSA": [12.0, 3.5],
        }
    )
    out = normalize(raw, SourceFile(season="1415", division="D1"))
    assert out["ou_source"].unique().tolist() == ["betbrain_avg_prematch"]
    assert out["x12_source"].unique().tolist() == ["pinnacle_prematch"]


def test_normalize_requires_core_columns():
    with pytest.raises(ValueError):
        normalize(pd.DataFrame({"HomeTeam": ["x"]}), SourceFile(season="2425", division="E0"))
