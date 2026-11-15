"""app/terrain.py — elevation grids for the 3D Terrain tab.

Loads verified orbital DEM elevation grids committed in data/processed/:
- Moon references: data/processed/moon_3d/{site_id}_3d.npz (key "elev_m", 5 m/px LOLA)
- Earth sites: data/processed/earth_3d_grids.npz (key "{site_id}", 30 m/px GLO-30 / NASADEM)
- Legacy single-tile path: data/processed/dem_tiles/{site_id}.npz (key "z" or "elev_m")
If a site's grid is not found on disk, falls back to a deterministic stub
grid shaped by the site's measured slope/roughness/relief statistics and
marks it as sample terrain (is_stub=True).
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
EARTH_3D_NPZ = PROC_DIR / "earth_3d_grids.npz"
TILE_DIR = PROC_DIR / "dem_tiles"

GRID = 64  # stub grid resolution (GRID x GRID)


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


# Native pixel scale of the verified orbital grids (documented in the module
# docstring): LOLA 5 m/px for Moon, Copernicus GLO-30 / NASADEM 30 m/px for Earth.
PIXEL_SCALE_M = {"moon": 5.0, "earth": 30.0}


def get_tile_data(row: pd.Series) -> tuple[np.ndarray, bool, float]:
    """Return (elevation grid, is_stub, tile half-width in metres) for one site.

    Compatibility wrapper over :func:`get_tile` that also reports the tile's
    half-width, derived from the grid shape and the dataset's native pixel
    scale (or the analysis radius for stub grids).
    """
    z, is_stub = get_tile(row)
    if is_stub:
        half_width_m = float(row.get("radius_m", 1000.0) or 1000.0)
    else:
        px = PIXEL_SCALE_M.get(str(row.get("body", "earth")), 30.0)
        half_width_m = z.shape[0] * px / 2.0
    return z, is_stub, half_width_m


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
def get_tile(row: pd.Series) -> tuple[np.ndarray, bool]:
    """Return (elevation grid in metres, is_stub) for one site.

    Reads verified orbital elevation grids from data/processed/moon_3d/,
    data/processed/earth_3d_grids.npz, or data/processed/dem_tiles/ when
    present; otherwise generates the labelled stub grid from measured stats.
    """
    site_id = str(row["site_id"])

    moon_path = MOON_3D_DIR / f"{site_id}_3d.npz"
    if moon_path.exists():
        with np.load(moon_path) as data:
            key = "elev_m" if "elev_m" in data.files else "z"
            return np.asarray(data[key], dtype=float), False

    if EARTH_3D_NPZ.exists():
        with np.load(EARTH_3D_NPZ) as data:
            if site_id in data.files:
                return np.asarray(data[site_id], dtype=float), False

    path = TILE_DIR / f"{site_id}.npz"
    if path.exists():
        with np.load(path) as data:
            key = "z" if "z" in data.files else "elev_m"
            return np.asarray(data[key], dtype=float), False

    return _stub_dem(row), True
