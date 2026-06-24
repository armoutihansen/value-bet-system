"""Fetch-and-cache football-data.co.uk CSVs.

Files land in a git-ignored cache and are never committed (ADR-0004). Existing
files are reused unless ``force=True``; a small delay keeps us polite to the
host (it advertises a request rate limit).
"""

from __future__ import annotations

import time
from pathlib import Path

import requests

from .sources import SourceFile, all_sources

_HEADERS = {
    "User-Agent": (
        "goalline-research/0.0 (personal, non-commercial research; "
        "https://github.com/armoutihansen/value-bet-system)"
    )
}


def fetch_one(
    src: SourceFile,
    cache_dir: Path,
    *,
    force: bool = False,
    timeout: int = 30,
    polite_delay: float = 0.5,
) -> Path:
    cache_dir.mkdir(parents=True, exist_ok=True)
    path = cache_dir / src.cache_name
    if path.exists() and not force:
        return path
    resp = requests.get(src.url, headers=_HEADERS, timeout=timeout)
    resp.raise_for_status()
    path.write_bytes(resp.content)
    time.sleep(polite_delay)
    return path


def fetch_all(
    cache_dir: Path,
    sources: list[SourceFile] | None = None,
    *,
    force: bool = False,
) -> list[Path]:
    sources = sources if sources is not None else all_sources()
    return [fetch_one(s, cache_dir, force=force) for s in sources]
