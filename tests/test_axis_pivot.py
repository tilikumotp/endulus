"""Tests for axis_pivot (radar-chart-friendly wide table)."""
import numpy as np
import pandas as pd

from scoring.similarity import axis_pivot


def _scores() -> pd.DataFrame:
    return pd.DataFrame({
        "site_id": ["a", "a", "a", "b", "b", "b"],
        "axis": ["mobility", "thermal", "surface"] * 2,
        "score": [0.4, 0.6, 0.8, 0.2, np.nan, 0.5],
        "q05": [0.3, 0.5, 0.7, 0.1, np.nan, 0.4],
        "q95": [0.5, 0.7, 0.9, 0.3, np.nan, 0.6],
    })


def test_pivot_shape_and_columns() -> None:
    pivot = axis_pivot(_scores())
    assert len(pivot) == 2
    assert set(pivot.columns) == {
        "site_id",
        "score_mobility", "score_thermal", "score_surface",
        "q05_mobility", "q05_thermal", "q05_surface",
        "q95_mobility", "q95_thermal", "q95_surface",
    }


def test_pivot_preserves_values_and_nan() -> None:
    pivot = axis_pivot(_scores())
    a = pivot[pivot["site_id"] == "a"].iloc[0]
    assert a["score_thermal"] == 0.6
    assert a["q95_surface"] == 0.9
    b = pivot[pivot["site_id"] == "b"].iloc[0]
    assert np.isnan(b["score_thermal"])  # NaN axis stays NaN
    assert b["score_surface"] == 0.5
