"""Tests for scoring.similarity on the committed mock data."""
from pathlib import Path

import pandas as pd

from scoring.similarity import axis_scores

ROOT = Path(__file__).resolve().parents[1]


def _load() -> tuple[pd.DataFrame, pd.DataFrame]:
    moon = pd.read_parquet(ROOT / "data" / "mock" / "features_moon.parquet")
    earth = pd.read_parquet(ROOT / "data" / "mock" / "features_earth.parquet")
    return moon, earth


def test_scores_in_unit_interval_and_ci_contains_point() -> None:
    moon, earth = _load()
    scores = axis_scores(moon.iloc[0], earth)
    assert scores["score"].between(0.0, 1.0).all()
    assert (scores["ci_low"] <= scores["score"]).all()
    assert (scores["score"] <= scores["ci_high"]).all()
    assert (scores["n_features_used"] > 0).all()


def test_same_seed_gives_identical_results() -> None:
    moon, earth = _load()
    a = axis_scores(moon.iloc[0], earth, n_boot=50, seed=7)
    b = axis_scores(moon.iloc[0], earth, n_boot=50, seed=7)
    pd.testing.assert_frame_equal(a, b)


def test_tuned_candidates_rank_top_per_axis() -> None:
    moon, earth = _load()
    scores = axis_scores(moon.iloc[0], earth)
    for axis in ("mobility", "thermal", "surface"):
        best = scores[scores["axis"] == axis].sort_values("score", ascending=False).iloc[0]
        assert str(best["site_id"]).startswith("mock_earth_similar"), (axis, best)


def test_nan_feature_is_skipped_and_reported() -> None:
    moon, earth = _load()
    scores = axis_scores(moon.iloc[0], earth)
    thermal = scores[scores["axis"] == "thermal"]
    nan_ti = earth[earth["thermal_inertia"].isna()]["site_id"]
    used = thermal[thermal["site_id"].isin(nan_ti)]["n_features_used"]
    assert (used == 1).all()  # temp_amplitude only
    assert (thermal[~thermal["site_id"].isin(nan_ti)]["n_features_used"] == 2).all()
