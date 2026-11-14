"""Blind validation of the method against known analogues (leader-owned skeleton)."""
from __future__ import annotations

import pandas as pd


def run_blind_validation(
    scores_df: pd.DataFrame,
    earth_df: pd.DataFrame,
    known_analog_ids: list[str] | None = None,
    top_k: int = 5,
) -> pd.DataFrame:
    """Check that known analogues (role=validation) rank near the top, run blind.

    Args:
        scores_df: axis_scores output for one reference site.
        earth_df: Earth feature table (needed to filter role=validation rows).
        known_analog_ids: explicit analogue site_ids; defaults to role=validation rows.
        top_k: count an analogue as recovered when it ranks in the top k per axis.

    Returns:
        Per-analogue per-axis rank summary, plus an overall recovery rate.
    """
    raise NotImplementedError("v0 blind validation comes after the core pipeline works")
