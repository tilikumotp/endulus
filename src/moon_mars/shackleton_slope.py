"""Extract real LRO LOLA (slope, roughness, relief, albedo) and Diviner (temp_amplitude) features for 5 Lunar South Pole reference sites."""
from __future__ import annotations

import argparse
from concurrent.futures import ThreadPoolExecutor
import json
import math
import struct
import urllib.request
from pathlib import Path
from typing import TypedDict

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import rasterio
import requests
from pyproj import Transformer

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
RAW_DIR = REPO_ROOT / "data" / "raw" / "moon"
PROCESSED_PATH = REPO_ROOT / "data" / "processed" / "features_moon.parquet"
PLOT_PATH = RAW_DIR / "shackleton_slope_check.png"

PGDA_ROOT = "https://pgda.gsfc.nasa.gov/data/LOLA_5mpp"
LDAM_LBL_FILENAME = "LDAM_50S_1000M_FLOAT.LBL"
LDAM_IMG_FILENAME = "LDAM_50S_1000M_FLOAT.IMG"
DIVINER_PCP_FILENAME = "pcp_avg_tbol_pols_sum_ltim01_240.tab"

MOON_STEREO_PROJ4 = (
    "+proj=stere +lat_0=-90 +lon_0=0 +k=1 +x_0=0 +y_0=0 +R=1737400 +units=m +no_defs"
)
MOON_GEOD_PROJ4 = "+proj=longlat +R=1737400 +no_defs"

ALBEDO_SRC = "LRO-L-LOLA-4-GDR-V1.0:LDAM_50S_1000M_V1.0_broadband_eq"
BROADBAND_ALBEDO_FACTOR = 0.38  # Zero-phase 1064nm normal to broadband solar hemispherical albedo (Vasavada et al. 2012; Hayne et al. 2017)
DIVINER_SRC = "LRO-L-DLRE-5-PCP-V1.0:pcp_avg_tbol_pols_240m_v2022"
LITHOLOGY_SRC = "LRO_LOLA_Diviner_SouthPole_Regolith_Zuber2012_Spudis2008"

DEFAULT_RADIUS_M = 1000.0

IDENTITY_COLS = ["site_id", "name", "body", "role", "lat", "lon", "radius_m"]
FEATURES = [
    "slope_mean",
    "slope_p90",
    "roughness",
    "relief",
    "temp_amplitude",
    "thermal_inertia",
    "albedo",
]
NATIVE_RES_M = {
    "slope_mean": 5.0,
    "slope_p90": 5.0,
    "roughness": 5.0,
    "relief": 5.0,
    "temp_amplitude": 240.0,
    "thermal_inertia": 240.0,
    "albedo": 1000.0,
}


class MoonSiteSpec(TypedDict):
    """Specification of a literature- and NASA-PGDA-verified Lunar South Pole reference site."""

    site_id: str
    name: str
    pgda_site: str
    dem_src: str
    lat: float
    lon: float
    radius_m: float
    lithology_class: str
    citation: str


VERIFIED_MOON_SITES: list[MoonSiteSpec] = [
    {
        "site_id": "moon_shackleton_rim",
        "name": "Shackleton Crater Rim (Site 04 ROI)",
        "pgda_site": "Site04",
        "dem_src": "LRO_LOLA_PGDA_Site04_5mpp_v2021",
        "lat": -89.7800,
        "lon": -156.3201,
        "radius_m": DEFAULT_RADIUS_M,
        "lithology_class": "regolith",
        "citation": (
            "Mazarico et al. (2011, Icarus 211:1066-1081) & Barker et al. (2021, PSS 203:105119), "
            "NASA GSFC PGDA Site04_ROIs.shp ROI #3 (X=-2678.8 m, Y=-6108.3 m)."
        ),
    },
    {
        "site_id": "moon_connecting_ridge",
        "name": "Connecting Ridge (Shackleton-de Gerlache Ridge, Site 01 ROI)",
        "pgda_site": "Site01",
        "dem_src": "LRO_LOLA_PGDA_Site01_5mpp_v2021",
        "lat": -89.4624,
        "lon": -137.0871,
        "radius_m": DEFAULT_RADIUS_M,
        "lithology_class": "regolith",
        "citation": (
            "Mazarico et al. (2011, Icarus 211:1066-1081) & Barker et al. (2021, PSS 203:105119), "
            "NASA GSFC PGDA Site01_ROIs.shp ROI #5 (X=-11100.8 m, Y=-11940.5 m); Artemis III Connecting Ridge."
        ),
    },
    {
        "site_id": "moon_de_gerlache_rim",
        "name": "de Gerlache Crater Rim (Site 11 ROI)",
        "pgda_site": "Site11",
        "dem_src": "LRO_LOLA_PGDA_Site11_5mpp_v2021",
        "lat": -88.6683,
        "lon": -68.3754,
        "radius_m": DEFAULT_RADIUS_M,
        "lithology_class": "regolith",
        "citation": (
            "Mazarico et al. (2011, Icarus 211:1066-1081) & Barker et al. (2021, PSS 203:105119), "
            "NASA GSFC PGDA Site11_ROIs.shp ROI #1 (X=-37540.7 m, Y=14882.0 m); Artemis III de Gerlache Rim."
        ),
    },
    {
        "site_id": "moon_shackleton_peak",
        "name": "Peak Near Shackleton (Site 07 ROI)",
        "pgda_site": "Site07",
        "dem_src": "LRO_LOLA_PGDA_Site07_5mpp_v2021",
        "lat": -88.8063,
        "lon": 123.5451,
        "radius_m": DEFAULT_RADIUS_M,
        "lithology_class": "anorthosite",
        "citation": (
            "Mazarico et al. (2011, Icarus 211:1066-1081) & Barker et al. (2021, PSS 203:105119), "
            "NASA GSFC PGDA Site07_ROIs.shp ROI #1 (X=30168.4 m, Y=-20002.2 m); Artemis III Peak Near Shackleton."
        ),
    },
    {
        "site_id": "moon_faustini_rim",
        "name": "Faustini Crater Rim A (PGDA LM7 Center)",
        "pgda_site": "LM7",
        "dem_src": "LRO_LOLA_PGDA_LM7_5mpp_v2021",
        "lat": -87.8897,
        "lon": 90.0000,
        "radius_m": DEFAULT_RADIUS_M,
        "lithology_class": "impact_breccia",
        "citation": (
            "Barker et al. (2021, PSS 203:105119), NASA GSFC PGDA Product 78 LM7_final_adj_5mpp_surf.tif "
            "grid center (X=64000.0 m, Y=0.0 m); Artemis III Faustini Rim A candidate region."
        ),
    },
]


def ordered_columns() -> list[str]:
    """Return all 37 contract columns in exact AGENTS.md section 5 order."""
    cols = list(IDENTITY_COLS)
    for feat in FEATURES:
        cols += [feat, f"{feat}_sd", f"{feat}_src", f"{feat}_res_m"]
    cols += ["lithology_class", "lithology_class_src"]
    return cols


def ensure_downloaded(url: str, filename: str, min_bytes: int = 1000) -> Path:
    """Download a file into data/raw/moon/ if not already present."""
    RAW_DIR.mkdir(parents=True, exist_ok=True)
    dest = RAW_DIR / filename
    if dest.exists() and dest.stat().st_size >= min_bytes:
        return dest
    print(f"[INDIRILIYOR] {url} -> {dest}")
    urllib.request.urlretrieve(url, dest)
    return dest


def _fetch_range(url: str, start: int, end: int) -> bytes:
    """Fetch an inclusive byte range [start, end] from a remote HTTP server supporting Range requests."""
    resp = requests.get(url, headers={"Range": f"bytes={start}-{end}"}, timeout=30)
    resp.raise_for_status()
    return resp.content


def fetch_pgda_window(
    site_id: str,
    pgda_site: str,
    suffix: str,
    x0_m: float,
    y0_m: float,
    buffer_m: float = 1100.0,
) -> tuple[np.ndarray, np.ndarray, np.ndarray, float, float]:
    """Read or fetch via HTTP Range a projected 5 m/px LOLA DEM window around (x0_m, y0_m) and cache in data/raw/moon/."""
    RAW_DIR.mkdir(parents=True, exist_ok=True)
    cache_npz = RAW_DIR / f"{site_id}_{pgda_site}_{suffix}_win.npz"
    if cache_npz.exists():
        d = np.load(cache_npz)
        return d["sub"], d["xs"], d["ys"], float(d["dx"]), float(d["dy"])

    local_full = RAW_DIR / f"{pgda_site}_final_adj_5mpp_{suffix}.tif"
    url = f"{PGDA_ROOT}/{pgda_site}/{pgda_site}_final_adj_5mpp_{suffix}.tif"

    if local_full.exists() and local_full.stat().st_size > 1_000_000:
        with open(local_full, "rb") as f:
            hdr = f.read(65536)
            ifd_off = struct.unpack("<I", hdr[4:8])[0]
            n_entries = struct.unpack("<H", hdr[ifd_off : ifd_off + 2])[0]
            tags = {
                struct.unpack("<HHII", hdr[ifd_off + 2 + i * 12 : ifd_off + 14 + i * 12])[0]: struct.unpack(
                    "<HHII", hdr[ifd_off + 2 + i * 12 : ifd_off + 14 + i * 12]
                )[1:]
                for i in range(n_entries)
            }
            w, h = tags[256][2], tags[257][2]
            strip_off_pos = tags[273][2]
            dx, dy, _ = struct.unpack("<3d", hdr[tags[33550][2] : tags[33550][2] + 24])
            _, _, _, ulx, uly, _ = struct.unpack("<6d", hdr[tags[33922][2] : tags[33922][2] + 48])
            f.seek(strip_off_pos)
            strip_offsets = struct.unpack(f"<{h}I", f.read(4 * h))
            c0 = max(0, int(math.floor((x0_m - buffer_m - ulx) / dx)))
            c1 = min(w, int(math.ceil((x0_m + buffer_m - ulx) / dx)) + 1)
            r0 = max(0, int(math.floor((uly - (y0_m + buffer_m)) / dy)))
            r1 = min(h, int(math.ceil((uly - (y0_m - buffer_m)) / dy)) + 1)
            f.seek(strip_offsets[r0])
            raw = f.read((r1 - r0) * w * 4)
    else:
        hdr = _fetch_range(url, 0, 65535)
        ifd_off = struct.unpack("<I", hdr[4:8])[0]
        n_entries = struct.unpack("<H", hdr[ifd_off : ifd_off + 2])[0]
        tags = {
            struct.unpack("<HHII", hdr[ifd_off + 2 + i * 12 : ifd_off + 14 + i * 12])[0]: struct.unpack(
                "<HHII", hdr[ifd_off + 2 + i * 12 : ifd_off + 14 + i * 12]
            )[1:]
            for i in range(n_entries)
        }
        w, h = tags[256][2], tags[257][2]
        strip_off_pos = tags[273][2]
        dx, dy, _ = struct.unpack("<3d", hdr[tags[33550][2] : tags[33550][2] + 24])
        _, _, _, ulx, uly, _ = struct.unpack("<6d", hdr[tags[33922][2] : tags[33922][2] + 48])
        need_end = strip_off_pos + 4 * h
        if need_end > len(hdr):
            hdr = _fetch_range(url, 0, need_end + 1024)
        strip_offsets = struct.unpack(f"<{h}I", hdr[strip_off_pos : strip_off_pos + 4 * h])
        c0 = max(0, int(math.floor((x0_m - buffer_m - ulx) / dx)))
        c1 = min(w, int(math.ceil((x0_m + buffer_m - ulx) / dx)) + 1)
        r0 = max(0, int(math.floor((uly - (y0_m + buffer_m)) / dy)))
        r1 = min(h, int(math.ceil((uly - (y0_m - buffer_m)) / dy)) + 1)
        byte_start = strip_offsets[r0]
        byte_end = strip_offsets[r1 - 1] + w * 4 - 1
        chunk_size = 512 * 1024
        ranges = [
            (cur, min(byte_end, cur + chunk_size - 1))
            for cur in range(byte_start, byte_end + 1, chunk_size)
        ]
        with ThreadPoolExecutor(max_workers=12) as pool:
            parts = list(pool.map(lambda se: _fetch_range(url, se[0], se[1]), ranges))
        raw = b"".join(parts)

    rows_arr = np.frombuffer(raw, dtype="<f4").reshape(r1 - r0, w)
    sub = rows_arr[:, c0:c1].astype(np.float64)
    sub[np.abs(sub) > 1e10] = np.nan
    xs = ulx + (np.arange(c0, c1) + 0.5) * dx
    ys = uly - (np.arange(r0, r1) + 0.5) * dy
    np.savez_compressed(cache_npz, sub=sub, xs=xs, ys=ys, dx=dx, dy=dy)
    return sub, xs, ys, float(dx), float(dy)


def extract_site_topography(site: MoonSiteSpec) -> dict[str, object]:
    """Compute slope_mean, slope_p90, planar-detrended roughness, relief, and 1-sigma SDs inside radius_m."""
    to_proj = Transformer.from_crs(MOON_GEOD_PROJ4, MOON_STEREO_PROJ4, always_xy=True)
    x0_m, y0_m = to_proj.transform(site["lon"], site["lat"])
    radius_m = site["radius_m"]

    elev, xs, ys, dx_m, dy_m = fetch_pgda_window(
        site["site_id"], site["pgda_site"], "surf", x0_m, y0_m, buffer_m=radius_m + 100.0
    )
    slp_err, _, _, _, _ = fetch_pgda_window(
        site["site_id"], site["pgda_site"], "slperr", x0_m, y0_m, buffer_m=radius_m + 100.0
    )

    if dx_m < 0.5 or dx_m > 10000.0:
        raise ValueError(f"Projeksiyon birimi metre degil! dx={dx_m}")

    dz_dy, dz_dx = np.gradient(elev, dy_m, dx_m)
    slope_deg = np.degrees(np.arctan(np.hypot(dz_dx, dz_dy)))

    xx, yy = np.meshgrid(xs, ys)
    dist_m = np.hypot(xx - x0_m, yy - y0_m)
    mask = (dist_m <= radius_m) & np.isfinite(slope_deg) & np.isfinite(elev)
    n_pix = int(np.sum(mask))
    if n_pix == 0:
        raise ValueError(f"Secilen koordinat ({site['lat']}, {site['lon']}) DEM sinirlari disinda!")

    site_slopes = slope_deg[mask]
    site_errs = slp_err[mask & np.isfinite(slp_err)]
    site_elev = elev[mask]
    dx_local = xx[mask] - x0_m
    dy_local = yy[mask] - y0_m

    design_mat = np.column_stack([dx_local, dy_local, np.ones_like(site_elev)])
    coeffs, _, _, _ = np.linalg.lstsq(design_mat, site_elev, rcond=None)
    residuals = site_elev - (design_mat @ coeffs)
    roughness_m = float(np.std(residuals, ddof=1))
    relief_m = float(np.max(site_elev) - np.min(site_elev))

    slope_mean = float(np.mean(site_slopes))
    slope_p90 = float(np.percentile(site_slopes, 90.0))

    # 200-draw bootstrap (docs/data_notes.md section 1) + PGDA RMS uncertainty (Barker et al. 2021)
    rng = np.random.default_rng(42)
    b_means, b_p90s, b_rough = [], [], []
    for _ in range(200):
        idx = rng.integers(0, n_pix, size=n_pix)
        b_means.append(np.mean(site_slopes[idx]))
        b_p90s.append(np.percentile(site_slopes[idx], 90.0))
        b_rough.append(np.std(residuals[idx], ddof=1))

    boot_mean_sd = float(np.std(b_means, ddof=1))
    boot_p90_sd = float(np.std(b_p90s, ddof=1))
    boot_rough_sd = float(np.std(b_rough, ddof=1))
    rms_model_sd = float(np.nanmedian(site_errs)) if len(site_errs) > 0 else boot_mean_sd

    return {
        "x0_m": float(x0_m),
        "y0_m": float(y0_m),
        "n_pixels": n_pix,
        "elev_min_m": float(np.min(site_elev)),
        "elev_max_m": float(np.max(site_elev)),
        "slope_min_deg": float(np.min(site_slopes)),
        "slope_max_deg": float(np.max(site_slopes)),
        "slope_mean": slope_mean,
        "slope_mean_sd": float(math.hypot(rms_model_sd, boot_mean_sd)),
        "slope_p90": slope_p90,
        "slope_p90_sd": float(math.hypot(rms_model_sd, boot_p90_sd)),
        "roughness": roughness_m,
        "roughness_sd": float(math.hypot(0.35, boot_rough_sd)),
        "relief": relief_m,
        "relief_sd": 0.50,
        "elev_win": elev,
        "slope_win": slope_deg,
        "xs_m": xs,
        "ys_m": ys,
    }


def extract_albedo_metrics(ldam_lbl_path: Path, x0_m: float, y0_m: float, radius_m: float) -> tuple[float, float]:
    """Extract broadband solar hemispherical albedo (0.38 * LOLA 1064 nm normal albedo) and 1-sigma std inside radius_m."""
    with rasterio.open(ldam_lbl_path) as src:
        alb = src.read(1).astype(np.float64)
        t = src.transform
        cols = np.arange(src.width)
        rows = np.arange(src.height)
        xs = t.c + (cols + 0.5) * t.a
        ys = t.f + (rows + 0.5) * t.e
        xx, yy = np.meshgrid(xs, ys)
        dist = np.hypot(xx - x0_m, yy - y0_m)
        mask = (dist <= radius_m) & (alb > 0.0) & (alb < 1.0)
        if int(np.sum(mask)) < 2:
            mask = (dist <= max(radius_m, 1500.0)) & (alb > 0.0) & (alb < 1.0)
        vals = alb[mask] * BROADBAND_ALBEDO_FACTOR
        return float(np.mean(vals)), float(np.std(vals, ddof=1))


def _binary_search_pcp_tab(pcp_tab_path: Path, lat: float, lon: float, radius_m: float) -> list[float]:
    """Binary-search the sorted 59-byte fixed-record Diviner polar table for cells within radius_m."""
    to_proj = Transformer.from_crs(MOON_GEOD_PROJ4, MOON_STEREO_PROJ4, always_xy=True)
    x0, _ = to_proj.transform(lon, lat)
    xn0 = x0 / 1_737_400.0
    rn = radius_m / 1_737_400.0

    file_size = pcp_tab_path.stat().st_size
    with open(pcp_tab_path, "rb") as f:
        hdr_len = len(f.readline())
        rec_len = len(f.readline())
        n_recs = (file_size - hdr_len) // rec_len

        def get_x(idx: int) -> float:
            f.seek(hdr_len + idx * rec_len)
            return float(f.read(rec_len).decode("ascii", errors="ignore").split(",")[0])

        lo, hi = 0, n_recs - 1
        while lo < hi:
            mid = (lo + hi) // 2
            if get_x(mid) < xn0 - rn - 0.001:
                lo = mid + 1
            else:
                hi = mid
        s_idx = lo
        lo, hi = s_idx, n_recs - 1
        while lo < hi:
            mid = (lo + hi) // 2
            if get_x(mid) <= xn0 + rn + 0.001:
                lo = mid + 1
            else:
                hi = mid
        e_idx = lo
        f.seek(hdr_len + s_idx * rec_len)
        block = f.read((e_idx - s_idx) * rec_len).decode("ascii", errors="ignore")

    vals: list[float] = []
    lat1, lon1 = math.radians(lat), math.radians(lon)
    for line in block.splitlines():
        parts = line.replace(",", " ").split()
        if len(parts) == 5:
            clat, clon, tbol = float(parts[3]), float(parts[2]), float(parts[4])
            if tbol > 0.0:
                lat2, lon2 = math.radians(clat), math.radians(clon)
                cos_d = math.sin(lat1) * math.sin(lat2) + math.cos(lat1) * math.cos(lat2) * math.cos(lon1 - lon2)
                d_m = 1_737_400.0 * math.acos(max(-1.0, min(1.0, cos_d)))
                if d_m <= radius_m:
                    vals.append(tbol)
    return vals


def extract_diviner_temp_metrics(
    site_id: str,
    pcp_tab_path: Path,
    lat: float,
    lon: float,
    radius_m: float,
) -> tuple[float, float]:
    """Extract bolometric surface temperature amplitude (max - min, K) and 200-draw bootstrap SD inside radius_m."""
    cache_json = RAW_DIR / f"{site_id}_diviner_tbol_240m.json"
    if cache_json.exists():
        cached = json.loads(cache_json.read_text(encoding="utf-8"))
        vals = cached.get("vals_k", [])
        if vals:
            arr = np.asarray(vals, dtype=np.float64)
        else:
            arr = np.asarray(_binary_search_pcp_tab(pcp_tab_path, lat, lon, radius_m), dtype=np.float64)
    else:
        arr = np.asarray(_binary_search_pcp_tab(pcp_tab_path, lat, lon, radius_m), dtype=np.float64)

    temp_amp = float(np.max(arr) - np.min(arr))
    rng = np.random.default_rng(42)
    b_amps = [
        float(np.max(arr[rng.integers(0, len(arr), len(arr))]) - np.min(arr[rng.integers(0, len(arr), len(arr))]))
        for _ in range(200)
    ]
    temp_amp_sd = float(max(np.std(b_amps, ddof=1), 2.5))
    return temp_amp, temp_amp_sd


def save_sanity_plot(site_results: list[tuple[MoonSiteSpec, dict[str, object]]], out_path: Path) -> None:
    """Plot South Polar Stereographic slope maps with 1 km analysis circles for all 5 reference sites."""
    n_sites = len(site_results)
    fig, axes = plt.subplots(1, n_sites, figsize=(4.2 * n_sites, 4.4), dpi=130)
    if n_sites == 1:
        axes = [axes]

    for ax, (site, stats) in zip(axes, site_results):
        xs_km = np.asarray(stats["xs_m"], dtype=float) / 1e3
        ys_km = np.asarray(stats["ys_m"], dtype=float) / 1e3
        x0_km = float(stats["x0_m"]) / 1e3
        y0_km = float(stats["y0_m"]) / 1e3
        rad_km = site["radius_m"] / 1e3
        slope_win = np.asarray(stats["slope_win"], dtype=float)
        extent_km = [float(xs_km.min()), float(xs_km.max()), float(ys_km.min()), float(ys_km.max())]

        im = ax.imshow(slope_win, extent=extent_km, origin="upper", cmap="inferno", vmin=0, vmax=40)
        circle = plt.Circle((x0_km, y0_km), rad_km, edgecolor="cyan", facecolor="none", linewidth=2.0)
        ax.add_patch(circle)
        ax.plot(x0_km, y0_km, "c+", markersize=8, markeredgewidth=1.8)
        ax.set_title(
            f"{site['site_id']}\n"
            f"mean={float(stats['slope_mean']):.2f}°, p90={float(stats['slope_p90']):.2f}°\n"
            f"rough={float(stats['roughness']):.1f}m, relief={float(stats['relief']):.0f}m",
            fontsize=8.5,
        )
        ax.set_xlabel("Stereografik X (km)", fontsize=8)
        ax.set_ylabel("Stereografik Y (km)", fontsize=8)
        fig.colorbar(im, ax=ax, fraction=0.046, pad=0.04, label="Eğim (°)")

    fig.tight_layout()
    out_path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(out_path)
    plt.close(fig)


def build_contract_dataframe(rows: list[dict[str, object]]) -> pd.DataFrame:
    """Create the Moon reference DataFrame with all 37 contract columns in exact AGENTS.md order."""
    df = pd.DataFrame(rows)
    for feat in FEATURES:
        df[feat] = df[feat].astype("float64")
        df[f"{feat}_sd"] = df[f"{feat}_sd"].astype("float64")
        df[f"{feat}_res_m"] = df[f"{feat}_res_m"].astype("float64")
        df[f"{feat}_src"] = df[f"{feat}_src"].fillna("").astype("string")
    df["lithology_class"] = df["lithology_class"].fillna("").astype("string")
    df["lithology_class_src"] = df["lithology_class_src"].fillna("").astype("string")
    return df[ordered_columns()]


def main() -> int:
    """Run LOLA DEM (+ Diviner & Albedo in stage 2) extraction for all 5 Lunar South Pole reference sites."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--stage",
        type=int,
        choices=[1, 2],
        default=2,
        help="1: DEM mobility features only; 2: Full DEM + Diviner temp_amplitude + LOLA albedo",
    )
    args = parser.parse_args()

    ldam_lbl_path: Path | None = None
    pcp_tab_path: Path | None = None
    if args.stage >= 2:
        ensure_downloaded(
            f"https://imbrium.mit.edu/DATA/LOLA_GDR/POLAR/FLOAT_IMG/{LDAM_IMG_FILENAME}",
            LDAM_IMG_FILENAME,
            1_000_000,
        )
        ldam_lbl_path = ensure_downloaded(
            f"https://imbrium.mit.edu/DATA/LOLA_GDR/POLAR/FLOAT_IMG/{LDAM_LBL_FILENAME}",
            LDAM_LBL_FILENAME,
            500,
        )
        pcp_tab_path = ensure_downloaded(
            f"https://pds-geosciences.wustl.edu/lro/urn-nasa-pds-lro_diviner_derived1/data_derived_pcp/diurnal/ltim/pols/{DIVINER_PCP_FILENAME}",
            DIVINER_PCP_FILENAME,
            1_000_000,
        )

    print(f"=== AY GUNEY KUTBU REFERANS PIPELINE (ASAMA {args.stage}, CRS: {MOON_STEREO_PROJ4}) ===")
    rows: list[dict[str, object]] = []
    site_results: list[tuple[MoonSiteSpec, dict[str, object]]] = []

    for site in VERIFIED_MOON_SITES:
        stats = extract_site_topography(site)
        site_results.append((site, stats))

        row: dict[str, object] = {
            "site_id": site["site_id"],
            "name": site["name"],
            "body": "moon",
            "role": "reference",
            "lat": float(site["lat"]),
            "lon": float(site["lon"]),
            "radius_m": float(site["radius_m"]),
        }
        for feat in FEATURES:
            row[feat] = np.nan
            row[f"{feat}_sd"] = np.nan
            row[f"{feat}_src"] = ""
            row[f"{feat}_res_m"] = float(NATIVE_RES_M[feat])

        for topo_feat in ["slope_mean", "slope_p90", "roughness", "relief"]:
            row[topo_feat] = float(stats[topo_feat])
            row[f"{topo_feat}_sd"] = float(stats[f"{topo_feat}_sd"])
            row[f"{topo_feat}_src"] = site["dem_src"]
            row[f"{topo_feat}_res_m"] = float(NATIVE_RES_M[topo_feat])

        if args.stage >= 2 and ldam_lbl_path is not None and pcp_tab_path is not None:
            temp_amp, temp_amp_sd = extract_diviner_temp_metrics(
                site["site_id"], pcp_tab_path, site["lat"], site["lon"], site["radius_m"]
            )
            albedo_val, albedo_sd = extract_albedo_metrics(
                ldam_lbl_path, float(stats["x0_m"]), float(stats["y0_m"]), site["radius_m"]
            )
            row["temp_amplitude"] = float(temp_amp)
            row["temp_amplitude_sd"] = float(temp_amp_sd)
            row["temp_amplitude_src"] = DIVINER_SRC
            row["temp_amplitude_res_m"] = float(NATIVE_RES_M["temp_amplitude"])

            row["albedo"] = float(albedo_val)
            row["albedo_sd"] = float(albedo_sd)
            row["albedo_src"] = ALBEDO_SRC
            row["albedo_res_m"] = float(NATIVE_RES_M["albedo"])

        row["lithology_class"] = site["lithology_class"]
        row["lithology_class_src"] = LITHOLOGY_SRC
        rows.append(row)

        print(
            f"[{site['site_id']}] ({site['lat']:.4f}°, {site['lon']:.4f}°) -> "
            f"X={float(stats['x0_m']):.1f}m, Y={float(stats['y0_m']):.1f}m | n_pix={stats['n_pixels']}"
        )
        print(
            f"   slope_mean={float(stats['slope_mean']):.4f}±{float(stats['slope_mean_sd']):.4f}° | "
            f"slope_p90={float(stats['slope_p90']):.4f}±{float(stats['slope_p90_sd']):.4f}° | "
            f"roughness={float(stats['roughness']):.4f}±{float(stats['roughness_sd']):.4f}m | "
            f"relief={float(stats['relief']):.4f}±{float(stats['relief_sd']):.4f}m"
        )
        if args.stage >= 2:
            print(
                f"   temp_amplitude={float(row['temp_amplitude']):.4f}±{float(row['temp_amplitude_sd']):.4f}K | "
                f"albedo={float(row['albedo']):.4f}±{float(row['albedo_sd']):.4f} | "
                f"thermal_inertia=NaN (res={row['thermal_inertia_res_m']}m)"
            )

    save_sanity_plot(site_results, PLOT_PATH)
    print(f"[GRAFIK] 5 sahalik gorsel kontrol haritasi kaydedildi: {PLOT_PATH}")

    df = build_contract_dataframe(rows)
    PROCESSED_PATH.parent.mkdir(parents=True, exist_ok=True)
    df.to_parquet(PROCESSED_PATH, index=False)
    print(f"[PARQUET] Sozlesme ciktisi yazildi ({len(df)} satir, {len(df.columns)} kolon): {PROCESSED_PATH}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
