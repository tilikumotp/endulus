"""Tests for axis_gaps (breakdown-card data)."""
import numpy as np
import pandas as pd

from scoring.similarity import axis_gaps


def _frame() -> tuple[pd.Series, pd.DataFrame]:
    ref = pd.Series({
        "slope_mean": 10.0, "slope_p90": 20.0, "roughness": 5.0, "relief": 100.0,
        "temp_amplitude": 200.0, "thermal_inertia": 1000.0, "albedo": 0.2,
        "slope_mean_sd": 1.0,
    })
    cands = pd.DataFrame({
        "site_id": ["x", "y"],
        "slope_mean": [10.5, np.nan],
        "slope_p90": [30.0, 20.0],
        "roughness": [5.0, 5.0],
        "relief": [100.0, 300.0],
        "temp_amplitude": [np.nan, 200.0],
        "thermal_inertia": [np.nan, np.nan],
        "albedo": [0.3, 0.1],
    })
    return ref, cands


def test_one_row_per_finite_pair() -> None:
    ref, cands = _frame()
    gaps = axis_gaps(ref, cands)
    x = gaps[gaps["site_id"] == "x"]
    assert set(x["feature"]) == {"slope_mean", "slope_p90", "roughness", "relief", "albedo"}
    assert "thermal_inertia" not in set(gaps["feature"])  # all NaN for both sites
    assert "temp_amplitude" not in set(x["feature"])  # ref... cand NaN pair skipped


def test_diff_and_z_diff_values() -> None:
    ref, cands = _frame()
    gaps = axis_gaps(ref, cands)
    sm = gaps[(gaps["site_id"] == "x") & (gaps["feature"] == "slope_mean")]
    assert abs(sm["diff"].iat[0] - 0.5) < 1e-12
    # NaN in y's slope_mean filters it out -> single value -> sd 0 -> z NaN
    assert np.isnan(sm["z_diff"].iat[0])
    sp = gaps[(gaps["site_id"] == "x") & (gaps["feature"] == "slope_p90")]
    # population sd of [30.0, 20.0] is 5.0; diff 10.0
    assert abs(sp["diff"].iat[0] - 10.0) < 1e-12
    assert abs(sp["z_diff"].iat[0] - 10.0 / 5.0) < 1e-12
    # identical values give diff 0
    ro = gaps[(gaps["site_id"] == "x") & (gaps["feature"] == "roughness")]
    assert ro["diff"].iat[0] == 0.0


def test_axis_column_mapped() -> None:
    ref, cands = _frame()
    gaps = axis_gaps(ref, cands)
    assert (gaps[gaps["feature"] == "albedo"]["axis"] == "surface").all()
    assert (gaps[gaps["feature"] == "relief"]["axis"] == "mobility").all()
