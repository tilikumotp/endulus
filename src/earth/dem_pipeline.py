"""Earth DEM feature extraction pipeline (Copernicus DEM GLO-30) following AGENTS.md contract."""

from __future__ import annotations

import math
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd
import pyproj
import rasterio
from rasterio.enums import Resampling
from rasterio.warp import calculate_default_transform, reproject
from rasterio.windows import from_bounds as window_from_bounds

COPERNICUS_DEM_SRC = "Copernicus_DEM_GLO-30_2023.1"

IDENTITY_COLS: list[str] = [
    "site_id",
    "name",
    "body",
    "role",
    "lat",
    "lon",
    "radius_m",
]

NUMERIC_FEATURES: list[str] = [
    "slope_mean",
    "slope_p90",
    "roughness",
    "relief",
    "temp_amplitude",
    "thermal_inertia",
    "albedo",
]

EARTH_NATIVE_RES_M: dict[str, float] = {
    "slope_mean": 30.0,
    "slope_p90": 30.0,
    "roughness": 30.0,
    "relief": 30.0,
    "temp_amplitude": 1000.0,
    "thermal_inertia": 1000.0,
    "albedo": 500.0,
}

CONTRACT_COLS: list[str] = (
    IDENTITY_COLS
    + [
        col
        for feat in NUMERIC_FEATURES
        for col in (feat, f"{feat}_sd", f"{feat}_src", f"{feat}_res_m")
    ]
    + ["lithology_class"]
)


def get_metric_crs(lat: float, lon: float) -> str:
    """Return the appropriate local metric EPSG code (UTM or Polar Stereographic) for a coordinate."""
    if lat >= 84.0:
        return "EPSG:3413"
    if lat <= -80.0:
        return "EPSG:3031"
    zone = int((math.floor((lon + 180.0) / 6.0) % 60) + 1)
    epsg = 32600 + zone if lat >= 0.0 else 32700 + zone
    return f"EPSG:{epsg}"


def copernicus_tile_url(lat: float, lon: float) -> str:
    """Build the AWS S3 public Cloud-Optimized GeoTIFF URL for Copernicus DEM GLO-30."""
    lat_fl = math.floor(lat)
    lon_fl = math.floor(lon)
    ns = f"N{abs(lat_fl):02d}" if lat_fl >= 0 else f"S{abs(lat_fl):02d}"
    ew = f"E{abs(lon_fl):03d}" if lon_fl >= 0 else f"W{abs(lon_fl):03d}"
    tile_id = f"Copernicus_DSM_COG_10_{ns}_00_{ew}_00_DEM"
    return f"https://copernicus-dem-30m.s3.amazonaws.com/{tile_id}/{tile_id}.tif"


def fetch_dem_patch(
    site_id: str,
    lat: float,
    lon: float,
    radius_m: float = 1000.0,
    raw_dir: Path = Path("data/raw/earth"),
) -> Path:
    """Download a small windowed DEM patch around (lat, lon) from Copernicus GLO-30 COG into data/raw/earth/."""
    raw_dir.mkdir(parents=True, exist_ok=True)
    out_tif = raw_dir / f"{site_id}_copdem30_wgs84.tif"
    if out_tif.exists():
        return out_tif

    buffer_m = radius_m * 2.5
    dlat = buffer_m / 111_320.0
    dlon = buffer_m / (111_320.0 * max(math.cos(math.radians(lat)), 0.1))
    west, south, east, north = lon - dlon, lat - dlat, lon + dlon, lat + dlat

    url = f"/vsicurl/{copernicus_tile_url(lat, lon)}"
    with rasterio.open(url) as src:
        win = window_from_bounds(west, south, east, north, transform=src.transform)
        win = win.round_offsets().round_lengths()
        data = src.read(1, window=win).astype(np.float32)
        win_transform = src.window_transform(win)
        profile = src.profile.copy()
        profile.update(
            height=data.shape[0],
            width=data.shape[1],
            transform=win_transform,
            dtype="float32",
            count=1,
            compress="deflate",
        )
        with rasterio.open(out_tif, "w", **profile) as dst:
            dst.write(data, 1)

    return out_tif


def reproject_dem_to_metric(
    src_tif: Path,
    dst_crs: str,
    res_m: float = 30.0,
) -> tuple[np.ndarray, rasterio.Affine, dict[str, Any]]:
    """Reproject a geographic DEM patch to a metric CRS at native 30m spacing before slope computation."""
    with rasterio.open(src_tif) as src:
        transform, width, height = calculate_default_transform(
            src.crs,
            dst_crs,
            src.width,
            src.height,
            *src.bounds,
            resolution=(res_m, res_m),
        )
        dst_data = np.full((height, width), np.nan, dtype=np.float32)
        reproject(
            source=rasterio.band(src, 1),
            destination=dst_data,
            src_transform=src.transform,
            src_crs=src.crs,
            dst_transform=transform,
            dst_crs=dst_crs,
            dst_nodata=np.nan,
            resampling=Resampling.bilinear,
        )
        summary = {
            "src_shape": (src.height, src.width),
            "src_crs": str(src.crs),
            "dst_shape": (height, width),
            "dst_crs": dst_crs,
            "dst_bounds": rasterio.transform.array_bounds(height, width, transform),
        }
    return dst_data, transform, summary


def compute_slope_in_radius(
    dem_m: np.ndarray,
    transform: rasterio.Affine,
    lat: float,
    lon: float,
    dst_crs: str,
    radius_m: float = 1000.0,
    n_boot: int = 200,
    seed: int = 42,
) -> dict[str, Any]:
    """Compute slope_mean, slope_p90 and 1-sigma bootstrap uncertainties inside radius_m on metric grid."""
    transformer = pyproj.Transformer.from_crs("EPSG:4326", dst_crs, always_xy=True)
    cx, cy = transformer.transform(lon, lat)

    dx = abs(transform.a)
    dy = abs(transform.e)
    dz_dy, dz_dx = np.gradient(dem_m, dy, dx)
    slope_deg = np.degrees(np.arctan(np.hypot(dz_dx, dz_dy)))

    rows, cols = np.indices(dem_m.shape)
    xs, ys = rasterio.transform.xy(transform, rows, cols, offset="center")
    xs_arr = np.asarray(xs, dtype=np.float64).reshape(dem_m.shape)
    ys_arr = np.asarray(ys, dtype=np.float64).reshape(dem_m.shape)

    dist_m = np.hypot(xs_arr - cx, ys_arr - cy)
    valid_mask = (dist_m <= radius_m) & np.isfinite(slope_deg) & np.isfinite(dem_m)

    valid_slopes = slope_deg[valid_mask]
    if valid_slopes.size == 0:
        raise ValueError(f"No valid DEM pixels found within {radius_m} m of ({lat}, {lon}).")

    rng = np.random.default_rng(seed)
    idx = rng.integers(0, valid_slopes.size, size=(n_boot, valid_slopes.size))
    boot_samples = valid_slopes[idx]
    slope_mean_sd = float(np.std(np.mean(boot_samples, axis=1), ddof=1))
    slope_p90_sd = float(np.std(np.percentile(boot_samples, 90.0, axis=1), ddof=1))

    return {
        "slope_mean": float(np.mean(valid_slopes)),
        "slope_mean_sd": max(slope_mean_sd, 1e-4),
        "slope_p90": float(np.percentile(valid_slopes, 90.0)),
        "slope_p90_sd": max(slope_p90_sd, 1e-4),
        "n_pixels": int(valid_slopes.size),
        "elev_min_m": float(np.min(dem_m[valid_mask])),
        "elev_max_m": float(np.max(dem_m[valid_mask])),
        "slope_min_deg": float(np.min(valid_slopes)),
        "slope_max_deg": float(np.max(valid_slopes)),
        "slope_grid": slope_deg,
        "mask_grid": valid_mask,
    }


def make_empty_contract_row(
    site_id: str,
    name: str,
    role: str,
    lat: float,
    lon: float,
    radius_m: float = 1000.0,
    lithology_class: str = "",
) -> dict[str, Any]:
    """Initialize a single Earth site row with all 36 contract columns and native resolutions."""
    row: dict[str, Any] = {
        "site_id": str(site_id),
        "name": str(name),
        "body": "earth",
        "role": str(role),
        "lat": float(lat),
        "lon": float(lon),
        "radius_m": float(radius_m),
    }
    for feat in NUMERIC_FEATURES:
        row[feat] = float("nan")
        row[f"{feat}_sd"] = float("nan")
        row[f"{feat}_src"] = ""
        row[f"{feat}_res_m"] = float(EARTH_NATIVE_RES_M[feat])
    row["lithology_class"] = str(lithology_class)
    return row


def build_contract_dataframe(rows: list[dict[str, Any]]) -> pd.DataFrame:
    """Assemble and type-cast the full 36-column Earth features DataFrame per AGENTS.md §5."""
    df = pd.DataFrame(rows)
    df = df[CONTRACT_COLS]
    for feat in NUMERIC_FEATURES:
        df[feat] = df[feat].astype("float64")
        df[f"{feat}_sd"] = df[f"{feat}_sd"].astype("float64")
        df[f"{feat}_src"] = df[f"{feat}_src"].fillna("").astype(str)
        df[f"{feat}_res_m"] = df[f"{feat}_res_m"].astype("float64")
    df["lat"] = df["lat"].astype("float64")
    df["lon"] = df["lon"].astype("float64")
    df["radius_m"] = df["radius_m"].astype("float64")
    df["lithology_class"] = df["lithology_class"].fillna("").astype(str)
    return df
