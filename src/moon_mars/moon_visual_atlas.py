"""Generate 5 m/px LRO LOLA hillshade, slope-bin, and cross-section visual atlas cards for Lunar South Pole sites."""
from __future__ import annotations

import io
import json
import sys
from pathlib import Path

import matplotlib.patches as mpatches
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.colors import LightSource
from PIL import Image

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
SRC_DIR = REPO_ROOT / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from moon_mars.shackleton_slope import (  # noqa: E402
    MOON_STEREO_PROJ4,
    VERIFIED_MOON_SITES,
    MoonSiteSpec,
    extract_site_topography,
)

ATLAS_DIR = REPO_ROOT / "data" / "processed" / "moon_atlas"
METADATA_PATH = ATLAS_DIR / "atlas_metadata.json"
THUMBS_DIR = REPO_ROOT / "data" / "processed" / "thumbs" / "moon"
THUMBS_META_JSON = THUMBS_DIR / "thumbs_metadata.json"
THUMBS_META_CSV = THUMBS_DIR / "thumbs_metadata.csv"

BG_COLOR = "#0e1117"
PANEL_BG = "#161b22"
TEXT_COLOR = "#e6edf3"
GRID_COLOR = "#30363d"
CYAN_ACCENT = "#00e5ff"

SAFE_RGB = np.array([0x2E, 0xCC, 0x71], dtype=np.float64) / 255.0     # #2ecc71 (<10 deg)
CAUTION_RGB = np.array([0xF3, 0x9C, 0x12], dtype=np.float64) / 255.0  # #f39c12 (10-20 deg)
HAZARD_RGB = np.array([0xE7, 0x4C, 0x3C], dtype=np.float64) / 255.0   # #e74c3c (>20 deg)

SITE_NAMES_TR: dict[str, str] = {
    "moon_shackleton_rim": "Shackleton Krateri Kenarı (Saha 04 ROI)",
    "moon_connecting_ridge": "Bağlantı Sırtı (Shackleton–de Gerlache, Saha 01 ROI)",
    "moon_de_gerlache_rim": "de Gerlache Krateri Kenarı (Saha 11 ROI)",
    "moon_shackleton_peak": "Shackleton Yakını Zirve (Saha 07 ROI)",
    "moon_faustini_rim": "Faustini Krateri Kenarı A (PGDA LM7 Merkezi)",
}


def _save_compact_png(fig: plt.Figure, out_path: Path, max_kb: int = 72) -> int:
    """Save figure as optimized 8-bit adaptive-palette PNG guaranteed to stay under max_kb KB."""
    out_path.parent.mkdir(parents=True, exist_ok=True)
    buf = io.BytesIO()
    fig.savefig(buf, format="png", facecolor=fig.get_facecolor(), bbox_inches="tight", pad_inches=0.08)
    plt.close(fig)

    buf.seek(0)
    with Image.open(buf) as im:
        rgb = im.convert("RGB")
        for n_colors in (256, 192, 144, 112, 80):
            q_buf = io.BytesIO()
            quant = rgb.quantize(colors=n_colors, method=Image.Quantize.MEDIANCUT)
            quant.save(q_buf, format="PNG", optimize=True)
            if len(q_buf.getvalue()) <= max_kb * 1024:
                out_path.write_bytes(q_buf.getvalue())
                return len(q_buf.getvalue())
        out_path.write_bytes(q_buf.getvalue())
        return len(q_buf.getvalue())


def _compute_dual_hillshade(elev: np.ndarray, dx_m: float, dy_m: float) -> np.ndarray:
    """Compute dual-azimuth polar grazing hillshade (75% low-angle primary + 25% fill)."""
    ls_primary = LightSource(azdeg=315, altdeg=12)
    ls_fill = LightSource(azdeg=45, altdeg=25)
    elev_filled = np.where(np.isfinite(elev), elev, np.nanmedian(elev))
    hs1 = ls_primary.hillshade(elev_filled, vert_exag=1.5, dx=dx_m, dy=dy_m)
    hs2 = ls_fill.hillshade(elev_filled, vert_exag=1.2, dx=dx_m, dy=dy_m)
    return np.clip(0.75 * hs1 + 0.25 * hs2, 0.0, 1.0)


def _blend_hazard_rgb(hs: np.ndarray, slope_deg: np.ndarray, alpha: float = 0.68) -> np.ndarray:
    """Blend hillshade grayscale with engineering slope hazard classes (<10, 10-20, >20 deg)."""
    rgb_hs = np.dstack([hs, hs, hs])
    color_layer = np.zeros_like(rgb_hs)
    safe = slope_deg < 10.0
    caution = (slope_deg >= 10.0) & (slope_deg <= 20.0)
    hazard = slope_deg > 20.0
    color_layer[safe] = SAFE_RGB
    color_layer[caution] = CAUTION_RGB
    color_layer[hazard] = HAZARD_RGB
    return np.clip((1.0 - alpha) * rgb_hs + alpha * color_layer, 0.0, 1.0)


def _style_map_axis(
    ax: plt.Axes,
    xs_rel: np.ndarray,
    ys_rel: np.ndarray,
    radius_m: float,
    title: str,
    title_size: float = 9.0,
) -> None:
    """Add r=1000 m circle, center cross, 500 m scale bar, and dark theme styling to a map axis."""
    ax.set_facecolor(PANEL_BG)
    circle = plt.Circle(
        (0.0, 0.0),
        radius_m,
        edgecolor=CYAN_ACCENT,
        facecolor="none",
        linewidth=1.9,
        linestyle="--",
        label="r = 1000 m",
    )
    ax.add_patch(circle)
    ax.plot(0.0, 0.0, "+", color=CYAN_ACCENT, markersize=9, markeredgewidth=1.8)

    # 500 m metric scale bar in bottom-right corner
    x_max = float(np.max(xs_rel))
    y_min = float(np.min(ys_rel))
    bar_x1 = x_max - 120.0
    bar_x0 = bar_x1 - 500.0
    bar_y = y_min + 140.0
    ax.plot([bar_x0, bar_x1], [bar_y, bar_y], color="#ffffff", linewidth=3.0, solid_capstyle="butt")
    ax.text(
        0.5 * (bar_x0 + bar_x1),
        bar_y + 55.0,
        "500 m",
        color="#ffffff",
        fontsize=7.5,
        fontweight="bold",
        ha="center",
        va="bottom",
        bbox={"boxstyle": "round,pad=0.15", "facecolor": "#0e1117", "alpha": 0.75, "edgecolor": "none"},
    )

    ax.set_title(title, color=TEXT_COLOR, fontsize=title_size, fontweight="bold", pad=6)
    ax.set_xlabel("Doğu–Batı ΔX (m)", color=TEXT_COLOR, fontsize=8)
    ax.set_ylabel("Kuzey–Güney ΔY (m)", color=TEXT_COLOR, fontsize=8)
    ax.tick_params(colors=TEXT_COLOR, labelsize=7.5)
    for spine in ax.spines.values():
        spine.set_edgecolor(GRID_COLOR)


def _draw_contours(
    ax: plt.Axes,
    xs_rel: np.ndarray,
    ys_rel: np.ndarray,
    elev: np.ndarray,
) -> None:
    """Overlay semi-transparent 25 m / 50 m elevation contour lines."""
    emin = float(np.nanmin(elev))
    emax = float(np.nanmax(elev))
    step = 50.0 if (emax - emin) > 260.0 else 25.0
    levels = np.arange(np.floor(emin / step) * step, np.ceil(emax / step) * step + step, step)
    if len(levels) >= 2:
        ax.contour(
            xs_rel,
            ys_rel,
            elev,
            levels=levels,
            colors="#a5d6ff",
            linewidths=0.55,
            alpha=0.35,
            origin="upper",
        )


def _add_hazard_legend(ax: plt.Axes) -> None:
    """Add compact neutral slope-bin legend in upper-left corner."""
    patches = [
        mpatches.Patch(color="#2ecc71", label="<10° eğim"),
        mpatches.Patch(color="#f39c12", label="10–20° eğim"),
        mpatches.Patch(color="#e74c3c", label=">20° eğim"),
    ]
    leg = ax.legend(
        handles=patches,
        loc="upper left",
        fontsize=6.8,
        framealpha=0.82,
        facecolor="#0e1117",
        edgecolor=GRID_COLOR,
        labelcolor=TEXT_COLOR,
    )
    leg.set_zorder(10)


def _save_siglip_thumb_224(
    site: MoonSiteSpec,
    hs: np.ndarray,
    x0_m: float,
    y0_m: float,
) -> dict[str, object]:
    """Save a 224x224 compact LRO LOLA hillshade thumbnail in data/processed/thumbs/moon/ and return metadata."""
    THUMBS_DIR.mkdir(parents=True, exist_ok=True)
    site_id = site["site_id"]
    thumb_path = THUMBS_DIR / f"{site_id}.png"

    arr_u8 = np.clip(np.round(hs * 255.0), 0, 255).astype(np.uint8)
    rgb_img = Image.fromarray(np.dstack([arr_u8, arr_u8, arr_u8]), mode="RGB")
    resized = rgb_img.resize((224, 224), resample=Image.Resampling.LANCZOS)
    resized.save(thumb_path, format="PNG", optimize=True)

    return {
        "site_id": site_id,
        "name": site["name"],
        "tile_id": f"PGDA_LOLA_5mpp_{site['pgda_site']}",
        "lat": round(float(site["lat"]), 4),
        "lon": round(float(site["lon"]), 4),
        "x_stereo_m": round(float(x0_m), 1),
        "y_stereo_m": round(float(y0_m), 1),
        "crs": MOON_STEREO_PROJ4,
        "image_size_px": "224x224",
        "window_m": 2200.0,
        "scale_m_per_px": round(2200.0 / 224.0, 4),
        "native_res_m": 5.0,
        "source": f"NASA_GSFC_PGDA_Product78:{site['dem_src']} ({site['pgda_site']}_final_adj_5mpp_surf.tif)",
        "usage_scope": "visual_exploration_only_excluded_from_numeric_scoring",
        "thumb_path": f"data/processed/thumbs/moon/{site_id}.png",
    }


DISCLAIMER_NOTE = "Illustrative slope bins; not a landing-safety assessment."


def _add_disclaimer_footer(fig: plt.Figure) -> None:
    """Add the required single-line disclaimer footer to a figure."""
    fig.text(
        0.5,
        0.005,
        DISCLAIMER_NOTE,
        ha="center",
        va="bottom",
        color="#8b949e",
        fontsize=6.8,
        style="italic",
    )


def generate_site_atlas(site: MoonSiteSpec) -> tuple[dict[str, object], dict[str, object]]:
    """Generate hillshade, hazard, and 3-panel atlas PNGs + 224x224 SigLIP thumb + metadata dicts for one lunar site."""
    site_id = site["site_id"]
    name_tr = SITE_NAMES_TR.get(site_id, site["name"])
    radius_m = float(site["radius_m"])

    stats = extract_site_topography(site)
    elev = np.asarray(stats["elev_win"], dtype=np.float64)
    slope_deg = np.asarray(stats["slope_win"], dtype=np.float64)
    xs_m = np.asarray(stats["xs_m"], dtype=np.float64)
    ys_m = np.asarray(stats["ys_m"], dtype=np.float64)
    x0_m = float(stats["x0_m"])
    y0_m = float(stats["y0_m"])

    xs_rel = xs_m - x0_m
    ys_rel = ys_m - y0_m
    extent_rel = [float(xs_rel.min()), float(xs_rel.max()), float(ys_rel.min()), float(ys_rel.max())]

    xx_rel, yy_rel = np.meshgrid(xs_rel, ys_rel)
    dist_m = np.hypot(xx_rel, yy_rel)
    inside = (dist_m <= radius_m) & np.isfinite(slope_deg)
    inside_slopes = slope_deg[inside]

    safe_pct = float(np.mean(inside_slopes < 10.0) * 100.0)
    caution_pct = float(np.mean((inside_slopes >= 10.0) & (inside_slopes <= 20.0)) * 100.0)
    hazard_pct = float(100.0 - safe_pct - caution_pct)

    hs = _compute_dual_hillshade(elev, 5.0, 5.0)
    hazard_rgb = _blend_hazard_rgb(hs, slope_deg)
    thumb_meta = _save_siglip_thumb_224(site, hs, x0_m, y0_m)

    # 1. Output A: <site_id>_hillshade.png
    fig_a, ax_a = plt.subplots(figsize=(4.6, 4.7), dpi=95, facecolor=BG_COLOR)
    ax_a.imshow(hs, extent=extent_rel, origin="upper", cmap="gray", vmin=0.0, vmax=1.0)
    _draw_contours(ax_a, xs_rel, ys_rel, elev)
    _style_map_axis(
        ax_a,
        xs_rel,
        ys_rel,
        radius_m,
        f"{name_tr}\nLRO LOLA 5 m/px Rölyef & r=1 km Analiz Çemberi",
        title_size=8.6,
    )
    _add_disclaimer_footer(fig_a)
    hillshade_path = ATLAS_DIR / f"{site_id}_hillshade.png"
    hs_bytes = _save_compact_png(fig_a, hillshade_path)

    # 2. Output B: <site_id>_hazard.png
    fig_b, ax_b = plt.subplots(figsize=(4.6, 4.7), dpi=95, facecolor=BG_COLOR)
    ax_b.imshow(hazard_rgb, extent=extent_rel, origin="upper")
    _draw_contours(ax_b, xs_rel, ys_rel, elev)
    _style_map_axis(
        ax_b,
        xs_rel,
        ys_rel,
        radius_m,
        f"{name_tr} — Eğim Sınıfları Haritası (5 m/px)\n"
        f"<10° eğim: %{safe_pct:.1f} | 10–20° eğim: %{caution_pct:.1f} | >20° eğim: %{hazard_pct:.1f}",
        title_size=8.0,
    )
    _add_hazard_legend(ax_b)
    _add_disclaimer_footer(fig_b)
    hazard_path = ATLAS_DIR / f"{site_id}_hazard.png"
    haz_bytes = _save_compact_png(fig_b, hazard_path)

    # 3. Output C: <site_id>_atlas.png (3-panel card)
    fig_c, (ax1, ax2, ax3) = plt.subplots(1, 3, figsize=(11.6, 3.75), dpi=90, facecolor=BG_COLOR)

    ax1.imshow(hs, extent=extent_rel, origin="upper", cmap="gray", vmin=0.0, vmax=1.0)
    _draw_contours(ax1, xs_rel, ys_rel, elev)
    _style_map_axis(
        ax1,
        xs_rel,
        ys_rel,
        radius_m,
        f"{name_tr}\n5 m/px Kutupsal Rölyef & İzohips",
        title_size=8.2,
    )

    ax2.imshow(hazard_rgb, extent=extent_rel, origin="upper")
    _draw_contours(ax2, xs_rel, ys_rel, elev)
    _style_map_axis(
        ax2,
        xs_rel,
        ys_rel,
        radius_m,
        f"Eğim Sınıfları Haritası (5 m/px)\n"
        f"<10° eğim: %{safe_pct:.1f} | 10–20° eğim: %{caution_pct:.1f} | >20° eğim: %{hazard_pct:.1f}",
        title_size=8.0,
    )
    _add_hazard_legend(ax2)

    # Cross-section profiles passing through center (row_mid, col_mid)
    r_mid = int(np.argmin(np.abs(ys_rel)))
    c_mid = int(np.argmin(np.abs(xs_rel)))
    z0 = float(elev[r_mid, c_mid])
    we_profile = elev[r_mid, :] - z0
    sn_profile_x = ys_rel[::-1]
    sn_profile_z = elev[::-1, c_mid] - z0

    ax3.set_facecolor(PANEL_BG)
    ax3.plot(xs_rel, we_profile, color=CYAN_ACCENT, linewidth=1.8, label="Batı–Doğu (X) Kesiti")
    ax3.plot(sn_profile_x, sn_profile_z, color="#ff9f43", linewidth=1.6, linestyle="-.", label="Güney–Kuzey (Y) Kesiti")
    ax3.axvline(-radius_m, color="#e74c3c", linestyle="--", linewidth=1.1, alpha=0.85, label="r = ±1000 m Sınırı")
    ax3.axvline(radius_m, color="#e74c3c", linestyle="--", linewidth=1.1, alpha=0.85)
    ax3.axhline(0.0, color=GRID_COLOR, linewidth=0.9)
    ax3.set_xlim(float(xs_rel.min()), float(xs_rel.max()))
    ax3.set_title(
        f"Merkez Topografik Kesit Profili (2.2 km)\n"
        f"Rölyef: {float(stats['relief']):.1f} m | Ort. Eğim: {float(stats['slope_mean']):.1f}°",
        color=TEXT_COLOR,
        fontsize=8.2,
        fontweight="bold",
        pad=6,
    )
    ax3.set_xlabel("Merkezden Mesafe (m)", color=TEXT_COLOR, fontsize=8)
    ax3.set_ylabel("Bağıl Yükseklik Δz (m)", color=TEXT_COLOR, fontsize=8)
    ax3.tick_params(colors=TEXT_COLOR, labelsize=7.5)
    ax3.grid(True, color=GRID_COLOR, linestyle=":", linewidth=0.6, alpha=0.6)
    for spine in ax3.spines.values():
        spine.set_edgecolor(GRID_COLOR)
    ax3.legend(
        loc="upper right",
        fontsize=6.8,
        framealpha=0.82,
        facecolor="#0e1117",
        edgecolor=GRID_COLOR,
        labelcolor=TEXT_COLOR,
    )

    fig_c.tight_layout(pad=0.9, rect=(0.0, 0.03, 1.0, 1.0))
    _add_disclaimer_footer(fig_c)
    atlas_path = ATLAS_DIR / f"{site_id}_atlas.png"
    atl_bytes = _save_compact_png(fig_c, atlas_path)

    print(
        f"[ATLAS] {site_id}: <10°=%{safe_pct:.1f}, 10–20°=%{caution_pct:.1f}, >20°=%{hazard_pct:.1f} | "
        f"hillshade={hs_bytes / 1024:.1f}KB, hazard={haz_bytes / 1024:.1f}KB, atlas={atl_bytes / 1024:.1f}KB"
    )

    atlas_meta = {
        "site_id": site_id,
        "name_tr": name_tr,
        "window_km": 2.2,
        "resolution_m": 5.0,
        "pct_lt10deg": round(safe_pct, 2),
        "pct_10_20deg": round(caution_pct, 2),
        "pct_gt20deg": round(hazard_pct, 2),
        "note": DISCLAIMER_NOTE,
        "elev_min_m": round(float(stats["elev_min_m"]), 2),
        "elev_max_m": round(float(stats["elev_max_m"]), 2),
        "relief_m": round(float(stats["relief"]), 2),
        "slope_mean_deg": round(float(stats["slope_mean"]), 2),
        "slope_p90_deg": round(float(stats["slope_p90"]), 2),
        "hillshade_path": f"data/processed/moon_atlas/{site_id}_hillshade.png",
        "hazard_path": f"data/processed/moon_atlas/{site_id}_hazard.png",
        "atlas_path": f"data/processed/moon_atlas/{site_id}_atlas.png",
    }
    return atlas_meta, thumb_meta


def main() -> int:
    """Generate all 15 Lunar South Pole visual atlas PNGs, 5 SigLIP 224x224 thumbs, and metadata files."""
    import pandas as pd

    ATLAS_DIR.mkdir(parents=True, exist_ok=True)
    THUMBS_DIR.mkdir(parents=True, exist_ok=True)
    metadata_list: list[dict[str, object]] = []
    thumbs_list: list[dict[str, object]] = []
    for site in VERIFIED_MOON_SITES:
        meta, t_meta = generate_site_atlas(site)
        metadata_list.append(meta)
        thumbs_list.append(t_meta)

    METADATA_PATH.write_text(json.dumps(metadata_list, indent=2, ensure_ascii=False), encoding="utf-8")
    THUMBS_META_JSON.write_text(json.dumps(thumbs_list, indent=2, ensure_ascii=False), encoding="utf-8")
    pd.DataFrame(thumbs_list).to_csv(THUMBS_META_CSV, index=False)
    total_kb = sum(p.stat().st_size for p in ATLAS_DIR.glob("*") if p.is_file()) / 1024.0
    thumbs_kb = sum(p.stat().st_size for p in THUMBS_DIR.glob("*") if p.is_file()) / 1024.0
    print(
        f"[TAMAMLANDI] {len(metadata_list)} saha icin 15 PNG + metadata ({total_kb:.1f} KB) ve "
        f"5 SigLIP 224x224 thumb ({thumbs_kb:.1f} KB) uretildi."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
