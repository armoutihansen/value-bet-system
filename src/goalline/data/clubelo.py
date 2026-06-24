"""ClubElo ratings: fetch, cache, and point-in-time lookup (ADR-0003).

Free public API at api.clubelo.com (HTTP only). The per-club endpoint
``http://api.clubelo.com/<NameWithoutSpaces>`` returns a club's full history;
each row carries ``From``/``To`` validity dates, so the rating as-of a match
date is leakage-free. Fetched at build time and never committed; football-data
team names are mapped to ClubElo spellings.

    uv run python -m goalline.data.clubelo   # fetch all dataset teams + validate
"""

from __future__ import annotations

import argparse
import time
from dataclasses import dataclass
from pathlib import Path

import numpy as np
import pandas as pd
import requests

_HEADERS = {"User-Agent": "goalline-research/0.0 (personal, non-commercial research)"}

# football-data.co.uk spelling -> ClubElo display name (identity unless listed).
CLUBELO_NAME: dict[str, str] = {
    "Nott'm Forest": "Forest",
    "Bayern Munich": "Bayern",
    "Ein Frankfurt": "Frankfurt",
    "FC Koln": "Koeln",
    "Fortuna Dusseldorf": "Duesseldorf",
    "Greuther Furth": "Fuerth",
    "Holstein Kiel": "Holstein",
    "M'gladbach": "Gladbach",
    "Nurnberg": "Nuernberg",
    "Schalke 04": "Schalke",
    "Werder Bremen": "Werder",
}


def clubelo_name(team: str) -> str:
    return CLUBELO_NAME.get(team, team)


def _url_name(display: str) -> str:
    return display.replace(" ", "")  # the API rejects spaces


def fetch_club_history(
    display_name: str, cache_dir: Path, *, force: bool = False, polite_delay: float = 0.3
) -> Path:
    cache_dir.mkdir(parents=True, exist_ok=True)
    path = cache_dir / f"{_url_name(display_name)}.csv"
    if path.exists() and not force:
        return path
    url = f"http://api.clubelo.com/{_url_name(display_name)}"
    resp = requests.get(url, headers=_HEADERS, timeout=30)
    resp.raise_for_status()
    path.write_bytes(resp.content)
    time.sleep(polite_delay)
    return path


def load_history(path: Path) -> pd.DataFrame:
    df = pd.read_csv(path)
    df = df[df["Elo"].notna()].copy()
    df["From"] = pd.to_datetime(df["From"])
    df["To"] = pd.to_datetime(df["To"])
    return df.sort_values("From").reset_index(drop=True)


@dataclass(frozen=True)
class EloIndex:
    """Point-in-time Elo lookup for one club."""

    starts: np.ndarray  # sorted From dates
    elos: np.ndarray

    def as_of(self, date) -> float:
        """Rating in effect at ``date`` (the most recent From <= date)."""
        i = int(np.searchsorted(self.starts, np.datetime64(date), side="right")) - 1
        return float(self.elos[i]) if i >= 0 else float("nan")


def build_index(teams, cache_dir: Path, *, fetch: bool = True) -> dict[str, EloIndex]:
    index = {}
    for team in teams:
        name = clubelo_name(team)
        if fetch:
            fetch_club_history(name, cache_dir)
        hist = load_history(cache_dir / f"{_url_name(name)}.csv")
        index[team] = EloIndex(hist["From"].to_numpy(), hist["Elo"].to_numpy(dtype=float))
    return index


def attach_elo(matches: pd.DataFrame, cache_dir: Path, *, fetch: bool = True) -> pd.DataFrame:
    teams = sorted(set(matches["home_team"]) | set(matches["away_team"]))
    index = build_index(teams, cache_dir, fetch=fetch)
    out = matches.copy()

    def lookup(team_col: str) -> list[float]:
        return [index[t].as_of(d) for t, d in zip(out[team_col], out["date"], strict=True)]

    out["elo_home"] = lookup("home_team")
    out["elo_away"] = lookup("away_team")
    out["elo_diff"] = out["elo_home"] - out["elo_away"]
    return out


def main() -> int:
    ap = argparse.ArgumentParser(description="Fetch + validate ClubElo coverage.")
    ap.add_argument("--data", type=Path, default=Path("data/processed/m1_dataset.parquet"))
    ap.add_argument("--cache", type=Path, default=Path("data/clubelo"))
    args = ap.parse_args()

    df = pd.read_parquet(args.data)
    teams = sorted(set(df["home_team"]) | set(df["away_team"]))
    print(f"Fetching ClubElo history for {len(teams)} teams ...")
    index = build_index(teams, args.cache, fetch=True)

    rows = []
    for t in teams:
        appearances = df[(df["home_team"] == t) | (df["away_team"] == t)]
        present = sum(not np.isnan(index[t].as_of(d)) for d in appearances["date"])
        n = len(appearances)
        rows.append({"team": t, "clubelo": clubelo_name(t), "matches": n, "elo_present": present})
    report = pd.DataFrame(rows)
    gaps = report[report["elo_present"] < report["matches"]]

    enriched = attach_elo(df, args.cache, fetch=False)
    covered = int(enriched["elo_diff"].notna().sum())
    print(f"matches with an Elo on both sides: {covered} of {len(df)}")
    if len(gaps):
        print("\nTeams with incomplete coverage (need a name fix):")
        print(gaps.to_string(index=False))
    else:
        print("All teams fully covered.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
