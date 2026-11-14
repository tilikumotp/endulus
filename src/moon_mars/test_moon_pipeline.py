"""Unit tests for the Lunar South Pole reference feature pipeline and broadband albedo sensitivity."""
from __future__ import annotations

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
from moon_mars.shackleton_slope import (  # noqa: E402
    MOON_GEOD_PROJ4,
    MOON_STEREO_PROJ4,
    PROCESSED_PATH,
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


def test_moon_topography_and_toterr_bounds() -> None:
    """Verify LOLA 5 m/px topography metrics and PGDA _toterr.tif pixel-based SDs are finite and non-constant."""
    df = pd.read_parquet(PROCESSED_PATH)
    for col in ("slope_mean", "slope_p90", "roughness", "relief"):
        assert df[col].notna().all()
        assert (df[col] > 0.0).all()
        assert df[f"{col}_sd"].notna().all()
        assert (df[f"{col}_sd"] > 0.0).all()
        assert (df[f"{col}_res_m"] == 5.0).all()

    assert (df["slope_p90"] > df["slope_mean"]).all()
    # relief_sd and roughness_sd must come from site-specific _toterr.tif + bootstrap, not a constant 0.50
    assert df["relief_sd"].nunique() == len(df)
    assert df["roughness_sd"].nunique() == len(df)
    assert not np.allclose(df["relief_sd"].to_numpy(dtype=float), 0.50)


def test_moon_thermal_and_albedo_bounds() -> None:
    """Verify Diviner temp_amplitude, broadband LOLA albedo, and NaN thermal_inertia follow contract bounds."""
    df = pd.read_parquet(PROCESSED_PATH)
    assert df["temp_amplitude"].between(50.0, 300.0).all()
    assert (df["temp_amplitude_sd"] >= 2.5).all()
    assert (df["temp_amplitude_res_m"] == 240.0).all()

    assert df["albedo"].between(0.05, 0.30).all()
    assert (df["albedo_sd"] > 0.0).all()
    assert (df["albedo_res_m"] == 1000.0).all()
    assert (df["albedo_src"] == "LRO-L-LOLA-4-GDR-V1.0:LDAM_50S_1000M_V1.0_broadband_eq").all()

    assert df["thermal_inertia"].isna().all()
    assert df["thermal_inertia_sd"].isna().all()
    assert (df["thermal_inertia_src"] == "").all()
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
    assert (res_df["spearman_rho_overall"] > 0.65).all()
    near_nom = res_df[res_df["factor"].between(0.34, 0.42)]
    assert (near_nom["spearman_rho_overall"] > 0.85).all()


if __name__ == "__main__":
    for fn in (
        test_moon_parquet_contract_36_cols,
        test_moon_crs_and_coordinates,
        test_moon_topography_and_toterr_bounds,
        test_moon_thermal_and_albedo_bounds,
        test_albedo_sensitivity_runs,
    ):
        fn()
        print(f"PASS: {fn.__name__}")
    print("ALL 5 MOON PIPELINE UNIT TESTS PASSED")
