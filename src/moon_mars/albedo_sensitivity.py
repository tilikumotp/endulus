"""Sensitivity analysis of the LOLA 1064 nm normal-to-broadband solar hemispherical albedo factor."""
from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.stats import spearmanr

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
SRC_DIR = REPO_ROOT / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from scoring.similarity import axis_scores, combine_axes  # noqa: E402

NOMINAL_FACTOR = 0.38
FACTORS = [0.30, 0.34, 0.38, 0.42, 0.46]

MOON_PARQUET = REPO_ROOT / "data" / "processed" / "features_moon.parquet"
EARTH_PARQUET = REPO_ROOT / "data" / "processed" / "features_earth.parquet"


def _evaluate_factor(
    ref_row: pd.Series,
    earth_df: pd.DataFrame,
    factor: float,
    n_boot: int = 100,
    seed: int = 42,
) -> tuple[float, pd.Series, pd.Series]:
    """Return (scaled_moon_albedo, surface_scores_series, overall_scores_series) for one factor."""
    scaled_row = ref_row.copy()
    scale_ratio = float(factor) / NOMINAL_FACTOR
    scaled_albedo = float(ref_row["albedo"]) * scale_ratio
    scaled_albedo_sd = float(ref_row["albedo_sd"]) * scale_ratio
    scaled_row["albedo"] = scaled_albedo
    scaled_row["albedo_sd"] = scaled_albedo_sd

    sc_df = axis_scores(scaled_row, earth_df, n_boot=n_boot, seed=seed)
    surf_df = sc_df[sc_df["axis"] == "surface"].set_index("site_id")["score"]
    ov_df = combine_axes(sc_df).set_index("site_id")["score"]
    return scaled_albedo, surf_df, ov_df


def run_albedo_sensitivity(
    moon_df: pd.DataFrame,
    earth_df: pd.DataFrame,
    factors: list[float] | None = None,
    n_boot: int = 100,
    seed: int = 42,
) -> pd.DataFrame:
    """Evaluate surface score shifts, overall score shifts, and rank stability across albedo factors."""
    active_factors = list(factors) if factors is not None else list(FACTORS)
    cand_ids = set(earth_df.loc[earth_df["role"] == "candidate", "site_id"].tolist())
    rows: list[dict[str, object]] = []

    for _, ref_row in moon_df.iterrows():
        ref_id = str(ref_row["site_id"])
        _, nom_surf, nom_ov = _evaluate_factor(ref_row, earth_df, NOMINAL_FACTOR, n_boot=n_boot, seed=seed)

        for factor in active_factors:
            scaled_alb, cur_surf, cur_ov = _evaluate_factor(
                ref_row, earth_df, float(factor), n_boot=n_boot, seed=seed
            )
            surf_delta = float(np.nanmean(np.abs(cur_surf - nom_surf)))
            ov_delta = float(np.nanmean(np.abs(cur_ov - nom_ov)))
            rho_res = spearmanr(nom_ov.to_numpy(dtype=float), cur_ov.to_numpy(dtype=float))
            rho = float(rho_res.statistic)

            ranked_all = cur_ov.sort_values(ascending=False).index.tolist()
            ranked_cand = [sid for sid in ranked_all if sid in cand_ids]

            rows.append(
                {
                    "ref_site_id": ref_id,
                    "factor": float(factor),
                    "moon_albedo_scaled": float(scaled_alb),
                    "mean_surface_score_delta": surf_delta,
                    "mean_overall_score_delta": ov_delta,
                    "spearman_rho_overall": rho,
                    "top1_site_id": ranked_all[0] if ranked_all else "",
                    "top3_site_ids": ", ".join(ranked_all[:3]),
                    "top1_candidate_id": ranked_cand[0] if ranked_cand else "",
                    "top3_candidate_ids": ", ".join(ranked_cand[:3]),
                }
            )

    return pd.DataFrame(rows)


def main() -> int:
    """Run broadband albedo sensitivity analysis on features_moon.parquet and features_earth.parquet."""
    moon_df = pd.read_parquet(MOON_PARQUET)
    earth_df = pd.read_parquet(EARTH_PARQUET)
    res_df = run_albedo_sensitivity(moon_df, earth_df)

    print("=== GENIS BANT ALBEDO AKTARIM HASSASIYETI ANALIZI (c in [0.30, 0.34, 0.38, 0.42, 0.46]) ===")
    for ref_id, grp in res_df.groupby("ref_site_id", sort=False):
        print(f"\nReferans Saha: {ref_id}")
        print(
            grp[
                [
                    "factor",
                    "moon_albedo_scaled",
                    "mean_surface_score_delta",
                    "mean_overall_score_delta",
                    "spearman_rho_overall",
                    "top1_site_id",
                    "top3_candidate_ids",
                ]
            ].to_string(index=False)
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
