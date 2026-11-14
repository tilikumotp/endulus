"""Descriptive blind top-k ranking diagnostics (leader-owned)."""
from __future__ import annotations

import numpy as np
import pandas as pd


def run_blind_validation(
    scores_df: pd.DataFrame,
    earth_df: pd.DataFrame,
    known_analog_ids: list[str] | None = None,
    top_k: int = 5,
) -> pd.DataFrame:
    """Rank validation sites per axis without exposing role labels to scoring.

    The scoring itself never sees roles; validation only reads the ranking
    afterwards. Every selected validation site is compared against every
    axis, so the result is descriptive unless expected site-axis pairs were
    defined from evidence before examining the rankings. An analogue counts
    as top-k for an axis when its rank among all scored sites is <= top_k.

    Args:
        scores_df: axis_scores output for one reference site.
        earth_df: Earth feature table; its role=validation rows are the default
            diagnostic set when known_analog_ids is None.
        known_analog_ids: explicit analogue site_ids (overrides the default).
        top_k: recovery threshold on the rank.

    Returns:
        Per (analogue, axis) rows: rank (NaN when the site has no finite score
        for that axis), n_sites ranked, in_top_k flag.
    """
    if known_analog_ids is None:
        if "role" not in earth_df.columns:
            raise ValueError("earth_df'te role kolonu yok; known_analog_ids ver")
        known_analog_ids = earth_df[earth_df["role"] == "validation"]["site_id"].tolist()
    rows = []
    for axis in sorted(set(scores_df["axis"].dropna())):
        sub = scores_df[scores_df["axis"] == axis].dropna(subset=["score"])
        order = sub.sort_values("score", ascending=False)
        rank_of = {sid: i + 1 for i, sid in enumerate(order["site_id"])}
        for sid in known_analog_ids:
            rank = rank_of.get(sid, np.nan)
            rows.append({
                "site_id": sid,
                "axis": axis,
                "rank": rank,
                "n_sites": len(order),
                "in_top_k": bool(pd.notna(rank) and rank <= top_k),
            })
    return pd.DataFrame(rows)[["site_id", "axis", "rank", "n_sites", "in_top_k"]]
