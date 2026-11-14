"""Earth DEM & MODIS feature extraction pipeline following AGENTS.md contract."""

from __future__ import annotations

import math
import struct
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd
import pyproj
import rasterio
import requests
from rasterio.enums import Resampling
from rasterio.io import MemoryFile
from rasterio.merge import merge
from rasterio.warp import calculate_default_transform, reproject
from rasterio.windows import Window, from_bounds as window_from_bounds

from src.earth.modis_pipeline import (
    check_mcd43a3_access,
    fetch_mcd43a3_albedo,
    fetch_mod11a2_temp_amplitude,
)
from src.earth.sites import VERIFIED_EARTH_SITES, SiteSpec

COPERNICUS_DEM_SRC = "Copernicus_DEM_GLO-30"

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


def copernicus_tile_url(lat_floor: int, lon_floor: int) -> str:
    """Build the AWS S3 public Cloud-Optimized GeoTIFF URL for a 1x1 deg Copernicus DEM GLO-30 tile."""
    ns = f"N{abs(lat_floor):02d}" if lat_floor >= 0 else f"S{abs(lat_floor):02d}"
    ew = f"E{abs(lon_floor):03d}" if lon_floor >= 0 else f"W{abs(lon_floor):03d}"
    tile_id = f"Copernicus_DSM_COG_10_{ns}_00_{ew}_00_DEM"
    return f"https://copernicus-dem-30m.s3.amazonaws.com/{tile_id}/{tile_id}.tif"


def _vsicurl_fallback(
    url: str,
    west: float,
    south: float,
    east: float,
    north: float,
) -> tuple[np.ndarray, rasterio.Affine, rasterio.crs.CRS] | None:
    """Fallback to GDAL /vsicurl/ if custom HTTP Range TIFF header parsing encounters BigTIFF or >16KB IFD."""
    with rasterio.open(f"/vsicurl/{url}") as src:
        t_west = max(west, src.bounds.left)
        t_south = max(south, src.bounds.bottom)
        t_east = min(east, src.bounds.right)
        t_north = min(north, src.bounds.top)
        if t_west >= t_east or t_south >= t_north:
            return None
        raw_win = window_from_bounds(t_west, t_south, t_east, t_north, transform=src.transform)
        r0 = max(0, math.floor(raw_win.row_off))
        r1 = min(src.height, math.ceil(raw_win.row_off + raw_win.height))
        c0 = max(0, math.floor(raw_win.col_off))
        c1 = min(src.width, math.ceil(raw_win.col_off + raw_win.width))
        win = Window(col_off=c0, row_off=r0, width=c1 - c0, height=r1 - r0)
        data = src.read(1, window=win).astype(np.float32)
        return data, src.window_transform(win), src.crs


def _read_cog_window_via_range(
    url: str,
    west: float,
    south: float,
    east: float,
    north: float,
) -> tuple[np.ndarray, rasterio.Affine, rasterio.crs.CRS] | None:
    """Fetch only the intersecting internal TIFF tiles via HTTP Range requests, with /vsicurl/ fallback."""
    try:
        r_hdr = requests.get(url, headers={"Range": "bytes=0-16383"}, timeout=15)
        if r_hdr.status_code not in (200, 206):
            return None
        hdr = bytearray(r_hdr.content)
        if hdr[:4] != b"II*\x00":
            return _vsicurl_fallback(url, west, south, east, north)

        ifd_off = struct.unpack("<I", hdr[4:8])[0]
        n_entries = struct.unpack("<H", hdr[ifd_off : ifd_off + 2])[0]
        tags: dict[int, tuple[int, int, int, int]] = {}
        for i in range(n_entries):
            pos = ifd_off + 2 + i * 12
            tag, typ, cnt, val_off = struct.unpack("<HHII", hdr[pos : pos + 12])
            tags[tag] = (typ, cnt, val_off, pos)

        struct.pack_into("<I", hdr, ifd_off + 2 + n_entries * 12, 0)

        img_w = tags[256][2]
        img_h = tags[257][2]
        tile_w = tags[322][2]
        tile_h = tags[323][2]
        _, n_tiles, off_pos, _ = tags[324]
        _, _, cnt_pos, _ = tags[325]

        orig_offsets = list(struct.unpack(f"<{n_tiles}I", hdr[off_pos : off_pos + 4 * n_tiles]))
        orig_counts = list(struct.unpack(f"<{n_tiles}I", hdr[cnt_pos : cnt_pos + 4 * n_tiles]))

        empty_hdr = bytearray(hdr)
        struct.pack_into(f"<{n_tiles}I", empty_hdr, off_pos, *([0] * n_tiles))
        struct.pack_into(f"<{n_tiles}I", empty_hdr, cnt_pos, *([0] * n_tiles))

        with MemoryFile(bytes(empty_hdr)) as mem_meta:
            with mem_meta.open() as ds_meta:
                t_west = max(west, ds_meta.bounds.left)
                t_south = max(south, ds_meta.bounds.bottom)
                t_east = min(east, ds_meta.bounds.right)
                t_north = min(north, ds_meta.bounds.top)
                if t_west >= t_east or t_south >= t_north:
                    return None
                raw_win = window_from_bounds(
                    t_west, t_south, t_east, t_north, transform=ds_meta.transform
                )
                r0 = max(0, math.floor(raw_win.row_off))
                r1 = min(img_h, math.ceil(raw_win.row_off + raw_win.height))
                c0 = max(0, math.floor(raw_win.col_off))
                c1 = min(img_w, math.ceil(raw_win.col_off + raw_win.width))
                win = Window(col_off=c0, row_off=r0, width=c1 - c0, height=r1 - r0)

        n_tx = math.ceil(img_w / tile_w)
        needed_indices: set[int] = set()
        for ty in range(r0 // tile_h, (r1 - 1) // tile_h + 1):
            for tx in range(c0 // tile_w, (c1 - 1) // tile_w + 1):
                needed_indices.add(ty * n_tx + tx)

        new_offsets = [0] * n_tiles
        new_counts = [0] * n_tiles
        payload = bytearray()
        for idx in sorted(needed_indices):
            t_off = orig_offsets[idx]
            t_cnt = orig_counts[idx]
            resp = requests.get(
                url, headers={"Range": f"bytes={t_off}-{t_off + t_cnt - 1}"}, timeout=20
            )
            resp.raise_for_status()
            chunk = resp.content
            new_offsets[idx] = len(hdr) + len(payload)
            new_counts[idx] = len(chunk)
            payload.extend(chunk)

        struct.pack_into(f"<{n_tiles}I", hdr, off_pos, *new_offsets)
        struct.pack_into(f"<{n_tiles}I", hdr, cnt_pos, *new_counts)

        with MemoryFile(bytes(hdr) + bytes(payload)) as mem:
            with mem.open() as src:
                data = src.read(1, window=win).astype(np.float32)
                win_transform = src.window_transform(win)
                crs = src.crs
        return data, win_transform, crs
    except Exception:
        return _vsicurl_fallback(url, west, south, east, north)


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
    if out_tif.exists() and out_tif.stat().st_size > 0:
        return out_tif

    buffer_m = radius_m * 2.5
    dlat = buffer_m / 111_320.0
    dlon = buffer_m / (111_320.0 * max(math.cos(math.radians(lat)), 0.1))
    west, south, east, north = lon - dlon, lat - dlat, lon + dlon, lat + dlat

    lat_tiles = range(math.floor(south), math.floor(north) + 1)
    lon_tiles = range(math.floor(west), math.floor(east) + 1)

    memfiles: list[MemoryFile] = []
    datasets = []
    try:
        for lt in lat_tiles:
            for ln in lon_tiles:
                res = _read_cog_window_via_range(
                    copernicus_tile_url(lt, ln), west, south, east, north
                )
                if res is None:
                    continue
                data, win_transform, crs = res
                profile = {
                    "driver": "GTiff",
                    "height": data.shape[0],
                    "width": data.shape[1],
                    "transform": win_transform,
                    "crs": crs,
                    "dtype": "float32",
                    "count": 1,
                    "nodata": np.nan,
                }
                mem = MemoryFile()
                dst_mem = mem.open(**profile)
                dst_mem.write(data, 1)
                memfiles.append(mem)
                datasets.append(dst_mem)

        if not datasets:
            raise RuntimeError(f"Failed to fetch Copernicus DEM tiles for {site_id}")

        if len(datasets) == 1:
            mosaic = datasets[0].read(1)
            out_transform = datasets[0].transform
            out_crs = datasets[0].crs
        else:
            mosaic_arr, out_transform = merge(datasets, nodata=np.nan)
            mosaic = mosaic_arr[0].astype(np.float32)
            out_crs = datasets[0].crs

        out_profile = {
            "driver": "GTiff",
            "height": mosaic.shape[0],
            "width": mosaic.shape[1],
            "count": 1,
            "dtype": "float32",
            "crs": out_crs,
            "transform": out_transform,
            "nodata": np.nan,
            "compress": "deflate",
        }
        with MemoryFile() as out_mem:
            with out_mem.open(**out_profile) as dst:
                dst.write(mosaic, 1)
            out_tif.write_bytes(out_mem.read())
    finally:
        for ds in datasets:
            ds.close()
        for mem in memfiles:
            mem.close()

    return out_tif


def reproject_dem_to_metric(
    src_tif: Path,
    dst_crs: str,
    res_m: float = 30.0,
) -> tuple[np.ndarray, rasterio.Affine, dict[str, Any]]:
    """Reproject a geographic DEM patch to a metric CRS at native 30m spacing before slope computation."""
    with MemoryFile(src_tif.read_bytes()) as mem:
        with mem.open() as src:
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
                src_nodata=np.nan,
                dst_nodata=np.nan,
                resampling=Resampling.bilinear,
            )
            summary = {
                "src_shape": (src.height, src.width),
                "src_crs": str(src.crs),
                "src_bounds": tuple(round(b, 5) for b in src.bounds),
                "dst_shape": (height, width),
                "dst_crs": dst_crs,
                "dst_bounds": tuple(
                    round(b, 1)
                    for b in rasterio.transform.array_bounds(height, width, transform)
                ),
            }
    return dst_data, transform, summary


def _detrended_roughness(dx_m: np.ndarray, dy_m: np.ndarray, z_m: np.ndarray) -> float:
    """Fit a first-order plane z = a*dx + b*dy + c via OLS and return std of residuals (m)."""
    design = np.column_stack([dx_m, dy_m, np.ones_like(dx_m)])
    coeffs, _, _, _ = np.linalg.lstsq(design, z_m, rcond=None)
    residuals = z_m - (design @ coeffs)
    return float(np.std(residuals, ddof=1))


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
    """Compute slope_mean, slope_p90, roughness, relief and 1-sigma uncertainties inside radius_m."""
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

    rel_x = xs_arr - cx
    rel_y = ys_arr - cy
    dist_m = np.hypot(rel_x, rel_y)
    valid_mask = (dist_m <= radius_m) & np.isfinite(slope_deg) & np.isfinite(dem_m)

    valid_slopes = slope_deg[valid_mask]
    valid_z = dem_m[valid_mask].astype(np.float64)
    valid_dx = rel_x[valid_mask]
    valid_dy = rel_y[valid_mask]
    if valid_slopes.size == 0:
        raise ValueError(f"No valid DEM pixels found within {radius_m} m of ({lat}, {lon}).")

    elev_min = float(np.min(valid_z))
    elev_max = float(np.max(valid_z))
    relief = float(elev_max - elev_min)
    roughness = _detrended_roughness(valid_dx, valid_dy, valid_z)

    rng = np.random.default_rng(seed)
    n_pix = valid_slopes.size
    idx = rng.integers(0, n_pix, size=(n_boot, n_pix))
    boot_slopes = valid_slopes[idx]
    slope_mean_sd = float(np.std(np.mean(boot_slopes, axis=1), ddof=1))
    slope_p90_sd = float(np.std(np.percentile(boot_slopes, 90.0, axis=1), ddof=1))

    boot_roughness = np.empty(n_boot, dtype=np.float64)
    boot_relief = np.empty(n_boot, dtype=np.float64)
    sigma_z_rel = 1.0  # 1 m relative pixel-level vertical uncertainty for relief propagation
    for b in range(n_boot):
        b_idx = idx[b]
        z_b = valid_z[b_idx] + rng.normal(0.0, sigma_z_rel, size=n_pix)
        boot_roughness[b] = _detrended_roughness(valid_dx[b_idx], valid_dy[b_idx], z_b)
        boot_relief[b] = float(np.max(z_b) - np.min(z_b))

    roughness_sd = float(np.std(boot_roughness, ddof=1))
    relief_sd = float(np.std(boot_relief, ddof=1))

    return {
        "slope_mean": float(np.mean(valid_slopes)),
        "slope_mean_sd": max(slope_mean_sd, 1e-4),
        "slope_p90": float(np.percentile(valid_slopes, 90.0)),
        "slope_p90_sd": max(slope_p90_sd, 1e-4),
        "roughness": roughness,
        "roughness_sd": max(roughness_sd, 1e-4),
        "relief": relief,
        "relief_sd": max(relief_sd, 1e-4),
        "n_pixels": int(n_pix),
        "elev_min_m": elev_min,
        "elev_max_m": elev_max,
        "slope_min_deg": float(np.min(valid_slopes)),
        "slope_max_deg": float(np.max(valid_slopes)),
        "slope_grid": slope_deg,
        "dem_grid": dem_m,
        "mask_grid": valid_mask,
        "rel_x_m": rel_x,
        "rel_y_m": rel_y,
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


def save_sanity_html(
    diagnostics: list[dict[str, Any]],
    out_html: Path = Path("data/raw/earth/slope_sanity_map.html"),
) -> Path:
    """Save an interactive Plotly sanity-check map of projected slope grids for visual verification."""
    import plotly.graph_objects as go
    from plotly.subplots import make_subplots

    fig = make_subplots(
        rows=2,
        cols=2,
        subplot_titles=[
            f"{d['site_id']} ({d['dst_crs']})<br>"
            f"slope={d['slope_mean']:.2f}° (p90={d['slope_p90']:.2f}°), "
            f"rough={d['roughness']:.1f}m, relief={d['relief']:.1f}m, "
            f"ΔT={d.get('temp_amplitude', float('nan')):.1f}K, "
            f"alb={d.get('albedo', float('nan')):.3f}"
            for d in diagnostics
        ],
    )
    theta = np.linspace(0.0, 2.0 * np.pi, 180)
    for idx, d in enumerate(diagnostics):
        r = idx // 2 + 1
        c = idx % 2 + 1
        x_axis = d["rel_x_m"][0, :]
        y_axis = d["rel_y_m"][:, 0]
        fig.add_trace(
            go.Heatmap(
                z=d["slope_grid"],
                x=x_axis,
                y=y_axis,
                colorscale="YlOrRd",
                zmin=0.0,
                zmax=35.0,
                colorbar={"title": "Slope (°)"} if idx == 0 else None,
                showscale=(idx == 0),
            ),
            row=r,
            col=c,
        )
        fig.add_trace(
            go.Scatter(
                x=d["radius_m"] * np.cos(theta),
                y=d["radius_m"] * np.sin(theta),
                mode="lines",
                line={"color": "cyan", "width": 2, "dash": "dash"},
                name="radius_m = 1000m",
                showlegend=(idx == 0),
            ),
            row=r,
            col=c,
        )
    fig.update_layout(
        title_text="Earth Topography & MODIS LST — Slope (°), Roughness (m), Relief (m), ΔT (K)",
        height=850,
        width=1000,
    )
    out_html.parent.mkdir(parents=True, exist_ok=True)
    fig.write_html(str(out_html))
    return out_html


def run_task2(
    sites: list[SiteSpec] | None = None,
    out_parquet: Path = Path("data/processed/features_earth.parquet"),
) -> pd.DataFrame:
    """Execute DEM topography + MODIS LST extraction and write contract parquet."""
    target_sites = sites if sites is not None else VERIFIED_EARTH_SITES
    rows: list[dict[str, Any]] = []
    diagnostics: list[dict[str, Any]] = []

    print("=== EARTH PIPELINE: COPERNICUS DEM GLO-30, MOD11A2.061 & MCD43A3.061 ===")
    for s in target_sites:
        sid = s["site_id"]
        lat = s["lat"]
        lon = s["lon"]
        radius_m = s["radius_m"]
        dst_crs = get_metric_crs(lat, lon)

        tif_path = fetch_dem_patch(sid, lat, lon, radius_m=radius_m)
        dem_m, transform, summary = reproject_dem_to_metric(tif_path, dst_crs=dst_crs, res_m=30.0)
        stats = compute_slope_in_radius(
            dem_m, transform, lat, lon, dst_crs=dst_crs, radius_m=radius_m
        )
        modis_lst = fetch_mod11a2_temp_amplitude(sid, lat, lon)
        modis_alb = fetch_mcd43a3_albedo(sid, lat, lon)

        alb_str = (
            f"{modis_alb['albedo']:.4f}±{modis_alb['albedo_sd']:.4f} ({modis_alb['tile_id']})"
            if modis_alb is not None
            else "NaN"
        )
        print(
            f"[{sid}] DEM dst={summary['dst_shape']} ({summary['dst_crs']}) | "
            f"MOD11A2={tuple(modis_lst['native_shape'])} res={tuple(modis_lst['native_res_m'])}m"
        )
        print(
            f"   slope_mean={stats['slope_mean']:.3f}±{stats['slope_mean_sd']:.3f}° | "
            f"slope_p90={stats['slope_p90']:.3f}±{stats['slope_p90_sd']:.3f}° | "
            f"roughness={stats['roughness']:.2f}±{stats['roughness_sd']:.2f}m | "
            f"relief={stats['relief']:.2f}±{stats['relief_sd']:.2f}m | "
            f"temp_amp={modis_lst['temp_amplitude']:.2f}±{modis_lst['temp_amplitude_sd']:.2f}K | "
            f"albedo={alb_str}"
        )

        row = make_empty_contract_row(
            site_id=sid,
            name=s["name"],
            role=s["role"],
            lat=lat,
            lon=lon,
            radius_m=radius_m,
            lithology_class=s["lithology_class"],
        )
        for feat in ("slope_mean", "slope_p90", "roughness", "relief"):
            row[feat] = stats[feat]
            row[f"{feat}_sd"] = stats[f"{feat}_sd"]
            row[f"{feat}_src"] = COPERNICUS_DEM_SRC
            row[f"{feat}_res_m"] = 30.0

        row["temp_amplitude"] = modis_lst["temp_amplitude"]
        row["temp_amplitude_sd"] = modis_lst["temp_amplitude_sd"]
        row["temp_amplitude_src"] = modis_lst["temp_amplitude_src"]
        row["temp_amplitude_res_m"] = 1000.0

        if modis_alb is not None:
            row["albedo"] = modis_alb["albedo"]
            row["albedo_sd"] = modis_alb["albedo_sd"]
            row["albedo_src"] = modis_alb["albedo_src"]
            row["albedo_res_m"] = 500.0

        rows.append(row)
        diagnostics.append(
            {
                "site_id": sid,
                "dst_crs": dst_crs,
                "radius_m": radius_m,
                "temp_amplitude": modis_lst["temp_amplitude"],
                "albedo": modis_alb["albedo"] if modis_alb is not None else float("nan"),
                **stats,
            }
        )

    ok_alb, alb_msg = check_mcd43a3_access()
    print(f"\n[MCD43A3.061 Albedo Status] available={ok_alb} -> {alb_msg}")

    df = build_contract_dataframe(rows)
    out_parquet.parent.mkdir(parents=True, exist_ok=True)
    df.to_parquet(out_parquet, index=False)
    html_path = save_sanity_html(diagnostics)
    print(f"Wrote contract parquet: {out_parquet} ({len(df)} rows, {len(df.columns)} cols)")
    print(f"Wrote visual sanity map: {html_path}")
    return df


if __name__ == "__main__":
    run_task2()
