"""Per-axis similarity scores with bootstrap uncertainty (leader-owned)."""
from __future__ import annotations

import numpy as np
import pandas as pd

from scoring.config import AXES

OUTPUT_COLS = ["site_id", "axis", "score", "ci_low", "ci_high", "n_features_used"]


def _axis_scores(
    axis: str,
    features: list[str],
    ref: pd.Series,
    cands: pd.DataFrame,
    n_boot: int,
    rng: np.random.Generator,
) -> pd.DataFrame:
    """Score one axis: standardized Euclidean distance, exp(-d), bootstrapped CI."""
    mean: dict[str, float] = {}
    std: dict[str, float] = {}
    for f in features:
        vals = pd.to_numeric(cands[f], errors="coerce").to_numpy(dtype=float)
        vals = vals[np.isfinite(vals)]
        mean[f] = float(np.mean(vals)) if vals.size else float("nan")
        std[f] = float(np.std(vals)) if vals.size else float("nan")

    rows: list[dict[str, float]] = []
    for i in range(len(cands)):
        used = [
            f for f in features
            if np.isfinite(mean[f]) and std[f] > 0.0
            and np.isfinite(pd.to_numeric(cands[f], errors="coerce").iat[i])
            and pd.notna(ref[f])
        ]
        if not used:
            rows.append({"score": np.nan, "ci_low": np.nan, "ci_high": np.nan,
                         "n_features_used": 0})
            continue
        cvals = np.array([float(cands[f].iat[i]) for f in used])
        rvals = np.array([float(ref[f]) for f in used])
        # NaN uncertainty means "unknown"; perturbing with 0 is the honest fallback.
        sd = np.array([float(ref[f"{f}_sd"]) if pd.notna(ref[f"{f}_sd"]) else 0.0
                       for f in used])
        sd = np.where(np.isfinite(sd), sd, 0.0)
        mu = np.array([mean[f] for f in used])
        sigma = np.array([std[f] for f in used])
        zc, zr = (cvals - mu) / sigma, (rvals - mu) / sigma
        point = float(np.exp(-float(np.sqrt(np.mean((zc - zr) ** 2)))))
        eps_c = rng.normal(0.0, sd, size=(n_boot, len(used)))
        eps_r = rng.normal(0.0, sd, size=(n_boot, len(used)))
        d_boot = np.sqrt(np.mean(
            (((cvals + eps_c) - mu) / sigma - ((rvals + eps_r) - mu) / sigma) ** 2, axis=1))
        ci_low, ci_high = np.percentile(np.exp(-d_boot), [5.0, 95.0])
        # The unperturbed point estimate can sit outside the perturbed percentile
        # band; clip so the contract invariant ci_low <= score <= ci_high always holds.
        ci_low, ci_high = min(ci_low, point), max(ci_high, point)
        rows.append({"score": point, "ci_low": float(ci_low), "ci_high": float(ci_high),
                     "n_features_used": len(used)})
    out = pd.DataFrame(rows)
    out.insert(0, "axis", axis)
    out.insert(0, "site_id", cands["site_id"].tolist())
    return out


def axis_scores(
    reference_row: pd.Series,
    candidates_df: pd.DataFrame,
    n_boot: int = 200,
    seed: int = 0,
) -> pd.DataFrame:
    """Score every candidate against one reference row, per axis, with a 5-95% CI."""
    missing = [c for feats in AXES.values() for c in feats if c not in candidates_df.columns]
    if missing:
        raise ValueError(f"candidates_df'te eksik kolonlar: {sorted(set(missing))}")
    rng = np.random.default_rng(seed)
    if candidates_df.empty:
        return pd.DataFrame(columns=OUTPUT_COLS)
    frames = [
        _axis_scores(axis, feats, reference_row, candidates_df, n_boot, rng)
        for axis, feats in AXES.items()
    ]
    out = pd.concat(frames, ignore_index=True)
    return out[OUTPUT_COLS]


def axis_pivot(scores_df: pd.DataFrame) -> pd.DataFrame:
    """Wide site x axis table (score/ci_low/ci_high per axis) for radar charts.

    Column names follow <stat>_<axis>, e.g. score_mobility; one row per site.
    NaN stays NaN when a site has no finite score for an axis.
    """
    pivot = scores_df.pivot(
        index="site_id", columns="axis", values=["score", "ci_low", "ci_high"]
    )
    pivot = pivot[sorted(pivot.columns)]
    pivot.columns = [f"{stat}_{axis}" for stat, axis in pivot.columns]
    return pivot.reset_index()


def combine_axes(
    scores_df: pd.DataFrame,
    axis_weights: dict[str, float] | None = None,
) -> pd.DataFrame:
    """Combine per-axis scores into one weighted score per site; NaN axes skipped.

    Axes missing from axis_weights default to weight 1.0; weight 0 excludes an
    axis. Cheap enough to call per mission change without re-running bootstraps.
    """
    if scores_df.empty:
        return pd.DataFrame(columns=["site_id", "score", "n_axes_used"])
    rows = []
    for sid in pd.unique(scores_df["site_id"]):
        grp = scores_df[scores_df["site_id"] == sid]
        w = grp["axis"].map(
            lambda a: float(axis_weights.get(a, 1.0)) if axis_weights else 1.0
        )
        valid = grp["score"].notna() & (w > 0.0)
        w_sum = float(w[valid].sum())
        if w_sum <= 0.0:
            rows.append({"site_id": sid, "score": np.nan, "n_axes_used": 0})
        else:
            rows.append({
                "site_id": sid,
                "score": float((grp["score"][valid] * w[valid]).sum() / w_sum),
                "n_axes_used": int(valid.sum()),
            })
    return pd.DataFrame(rows)[["site_id", "score", "n_axes_used"]]


def axis_gaps(reference_row: pd.Series, candidates_df: pd.DataFrame) -> pd.DataFrame:
    """Per-feature reference-vs-candidate comparison for the 'breakdown' card.

    One row per (site, feature) where both values are finite; diff is in the
    feature's native unit, z_diff is diff normalized by the candidate sd.
    """
    axis_of = {f: a for a, feats in AXES.items() for f in feats}
    feats = list(axis_of)
    cvals = candidates_df[feats].apply(pd.to_numeric, errors="coerce")
    rvals = pd.to_numeric(reference_row.reindex(feats), errors="coerce")
    stats: dict[str, tuple[float, float]] = {}
    for f in feats:
        vals = cvals[f].to_numpy(dtype=float)
        vals = vals[np.isfinite(vals)]
        stats[f] = (float(np.mean(vals)) if vals.size else float("nan"),
                    float(np.std(vals)) if vals.size else float("nan"))
    rows = []
    for i in range(len(candidates_df)):
        for f in feats:
            cv = float(cvals[f].iat[i]) if pd.notna(cvals[f].iat[i]) else float("nan")
            rv = float(rvals[f]) if pd.notna(rvals[f]) else float("nan")
            if not (np.isfinite(rv) and np.isfinite(cv)):
                continue
            mu, sigma = stats[f]
            rows.append({
                "site_id": candidates_df["site_id"].iat[i],
                "axis": axis_of[f],
                "feature": f,
                "ref_value": rv,
                "cand_value": cv,
                "diff": cv - rv,
                "z_diff": (cv - rv) / sigma if sigma > 0.0 else np.nan,
            })
    return pd.DataFrame(rows)[["site_id", "axis", "feature", "ref_value",
                               "cand_value", "diff", "z_diff"]]
