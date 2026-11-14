"""Build 2.22x2.22 km (74x74 @ 30 m) Earth DEM elevation grids co-registered with E5 Sentinel-2 patches."""

from __future__ import annotations

import json
import math
from pathlib import Path
from typing import Any

import numpy as np
from pyproj import Transformer
import rasterio
from rasterio.enums import Resampling
from rasterio.transform import Affine
from rasterio.warp import reproject
from rasterio.windows import Window, bounds as window_bounds

from src.earth.build_atlas import (
    COLLECTION as S2_COLLECTION,
    STAC_SEARCH_URL,
    TARGET_PX as E5_TARGET_PX,
    _make_retrying_session,
    _site_pixel_in_item,
)
from src.earth.dem_pipeline import (
    COPERNICUS_DEM_SRC,
    NASADEM_DEM_SRC,
    fetch_dem_patch,
    get_dem_source,
)
from src.earth.sites import VERIFIED_EARTH_SITES

ATLAS_META_PATH = Path("data/processed/earth_atlas/metadata.json")
OUT_NPZ_PATH = Path("data/processed/earth_3d_grids.npz")
OUT_META_PATH = Path("data/processed/earth_3d_meta.json")

GRID_CELLS = 74
GRID_RES_M = 30.0
WINDOW_SIDE_M = GRID_CELLS * GRID_RES_M  # 2220.0 m (~2.2x2.2 km at 30 m native spacing)
HALF_SIDE_M = WINDOW_SIDE_M / 2.0
E5_FOOTPRINT_M = E5_TARGET_PX * 10.0  # 5120.0 m (512 px @ 10 m)

COPERNICUS_VERSION = (
    "Copernicus DEM GLO-30 DGED (COP-DEM_GLO-30-DGED; "
    "AWS COG / Planetary Computer cop-dem-glo-30, TanDEM-X 2021-04-22; "
    "ESA Product Handbook GEO.2018-1988-2)"
)
NASADEM_VERSION = (
    "NASADEM Merged DEM Global 1 arc second V001 "
    "(fallback only where Copernicus GLO-30 tile N39E044 is absent)"
)
GLO30_SIGMA_Z_REL_M = 1.0


def _fetch_s2_items_by_id(scene_ids: list[str]) -> dict[str, dict[str, Any]]:
    """Fetch STAC item metadata for all unique E5 Sentinel-2 L2A scene IDs."""
    sess = _make_retrying_session()
    items: dict[str, dict[str, Any]] = {}
    unique_ids = sorted(set(scene_ids))
    for i in range(0, len(unique_ids), 20):
        batch = unique_ids[i : i + 20]
        resp = sess.post(
            STAC_SEARCH_URL,
            json={"collections": [S2_COLLECTION], "ids": batch, "limit": len(batch) + 5},
            timeout=(10, 20),
        )
        resp.raise_for_status()
        for feat in resp.json().get("features", []):
            if "id" in feat:
                items[str(feat["id"])] = feat
    missing = [sid for sid in unique_ids if sid not in items]
    if missing:
        raise RuntimeError(f"Missing Sentinel-2 STAC items for E5 scenes: {missing}")
    return items


def _compute_e5_alignment(atlas_entry: dict[str, Any], s2_item: dict[str, Any]) -> dict[str, Any]:
    """Compute exact UTM center and E5 texture UV bounds for a site's 512x512 E5 patch."""
    lat = float(atlas_entry["lat"])
    lon = float(atlas_entry["lon"])
    rc = _site_pixel_in_item(s2_item, lat, lon)
    if rc is None:
        raise ValueError(f"Could not project ({lat}, {lon}) into S2 item {s2_item.get('id')}")
    row, col, _, _ = rc

    epsg = int(s2_item["properties"]["proj:epsg"])
    a, b, x0, d, e, y0 = s2_item["assets"]["visual"]["proj:transform"][:6]
    if abs(abs(float(a)) - 10.0) > 1e-6 or abs(abs(float(e)) - 10.0) > 1e-6 or b != 0 or d != 0:
        raise ValueError(f"Unexpected S2 visual transform in {s2_item.get('id')}: {(a, b, x0, d, e, y0)}")

    half_px = E5_TARGET_PX // 2
    s2_aff = Affine(float(a), 0.0, float(x0), 0.0, float(e), float(y0))
    left, bottom, right, top = window_bounds(Window(col - half_px, row - half_px, E5_TARGET_PX, E5_TARGET_PX), s2_aff)
    x_center = 0.5 * (left + right)
    y_center = 0.5 * (bottom + top)

    to_utm = Transformer.from_crs("EPSG:4326", f"EPSG:{epsg}", always_xy=True)
    to_wgs = Transformer.from_crs(f"EPSG:{epsg}", "EPSG:4326", always_xy=True)
    site_x, site_y = to_utm.transform(lon, lat)
    center_lon, center_lat = to_wgs.transform(x_center, y_center)
    offset_m = math.hypot(x_center - site_x, y_center - site_y)

    half_e5 = E5_FOOTPRINT_M / 2.0
    uv_min = (half_e5 - HALF_SIDE_M) / E5_FOOTPRINT_M
    uv_max = (half_e5 + HALF_SIDE_M) / E5_FOOTPRINT_M
    px_min = round(uv_min * E5_TARGET_PX, 4)
    px_max = round(uv_max * E5_TARGET_PX, 4)

    return {
        "crs_epsg": f"EPSG:{epsg}",
        "x_center_m": round(float(x_center), 3),
        "y_center_m": round(float(y_center), 3),
        "center_lat": round(float(center_lat), 7),
        "center_lon": round(float(center_lon), 7),
        "center_offset_from_site_m": round(float(offset_m), 3),
        "e5_scene_id": str(atlas_entry["scene_id"]),
        "e5_file": str(atlas_entry["file"]),
        "e5_uv_box": [uv_min, uv_min, uv_max, uv_max],
        "e5_px_crop_xyxy": [px_min, px_min, px_max, px_max],
    }


def _extract_centered_dem_grid(
    src_tif: Path,
    dst_crs: str,
    x_center: float,
    y_center: float,
) -> tuple[np.ndarray, list[float]]:
    """Reproject a DEM patch into an exact north-up 74x74 grid at 30 m centered on (x_center, y_center)."""
    dst_transform = Affine(
        GRID_RES_M,
        0.0,
        x_center - HALF_SIDE_M,
        0.0,
        -GRID_RES_M,
        y_center + HALF_SIDE_M,
    )
    dst_grid = np.full((GRID_CELLS, GRID_CELLS), np.nan, dtype=np.float32)
    with rasterio.open(src_tif) as src:
        reproject(
            source=rasterio.band(src, 1),
            destination=dst_grid,
            src_transform=src.transform,
            src_crs=src.crs,
            dst_transform=dst_transform,
            dst_crs=dst_crs,
            src_nodata=src.nodata if src.nodata is not None else np.nan,
            dst_nodata=np.nan,
            resampling=Resampling.bilinear,
        )
    if not np.all(np.isfinite(dst_grid)):
        n_bad = int(np.sum(~np.isfinite(dst_grid)))
        raise ValueError(f"Non-finite cells ({n_bad}) in {src_tif.name} centered grid")
    aff_list = [round(float(v), 3) for v in dst_transform[:6]]
    return dst_grid, aff_list


def build_earth_3d_grids(
    atlas_meta_path: Path = ATLAS_META_PATH,
    out_npz: Path = OUT_NPZ_PATH,
    out_meta: Path = OUT_META_PATH,
    raw_dir: Path = Path("data/raw/earth"),
) -> dict[str, Any]:
    """Generate compressed 74x74 Earth 3D DEM grids aligned with E5 patches and save metadata JSON."""
    if not atlas_meta_path.exists():
        raise FileNotFoundError(f"Missing E5 metadata JSON: {atlas_meta_path}")
    atlas_raw = json.loads(atlas_meta_path.read_text(encoding="utf-8"))
    atlas_by_id = {entry["site_id"]: entry for entry in atlas_raw.get("sites", [])}

    missing_atlas = [s["site_id"] for s in VERIFIED_EARTH_SITES if s["site_id"] not in atlas_by_id]
    if missing_atlas:
        raise RuntimeError(f"Sites missing from E5 metadata: {missing_atlas}")

    s2_items = _fetch_s2_items_by_id([atlas_by_id[s["site_id"]]["scene_id"] for s in VERIFIED_EARTH_SITES])

    grids: dict[str, np.ndarray] = {}
    site_records: list[dict[str, Any]] = []
    source_counts: dict[str, int] = {}

    for site in VERIFIED_EARTH_SITES:
        site_id = site["site_id"]
        lat = float(site["lat"])
        lon = float(site["lon"])
        atlas_entry = atlas_by_id[site_id]
        s2_item = s2_items[atlas_entry["scene_id"]]

        align = _compute_e5_alignment(atlas_entry, s2_item)
        dem_tif = fetch_dem_patch(site_id, lat, lon, radius_m=1000.0, raw_dir=raw_dir)
        dem_src = get_dem_source(dem_tif)
        source_counts[dem_src] = source_counts.get(dem_src, 0) + 1

        grid, aff_list = _extract_centered_dem_grid(
            dem_tif,
            align["crs_epsg"],
            align["x_center_m"],
            align["y_center_m"],
        )
        grids[site_id] = grid

        is_glo30 = dem_src == COPERNICUS_DEM_SRC
        elev_min = float(np.min(grid))
        elev_max = float(np.max(grid))
        site_records.append(
            {
                "site_id": site_id,
                "name": site["name"],
                "role": site["role"],
                "site_lat": lat,
                "site_lon": lon,
                **align,
                "window_side_m": WINDOW_SIDE_M,
                "res_m": GRID_RES_M,
                "shape": [GRID_CELLS, GRID_CELLS],
                "affine_utm": aff_list,
                "bounds_utm_m": [
                    round(align["x_center_m"] - HALF_SIDE_M, 3),
                    round(align["y_center_m"] - HALF_SIDE_M, 3),
                    round(align["x_center_m"] + HALF_SIDE_M, 3),
                    round(align["y_center_m"] + HALF_SIDE_M, 3),
                ],
                "dem_source": dem_src,
                "dem_version": COPERNICUS_VERSION if is_glo30 else NASADEM_VERSION,
                "vertical_datum": "EGM2008" if is_glo30 else "EGM96",
                "sigma_z_rel_m": GLO30_SIGMA_Z_REL_M if is_glo30 else None,
                "elev_min_m": round(elev_min, 2),
                "elev_max_m": round(elev_max, 2),
                "elev_mean_m": round(float(np.mean(grid)), 2),
                "elev_std_m": round(float(np.std(grid)), 2),
                "relief_m": round(elev_max - elev_min, 2),
            }
        )

    out_npz.parent.mkdir(parents=True, exist_ok=True)
    tmp_npz = out_npz.with_suffix(".tmp")
    with tmp_npz.open("wb") as f:
        np.savez_compressed(f, **grids)
    tmp_npz.replace(out_npz)

    meta_payload: dict[str, Any] = {
        "purpose": (
            "Compact 3D terrain visualization grids aligned to E5 Sentinel-2 patch centers; "
            "visualization only — does not generate new contract features or alter features_earth.parquet *_src."
        ),
        "primary_source": COPERNICUS_DEM_SRC,
        "primary_version": COPERNICUS_VERSION,
        "fallback_source": NASADEM_DEM_SRC,
        "fallback_version": NASADEM_VERSION,
        "fallback_sites": [r["site_id"] for r in site_records if r["dem_source"] != COPERNICUS_DEM_SRC],
        "source_counts": source_counts,
        "glo30_sigma_z_rel_m": GLO30_SIGMA_Z_REL_M,
        "glo30_sigma_z_rel_ref": "Airbus / ESA Copernicus DEM Product Handbook (2022, GEO.2018-1988-2, Sec 4.2: LE90 < 2.0 m)",
        "window_side_m": WINDOW_SIDE_M,
        "grid_res_m": GRID_RES_M,
        "grid_shape": [GRID_CELLS, GRID_CELLS],
        "dtype": "float32",
        "units": "meters",
        "vertical_reference": (
            "EGM2008 orthometric height for Copernicus_DEM_GLO-30 (39 sites); "
            "EGM96 orthometric height for NASADEM_HGT_v001 fallback (earth_agri_dogubayazit_flow)"
        ),
        "e5_alignment": (
            "Grid center (x_center_m, y_center_m) matches the exact geometric center of the "
            "512x512 (5120x5120 m) Sentinel-2 L2A visual patch in data/processed/earth_atlas/<site_id>.webp; "
            "grid edges correspond to exact E5 pixels [145:367, 145:367] (UV [0.283203125, 0.716796875])."
        ),
        "site_count": len(site_records),
        "npz_file": out_npz.name,
        "npz_size_bytes": out_npz.stat().st_size,
        "sites": site_records,
    }

    tmp_meta = out_meta.with_suffix(".tmp")
    tmp_meta.write_text(json.dumps(meta_payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    tmp_meta.replace(out_meta)
    return meta_payload


if __name__ == "__main__":
    summary = build_earth_3d_grids()
    print(f"Sites: {summary['site_count']} | Sources: {summary['source_counts']}")
    print(
        f"NPZ: {OUT_NPZ_PATH} ({summary['npz_size_bytes']:,} bytes = "
        f"{summary['npz_size_bytes'] / (1024 * 1024):.3f} MB)"
    )
    print(f"Meta: {OUT_META_PATH} ({OUT_META_PATH.stat().st_size:,} bytes)")
    max_off = max(r["center_offset_from_site_m"] for r in summary["sites"])
    min_z = min(r["elev_min_m"] for r in summary["sites"])
    max_z = max(r["elev_max_m"] for r in summary["sites"])
    print(f"Max E5 center offset: {max_off:.2f} m | Elevation span across 40 sites: [{min_z:.1f} m, {max_z:.1f} m]")
