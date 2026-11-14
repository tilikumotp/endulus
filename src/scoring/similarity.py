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
