"""Per league-season coverage of the key odds columns.

This is the empirical verification of the data audit (ADR-0003): which seasons
actually carry a Pinnacle *closing* O/U 2.5 benchmark, versus only pre-match
Pinnacle or older Betbrain aggregates. Reports presence and fill-rate, not just
column existence.
"""

from __future__ import annotations

from pathlib import Path

import pandas as pd

from . import schema
from .ingest import read_raw
from .sources import SourceFile, all_sources


def _fill_rate(df: pd.DataFrame, col: str, n_matches: int) -> float | None:
    if col not in df.columns or n_matches == 0:
        return None
    return round(float(pd.to_numeric(df[col], errors="coerce").notna().sum()) / n_matches * 100, 1)


def column_coverage(
    cache_dir: Path,
    sources: list[SourceFile] | None = None,
) -> pd.DataFrame:
    sources = sources if sources is not None else all_sources()
    rows = []
    for src in sources:
        path = cache_dir / src.cache_name
        if not path.exists():
            rows.append({"league": src.league, "season": src.season_label, "status": "MISSING"})
            continue
        df = read_raw(path).dropna(how="all")
        n = int(df["HomeTeam"].notna().sum()) if "HomeTeam" in df.columns else 0
        rows.append(
            {
                "league": src.league,
                "season": src.season_label,
                "matches": n,
                "pinnacle_close_OU%": _fill_rate(df, schema.PINNACLE_CLOSING_OU[0], n),
                "pinnacle_prematch_OU%": _fill_rate(df, schema.PINNACLE_PREMATCH_OU[0], n),
                "betbrain_OU%": _fill_rate(df, schema.BETBRAIN_OU[0], n),
                "pinnacle_close_1X2%": _fill_rate(df, "PSCH", n),
            }
        )
    return pd.DataFrame(rows)
