"""Tests for scoring.similarity on the committed processed datasets and unit fixtures."""
from pathlib import Path

import numpy as np
import pandas as pd

from scoring.similarity import axis_scores

ROOT = Path(__file__).resolve().parents[1]


def _load() -> tuple[pd.DataFrame, pd.DataFrame]:
    moon = pd.read_parquet(ROOT / "data" / "processed" / "features_moon.parquet")
    earth = pd.read_parquet(ROOT / "data" / "processed" / "features_earth.parquet")
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
    ref = pd.Series({
        "site_id": "ref", "name": "ref", "body": "moon", "role": "reference",
        "lat": -89.8, "lon": 0.0, "radius_m": 1000.0,
        "slope_mean": 10.0, "slope_mean_sd": 0.5,
        "slope_p90": 18.0, "slope_p90_sd": 0.5,
        "roughness": 20.0, "roughness_sd": 0.5,
        "relief": 150.0, "relief_sd": 1.0,
        "temp_amplitude": 30.0, "temp_amplitude_sd": 1.0,
        "thermal_inertia": float("nan"), "thermal_inertia_sd": float("nan"),
        "albedo": 0.14, "albedo_sd": 0.005,
    })
    cands = pd.DataFrame([
        {
            "site_id": "near_match", "name": "near_match", "body": "earth", "role": "validation",
            "lat": 0.0, "lon": 0.0, "radius_m": 1000.0,
            "slope_mean": 10.2, "slope_mean_sd": 0.5,
            "slope_p90": 18.1, "slope_p90_sd": 0.5,
            "roughness": 20.5, "roughness_sd": 0.5,
            "relief": 152.0, "relief_sd": 1.0,
            "temp_amplitude": 29.5, "temp_amplitude_sd": 1.0,
            "thermal_inertia": float("nan"), "thermal_inertia_sd": float("nan"),
            "albedo": 0.141, "albedo_sd": 0.005,
        },
        {
            "site_id": "far_mismatch", "name": "far_mismatch", "body": "earth", "role": "candidate",
            "lat": 10.0, "lon": 10.0, "radius_m": 1000.0,
            "slope_mean": 28.0, "slope_mean_sd": 0.5,
            "slope_p90": 45.0, "slope_p90_sd": 0.5,
            "roughness": 95.0, "roughness_sd": 0.5,
            "relief": 600.0, "relief_sd": 1.0,
            "temp_amplitude": 5.0, "temp_amplitude_sd": 1.0,
            "thermal_inertia": float("nan"), "thermal_inertia_sd": float("nan"),
            "albedo": 0.35, "albedo_sd": 0.005,
        },
    ])
    scores = axis_scores(ref, cands)
    for axis in ("mobility", "thermal", "surface"):
        best = scores[scores["axis"] == axis].sort_values("score", ascending=False).iloc[0]
        assert str(best["site_id"]) == "near_match", (axis, best)


def test_nan_feature_is_skipped_and_reported() -> None:
    moon, earth = _load()
    scores = axis_scores(moon.iloc[0], earth)
    thermal = scores[scores["axis"] == "thermal"]
    nan_ti = earth[earth["thermal_inertia"].isna()]["site_id"]
    used = thermal[thermal["site_id"].isin(nan_ti)]["n_features_used"]
    assert (used == 1).all()  # temp_amplitude only when thermal_inertia is NaN


def test_reference_far_outside_pool_does_not_collapse_scores() -> None:
    """Regression: candidates-only sigma gave exp(-22) ~ 1e-10 thermal scores.

    With the reference pooled into the standardization and the +-3 sigma z-cap,
    |zc - zr| <= 6 by construction, so scores are bounded below by exp(-6) at
    ANY pool size and stay strictly ordered in the candidate value.
    """
    moon, earth = _load()
    scores = axis_scores(moon.iloc[0], earth)
    thermal = scores[scores["axis"] == "thermal"].merge(
        earth[["site_id", "temp_amplitude"]], on="site_id"
    )
    assert (thermal["score"] >= float(np.exp(-6.0))).all(), thermal["score"].tolist()
    ordered = thermal.sort_values("temp_amplitude")["score"].to_numpy()
    assert np.all(np.diff(ordered) > 0), ordered


def test_scores_stable_as_candidate_pool_grows() -> None:
    """Regression: pooled z of a far-out reference grows ~ sqrt(k+1) with the
    pool size (k=4 -> z 2.3, k=28 -> z 5.4), so without the +-3 z-cap scores
    re-collapse once the grid expands. The cap must keep them bounded and
    monotone in the candidate value, at ANY pool size.
    """
    ref = {
        "site_id": "ref", "name": "ref", "body": "moon", "role": "reference",
        "lat": 0.0, "lon": 0.0, "radius_m": 1000.0,
        "slope_mean": 5.0, "slope_mean_sd": 1.0, "slope_p90": 10.0,
        "slope_p90_sd": 1.0, "roughness": 5.0, "roughness_sd": 1.0,
        "relief": 50.0, "relief_sd": 5.0, "temp_amplitude": 227.0,
        "temp_amplitude_sd": 5.0, "thermal_inertia": float("nan"),
        "albedo": float("nan"),
    }

    def _cands(n: int) -> pd.DataFrame:
        rows = []
        temps = np.linspace(5.0, 25.0, n)
        for i, temp in enumerate(temps):
            rows.append({
                "site_id": f"c{i:02d}", "name": f"c{i}", "body": "earth",
                "role": "candidate", "lat": 0.0, "lon": 0.1 * i,
                "radius_m": 1000.0,
                "slope_mean": 5.0, "slope_p90": 10.0, "roughness": 5.0,
                "relief": 50.0, "temp_amplitude": float(temp),
                "temp_amplitude_sd": 1.0, "thermal_inertia": float("nan"),
                "albedo": float("nan"),
            })
        return pd.DataFrame(rows)

    for n in (4, 28, 60):
        scores = axis_scores(ref, _cands(n), n_boot=50, seed=0)
        thermal = scores[scores["axis"] == "thermal"].sort_values("score")
        s = thermal["score"].to_numpy()
        assert (s > 0.02).all(), (n, s)          # no re-collapse at scale
        assert np.all(np.diff(s) > 0), (n, s)    # ordering strictly preserved


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
