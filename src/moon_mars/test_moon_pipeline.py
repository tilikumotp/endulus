"""Unit tests for the Lunar South Pole reference feature pipeline, visual atlas, and broadband albedo sensitivity."""
from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd
from pyproj import Transformer

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
SRC_DIR = REPO_ROOT / "src"
SCRIPTS_DIR = REPO_ROOT / "scripts"
for p in (SRC_DIR, SCRIPTS_DIR):
    if str(p) not in sys.path:
        sys.path.insert(0, str(p))

from moon_mars.albedo_sensitivity import FACTORS, NOMINAL_FACTOR, run_albedo_sensitivity  # noqa: E402
from moon_mars.moon_visual_atlas import ATLAS_DIR, METADATA_PATH, THUMBS_DIR, THUMBS_META_CSV, THUMBS_META_JSON  # noqa: E402
from moon_mars.shackleton_slope import (  # noqa: E402
    MOON_GEOD_PROJ4,
    MOON_STEREO_PROJ4,
    PROCESSED_PATH,
    VERIFIED_MOON_SITES,
    ordered_columns,
)
from validate_contract import validate  # noqa: E402

EARTH_PATH = REPO_ROOT / "data" / "processed" / "features_earth.parquet"


def test_moon_parquet_contract_36_cols() -> None:
    """Verify features_moon.parquet has 5 rows, exact 36 contract columns, and 0 errors/warnings/MOCKs."""
    assert PROCESSED_PATH.exists(), f"Missing {PROCESSED_PATH}"
    df = pd.read_parquet(PROCESSED_PATH)
    expected_cols = ordered_columns()
    assert len(expected_cols) == 36
    assert list(df.columns) == expected_cols
    assert len(df) == 5
    errors, warnings, _ = validate(PROCESSED_PATH, fail_on_mock=True)
    assert errors == []
    assert warnings == []


def test_moon_crs_and_coordinates() -> None:
    """Verify all 5 reference sites lie in the Lunar South Pole (lat <= -87 deg) and project to meters."""
    df = pd.read_parquet(PROCESSED_PATH)
    assert (df["body"] == "moon").all()
    assert (df["role"] == "reference").all()
    assert (df["lat"] <= -87.0).all()
    assert (df["lat"] >= -90.0).all()
    assert (df["lon"].between(-180.0, 180.0)).all()
    assert (df["radius_m"] == 1000.0).all()

    to_proj = Transformer.from_crs(MOON_GEOD_PROJ4, MOON_STEREO_PROJ4, always_xy=True)
    for _, row in df.iterrows():
        x_m, y_m = to_proj.transform(float(row["lon"]), float(row["lat"]))
        dist_from_pole_m = float(np.hypot(x_m, y_m))
        assert 1000.0 < dist_from_pole_m < 100_000.0


def test_moon_toterr_uncertainty_not_constant() -> None:
    """Verify LOLA 5 m/px topography metrics and PGDA _toterr.tif pixel-based SDs are finite and non-constant."""
    df = pd.read_parquet(PROCESSED_PATH)
    for col in ("slope_mean", "slope_p90", "roughness", "relief"):
        assert df[col].notna().all()
        assert (df[col] > 0.0).all()
        assert df[f"{col}_sd"].notna().all()
        assert (df[f"{col}_sd"] > 0.0).all()
        assert (df[f"{col}_res_m"] == 5.0).all()

    assert (df["slope_p90"] > df["slope_mean"]).all()
    assert df["relief_sd"].nunique() == len(df)
    assert df["roughness_sd"].nunique() == len(df)
    assert not np.allclose(df["relief_sd"].to_numpy(dtype=float), 0.50)


def test_moon_visual_atlas_files_and_sizes() -> None:
    """Verify 5-site visual atlas PNGs and metadata exist, each PNG < 120 KB, total < 1.2 MB, and hazard % sum to 100."""
    assert METADATA_PATH.exists(), f"Missing {METADATA_PATH}"
    meta_list = json.loads(METADATA_PATH.read_text(encoding="utf-8"))
    assert len(meta_list) == len(VERIFIED_MOON_SITES)

    total_bytes = METADATA_PATH.stat().st_size
    for item in meta_list:
        sid = item["site_id"]
        assert item.get("note") == "Illustrative slope bins; not a landing-safety assessment."
        pct_sum = (
            float(item["pct_lt10deg"])
            + float(item["pct_10_20deg"])
            + float(item["pct_gt20deg"])
        )
        assert np.isclose(pct_sum, 100.0, atol=0.15), f"{sid} slope bin pct sum={pct_sum}"
        for suffix in ("hillshade", "hazard", "atlas"):
            png_path = ATLAS_DIR / f"{sid}_{suffix}.png"
            assert png_path.exists(), f"Missing {png_path}"
            sz = png_path.stat().st_size
            assert 5_000 < sz <= 120 * 1024, f"{png_path.name} size {sz / 1024:.1f} KB exceeds 120 KB limit"
            total_bytes += sz

    assert total_bytes < int(1.2 * 1024 * 1024), f"Total atlas size {total_bytes / 1024:.1f} KB exceeds 1.2 MB"

    # M3: Verify 224x224 SigLIP thumbnails and metadata table
    assert THUMBS_META_JSON.exists(), f"Missing {THUMBS_META_JSON}"
    assert THUMBS_META_CSV.exists(), f"Missing {THUMBS_META_CSV}"
    thumbs_meta = json.loads(THUMBS_META_JSON.read_text(encoding="utf-8"))
    assert len(thumbs_meta) == len(VERIFIED_MOON_SITES)
    from PIL import Image
    for t_item in thumbs_meta:
        for req_key in ("site_id", "tile_id", "lat", "lon", "scale_m_per_px", "source", "usage_scope", "thumb_path"):
            assert req_key in t_item
        t_path = THUMBS_DIR / f"{t_item['site_id']}.png"
        assert t_path.exists(), f"Missing thumb {t_path}"
        with Image.open(t_path) as im:
            assert im.size == (224, 224)


def test_moon_thermal_and_albedo_bounds() -> None:
    """Verify Diviner temp_amplitude, 1D Hayne (2017) thermal_inertia (50-500 TIU), and broadband LOLA albedo."""
    df = pd.read_parquet(PROCESSED_PATH)
    assert df["temp_amplitude"].between(50.0, 300.0).all()
    assert (df["temp_amplitude_sd"] >= 2.5).all()
    assert (df["temp_amplitude_res_m"] == 240.0).all()

    assert df["albedo"].between(0.05, 0.30).all()
    assert (df["albedo_sd"] > 0.0).all()
    assert (df["albedo_res_m"] == 1000.0).all()
    assert (df["albedo_src"] == "LRO-L-LOLA-4-GDR-V1.0:LDAM_50S_1000M_V1.0_broadband_eq").all()

    assert df["thermal_inertia"].between(50.0, 500.0).all()
    assert (df["thermal_inertia_sd"] > 0.0).all()
    assert (df["thermal_inertia_src"] == "LRO-L-DLRE-5-PCP-V1.0:1D_Hayne2017_polar_TI_v1").all()
    assert (df["thermal_inertia_res_m"] == 240.0).all()


def test_albedo_sensitivity_runs() -> None:
    """Verify run_albedo_sensitivity executes across all 5 Moon sites and matches identity at factor=0.38."""
    moon_df = pd.read_parquet(PROCESSED_PATH)
    earth_df = pd.read_parquet(EARTH_PATH)
    res_df = run_albedo_sensitivity(moon_df, earth_df, n_boot=50, seed=42)

    assert len(res_df) == len(moon_df) * len(FACTORS)
    nom = res_df[np.isclose(res_df["factor"], NOMINAL_FACTOR)]
    assert len(nom) == len(moon_df)
    assert np.allclose(nom["mean_surface_score_delta"], 0.0, atol=1e-12)
    assert np.allclose(nom["mean_overall_score_delta"], 0.0, atol=1e-12)
    assert np.allclose(nom["spearman_rho_overall"], 1.0, atol=1e-12)
    assert (res_df["spearman_rho_overall"] > 0.60).all()
    near_nom = res_df[res_df["factor"].between(0.34, 0.42)]
    assert (near_nom["spearman_rho_overall"] > 0.85).all()


if __name__ == "__main__":
    for fn in (
        test_moon_parquet_contract_36_cols,
        test_moon_crs_and_coordinates,
        test_moon_toterr_uncertainty_not_constant,
        test_moon_visual_atlas_files_and_sizes,
        test_moon_thermal_and_albedo_bounds,
        test_albedo_sensitivity_runs,
    ):
        fn()
        print(f"PASS: {fn.__name__}")
    print("ALL 6 MOON PIPELINE UNIT TESTS PASSED")
