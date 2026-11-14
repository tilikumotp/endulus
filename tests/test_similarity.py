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


def test_reference_far_outside_pool_does_not_collapse_scores() -> None:
    """Regression: candidates-only sigma gave exp(-22) ~ 1e-10 thermal scores.

    With the reference pooled into the standardization, z saturates near
    sqrt((k+1)/k) and scores stay in a usable range.
    """
    moon, earth = _load()
    scores = axis_scores(moon.iloc[0], earth)
    thermal = scores[scores["axis"] == "thermal"]["score"]
    assert (thermal > 0.05).all(), thermal.tolist()


def test_bootstrap_uses_candidate_sd() -> None:
    """Regression: candidate noise used the reference's sd (line 44 bug).

    A wide candidate *_sd with a zero-ref sd must still widen the CI.
    """
    ref = {
        "site_id": "ref", "name": "ref", "body": "moon", "role": "reference",
        "lat": 0.0, "lon": 0.0, "radius_m": 1000.0,
        "slope_mean": 5.0, "slope_mean_sd": 0.0, "slope_p90": 10.0,
        "slope_p90_sd": 0.0, "roughness": 5.0, "roughness_sd": 0.0,
        "relief": 50.0, "relief_sd": 0.0, "temp_amplitude": 20.0,
        "temp_amplitude_sd": float("nan"), "thermal_inertia": float("nan"),
        "albedo": float("nan"),
    }
    rows = []
    for sid, temp in (("a", 18.0), ("b", 22.0)):
        rows.append({
            "site_id": sid, "name": sid, "body": "earth", "role": "candidate",
            "lat": 0.0, "lon": 1.0, "radius_m": 1000.0,
            "slope_mean": 5.0, "slope_p90": 10.0, "roughness": 5.0,
            "relief": 50.0, "temp_amplitude": temp,
            "temp_amplitude_sd": 5.0, "thermal_inertia": float("nan"),
            "albedo": float("nan"),
        })
    cands = pd.DataFrame(rows)
    scores = axis_scores(ref, cands, n_boot=200, seed=0)
    thermal = scores[scores["axis"] == "thermal"]
    assert thermal["score"].notna().all()
    assert ((thermal["ci_high"] - thermal["ci_low"]) > 0.05).all()
