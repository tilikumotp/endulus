"""app/terrain.py — elevation grids for the 3D Terrain tab.

Loads verified DEM grids committed in data/processed/:
  - Moon (M6): data/processed/moon_3d/{site_id}_3d.npz (key "elev_m", 5 m/px)
  - Earth (E7): data/processed/earth_3d_grids.npz (key "{site_id}", 30 m/px)
Falls back to data/processed/dem_tiles/{site_id}.npz ("z") and finally a
deterministic stub grid built from the site's measured slope/roughness/relief.
"""
from __future__ import annotations

import hashlib
import pathlib

import numpy as np
import pandas as pd
import streamlit as st
from scipy.ndimage import zoom

ROOT = pathlib.Path(__file__).resolve().parent.parent
PROC_DIR = ROOT / "data" / "processed"
MOON_3D_DIR = PROC_DIR / "moon_3d"
EARTH_3D_PATH = PROC_DIR / "earth_3d_grids.npz"
TILE_DIR = PROC_DIR / "dem_tiles"

GRID = 64  # stub grid resolution (GRID x GRID)
EARTH_3D_HALF_WIDTH_M = 1110.0  # 74 x 30 m = 2220 m total window (E7)
MOON_3D_DEFAULT_DX_M = 5.0


def _seed(site_id: str) -> int:
    """Deterministic seed derived from the site code."""
    return int(hashlib.sha256(site_id.encode("utf-8")).hexdigest()[:8], 16)


def _stub_dem(row: pd.Series) -> np.ndarray:
    """Generated terrain shaped by the site's real measured stats.

    Uses the measured mean slope for the overall tilt, the measured
    relief for the vertical range and the measured roughness for fine
    detail. Not a real DEM — the UI must label it as sample terrain.
    """
    radius = float(row.get("radius_m", 1000.0) or 1000.0)
    relief = float(np.nan_to_num(float(row.get("relief", np.nan)), nan=60.0))
    slope = np.radians(float(np.nan_to_num(
        float(row.get("slope_mean", np.nan)), nan=10.0)))
    rough = float(np.nan_to_num(float(row.get("roughness", np.nan)),
                                nan=max(relief * 0.15, 1.0)))

    rng = np.random.default_rng(_seed(str(row["site_id"])))
    y, x = np.mgrid[-radius:radius:GRID * 1j, -radius:radius:GRID * 1j]

    # Overall tilt in a fixed random bearing, magnitude = measured slope.
    bearing = rng.uniform(0.0, 2.0 * np.pi)
    z = np.tan(slope) * (x * np.cos(bearing) + y * np.sin(bearing))

    # Broad landforms: a few sinusoids with amplitudes sharing the relief.
    for amp_share, wavelength in [(0.50, 1.6), (0.25, 0.9), (0.15, 0.5)]:
        phase_x, phase_y = rng.uniform(0.0, 2.0 * np.pi, size=2)
        k = 2.0 * np.pi / (wavelength * 2.0 * radius)
        z += relief * amp_share * np.sin(k * x + phase_x) * np.cos(k * y + phase_y)

    # Fine detail at the measured roughness magnitude: multi-octave smooth
    # noise (coarse-to-fine, bicubic upsampling) so the surface reads as
    # landform, not static.
    def _octave(coarse: int) -> np.ndarray:
        g = rng.normal(0.0, 1.0, (coarse, coarse))
        return zoom(g, GRID / coarse, order=3, mode="nearest")[:GRID, :GRID]

    detail = rough * (0.65 * _octave(8) + 0.35 * _octave(16))
    z += detail

    # Rescale the total range to the measured relief.
    span = float(z.max() - z.min())
    if span > 0:
        z = (z - z.min()) / span * relief
    return z.astype(float)


def hillshade(z: np.ndarray, radius_m: float) -> np.ndarray:
    """Grayscale hillshade (0–1) with a NW light source at 45° elevation."""
    cell = (2.0 * radius_m) / (z.shape[1] - 1)
    dz_dy, dz_dx = np.gradient(z, cell, cell)
    slope_ang = np.arctan(np.hypot(dz_dx, dz_dy))
    aspect = np.arctan2(dz_dx, dz_dy)
    az = np.radians(315.0)
    alt = np.radians(45.0)
    shade = (np.sin(alt) * np.cos(slope_ang)
             + np.cos(alt) * np.sin(slope_ang) * np.cos(az - aspect))
    return np.clip(shade, 0.0, 1.0)


@st.cache_data(show_spinner=False)
def _load_earth_grid_archive(mtime: float) -> dict[str, np.ndarray]:
    """Load the committed E7 Earth 3D NPZ archive once per file mtime."""
    if not EARTH_3D_PATH.exists():
        return {}
    with np.load(EARTH_3D_PATH) as archive:
        return {key: np.asarray(archive[key], dtype=float) for key in archive.files}


def get_tile_data(row: pd.Series) -> tuple[np.ndarray, bool, float]:
    """Return ``(elev_m, is_stub, half_width_m)`` for one Moon or Earth site.

    Prefers verified M6 (`moon_3d/`) and E7 (`earth_3d_grids.npz`) DEM grids
    over legacy `dem_tiles/` or the labelled synthetic stub fallback.
    """
    site_id = str(row["site_id"])
    radius_m = float(row.get("radius_m", 1000.0) or 1000.0)

    moon_path = MOON_3D_DIR / f"{site_id}_3d.npz"
    if moon_path.exists():
        with np.load(moon_path) as data:
            z = np.asarray(data["elev_m"], dtype=float)
            dx = float(data["dx_m"]) if "dx_m" in data else MOON_3D_DEFAULT_DX_M
        half_w = 0.5 * max(z.shape[1] - 1, 1) * dx
        return z, False, half_w

    if EARTH_3D_PATH.exists():
        earth_grids = _load_earth_grid_archive(EARTH_3D_PATH.stat().st_mtime)
        if site_id in earth_grids:
            return earth_grids[site_id], False, EARTH_3D_HALF_WIDTH_M

    legacy_path = TILE_DIR / f"{site_id}.npz"
    if legacy_path.exists():
        with np.load(legacy_path) as data:
            z = np.asarray(data["z"], dtype=float)
            half_w = float(data["radius_m"]) if "radius_m" in data else radius_m
        return z, False, half_w

    return _stub_dem(row), True, radius_m


@st.cache_data(show_spinner=False)
def get_tile(row: pd.Series) -> tuple[np.ndarray, bool]:
    """Return ``(elevation grid in metres, is_stub)`` for one site."""
    z, is_stub, _ = get_tile_data(row)
    return z, is_stub
