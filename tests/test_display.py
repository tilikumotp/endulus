"""Tests for scoring.display (leader-owned)."""
import numpy as np
import pytest

from scoring.display import expanded_interval


def test_point_inside_interval_is_untouched() -> None:
    lo, hi, widened = expanded_interval(0.40, 0.21, 0.50)
    assert (lo, hi) == (0.21, 0.50)
    assert widened is False


def test_point_above_q95_widens_upper_bound() -> None:
    lo, hi, widened = expanded_interval(0.51, 0.21, 0.50)
    assert (lo, hi) == (0.21, 0.51)
    assert widened is True


def test_point_below_q05_widens_lower_bound() -> None:
    lo, hi, widened = expanded_interval(0.10, 0.21, 0.50)
    assert (lo, hi) == (0.10, 0.50)
    assert widened is True


def test_nonfinite_inputs_pass_through() -> None:
    # NaN score: interval is returned unchanged, nothing widened.
    lo, hi, widened = expanded_interval(float("nan"), 0.21, 0.50)
    assert (lo, hi) == (0.21, 0.50) and widened is False
    # NaN quantile: the missing bound propagates, no widening.
    lo, hi, widened = expanded_interval(0.4, float("nan"), 0.5)
    assert np.isnan(lo) and hi == 0.5 and widened is False


def test_never_moves_scored_values() -> None:
    """The helper is display-only; raw quantiles stay available upstream."""
    raw_lo, raw_hi = 0.21, 0.50
    lo, hi, _ = expanded_interval(0.51, raw_lo, raw_hi)
    assert raw_lo == 0.21 and raw_hi == 0.50  # inputs unchanged
    assert lo <= 0.51 <= hi
