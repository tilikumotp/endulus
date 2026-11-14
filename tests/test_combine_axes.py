"""Tests for combine_axes mission weighting (no RNG involved)."""
import numpy as np
import pandas as pd

from scoring.similarity import combine_axes


def _scores() -> pd.DataFrame:
    return pd.DataFrame({
        "site_id": ["a"] * 3 + ["b"] * 3,
        "axis": ["mobility", "thermal", "surface"] * 2,
        "score": [0.4, 0.6, 0.8, 0.2, np.nan, 0.5],
    })


def test_equal_weights_give_plain_mean() -> None:
    out = combine_axes(_scores())
    a = out[out["site_id"] == "a"].iloc[0]
    assert abs(a["score"] - (0.4 + 0.6 + 0.8) / 3) < 1e-12
    assert a["n_axes_used"] == 3
    b = out[out["site_id"] == "b"].iloc[0]
    assert abs(b["score"] - (0.2 + 0.5) / 2) < 1e-12  # NaN thermal skipped
    assert b["n_axes_used"] == 2


def test_zero_weight_excludes_axis() -> None:
    out = combine_axes(_scores(), {"mobility": 0.0, "thermal": 1.0, "surface": 1.0})
    a = out[out["site_id"] == "a"].iloc[0]
    assert abs(a["score"] - (0.6 + 0.8) / 2) < 1e-12
    assert a["n_axes_used"] == 2


def test_partial_weight_dict_defaults_to_one() -> None:
    out = combine_axes(_scores(), {"mobility": 2.0})
    a = out[out["site_id"] == "a"].iloc[0]
    assert abs(a["score"] - (0.4 * 2 + 0.6 + 0.8) / 4) < 1e-12


def test_all_weights_zero_gives_nan() -> None:
    out = combine_axes(_scores(), {"mobility": 0.0, "thermal": 0.0, "surface": 0.0})
    assert out["score"].isna().all()
    assert (out["n_axes_used"] == 0).all()


def test_mission_presets_change_ranking() -> None:
    from scoring.config import MISSION_PRESETS

    scores = pd.DataFrame({
        "site_id": ["flat"] * 3 + ["cold"] * 3,
        "axis": ["mobility", "thermal", "surface"] * 2,
        "score": [0.9, 0.3, 0.5, 0.1, 0.9, 0.5],
    })
    rover = combine_axes(scores, MISSION_PRESETS["rover_mobility"])
    isru = combine_axes(scores, MISSION_PRESETS["isru_ice"])
    assert rover.iloc[0]["site_id"] == "flat"
    assert rover.sort_values("score", ascending=False).iloc[0]["site_id"] == "flat"
    assert isru.sort_values("score", ascending=False).iloc[0]["site_id"] == "cold"
