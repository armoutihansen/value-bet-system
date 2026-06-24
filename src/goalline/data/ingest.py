"""Load raw football-data.co.uk CSVs and normalize to the M1 schema.

The normalized frame is one row per played match with goals, the derived
Over/Under 2.5 outcome, and the best-available Pinnacle (closing-preferred)
O/U 2.5 and 1X2 odds, each tagged with provenance so downstream code can
restrict to a sharp closing benchmark (ADR-0007).
"""

from __future__ import annotations

from pathlib import Path

import pandas as pd

from . import schema
from .sources import SourceFile, all_sources

_ENCODINGS = ("utf-8-sig", "cp1252", "latin-1")


def read_raw(path: Path) -> pd.DataFrame:
    """Read a raw CSV, tolerating football-data's Windows-1252 encoding and
    occasional ragged rows."""
    last_err: Exception | None = None
    for enc in _ENCODINGS:
        try:
            return pd.read_csv(path, encoding=enc, on_bad_lines="skip")
        except (UnicodeDecodeError, pd.errors.ParserError) as err:  # pragma: no cover
            last_err = err
    raise ValueError(f"could not parse {path}: {last_err}")


def _first_present_pair(df: pd.DataFrame, candidates: list[tuple[str, str, str]]):
    """Return (over_col, under_col, provenance) of the first candidate whose
    both columns exist, else None."""
    for over_col, under_col, label in candidates:
        if over_col in df.columns and under_col in df.columns:
            return over_col, under_col, label
    return None


def _first_present_triple(df: pd.DataFrame, candidates):
    for cols, label in candidates:
        if all(c in df.columns for c in cols):
            return cols, label
    return None


def normalize(raw: pd.DataFrame, src: SourceFile) -> pd.DataFrame:
    """Normalize one raw league-season frame to the M1 schema."""
    df = raw.dropna(how="all").copy()

    # Require the core match fields.
    missing = [c for c in schema.CORE if c not in df.columns]
    if missing:
        raise ValueError(f"{src.cache_name} missing core columns: {missing}")
    df = df.rename(columns=schema.CORE)
    df = df.dropna(subset=["home_team", "away_team", "date"])

    # Goals -> ints; drop unplayed/postponed rows.
    for col in ("home_goals", "away_goals"):
        df[col] = pd.to_numeric(df[col], errors="coerce")
    df = df.dropna(subset=["home_goals", "away_goals"])
    df["home_goals"] = df["home_goals"].astype(int)
    df["away_goals"] = df["away_goals"].astype(int)

    df["date"] = pd.to_datetime(df["date"], dayfirst=True, format="mixed", errors="coerce")
    df = df.dropna(subset=["date"])

    # Derived target.
    df["total_goals"] = df["home_goals"] + df["away_goals"]
    df["over_2_5"] = df["total_goals"] > 2.5

    # Metadata (authoritative, from the source definition).
    df["season"] = src.season_label
    df["league"] = src.league
    df["division"] = src.division

    # O/U 2.5 odds (closing-preferred) with provenance.
    ou = _first_present_pair(df, schema.OU_2_5_CANDIDATES)
    if ou is not None:
        over_col, under_col, label = ou
        df["over_odds"] = pd.to_numeric(df[over_col], errors="coerce")
        df["under_odds"] = pd.to_numeric(df[under_col], errors="coerce")
        df["ou_source"] = label
    else:
        df["over_odds"] = pd.NA
        df["under_odds"] = pd.NA
        df["ou_source"] = pd.NA

    # 1X2 odds (closing-preferred) with provenance.
    x12 = _first_present_triple(df, schema.ONE_X_TWO_CANDIDATES)
    if x12 is not None:
        (h, d, a), label = x12
        df["home_odds"] = pd.to_numeric(df[h], errors="coerce")
        df["draw_odds"] = pd.to_numeric(df[d], errors="coerce")
        df["away_odds"] = pd.to_numeric(df[a], errors="coerce")
        df["x12_source"] = label
    else:
        df["home_odds"] = df["draw_odds"] = df["away_odds"] = pd.NA
        df["x12_source"] = pd.NA

    # Decimal odds must exceed 1.0; treat invalid source values (e.g. a 0.0
    # placeholder) as missing rather than a real price.
    for col in ("over_odds", "under_odds", "home_odds", "draw_odds", "away_odds"):
        s = pd.to_numeric(df[col], errors="coerce")
        df[col] = s.where(s > 1.0)

    return df[schema.NORMALIZED_COLUMNS].reset_index(drop=True)


def build_dataset(
    cache_dir: Path,
    sources: list[SourceFile] | None = None,
) -> pd.DataFrame:
    """Normalize and concatenate all cached league-seasons."""
    sources = sources if sources is not None else all_sources()
    frames = []
    for src in sources:
        path = cache_dir / src.cache_name
        if not path.exists():
            continue
        frames.append(normalize(read_raw(path), src))
    if not frames:
        raise FileNotFoundError(f"no cached files found in {cache_dir}")
    return pd.concat(frames, ignore_index=True)
