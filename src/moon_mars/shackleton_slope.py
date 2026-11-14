"""Download LRO LOLA South Pole (~16x16 km Shackleton box), compute polar slope, plot, and write contract parquet."""
from __future__ import annotations

import argparse
import math
import urllib.request
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import rasterio
from pyproj import Transformer

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
RAW_DIR = REPO_ROOT / "data" / "raw" / "moon"
PROCESSED_PATH = REPO_ROOT / "data" / "processed" / "features_moon.parquet"
PLOT_PATH = RAW_DIR / "shackleton_slope_check.png"

PGDA_BASE = "https://pgda.gsfc.nasa.gov/data/LOLA_5mpp/Site04"
DEM_FILENAME = "Site04_final_adj_5mpp_surf.tif"
SLPERR_FILENAME = "Site04_final_adj_5mpp_slperr.tif"
PRODUCT_SRC = "LRO_LOLA_PGDA_Site04_5mpp_v2021"

DEFAULT_RADIUS_M = 1000.0

# Official NASA PGDA Site04_ROIs.shp ROI #3 centroid on Shackleton Crater Rim (Barker et al. 2021 / Mazarico et al. 2011)
DEFAULT_SITE_ID = "moon_shackleton_rim"
DEFAULT_SITE_NAME = "Shackleton Crater Rim (Site 04 ROI)"
DEFAULT_LAT = -89.7800
DEFAULT_LON = -156.3201

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


def ordered_columns() -> list[str]:
    """Return all 37 contract columns in exact AGENTS.md section 5 order."""
    cols = list(IDENTITY_COLS)
    for feat in FEATURES:
        cols += [feat, f"{feat}_sd", f"{feat}_src", f"{feat}_res_m"]
    cols += ["lithology_class", "lithology_class_src"]
    return cols


def ensure_downloaded(filename: str) -> Path:
    """Download a PGDA Site04 GeoTIFF into data/raw/moon/ if not already present."""
    RAW_DIR.mkdir(parents=True, exist_ok=True)
    dest = RAW_DIR / filename
    if dest.exists() and dest.stat().st_size > 1_000_000:
        print(f"[RAW] Mevcut dosya kullaniliyor: {dest} ({dest.stat().st_size / 1e6:.2f} MB)")
        return dest
    url = f"{PGDA_BASE}/{filename}"
    print(f"[INDIRILIYOR] {url} -> {dest}")
    urllib.request.urlretrieve(url, dest)
    print(f"[TAMAMLANDI] {dest.name} ({dest.stat().st_size / 1e6:.2f} MB)")
    return dest


def compute_slope_from_dem(dem_path: Path, slperr_path: Path) -> tuple[np.ndarray, np.ndarray, np.ndarray, dict]:
    """Read projected DEM and slope-error rasters, verify CRS in meters, and compute slope in degrees."""
    with rasterio.open(dem_path) as src:
        crs = src.crs
        transform = src.transform
        bounds = src.bounds
        shape = src.shape
        nodata = src.nodata
        dx_m = float(abs(transform.a))
        dy_m = float(abs(transform.e))
        if dx_m < 0.5 or dx_m > 10000.0:
            raise ValueError(f"Projeksiyon birimi metre degil! dx={dx_m}")
        elev = src.read(1).astype(np.float64)
        if nodata is not None:
            elev[elev == nodata] = np.nan

    with rasterio.open(slperr_path) as esrc:
        slp_err = esrc.read(1).astype(np.float64)
        if esrc.nodata is not None:
            slp_err[slp_err == esrc.nodata] = np.nan

    # Compute slope in degrees on the projected Polar Stereographic grid (meters)
    dz_dy, dz_dx = np.gradient(elev, dy_m, dx_m)
    slope_deg = np.degrees(np.arctan(np.hypot(dz_dx, dz_dy)))

    meta = {
        "shape": shape,
        "crs": crs,
        "crs_wkt": str(crs),
        "bounds_m": bounds,
        "transform": transform,
        "res_m": dx_m,
    }
    return elev, slope_deg, slp_err, meta


def extract_site_metrics(
    elev: np.ndarray,
    slope_deg: np.ndarray,
    slp_err: np.ndarray,
    meta: dict,
    lat: float,
    lon: float,
    radius_m: float,
) -> dict[str, float]:
    """Extract slope_mean, slope_p90, and 1-sigma uncertainties inside radius_m around (lat, lon)."""
    transform = meta["transform"]
    rows, cols = meta["shape"]
    crs = meta["crs"]
    to_proj = Transformer.from_crs(crs.geodetic_crs, crs, always_xy=True)
    x0, y0 = to_proj.transform(lon, lat)

    col_idx = np.arange(cols)
    row_idx = np.arange(rows)
    x_coords = transform.c + (col_idx + 0.5) * transform.a
    y_coords = transform.f + (row_idx + 0.5) * transform.e
    xx, yy = np.meshgrid(x_coords, y_coords)

    dist_m = np.hypot(xx - x0, yy - y0)
    mask = (dist_m <= radius_m) & np.isfinite(slope_deg)
    n_pix = int(np.sum(mask))
    if n_pix == 0:
        raise ValueError(f"Secilen koordinat ({lat}, {lon}) -> ({x0:.1f}, {y0:.1f}) m DEM sinirlari disinda!")

    site_slopes = slope_deg[mask]
    site_errs = slp_err[mask & np.isfinite(slp_err)]
    site_elev = elev[mask & np.isfinite(elev)]

    slope_mean = float(np.nanmean(site_slopes))
    slope_p90 = float(np.nanpercentile(site_slopes, 90.0))

    # 1-sigma uncertainty combining NASA PGDA RMS slope uncertainty and spatial standard error
    rms_model_sd = float(np.nanmedian(site_errs)) if len(site_errs) > 0 else float(np.nanstd(site_slopes) / math.sqrt(n_pix))
    spatial_se = float(np.nanstd(site_slopes) / math.sqrt(max(n_pix, 1)))
    slope_mean_sd = float(math.hypot(rms_model_sd, spatial_se))
    slope_p90_sd = float(math.hypot(rms_model_sd, 1.25 * spatial_se))

    return {
        "x0_m": float(x0),
        "y0_m": float(y0),
        "n_pixels": n_pix,
        "elev_min_m": float(np.nanmin(site_elev)),
        "elev_max_m": float(np.nanmax(site_elev)),
        "slope_min_deg": float(np.nanmin(site_slopes)),
        "slope_max_deg": float(np.nanmax(site_slopes)),
        "slope_mean": slope_mean,
        "slope_mean_sd": slope_mean_sd,
        "slope_p90": slope_p90,
        "slope_p90_sd": slope_p90_sd,
    }


def save_sanity_plot(
    elev: np.ndarray,
    slope_deg: np.ndarray,
    meta: dict,
    site_stats: dict[str, float],
    lat: float,
    lon: float,
    radius_m: float,
    out_path: Path,
) -> None:
    """Plot Shackleton elevation and slope maps with the 1 km analysis circle."""
    bounds = meta["bounds_m"]
    extent_km = [bounds.left / 1e3, bounds.right / 1e3, bounds.bottom / 1e3, bounds.top / 1e3]
    x0_km = site_stats["x0_m"] / 1e3
    y0_km = site_stats["y0_m"] / 1e3
    rad_km = radius_m / 1e3

    fig, axes = plt.subplots(1, 2, figsize=(13, 6), dpi=140)
    im0 = axes[0].imshow(elev, extent=extent_km, origin="upper", cmap="terrain")
    axes[0].set_title("LRO LOLA Site04 Yükseklik (DEM, 5 m/piksel)")
    axes[0].set_xlabel("Kutupsal Stereografik X (km)")
    axes[0].set_ylabel("Kutupsal Stereografik Y (km)")
    fig.colorbar(im0, ax=axes[0], label="Yükseklik (m)")

    im1 = axes[1].imshow(slope_deg, extent=extent_km, origin="upper", cmap="inferno", vmin=0, vmax=45)
    axes[1].set_title(
        f"Kutupsal Eğim Haritası (Derece)\n"
        f"mean={site_stats['slope_mean']:.2f}°, p90={site_stats['slope_p90']:.2f}° (r={radius_m:.0f} m)"
    )
    axes[1].set_xlabel("Kutupsal Stereografik X (km)")
    axes[1].set_ylabel("Kutupsal Stereografik Y (km)")
    fig.colorbar(im1, ax=axes[1], label="Eğim (derece)")

    for ax in axes:
        circle = plt.Circle((x0_km, y0_km), rad_km, edgecolor="cyan", facecolor="none", linewidth=2.2, label="r = 1 km")
        ax.add_patch(circle)
        ax.plot(x0_km, y0_km, "c+", markersize=10, markeredgewidth=2)
        ax.annotate(
            f"moon_shackleton_rim\n({lat:.4f}°, {lon:.4f}°)",
            xy=(x0_km, y0_km),
            xytext=(x0_km - 5.2, y0_km + 2.2),
            color="white",
            fontsize=8,
            weight="bold",
            bbox=dict(boxstyle="round,pad=0.25", fc="black", alpha=0.75),
            arrowprops=dict(arrowstyle="->", color="cyan", lw=1.4),
        )

    fig.tight_layout()
    out_path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(out_path)
    plt.close(fig)


def build_contract_dataframe(
    site_id: str,
    name: str,
    lat: float,
    lon: float,
    radius_m: float,
    site_stats: dict[str, float],
) -> pd.DataFrame:
    """Create the 1-row Moon reference DataFrame with all 37 contract columns."""
    row: dict[str, object] = {
        "site_id": site_id,
        "name": name,
        "body": "moon",
        "role": "reference",
        "lat": float(lat),
        "lon": float(lon),
        "radius_m": float(radius_m),
    }
    for feat in FEATURES:
        row[feat] = np.nan
        row[f"{feat}_sd"] = np.nan
        row[f"{feat}_src"] = None
        row[f"{feat}_res_m"] = float(NATIVE_RES_M[feat])

    row["slope_mean"] = float(site_stats["slope_mean"])
    row["slope_mean_sd"] = float(site_stats["slope_mean_sd"])
    row["slope_mean_src"] = PRODUCT_SRC
    row["slope_mean_res_m"] = float(NATIVE_RES_M["slope_mean"])

    row["slope_p90"] = float(site_stats["slope_p90"])
    row["slope_p90_sd"] = float(site_stats["slope_p90_sd"])
    row["slope_p90_src"] = PRODUCT_SRC
    row["slope_p90_res_m"] = float(NATIVE_RES_M["slope_p90"])

    row["lithology_class"] = None
    row["lithology_class_src"] = None

    df = pd.DataFrame([row])
    for feat in FEATURES:
        df[feat] = df[feat].astype("float64")
        df[f"{feat}_sd"] = df[f"{feat}_sd"].astype("float64")
        df[f"{feat}_res_m"] = df[f"{feat}_res_m"].astype("float64")
        df[f"{feat}_src"] = df[f"{feat}_src"].astype("string")
    df["lithology_class"] = df["lithology_class"].astype("string")
    df["lithology_class_src"] = df["lithology_class_src"].astype("string")
    return df[ordered_columns()]


def main() -> int:
    """Run download, polar slope computation, sanity check plot, and parquet write."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--lat", type=float, default=DEFAULT_LAT, help="Shackleton ref latitude (deg)")
    parser.add_argument("--lon", type=float, default=DEFAULT_LON, help="Shackleton ref longitude (deg)")
    parser.add_argument("--radius-m", type=float, default=DEFAULT_RADIUS_M, help="Analysis radius in meters")
    args = parser.parse_args()

    dem_path = ensure_downloaded(DEM_FILENAME)
    slperr_path = ensure_downloaded(SLPERR_FILENAME)

    elev, slope_deg, slp_err, meta = compute_slope_from_dem(dem_path, slperr_path)
    bounds = meta["bounds_m"]
    box_w_km = (bounds.right - bounds.left) / 1e3
    box_h_km = (bounds.top - bounds.bottom) / 1e3

    print("\n=== RASTER OZET BILGILERI (BAGLAMA YUKLENMEDI) ===")
    print(f"Dosya        : {dem_path.name}")
    print(f"Boyut (shape): {meta['shape']} piksel ({box_w_km:.2f} km x {box_h_km:.2f} km)")
    print(f"Cozunurluk   : {meta['res_m']} m/piksel")
    print(f"CRS          : {meta['crs_wkt']}")
    print(f"Bounds (m)   : left={bounds.left:.1f}, bottom={bounds.bottom:.1f}, right={bounds.right:.1f}, top={bounds.top:.1f}")
    print(f"Kutu Yukseklik (min..max): {np.nanmin(elev):.2f} m .. {np.nanmax(elev):.2f} m")
    print(f"Kutu Egim      (min..max): {np.nanmin(slope_deg):.3f} deg .. {np.nanmax(slope_deg):.3f} deg")

    site_stats = extract_site_metrics(elev, slope_deg, slp_err, meta, args.lat, args.lon, args.radius_m)
    print("\n=== REFERANS SAHA SONUCLARI (moon_shackleton_rim, r=1000 m) ===")
    print(f"Koordinat (lat, lon) : ({args.lat:.4f} deg, {args.lon:.4f} deg)")
    print(f"Kutupsal (X, Y)      : ({site_stats['x0_m']:.1f} m, {site_stats['y0_m']:.1f} m)")
    print(f"Piksel sayisi (r=1km): {site_stats['n_pixels']}")
    print(f"Yukseklik (min..max) : {site_stats['elev_min_m']:.2f} m .. {site_stats['elev_max_m']:.2f} m")
    print(f"Egim      (min..max) : {site_stats['slope_min_deg']:.3f} deg .. {site_stats['slope_max_deg']:.3f} deg")
    print(f"slope_mean           : {site_stats['slope_mean']:.4f} deg (+/- {site_stats['slope_mean_sd']:.4f} deg)")
    print(f"slope_p90            : {site_stats['slope_p90']:.4f} deg (+/- {site_stats['slope_p90_sd']:.4f} deg)")

    save_sanity_plot(elev, slope_deg, meta, site_stats, args.lat, args.lon, args.radius_m, PLOT_PATH)
    print(f"\n[GRAFIK] Gorsel kontrol haritasi kaydedildi: {PLOT_PATH}")

    df = build_contract_dataframe(DEFAULT_SITE_ID, DEFAULT_SITE_NAME, args.lat, args.lon, args.radius_m, site_stats)
    PROCESSED_PATH.parent.mkdir(parents=True, exist_ok=True)
    df.to_parquet(PROCESSED_PATH, index=False)
    print(f"[PARQUET] Sozlesme ciktisi yazildi ({len(df.columns)} kolon): {PROCESSED_PATH}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
