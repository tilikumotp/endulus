"""Minimal Earth-site portfolio selection (leader-owned skeleton, v0 pending)."""
from __future__ import annotations

import pandas as pd


def select_portfolio(
    scores_df: pd.DataFrame,
    min_score: float,
    axes: list[str] | None = None,
) -> tuple[list[str], list[str]]:
    """Pick the smallest set of Earth sites covering the most axes above min_score.

    Args:
        scores_df: axis_scores output (site_id, axis, score, ...).
        min_score: an axis counts as covered by a site when its score >= min_score.
        axes: axes to cover; defaults to every axis present in scores_df.

    Returns:
        (selected site_ids in pick order, axes still uncovered).
    """
    raise NotImplementedError("v0 greedy selection comes after the core pipeline works")
