"""football-data.co.uk source definitions for Milestone 1.

Division codes: E0 = Premier League, D1 = Bundesliga.
Season codes: "1415" == 2014/15 ... "2425" == 2024/25.

Earlier seasons exist on football-data.co.uk (EPL back to 1993/94) and may be
added later as training warm-up; M1 fetches 2014/15 onward.
"""

from __future__ import annotations

from dataclasses import dataclass

BASE_URL = "https://www.football-data.co.uk/mmz4281/{season}/{division}.csv"

DIVISIONS: dict[str, str] = {
    "E0": "Premier League",
    "D1": "Bundesliga",
}

SEASONS: tuple[str, ...] = (
    "1415", "1516", "1617", "1718", "1819",
    "1920", "2021", "2122", "2223", "2324", "2425",
)


@dataclass(frozen=True)
class SourceFile:
    """One league-season CSV on football-data.co.uk."""

    season: str
    division: str

    @property
    def url(self) -> str:
        return BASE_URL.format(season=self.season, division=self.division)

    @property
    def league(self) -> str:
        return DIVISIONS[self.division]

    @property
    def season_label(self) -> str:
        """'1415' -> '2014/15'."""
        return f"{2000 + int(self.season[:2])}/{self.season[2:]}"

    @property
    def cache_name(self) -> str:
        return f"{self.division}_{self.season}.csv"


def all_sources(
    seasons: tuple[str, ...] = SEASONS,
    divisions: tuple[str, ...] = tuple(DIVISIONS),
) -> list[SourceFile]:
    return [SourceFile(season=s, division=d) for d in divisions for s in seasons]
