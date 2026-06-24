"""ClubElo mapping and point-in-time lookup tests (no network)."""

from __future__ import annotations

import math

import numpy as np
import pandas as pd

from goalline.data.clubelo import EloIndex, clubelo_name


def test_name_mapping_overrides_and_identity():
    assert clubelo_name("Bayern Munich") == "Bayern"
    assert clubelo_name("Nott'm Forest") == "Forest"
    assert clubelo_name("Arsenal") == "Arsenal"  # identity when not overridden


def test_elo_as_of_uses_most_recent_prior_rating():
    starts = pd.to_datetime(["2020-01-01", "2020-02-01"]).to_numpy()
    idx = EloIndex(starts, np.array([1500.0, 1600.0]))
    assert idx.as_of(pd.Timestamp("2020-01-15")) == 1500.0
    assert idx.as_of(pd.Timestamp("2020-02-15")) == 1600.0
    assert idx.as_of(pd.Timestamp("2020-02-01")) == 1600.0  # boundary is inclusive


def test_elo_as_of_is_nan_before_first_rating():
    starts = pd.to_datetime(["2020-01-01"]).to_numpy()
    idx = EloIndex(starts, np.array([1500.0]))
    assert math.isnan(idx.as_of(pd.Timestamp("2019-06-01")))
