"""Per-axis similarity scores with Monte Carlo uncertainty (leader-owned)."""
from __future__ import annotations

import hashlib

import numpy as np
import pandas as pd

from scoring.config import AXES

OUTPUT_COLS = ["site_id", "axis", "score", "q05", "q95", "n_features_used"]
DRAW_COLS = ["site_id", "axis", "draw", "score"]


def _as_float(value: object) -> float:
    """Convert a scalar to float, returning NaN when it is unavailable."""
    try:
        return float(value)
    except (TypeError, ValueError):
        return float("nan")


def _pool_stats(
    feature: str,
    reference_row: pd.Series,
    candidates_df: pd.DataFrame,
) -> tuple[float, float]:
    """Return population mean/std for candidates and the reference."""
    values = pd.to_numeric(candidates_df[feature], errors="coerce").to_numpy(
        dtype=float
    )
    values = values[np.isfinite(values)]
    ref_value = _as_float(reference_row.get(feature, np.nan))
    pool = np.append(values, ref_value) if np.isfinite(ref_value) else values
    if not pool.size:
        return float("nan"), float("nan")
    return float(np.mean(pool)), float(np.std(pool))


def _rng_for_site_axis(seed: int, axis: str, site_id: object) -> np.random.Generator:
    """Create a stable random stream independent of candidate row order."""
    digest = hashlib.blake2b(
        f"{axis}\0{site_id}".encode("utf-8"), digest_size=8
    ).digest()
    stable_id = int.from_bytes(digest, byteorder="little")
    seed_sequence = np.random.SeedSequence([
        seed,
        stable_id & 0xFFFFFFFF,
        stable_id >> 32,
    ])
    return np.random.default_rng(seed_sequence)


def _axis_scores(
    axis: str,
    features: list[str],
    reference_row: pd.Series,
    candidates_df: pd.DataFrame,
    n_draws: int,
    seed: int,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Score one axis with an uncapped RMS standardized distance."""
    stats = {
        feature: _pool_stats(feature, reference_row, candidates_df)
        for feature in features
    }
    summary_rows: list[dict[str, object]] = []
    sample_matrix = np.full((len(candidates_df), n_draws), np.nan, dtype=float)

    for i, (_, candidate) in enumerate(candidates_df.iterrows()):
        used = [
            feature for feature in features
            if np.isfinite(stats[feature][0])
            and stats[feature][1] > 0.0
            and np.isfinite(_as_float(candidate.get(feature, np.nan)))
            and np.isfinite(_as_float(reference_row.get(feature, np.nan)))
        ]
        if not used:
            summary_rows.append({
                "score": np.nan,
                "q05": np.nan,
                "q95": np.nan,
                "n_features_used": 0,
            })
            continue

        candidate_values = np.array(
            [_as_float(candidate[feature]) for feature in used], dtype=float
        )
        reference_values = np.array(
            [_as_float(reference_row[feature]) for feature in used], dtype=float
        )
        scales = np.array([stats[feature][1] for feature in used], dtype=float)
        delta = (candidate_values - reference_values) / scales
        point_score = float(np.exp(-np.sqrt(np.mean(delta ** 2))))

        candidate_sd = np.array([
            _as_float(candidate.get(f"{feature}_sd", np.nan))
            for feature in used
        ], dtype=float)
        reference_sd = np.array([
            _as_float(reference_row.get(f"{feature}_sd", np.nan))
            for feature in used
        ], dtype=float)
        if np.isinf(candidate_sd).any() or np.isinf(reference_sd).any():
            raise ValueError(
                f"Infinite uncertainty for candidate {candidate.get('site_id')!r} "
                f"on axis {axis!r}; use NaN when uncertainty is unknown"
            )
        if np.any(candidate_sd[np.isfinite(candidate_sd)] < 0.0):
            raise ValueError(
                f"Negative uncertainty for candidate {candidate.get('site_id')!r}"
            )
        if np.any(reference_sd[np.isfinite(reference_sd)] < 0.0):
            raise ValueError(
                f"Negative uncertainty for reference feature(s) on axis {axis!r}"
            )

        if np.isfinite(candidate_sd).all() and np.isfinite(reference_sd).all():
            rng = _rng_for_site_axis(
                seed, axis, candidate.get("site_id", i)
            )
            candidate_noise = rng.normal(
                0.0, candidate_sd, size=(n_draws, len(used))
            )
            reference_noise = rng.normal(
                0.0, reference_sd, size=(n_draws, len(used))
            )
            draw_delta = (
                candidate_values + candidate_noise
                - reference_values - reference_noise
            ) / scales
            draw_scores = np.exp(
                -np.sqrt(np.mean(draw_delta ** 2, axis=1))
            )
            sample_matrix[i] = draw_scores
            q05, q95 = np.percentile(draw_scores, [5.0, 95.0])
        else:
            q05 = q95 = np.nan

        summary_rows.append({
            "score": point_score,
            "q05": float(q05),
            "q95": float(q95),
            "n_features_used": len(used),
        })

    summary = pd.DataFrame(summary_rows)
    summary.insert(0, "axis", axis)
    summary.insert(0, "site_id", candidates_df["site_id"].tolist())
    draws = pd.DataFrame({
        "site_id": np.repeat(candidates_df["site_id"].to_numpy(), n_draws),
        "axis": axis,
        "draw": np.tile(np.arange(n_draws, dtype=int), len(candidates_df)),
        "score": sample_matrix.reshape(-1),
    })
    return summary, draws[DRAW_COLS]


def axis_scores_with_draws(
    reference_row: pd.Series,
    candidates_df: pd.DataFrame,
    n_boot: int = 200,
    seed: int = 0,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Return per-axis summaries and the Monte Carlo draws behind their quantiles.

    ``n_boot`` retains its historical name for call compatibility; these are
    independent Gaussian uncertainty-propagation draws, not bootstrap samples.
    """
    if not isinstance(n_boot, int) or n_boot <= 0:
        raise ValueError("n_boot must be a positive integer")
    if not isinstance(seed, int) or seed < 0:
        raise ValueError("seed must be a non-negative integer")
    missing = [
        feature for features in AXES.values() for feature in features
        if feature not in candidates_df.columns
    ]
    if missing:
        raise ValueError(
            f"candidates_df'te eksik kolonlar: {sorted(set(missing))}"
        )
    if candidates_df.empty:
        return (
            pd.DataFrame(columns=OUTPUT_COLS),
            pd.DataFrame(columns=DRAW_COLS),
        )

    summaries: list[pd.DataFrame] = []
    draws: list[pd.DataFrame] = []
    for axis, features in AXES.items():
        axis_summary, axis_draws = _axis_scores(
            axis, features, reference_row, candidates_df, n_boot, seed
        )
        summaries.append(axis_summary)
        draws.append(axis_draws)
    return (
        pd.concat(summaries, ignore_index=True)[OUTPUT_COLS],
        pd.concat(draws, ignore_index=True)[DRAW_COLS],
    )


def axis_scores(
    reference_row: pd.Series,
    candidates_df: pd.DataFrame,
    n_boot: int = 200,
    seed: int = 0,
) -> pd.DataFrame:
    """Score candidates by axis, returning 5th/95th Monte Carlo percentiles."""
    scores, _ = axis_scores_with_draws(
        reference_row, candidates_df, n_boot=n_boot, seed=seed
    )
    return scores


def axis_pivot(scores_df: pd.DataFrame) -> pd.DataFrame:
    """Wide site x axis table (score/q05/q95 per axis) for radar charts."""
    pivot = scores_df.pivot(
        index="site_id", columns="axis", values=["score", "q05", "q95"]
    )
    pivot = pivot[sorted(pivot.columns)]
    pivot.columns = [f"{stat}_{axis}" for stat, axis in pivot.columns]
    return pivot.reset_index()


def _validated_weights(
    axis_weights: dict[str, float] | None,
    axes: pd.Series,
) -> pd.Series:
    """Map axes to finite non-negative weights; unspecified axes default to 1."""
    weights = axes.map(
        lambda axis: float(axis_weights.get(axis, 1.0))
        if axis_weights else 1.0
    )
    if not np.isfinite(weights.to_numpy(dtype=float)).all():
        raise ValueError("Axis weights must be finite numbers")
    if (weights < 0.0).any():
        raise ValueError("Axis weights must be non-negative")
    return weights


def combine_axes(
    scores_df: pd.DataFrame,
    axis_weights: dict[str, float] | None = None,
) -> pd.DataFrame:
    """Combine point scores with a weighted mean; unavailable axes are skipped.

    Axes missing from ``axis_weights`` default to weight 1.0; weight 0 excludes
    an axis. Use :func:`combine_axes_with_uncertainty` for total-score ranges.
    """
    if scores_df.empty:
        return pd.DataFrame(columns=["site_id", "score", "n_axes_used"])
    rows = []
    for site_id in pd.unique(scores_df["site_id"]):
        group = scores_df[scores_df["site_id"] == site_id]
        weights = _validated_weights(axis_weights, group["axis"])
        valid = group["score"].notna() & (weights > 0.0)
        weight_sum = float(weights[valid].sum())
        if weight_sum <= 0.0:
            rows.append({"site_id": site_id, "score": np.nan, "n_axes_used": 0})
        else:
            rows.append({
                "site_id": site_id,
                "score": float(
                    (group.loc[valid, "score"] * weights[valid]).sum()
                    / weight_sum
                ),
                "n_axes_used": int(valid.sum()),
            })
    return pd.DataFrame(rows)[["site_id", "score", "n_axes_used"]]


def combine_axes_with_uncertainty(
    scores_df: pd.DataFrame,
    draws_df: pd.DataFrame,
    axis_weights: dict[str, float] | None = None,
) -> pd.DataFrame:
    """Combine aligned axis draws and return 5th/95th total-score percentiles.

    A total interval is unavailable if any positively weighted, scoreable axis
    lacks complete uncertainty draws. This avoids treating unknown SD as zero.
    """
    combined = combine_axes(scores_df, axis_weights)
    combined["q05"] = np.nan
    combined["q95"] = np.nan
    if scores_df.empty or draws_df.empty:
        return combined[["site_id", "score", "n_axes_used", "q05", "q95"]]

    for row_index, site_id in enumerate(combined["site_id"]):
        group = scores_df[scores_df["site_id"] == site_id]
        weights = _validated_weights(axis_weights, group["axis"])
        valid = group["score"].notna() & (weights > 0.0)
        if not valid.any():
            continue
        required_axes = group.loc[valid, "axis"].tolist()
        axis_weights_used = weights[valid].to_numpy(dtype=float)
        site_draws = draws_df[
            (draws_df["site_id"] == site_id)
            & draws_df["axis"].isin(required_axes)
        ]
        if site_draws.empty:
            continue
        draw_scores = site_draws.pivot(
            index="draw", columns="axis", values="score"
        ).reindex(columns=required_axes)
        values = draw_scores.to_numpy(dtype=float)
        if values.size == 0 or not np.isfinite(values).all():
            continue
        total_draws = np.average(
            values, axis=1, weights=axis_weights_used
        )
        q05, q95 = np.percentile(total_draws, [5.0, 95.0])
        combined.loc[row_index, "q05"] = float(q05)
        combined.loc[row_index, "q95"] = float(q95)
    return combined[["site_id", "score", "n_axes_used", "q05", "q95"]]


def axis_gaps(
    reference_row: pd.Series,
    candidates_df: pd.DataFrame,
) -> pd.DataFrame:
    """Compare raw feature differences and their uncapped standardized values."""
    axis_of = {feature: axis for axis, features in AXES.items()
               for feature in features}
    features = list(axis_of)
    candidate_values = candidates_df[features].apply(
        pd.to_numeric, errors="coerce"
    )
    reference_values = pd.to_numeric(
        reference_row.reindex(features), errors="coerce"
    )
    stats = {
        feature: _pool_stats(feature, reference_row, candidates_df)
        for feature in features
    }
    rows = []
    for i in range(len(candidates_df)):
        for feature in features:
            candidate_value = _as_float(candidate_values[feature].iat[i])
            reference_value = _as_float(reference_values[feature])
            if not (np.isfinite(reference_value) and np.isfinite(candidate_value)):
                continue
            _, scale = stats[feature]
            z_diff = (
                (candidate_value - reference_value) / scale
                if scale > 0.0 else np.nan
            )
            rows.append({
                "site_id": candidates_df["site_id"].iat[i],
                "axis": axis_of[feature],
                "feature": feature,
                "ref_value": reference_value,
                "cand_value": candidate_value,
                "diff": candidate_value - reference_value,
                "z_diff": float(z_diff) if np.isfinite(z_diff) else np.nan,
            })
    return pd.DataFrame(rows)[[
        "site_id", "axis", "feature", "ref_value", "cand_value", "diff",
        "z_diff",
    ]]
