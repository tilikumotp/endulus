"""Minimal Earth-site portfolio selection (leader-owned)."""
from __future__ import annotations

import pandas as pd


def select_portfolio(
    scores_df: pd.DataFrame,
    min_score: float,
    axes: list[str] | None = None,
) -> tuple[list[str], list[str]]:
    """Greedy set cover; exact minimum site count when covering at most 3 axes.

    A site covers an axis when its score for that axis is >= min_score. Each
    round picks the site covering the most still-uncovered axes; ties break by
    total score over those axes, then by site_id (deterministic). With at most
    three axes, this greedy choice also minimizes the number of selected sites.
    For larger axis sets, it remains a heuristic. Stops when no site covers
    anything new.

    Args:
        scores_df: axis_scores output (site_id, axis, score, ...).
        min_score: coverage threshold for an axis.
        axes: axes to cover; defaults to every axis present in scores_df.

    Returns:
        (selected site_ids in pick order, axes still uncovered, sorted).
    """
    if axes is None:
        axes = sorted(set(scores_df["axis"].dropna()))
    remaining = set(axes)
    chosen: set[str] = set()
    selected: list[str] = []
    while remaining:
        candidates: list[tuple[str, list[str], float]] = []
        for sid in pd.unique(scores_df["site_id"]):
            if sid in chosen:
                continue
            grp = scores_df[scores_df["site_id"] == sid]
            sc = dict(zip(grp["axis"], grp["score"]))
            new = [a for a in sorted(remaining)
                   if pd.notna(sc.get(a)) and sc[a] >= min_score]
            if new:
                candidates.append((str(sid), new, sum(sc[a] for a in new)))
        if not candidates:
            break
        best_sid, best_new, _ = sorted(
            candidates, key=lambda t: (-len(t[1]), -t[2], t[0]))[0]
        selected.append(best_sid)
        chosen.add(best_sid)
        remaining -= set(best_new)
    return selected, sorted(remaining)
