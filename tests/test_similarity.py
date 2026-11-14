"""Tests for scoring.similarity on the committed processed datasets and unit fixtures."""
from pathlib import Path

import numpy as np
import pandas as pd

from scoring.similarity import (
    axis_gaps,
    axis_scores,
    axis_scores_with_draws,
    combine_axes_with_uncertainty,
)

ROOT = Path(__file__).resolve().parents[1]


def _load() -> tuple[pd.DataFrame, pd.DataFrame]:
    moon = pd.read_parquet(ROOT / "data" / "processed" / "features_moon.parquet")
    earth = pd.read_parquet(ROOT / "data" / "processed" / "features_earth.parquet")
    return moon, earth


def test_scores_and_monte_carlo_quantiles_are_valid() -> None:
    moon, earth = _load()
    scores = axis_scores(moon.iloc[0], earth)
    active = scores[scores["axis"] != "thermal"]
    assert active["score"].between(0.0, 1.0).all()
    assert active["q05"].notna().all()
    assert (active["q05"] <= active["q95"]).all()
    assert (active["n_features_used"] > 0).all()

    # Leader Decision #30: Moon thermal features are NaN in v1 -> suspended axis.
    thermal = scores[scores["axis"] == "thermal"]
    assert (thermal["n_features_used"] == 0).all()
    assert thermal["score"].isna().all()
    assert thermal["q05"].isna().all() and thermal["q95"].isna().all()


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
    assert (thermal["n_features_used"] == 0).all()

    # When only thermal_inertia is NaN on a finite-temp reference, thermal uses 1 feature.
    ref_with_temp = moon.iloc[0].copy()
    ref_with_temp["temp_amplitude"] = 120.0
    ref_with_temp["temp_amplitude_sd"] = 3.0
    scores_temp = axis_scores(ref_with_temp, earth)
    thermal_temp = scores_temp[scores_temp["axis"] == "thermal"]
    nan_ti = earth[earth["thermal_inertia"].isna()]["site_id"]
    used = thermal_temp[thermal_temp["site_id"].isin(nan_ti)]["n_features_used"]
    assert (used == 1).all()  # temp_amplitude only when thermal_inertia is NaN


def test_componentwise_z_clipping_can_reverse_multifeature_rank() -> None:
    """The uncapped distance keeps the nearest candidate first."""
    rng = np.random.default_rng(42)
    for _ in range(7):
        values = rng.normal(size=(20, 2))
        values *= 10 ** rng.uniform(-0.2, 1.0, size=(20, 2))
        reference_values = (
            rng.normal(size=2) * 10 ** rng.uniform(-0.2, 1.0, size=2)
        )
    ref = pd.Series({
        "site_id": "ref", "slope_mean": reference_values[0],
        "slope_p90": reference_values[1],
    })
    cands = pd.DataFrame({
        "site_id": [f"c{i:02d}" for i in range(len(values))],
        "slope_mean": values[:, 0],
        "slope_p90": values[:, 1],
        "roughness": np.nan, "relief": np.nan,
        "temp_amplitude": np.nan, "thermal_inertia": np.nan, "albedo": np.nan,
        "slope_mean_sd": 0.0, "slope_p90_sd": 0.0,
    })
    scores = axis_scores(ref, cands, n_boot=10, seed=1)
    mobility = scores[scores["axis"] == "mobility"].set_index("site_id")

    raw_distances = {}
    capped_distances = {}
    for site_id in ("c05", "c18"):
        candidate = cands[cands["site_id"] == site_id].iloc[0]
        raw_z = []
        capped_z = []
        for feature in ("slope_mean", "slope_p90"):
            pool = np.append(cands[feature].to_numpy(), ref[feature])
            mean, scale = float(np.mean(pool)), float(np.std(pool))
            candidate_z = (candidate[feature] - mean) / scale
            reference_z = (ref[feature] - mean) / scale
            raw_z.append(candidate_z - reference_z)
            capped_z.append(
                np.clip(candidate_z, -3.0, 3.0)
                - np.clip(reference_z, -3.0, 3.0)
            )
        raw_distances[site_id] = float(np.sqrt(np.mean(np.square(raw_z))))
        capped_distances[site_id] = float(np.sqrt(np.mean(np.square(capped_z))))

    assert raw_distances["c05"] < raw_distances["c18"]
    assert capped_distances["c18"] < capped_distances["c05"]
    assert mobility.loc["c05", "score"] > mobility.loc["c18", "score"]


def test_axis_gaps_match_uncapped_score_distance() -> None:
    moon, earth = _load()
    scores = axis_scores(moon.iloc[0], earth)
    gaps = axis_gaps(moon.iloc[0], earth)
    assert (gaps["z_diff"].abs() > 3.0).any()
    for row in scores.itertuples(index=False):
        used = gaps[
            (gaps["site_id"] == row.site_id) & (gaps["axis"] == row.axis)
        ]["z_diff"].dropna()
        if not used.empty:
            expected = float(np.exp(-np.sqrt(np.mean(used.to_numpy() ** 2))))
            assert np.isclose(row.score, expected)


def test_draws_are_independent_of_candidate_row_order() -> None:
    moon, earth = _load()
    scores_a, draws_a = axis_scores_with_draws(
        moon.iloc[0], earth, n_boot=50, seed=7
    )
    scores_b, draws_b = axis_scores_with_draws(
        moon.iloc[0], earth.sample(frac=1.0, random_state=5),
        n_boot=50, seed=7,
    )
    pd.testing.assert_frame_equal(
        scores_a.sort_values(["site_id", "axis"]).reset_index(drop=True),
        scores_b.sort_values(["site_id", "axis"]).reset_index(drop=True),
    )
    pd.testing.assert_frame_equal(
        draws_a.sort_values(["site_id", "axis", "draw"]).reset_index(drop=True),
        draws_b.sort_values(["site_id", "axis", "draw"]).reset_index(drop=True),
    )


def test_uncertainty_draws_use_candidate_sd() -> None:
    """Candidate and reference uncertainties both contribute to draws."""
    ref = pd.Series({
        "site_id": "ref", "name": "ref", "body": "moon", "role": "reference",
        "lat": 0.0, "lon": 0.0, "radius_m": 1000.0,
        "slope_mean": 5.0, "slope_mean_sd": 0.0, "slope_p90": 10.0,
        "slope_p90_sd": 0.0, "roughness": 5.0, "roughness_sd": 0.0,
        "relief": 50.0, "relief_sd": 0.0, "temp_amplitude": 20.0,
        "temp_amplitude_sd": 0.0, "thermal_inertia": float("nan"),
        "albedo": float("nan"),
    })
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
    assert ((thermal["q95"] - thermal["q05"]) > 0.05).all()


def test_unknown_feature_sd_leaves_interval_unavailable() -> None:
    ref = pd.Series({
        "site_id": "ref", "temp_amplitude": 20.0,
        "temp_amplitude_sd": float("nan"),
    })
    cands = pd.DataFrame({
        "site_id": ["a"],
        "slope_mean": [np.nan], "slope_p90": [np.nan],
        "roughness": [np.nan], "relief": [np.nan],
        "temp_amplitude": [18.0], "temp_amplitude_sd": [5.0],
        "thermal_inertia": [np.nan], "albedo": [np.nan],
    })
    scores, draws = axis_scores_with_draws(ref, cands, n_boot=20)
    thermal = scores[scores["axis"] == "thermal"].iloc[0]
    assert np.isfinite(thermal["score"])
    assert np.isnan(thermal["q05"])
    assert np.isnan(thermal["q95"])
    assert draws.loc[draws["axis"] == "thermal", "score"].isna().all()

    overall = combine_axes_with_uncertainty(scores, draws)
    assert np.isfinite(overall.iloc[0]["score"])
    assert np.isnan(overall.iloc[0]["q05"])
    assert np.isnan(overall.iloc[0]["q95"])


def test_negative_feature_sd_is_rejected() -> None:
    ref = pd.Series({
        "site_id": "ref", "temp_amplitude": 20.0,
        "temp_amplitude_sd": 1.0,
    })
    cands = pd.DataFrame({
        "site_id": ["a"],
        "slope_mean": [np.nan], "slope_p90": [np.nan],
        "roughness": [np.nan], "relief": [np.nan],
        "temp_amplitude": [18.0], "temp_amplitude_sd": [-1.0],
        "thermal_inertia": [np.nan], "albedo": [np.nan],
    })
    try:
        axis_scores(ref, cands)
    except ValueError as exc:
        assert "Negative uncertainty" in str(exc)
    else:
        raise AssertionError("negative feature SD should be rejected")
