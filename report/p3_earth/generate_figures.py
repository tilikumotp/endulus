"""Generate 9 offline Turkish technical figures for p3-earth from verified local artifacts."""

from __future__ import annotations

import io
import json
import math
import re
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Any

import matplotlib
matplotlib.use("Agg")
import matplotlib.gridspec as gridspec
import matplotlib.patches as mpatches
import matplotlib.pyplot as plt
from matplotlib.colors import LightSource, ListedColormap
import numpy as np
import pandas as pd
from PIL import Image

REPO_ROOT = Path(__file__).resolve().parents[2]
OUT_DIR = REPO_ROOT / "report" / "p3_earth" / "figures"
PARQUET_PATH = REPO_ROOT / "data" / "processed" / "features_earth.parquet"
GRIDS_PATH = REPO_ROOT / "data" / "processed" / "earth_3d_grids.npz"
META3D_PATH = REPO_ROOT / "data" / "processed" / "earth_3d_meta.json"
ATLAS_DIR = REPO_ROOT / "data" / "processed" / "earth_atlas"
DOCS_DIR = REPO_ROOT / "docs"
PREV_PARQUET_REV = "c9620d8"

sys.path.insert(0, str(REPO_ROOT))
from src.earth.mixed_pixel import MADDE3_AUDITED_RECORDS  # noqa: E402


LITHOLOGY_TR = {
    "basalt": "Bazalt",
    "pyroclastic_tuff": "Piroklastik Tüf",
    "evaporite": "Evaporit",
    "impact_breccia": "Çarpma Breşi",
    "regolith_permafrost": "Regolit / Permafrost",
}

SITE_SHORT_TR = {
    "earth_etna_cisternazza": "Etna (Cisternazza)",
    "earth_atacama_yungay": "Atacama (Yungay)",
    "earth_haughton_crater": "Haughton Krateri",
    "earth_mauna_loa_hiseas": "Mauna Loa (HI-SEAS)",
    "earth_mcmurdo_wright_valley": "McMurdo (Wright Valley)",
    "earth_lanzarote_timanfaya": "Lanzarote (Timanfaya)",
    "earth_meteor_crater_arizona": "Meteor Krateri (AZ)",
    "earth_craters_of_the_moon": "Craters of the Moon",
    "earth_svalbard_bockfjorden": "Svalbard (Bockfjorden)",
    "earth_lunar_crater_nevada": "Lunar Crater (NV)",
    "earth_karacadag_summit": "Karacadağ (Zirve)",
    "earth_karacadag_ovabag": "Karacadağ (Ovabağ)",
    "earth_kula_divlit": "Kula (Divlit)",
    "earth_tendurek_shield": "Tendürek",
    "earth_erciyes_kojugedigi": "Erciyes",
    "earth_hasandagi_kecekalecik": "Hasandağı",
    "earth_acigol_guneydag": "Acıgöl (Güneydağ)",
    "earth_cappadocia_kavakkoy": "Kapadokya (Kavak)",
    "earth_tuz_golu_south": "Tuz Gölü (Güney)",
    "earth_salda_terrace": "Salda Gölü (Teras)",
    "earth_askja_holuhraun": "Askja / Holuhraun",
    "earth_harrat_rahat_madinah": "Harrat Rahat",
    "earth_pinacate_el_elegante": "Pinacate (El Elegante)",
    "earth_puna_campo_piedra_pomez": "Puna (Piedra Pómez)",
    "earth_deccan_mahabaleshwar": "Deccan (Panchgani)",
    "earth_harrat_ash_shaam": "Harrat Ash Shaam",
    "earth_kilbourne_hole_nm": "Kilbourne Hole",
    "earth_qaidam_dalangtan": "Qaidam (Dalangtan)",
    "earth_karapinar_meke": "Karapınar (Meke)",
    "earth_suphan_south_apron": "Süphan (Güney Etek)",
    "earth_nemrut_caldera_flank": "Nemrut Kalderası",
    "earth_agri_dogubayazit_flow": "Ağrı (Doğubayazıt)",
    "earth_payunia_pampa_negra": "Payunia (Pampa Negra)",
    "earth_chajnantor_plateau": "Chajnantor Platosu",
    "earth_waw_an_namus_apron": "Waw an Namus",
    "earth_tibesti_tarso_voon": "Tibesti (Tarso Voon)",
    "earth_paricutin_lava_field": "Parícutin",
    "earth_tolbachik_apron": "Tolbachik",
    "earth_kilauea_kau_desert": "Kīlauea (Kaʻū)",
    "earth_tongariro_rangipo": "Tongariro (Rangipo)",
}


def setup_rc() -> None:
    """Configure clean matplotlib defaults with UTF-8 Turkish support."""
    plt.rcParams.update(
        {
            "font.family": "DejaVu Sans",
            "font.size": 9.5,
            "axes.titlesize": 11,
            "axes.labelsize": 9.5,
            "xtick.labelsize": 8.5,
            "ytick.labelsize": 8.5,
            "axes.edgecolor": "#475569",
            "axes.linewidth": 0.8,
            "figure.facecolor": "#FFFFFF",
            "axes.facecolor": "#F8FAFC",
            "savefig.dpi": 200,
        }
    )


def haversine_km(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Compute great-circle distance in kilometers."""
    r = 6371.0088
    p1, p2 = math.radians(lat1), math.radians(lat2)
    dp = math.radians(lat2 - lat1)
    dl = math.radians(lon2 - lon1)
    a = math.sin(dp / 2) ** 2 + math.cos(p1) * math.cos(p2) * math.sin(dl / 2) ** 2
    return 2 * r * math.asin(math.sqrt(a))


def load_prev_parquet() -> pd.DataFrame:
    """Load pre-f823514 features_earth.parquet from git history without touching disk."""
    git_bin = shutil.which("git") or r"C:\Program Files\Git\cmd\git.exe"
    raw = subprocess.check_output(
        [git_bin, "show", f"{PREV_PARQUET_REV}:data/processed/features_earth.parquet"],
        cwd=str(REPO_ROOT),
    )
    return pd.read_parquet(io.BytesIO(raw))


def make_fig01(df: pd.DataFrame) -> Path:
    """Fig 01: Global lat/lon site distribution with dedicated Turkey candidate zoom panel."""
    fig = plt.figure(figsize=(14.5, 9.4))
    gs = gridspec.GridSpec(2, 2, figure=fig, height_ratios=[1.55, 0.95], width_ratios=[1.85, 0.75], hspace=0.28, wspace=0.14)
    fig.subplots_adjust(left=0.06, right=0.98, top=0.88, bottom=0.09)

    ax = fig.add_subplot(gs[0, :])
    ax_tr = fig.add_subplot(gs[1, 0])
    ax_info = fig.add_subplot(gs[1, 1])

    ax.set_xlim(-175, 185)
    ax.set_ylim(-88, 86)
    ax.grid(True, linestyle=":", color="#CBD5E1", linewidth=0.7, zorder=0)
    ax.axhline(0, color="#94A3B8", linestyle="--", linewidth=0.7, zorder=1)
    ax.axhline(60, color="#D97706", linestyle=":", linewidth=0.8, alpha=0.6, zorder=1)
    ax.axhline(-56, color="#D97706", linestyle=":", linewidth=0.8, alpha=0.6, zorder=1)
    ax.text(-172, 62.0, "NASADEM alt/üst sınırı (~60°N – 56°S)", fontsize=7.8, color="#B45309")

    is_tr = (df["lat"].between(36.0, 42.2)) & (df["lon"].between(26.0, 45.5)) & (df["role"] == "candidate")
    val_df = df[df["role"] == "validation"]
    tr_df = df[is_tr]
    gl_df = df[(df["role"] == "candidate") & (~is_tr)]

    ax.scatter(
        gl_df["lon"], gl_df["lat"], s=72, c="#0D9488", edgecolors="#0F172A", linewidths=0.7,
        marker="o", zorder=4, label=f"Küresel Aday Sahalar (n={len(gl_df)})",
    )
    ax.scatter(
        tr_df["lon"], tr_df["lat"], s=65, c="#7C3AED", edgecolors="#0F172A", linewidths=0.7,
        marker="s", zorder=4, label=f"Türkiye Aday Sahaları (n={len(tr_df)}, alt sol panel)",
    )
    ax.scatter(
        val_df["lon"], val_df["lat"], s=110, c="#DC2626", edgecolors="#0F172A", linewidths=0.9,
        marker="D", zorder=5, label=f"Doğrulama Sahaları (n={len(val_df)})",
    )

    val_offsets = {
        "earth_etna_cisternazza": (-7, -8, "right"),
        "earth_atacama_yungay": (-7, 2, "right"),
        "earth_haughton_crater": (7, -2, "left"),
        "earth_mauna_loa_hiseas": (7, 9, "left"),
        "earth_mcmurdo_wright_valley": (-8, 8, "right"),
        "earth_lanzarote_timanfaya": (-7, -3, "right"),
        "earth_meteor_crater_arizona": (7, 4, "left"),
        "earth_craters_of_the_moon": (7, 9, "left"),
        "earth_svalbard_bockfjorden": (7, -2, "left"),
        "earth_lunar_crater_nevada": (-7, 6, "right"),
    }
    for _, row in val_df.iterrows():
        dx, dy, ha = val_offsets[row["site_id"]]
        ax.annotate(
            SITE_SHORT_TR[row["site_id"]],
            xy=(row["lon"], row["lat"]),
            xytext=(dx, dy),
            textcoords="offset points",
            fontsize=8.0,
            fontweight="bold",
            color="#991B1B",
            ha=ha,
            va="center",
            bbox=dict(boxstyle="round,pad=0.18", fc="#FEF2F2", ec="#FCA5A5", lw=0.6, alpha=0.92),
            arrowprops=dict(arrowstyle="-", color="#FCA5A5", lw=0.6),
            zorder=6,
        )

    gl_offsets = {
        "earth_askja_holuhraun": (-7, 4, "right"),
        "earth_harrat_rahat_madinah": (7, -8, "left"),
        "earth_pinacate_el_elegante": (-7, -12, "right"),
        "earth_puna_campo_piedra_pomez": (7, -10, "left"),
        "earth_deccan_mahabaleshwar": (7, 3, "left"),
        "earth_harrat_ash_shaam": (7, -3, "left"),
        "earth_kilbourne_hole_nm": (7, -5, "left"),
        "earth_qaidam_dalangtan": (7, 4, "left"),
        "earth_payunia_pampa_negra": (7, -6, "left"),
        "earth_chajnantor_plateau": (7, 10, "left"),
        "earth_waw_an_namus_apron": (-7, -3, "right"),
        "earth_tibesti_tarso_voon": (-7, -11, "right"),
        "earth_paricutin_lava_field": (7, 5, "left"),
        "earth_tolbachik_apron": (-7, 3, "right"),
        "earth_kilauea_kau_desert": (7, -10, "left"),
        "earth_tongariro_rangipo": (-7, 5, "right"),
    }
    for _, row in gl_df.iterrows():
        dx, dy, ha = gl_offsets[row["site_id"]]
        ax.annotate(
            SITE_SHORT_TR[row["site_id"]],
            xy=(row["lon"], row["lat"]),
            xytext=(dx, dy),
            textcoords="offset points",
            fontsize=7.5,
            color="#0F766E",
            ha=ha,
            va="center",
            arrowprops=dict(arrowstyle="-", color="#99F6E4", lw=0.6),
            zorder=5,
        )

    rect = mpatches.Rectangle((27.0, 36.4), 19.0, 4.3, lw=1.2, ec="#7C3AED", fc="#EDE9FE", alpha=0.35, zorder=2)
    ax.add_patch(rect)
    ax.text(36.5, 45.2, f"Türkiye (n={len(tr_df)}, altta yakınlaştırma)", fontsize=8.0, fontweight="bold", color="#5B21B6", ha="center")
    ax.set_xlabel("Boylam (WGS84, °)", fontweight="bold")
    ax.set_ylabel("Enlem (WGS84, °)", fontweight="bold")
    ax.legend(loc="lower left", frameon=True, facecolor="#FFFFFF", edgecolor="#CBD5E1", fontsize=8.5)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)

    # Bottom-left: spacious dedicated Turkey panel
    ax_tr.set_facecolor("#FAF5FF")
    ax_tr.set_xlim(27.0, 46.8)
    ax_tr.set_ylim(36.2, 40.8)
    ax_tr.grid(True, linestyle=":", color="#DDD6FE", linewidth=0.7)
    ax_tr.scatter(tr_df["lon"], tr_df["lat"], s=72, c="#7C3AED", edgecolors="#0F172A", lw=0.7, marker="s", zorder=4)
    tr_offsets = {
        "earth_kula_divlit": (0, 14, "center"),
        "earth_salda_terrace": (0, -14, "center"),
        "earth_tuz_golu_south": (-14, -4, "right"),
        "earth_karapinar_meke": (-10, -16, "right"),
        "earth_hasandagi_kecekalecik": (10, -15, "left"),
        "earth_acigol_guneydag": (-6, 18, "right"),
        "earth_cappadocia_kavakkoy": (6, 22, "left"),
        "earth_erciyes_kojugedigi": (14, -4, "left"),
        "earth_karacadag_summit": (-12, -14, "right"),
        "earth_karacadag_ovabag": (12, 6, "left"),
        "earth_nemrut_caldera_flank": (-14, 14, "right"),
        "earth_suphan_south_apron": (14, -10, "left"),
        "earth_tendurek_shield": (-14, 14, "right"),
        "earth_agri_dogubayazit_flow": (10, -8, "left"),
    }
    for _, row in tr_df.iterrows():
        dx, dy, ha = tr_offsets[row["site_id"]]
        lbl = SITE_SHORT_TR[row["site_id"]]
        if row["site_id"] == "earth_agri_dogubayazit_flow":
            lbl += "\n(NASADEM)"
        ax_tr.annotate(
            lbl,
            xy=(row["lon"], row["lat"]),
            xytext=(dx, dy),
            textcoords="offset points",
            fontsize=7.8,
            color="#4C1D95",
            ha=ha,
            va="center",
            arrowprops=dict(arrowstyle="-", color="#A78BFA", lw=0.7),
            zorder=5,
        )
    ax_tr.set_title(f"Türkiye Aday Sahaları Yakınlaştırması (n={len(tr_df)})", fontsize=10, fontweight="bold", color="#4C1D95", pad=6)
    ax_tr.set_xlabel("Boylam (°E)", fontweight="bold")
    ax_tr.set_ylabel("Enlem (°N)", fontweight="bold")
    ax_tr.spines["top"].set_visible(False)
    ax_tr.spines["right"].set_visible(False)

    # Bottom-right: concise data & projection summary card
    ax_info.axis("off")
    glo_n = int((df["slope_mean_src"] == "Copernicus_DEM_GLO-30").sum())
    nasa_n = int((df["slope_mean_src"] == "NASADEM_HGT_v001").sum())
    n_val, n_cand = int((df["role"] == "validation").sum()), int((df["role"] == "candidate").sum())
    info_txt = (
        f"Saha Envanteri ve Projeksiyon Özeti\n\n"
        f"• Toplam saha: {len(df)} (Doğrulama: {n_val}, Aday: {n_cand})\n"
        f"• Türkiye adayları: {len(tr_df)} | Küresel adaylar: {len(gl_df)}\n"
        f"• Analiz penceresi: r = {float(df['radius_m'].iloc[0]):.0f} m\n\n"
        f"DEM & Düşey Datum:\n"
        f"• Copernicus_DEM_GLO-30 (EGM2008): {glo_n}/{len(df)}\n"
        f"• NASADEM_HGT_v001 (EGM96, Ağrı fallback): {nasa_n}/{len(df)}\n\n"
        f"Projeksiyon Kuralı:\n"
        f"• Eğim ve mesafeler yerel UTM / UPS Polar\n"
        f"  Stereografik (Svalbard >60°N, McMurdo <-56°S)\n"
        f"  üzerinden metrik olarak hesaplanmıştır."
    )
    ax_info.text(
        0.04, 0.96, info_txt, va="top", ha="left", fontsize=8.4, color="#1E293B", linespacing=1.35,
        bbox=dict(boxstyle="round,pad=0.6", fc="#F8FAFC", ec="#CBD5E1", lw=1.1),
    )

    fig.suptitle(
        f"Dünya Analog Aday ve Doğrulama Sahalarının Küresel Dağılımı (Toplam n={len(df)} Saha)",
        fontsize=13.5, fontweight="bold", y=0.96, color="#0F172A",
    )
    fig.text(
        0.5, 0.918,
        f"features_earth.parquet: {n_val} Doğrulama + {n_cand} Aday ({len(tr_df)} Türkiye, {len(gl_df)} Küresel) | Yerel koordinat ağı, çevrimiçi altlık indirilmemiştir",
        ha="center", fontsize=9.5, color="#475569",
    )
    fig.text(
        0.06, 0.02,
        "Not: thermal_inertia 40/40 sahada veri yok (NaN); temp_amplitude geçici tanımdır (docs/data_notes.md f33d0a4).",
        fontsize=8, style="italic", color="#475569",
    )
    out = OUT_DIR / "fig01_site_map.png"
    fig.savefig(out, dpi=200)
    plt.close(fig)
    return out


def make_fig02(df: pd.DataFrame, meta3d: dict[str, Any], atlas_meta: dict[str, Any]) -> Path:
    """Fig 02: Data pipeline flowchart from raw sources to 36-column parquet & gates."""
    fig, ax = plt.subplots(figsize=(14.5, 7.6))
    fig.subplots_adjust(left=0.02, right=0.98, top=0.86, bottom=0.10)
    ax.set_xlim(0, 100)
    ax.set_ylim(0, 100)
    ax.axis("off")

    n_rows, n_cols = df.shape
    glo_n = int((df["slope_mean_src"] == "Copernicus_DEM_GLO-30").sum())
    nasa_n = int((df["slope_mean_src"] == "NASADEM_HGT_v001").sum())
    ti_nan = int(df["thermal_inertia"].isna().sum())
    n_lith = int(df["lithology_class"].nunique())
    n_atlas = int(atlas_meta["included_count"])
    n_3d = int(meta3d["site_count"])
    res_dem = float(df["slope_mean_res_m"].iloc[0])
    res_lst = float(df["temp_amplitude_res_m"].iloc[0])
    res_alb = float(df["albedo_res_m"].iloc[0])

    def draw_box(x: float, y: float, w: float, h: float, title: str, body: str, fc: str, ec: str, tc: str = "#0F172A") -> None:
        box = mpatches.FancyBboxPatch(
            (x, y), w, h, boxstyle="round,pad=0.6,rounding_size=1.4",
            facecolor=fc, edgecolor=ec, linewidth=1.4, zorder=3,
        )
        ax.add_patch(box)
        title_lines = title.count("\n") + 1
        title_fs = 8.8 if w < 15 else 9.2
        body_fs = 7.4 if w < 15 else 8.0
        ax.text(x + w / 2, y + h - 1.6, title, ha="center", va="top", fontsize=title_fs, fontweight="bold", color=tc, linespacing=1.18, zorder=4)
        header_h = 2.4 + title_lines * 3.6
        body_y = y + (h - header_h) / 2.0
        ax.text(x + w / 2, body_y, body, ha="center", va="center", fontsize=body_fs, color="#1E293B", linespacing=1.28, zorder=4)

    def arrow(x1: float, y1: float, x2: float, y2: float) -> None:
        ax.annotate(
            "", xy=(x2, y2), xytext=(x1, y1),
            arrowprops=dict(arrowstyle="-|>,head_width=0.5,head_length=0.8", color="#475569", lw=1.4),
            zorder=2,
        )

    # Column headers
    headers = [(14, "1. Yörünge & Yardımcı Kaynaklar"), (43, "2. Metrik İşleme (r = 1000 m)"), (72, "3. Sözleşme Çıktısı"), (91, "4. Doğrulama")]
    for hx, htxt in headers:
        ax.text(hx, 96, htxt, ha="center", va="center", fontsize=10, fontweight="bold", color="#0F172A")

    # Column 1
    draw_box(2, 74, 24, 17, "Sayısal Yükseklik (DEM)",
             f"AWS S3 Copernicus GLO-30 ({glo_n}/{n_rows})\nPlanetary Computer NASADEM ({nasa_n}/{n_rows} Ağrı)\nÇözünürlük: {res_dem:.0f} m (1 yay-sn)",
             "#EFF6FF", "#2563EB", "#1E40AF")
    draw_box(2, 53, 24, 17, "Yüzey Sıcaklığı (LST)",
             f"MODIS Terra MOD11A2.061 (8-günlük)\n2024 tam yıl, max 24 kompozit, QC<=1\nÇözünürlük: {res_lst:.0f} m (926.6 m sinüzoidal)",
             "#FFF7ED", "#EA580C", "#9A3412")
    draw_box(2, 32, 24, 17, "Geniş Bant Albedo",
             f"LP DAAC MCD43A3.061 ({n_rows}/{n_rows})\nBSA_shortwave, 5x5 px, Çözünürlük: {res_alb:.0f} m\nÇapraz kontrol: MCD43A4.061 Liang",
             "#ECFDF5", "#059669", "#065F46")
    draw_box(2, 11, 24, 17, "Termal Eylemsizlik & Bağlam",
             "thermal_inertia: Ortak küresel ürün YOK\nSentinel-2 L2A (10 m) & ESA WorldCover\nLiteratür + MTA 1:500.000 paftalar",
             "#F1F5F9", "#64748B", "#334155")

    # Column 2
    draw_box(31, 74, 24, 17, "Mobilite Ekseni Türevleri",
             "Yerel UTM / UPS Polar Stereografik\nslope_mean, slope_p90, roughness, relief\n200 bootstrap _sd (sigma_z_rel = 1.0 m)",
             "#DBEAFE", "#2563EB", "#1E3A8A")
    draw_box(31, 53, 24, 17, "Termal Ekseni (Geçici Tanım)",
             "temp_amplitude = LST_Day - LST_Night\n2024 yıllık ort. ΔT + birleşik _sd\n[GEÇİCİ TANIM: docs/data_notes.md f33d0a4]",
             "#FFEDD5", "#EA580C", "#9A3412")
    draw_box(31, 32, 24, 17, "Yüzey Ekseni & NaN Politikası",
             f"albedo + çok-granül örneklem albedo_sd\nthermal_inertia = {ti_nan}/{n_rows} NaN (veri yok)\n0 yer tutucu ve sentetik değer YASAK",
             "#D1FAE5", "#059669", "#065F46")
    draw_box(31, 11, 24, 17, "Nitelik & Yardımcı Ürünler",
             f"lithology_class ({n_lith} sınıf; skora girmez)\nE5 Görsel Atlas ({n_atlas} WebP, 512x512)\nE7 3B DEM Grid ({n_3d} x 74x74 float32)",
             "#F3E8FF", "#7C3AED", "#5B21B6")

    # Column 3
    draw_box(60, 26, 23, 55, f"features_earth.parquet\n({n_rows} satır x {n_cols} sütun)",
             f"• 7 kimlik sütunu\n  (site_id, name, body, role,\n   lat, lon, radius_m)\n\n"
             f"• 7 özellik x 4 sütun = 28:\n  değer, _sd, _src, _res_m\n\n"
             f"• 1 nitel sütun:\n  lithology_class\n\n"
             f"• 0/{n_rows} MOCK\n• thermal_inertia: {ti_nan}/{n_rows} NaN\n  (veri yok)",
             "#FEFCE8", "#CA8A04", "#854D0E")

    # Column 4
    draw_box(86, 56, 12.5, 29, "Sözleşme &\nBirim Testleri",
             "validate_contract\n--fail-on-mock\n(0 hata, 0 uyarı)\n\npytest -q\n(denetim testleri)",
             "#DCFCE7", "#16A34A", "#166534")
    draw_box(86, 22, 12.5, 29, "Bilimsel &\nGörsel Denetim",
             "MCD43A4 Liang\n& NDSI kontrolü\n\n5 MIXED_*\nWC/S2 ayrımı\n\nBeklenti (10/30)",
             "#E0F2FE", "#0284C7", "#075985")

    for ymid in [82.5, 61.5, 40.5, 19.5]:
        arrow(26.6, ymid, 30.4, ymid)
    for ymid in [82.5, 61.5, 40.5, 19.5]:
        arrow(55.6, ymid, 59.4, min(75.0, max(32.0, ymid)))
    arrow(83.6, 62.0, 85.4, 68.0)
    arrow(83.6, 44.0, 85.4, 36.5)

    fig.suptitle(
        "Dünya (p3-earth) Veri Akışı ve 36 Sütunlu Sözleşme Mimarisi",
        fontsize=13.5, fontweight="bold", y=0.96, color="#0F172A",
    )
    fig.text(
        0.5, 0.91,
        f"Tüm rakamlar features_earth.parquet ({n_rows}x{n_cols}), earth_3d_meta.json ({n_3d} grid) ve earth_atlas/metadata.json ({n_atlas} sahne) dosyalarından okunmuştur.",
        ha="center", fontsize=9.5, color="#475569",
    )
    fig.text(
        0.02, 0.02,
        "Geçici tanım notu (docs/data_notes.md f33d0a4): Dünya temp_amplitude (2024 yıllık gündüz–gece ort.) ile Ay ltim01 uzamsal farkı arasında tanım uyuşmazlığı sürmektedir; thermal_inertia = 40/40 NaN (veri yok).",
        fontsize=8, style="italic", color="#475569",
    )
    out = OUT_DIR / "fig02_pipeline.png"
    fig.savefig(out, dpi=200)
    plt.close(fig)
    return out


def make_fig03(df: pd.DataFrame) -> Path:
    """Fig 03: Horizontal boxplots of slope_mean, albedo, temp_amplitude by lithology."""
    order = df["lithology_class"].value_counts().index.tolist()
    labels_y = [f"{LITHOLOGY_TR[c]}\n(n={int((df['lithology_class'] == c).sum())})" for c in order]

    fig, axes = plt.subplots(1, 3, figsize=(14.5, 6.2), sharey=True)
    fig.subplots_adjust(left=0.14, right=0.98, top=0.81, bottom=0.17, wspace=0.12)

    specs = [
        ("slope_mean", "Ortalama Eğim (°)", "#2563EB"),
        ("albedo", "Geniş Bant Albedo (MCD43A3, 0–1)", "#059669"),
        ("temp_amplitude", "Sıcaklık Genliği ΔT (K) [Geçici Tanım]", "#EA580C"),
    ]
    rng = np.random.default_rng(42)

    for ax, (col, xlabel, accent) in zip(axes, specs):
        grouped = [df.loc[df["lithology_class"] == c, col].dropna().to_numpy() for c in order]
        bp = ax.boxplot(
            grouped,
            orientation="horizontal",
            widths=0.52,
            patch_artist=True,
            showfliers=False,
            medianprops=dict(color="#0F172A", linewidth=1.8),
            whiskerprops=dict(color="#475569", linewidth=1.0),
            capprops=dict(color="#475569", linewidth=1.0),
            boxprops=dict(facecolor=accent, alpha=0.22, edgecolor=accent, linewidth=1.2),
        )
        _ = bp
        for idx, c in enumerate(order, start=1):
            sub = df[df["lithology_class"] == c]
            jitter = rng.uniform(-0.16, 0.16, size=len(sub))
            cand_m = sub["role"] == "candidate"
            val_m = sub["role"] == "validation"
            ax.scatter(
                sub.loc[cand_m, col], np.full(cand_m.sum(), idx) + jitter[cand_m.to_numpy()],
                s=34, color="#334155", alpha=0.72, marker="o", zorder=4, label="Aday" if idx == 1 else "",
            )
            ax.scatter(
                sub.loc[val_m, col], np.full(val_m.sum(), idx) + jitter[val_m.to_numpy()],
                s=46, color="#DC2626", edgecolors="#0F172A", linewidths=0.7, marker="D", zorder=5,
                label="Doğrulama" if idx == 1 else "",
            )
        ax.set_yticks(range(1, len(order) + 1))
        ax.set_yticklabels(labels_y, fontsize=9)
        ax.invert_yaxis()
        ax.set_xlabel(xlabel, fontweight="bold")
        ax.grid(True, axis="x", linestyle=":", color="#CBD5E1", linewidth=0.8)
        ax.spines["top"].set_visible(False)
        ax.spines["right"].set_visible(False)

    axes[2].legend(loc="lower right", frameon=True, facecolor="#FFFFFF", edgecolor="#CBD5E1", fontsize=8.5)
    fig.suptitle(
        "Litoloji Sınıfına Göre Temel Sayısal Özellik Dağılımları (n=40 Dünya Sahası)",
        fontsize=13.5, fontweight="bold", y=0.95, color="#0F172A",
    )
    fig.text(
        0.5, 0.89,
        "features_earth.parquet değerleri; nokta dağılımları ve kutu-bıyık özetleri (tekil/ikili sınıflar nokta olarak gösterilmiştir)",
        ha="center", fontsize=9.5, color="#475569",
    )
    fig.text(
        0.04, 0.03,
        "Not 1: thermal_inertia 40/40 NaN (veri yok) olduğu için grafikte yer almaz.   Not 2: temp_amplitude tanımı geçicidir (docs/data_notes.md f33d0a4); Ay ile doğrudan termal kıyas yapılmaz.",
        fontsize=8, style="italic", color="#475569",
    )
    out = OUT_DIR / "fig03_features_by_lithology.png"
    fig.savefig(out, dpi=200)
    plt.close(fig)
    return out


def parse_albedo_crosscheck(df: pd.DataFrame) -> pd.DataFrame:
    """Parse documented MCD43A4/Liang cross-check metrics from docs and match parquet."""
    eray_lines = (DOCS_DIR / "eray_kaynakça.md").read_text(encoding="utf-8").splitlines()
    dse_lines = (DOCS_DIR / "data_sources_earth.md").read_text(encoding="utf-8").splitlines()
    df_idx = df.set_index("site_id")
    records: list[dict[str, Any]] = []

    in_sec3 = False
    for line in eray_lines:
        if line.startswith("## 3."):
            in_sec3 = True
            continue
        if line.startswith("## 4."):
            break
        if in_sec3 and line.startswith("| ") and "`earth_" in line:
            cols = [c.strip() for c in line.strip().strip("|").split("|")]
            sid = cols[1].strip("`")
            c4 = cols[8]
            m = re.match(r"^`([0-9.]+)`\s*\(NDSI\s*`([^`]+)`\s*,\s*kar\s*`([^`]+)`\)", c4)
            if m:
                flag = "ana"
                if sid == "earth_mcmurdo_wright_valley":
                    flag = "mcmurdo_kar"
                records.append(
                    {
                        "site_id": sid,
                        "label": SITE_SHORT_TR[sid],
                        "mcd43a3": float(df_idx.loc[sid, "albedo"]),
                        "mcd43a3_sd": float(df_idx.loc[sid, "albedo_sd"]),
                        "mcd43a4": float(m.group(1)),
                        "ndsi": float(m.group(2)),
                        "snow_masked": m.group(3),
                        "group": flag,
                    }
                )
            elif "Dry run" in c4:
                ms = re.search(r"`([0-9.]+)`", c4)
                if ms:
                    records.append(
                        {
                            "site_id": sid,
                            "label": SITE_SHORT_TR[sid],
                            "mcd43a3": float(df_idx.loc[sid, "albedo"]),
                            "mcd43a3_sd": float(df_idx.loc[sid, "albedo_sd"]),
                            "mcd43a4": float(ms.group(1)),
                            "ndsi": float("nan"),
                            "snow_masked": "0/100",
                            "group": "salda_ek",
                        }
                    )

    for line in dse_lines:
        if "`earth_tuz_golu_south` (Yanlış Pozitif Var)" in line:
            m_val = re.search(r"Liang yedeği `([0-9.]+)`", line)
            m_mask = re.search(r"`(\d+/\d+)` piksel", line)
            records.append(
                {
                    "site_id": "earth_tuz_golu_south",
                    "label": SITE_SHORT_TR["earth_tuz_golu_south"],
                    "mcd43a3": float(df_idx.loc["earth_tuz_golu_south", "albedo"]),
                    "mcd43a3_sd": float(df_idx.loc["earth_tuz_golu_south", "albedo_sd"]),
                    "mcd43a4": float(m_val.group(1)),
                    "ndsi": float("nan"),
                    "snow_masked": m_mask.group(1),
                    "group": "tuz_yanlis_kar",
                }
            )
    return pd.DataFrame(records)


def make_fig04(df: pd.DataFrame) -> Path:
    """Fig 04: MCD43A3 (parquet) vs MCD43A4 Liang (2001) crosscheck with snow-mask flags."""
    cdf = parse_albedo_crosscheck(df)
    fig, ax = plt.subplots(figsize=(10.4, 8.8))
    fig.subplots_adjust(left=0.10, right=0.96, top=0.87, bottom=0.22)

    lim = (0.0, 0.325)
    xs = np.linspace(lim[0], lim[1], 100)
    ax.fill_between(xs, np.maximum(0, xs - 0.03), np.minimum(0.335, xs + 0.03), color="#E2E8F0", alpha=0.55, label="±0.03 uyum bandı")
    ax.plot(xs, xs, linestyle="--", color="#334155", linewidth=1.4, label="y = x (birebir uyum)")

    ana = cdf[cdf["group"] == "ana"]
    mcm = cdf[cdf["group"] == "mcmurdo_kar"]
    tuz = cdf[cdf["group"] == "tuz_yanlis_kar"]
    sal = cdf[cdf["group"] == "salda_ek"]

    ax.errorbar(
        ana["mcd43a3"], ana["mcd43a4"], xerr=ana["mcd43a3_sd"],
        fmt="o", markersize=8, color="#2563EB", ecolor="#93C5FD", elinewidth=1.4, capsize=3,
        markeredgecolor="#0F172A", markeredgewidth=0.8, zorder=4,
        label=f"Ana Çapraz Kontrol (n={len(ana)}, karsız/Svalbard 11/94)",
    )
    ax.errorbar(
        mcm["mcd43a3"], mcm["mcd43a4"], xerr=mcm["mcd43a3_sd"],
        fmt="D", markersize=10, color="#D97706", ecolor="#FCD34D", elinewidth=1.8, capsize=4,
        markeredgecolor="#0F172A", markeredgewidth=1.0, zorder=6,
        label="McMurdo (kar maskesi uyarısı: 19/41 piksel)",
    )
    ax.errorbar(
        tuz["mcd43a3"], tuz["mcd43a4"], xerr=tuz["mcd43a3_sd"],
        fmt="*", markersize=14, color="#DC2626", ecolor="#FCA5A5", elinewidth=1.6, capsize=3,
        markeredgecolor="#0F172A", markeredgewidth=0.9, zorder=7,
        label="Tuz Gölü (kuru-çalışma tek px: 30/31 YANLIŞ kar maskesi)",
    )
    ax.errorbar(
        sal["mcd43a3"], sal["mcd43a4"], xerr=sal["mcd43a3_sd"],
        fmt="s", markersize=8, color="#7C3AED", ecolor="#C4B5FD", elinewidth=1.4, capsize=3,
        markeredgecolor="#0F172A", markeredgewidth=0.8, zorder=5,
        label="Salda Terası (ek kuru-çalışma: 0/100 kar)",
    )

    label_pos = {
        "earth_askja_holuhraun": (8, -10, "left"),
        "earth_etna_cisternazza": (10, -4, "left"),
        "earth_pinacate_el_elegante": (-12, 0, "right"),
        "earth_svalbard_bockfjorden": (10, -10, "left"),
        "earth_karacadag_summit": (12, -9, "left"),
        "earth_agri_dogubayazit_flow": (12, 4, "left"),
        "earth_suphan_south_apron": (12, -14, "left"),
        "earth_atacama_yungay": (12, 0, "left"),
        "earth_haughton_crater": (10, -12, "left"),
        "earth_salda_terrace": (12, 5, "left"),
    }
    for _, row in pd.concat([ana, sal]).iterrows():
        dx, dy, ha = label_pos[row["site_id"]]
        extra = " (11/94 kar)" if row["site_id"] == "earth_svalbard_bockfjorden" else ""
        ax.annotate(
            f"{row['label']}{extra}",
            xy=(row["mcd43a3"], row["mcd43a4"]),
            xytext=(dx, dy),
            textcoords="offset points",
            fontsize=8.2,
            color="#1E293B",
            ha=ha,
            va="center",
            arrowprops=dict(arrowstyle="-", color="#94A3B8", lw=0.7),
            zorder=7,
        )

    # Prominent callouts for McMurdo & Tuz Golu placed in clean empty whitespace
    mr = mcm.iloc[0]
    ax.annotate(
        f"McMurdo (Wright Valley)\nKAR MASKESİ UYARISI:\n{mr['snow_masked']} piksel NDSI≥0.40 elendi\n(NDSI ort={mr['ndsi']:+.3f}; A3={mr['mcd43a3']:.3f}, A4={mr['mcd43a4']:.3f})",
        xy=(mr["mcd43a3"], mr["mcd43a4"]),
        xytext=(0.008, 0.172),
        fontsize=8.0,
        fontweight="bold",
        color="#92400E",
        bbox=dict(boxstyle="round,pad=0.35", fc="#FEF3C7", ec="#D97706", lw=1.1),
        arrowprops=dict(arrowstyle="->", color="#D97706", lw=1.3),
        zorder=8,
    )
    tr = tuz.iloc[0]
    ax.annotate(
        f"Tuz Gölü Güneyi — YANLIŞ KAR MASKESİ:\n{tr['snow_masked']} piksel (%96.8) parlak halit yüzünden elendi!\n(Tek px A4={tr['mcd43a4']:.4f}; A3={tr['mcd43a3']:.4f} etkilenmez)",
        xy=(tr["mcd43a3"], tr["mcd43a4"]),
        xytext=(0.012, 0.278),
        fontsize=8.0,
        fontweight="bold",
        color="#991B1B",
        bbox=dict(boxstyle="round,pad=0.35", fc="#FEE2E2", ec="#DC2626", lw=1.1),
        arrowprops=dict(arrowstyle="->", color="#DC2626", lw=1.3),
        zorder=8,
    )

    main10 = cdf[cdf["group"].isin(["ana", "mcmurdo_kar"])]
    r10 = main10["mcd43a3"].corr(main10["mcd43a4"])
    mae10 = float(np.mean(np.abs(main10["mcd43a3"] - main10["mcd43a4"])))
    r9 = ana["mcd43a3"].corr(ana["mcd43a4"])
    mae9 = float(np.mean(np.abs(ana["mcd43a3"] - ana["mcd43a4"])))

    ax.text(
        0.97, 0.04,
        f"Dokümandaki 10 ana saha:\n"
        f"  r = {r10:.3f}, MAE = {mae10:.4f}\n"
        f"McMurdo hariç (9 saha):\n"
        f"  r = {r9:.3f}, MAE = {mae9:.4f}",
        transform=ax.transAxes, ha="right", va="bottom", fontsize=8.5, color="#0F172A",
        bbox=dict(boxstyle="round,pad=0.4", fc="#FFFFFF", ec="#CBD5E1", lw=0.9),
        zorder=8,
    )

    ax.set_xlim(lim)
    ax.set_ylim(lim)
    ax.set_aspect("equal")
    ax.set_xlabel("Parquet Birincil Albedo: MCD43A3.061 (Albedo_BSA_shortwave ± sd)", fontweight="bold")
    ax.set_ylabel("Bağımsız Çapraz Kontrol: MCD43A4.061 NBAR + Liang (2001) + NDSI<0.40", fontweight="bold")
    ax.grid(True, linestyle=":", color="#CBD5E1", linewidth=0.8)
    handles, labels = ax.get_legend_handles_labels()
    fig.legend(
        handles, labels, loc="lower center", bbox_to_anchor=(0.53, 0.068),
        ncol=2, frameon=True, facecolor="#FFFFFF", edgecolor="#CBD5E1", fontsize=8.0,
    )
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)

    fig.suptitle(
        "MODIS MCD43A3 (Parquet) vs MCD43A4/Liang (2001) Albedo Çapraz Kontrolü",
        fontsize=13.5, fontweight="bold", y=0.96, color="#0F172A",
    )
    fig.text(
        0.5, 0.915,
        "10 ana çapraz kontrol sahası + Tuz Gölü & Salda kuru-çalışma notları (yatay çubuklar = MCD43A3 1-sigma sd)",
        ha="center", fontsize=9.5, color="#475569",
    )
    fig.text(
        0.04, 0.015,
        "Uyarı: Tuz Gölü'nde S2/MODIS NDSI≥0.40 parlak halit tuz kabuğunda yanlış kar pozitifi üretir; MCD43A3 birincil albedosu NDSI maskesi\nkullanmadığından bundan etkilenmez. Kaynak: docs/eray_kaynakça.md §3 ve docs/data_sources_earth.md §7.",
        fontsize=7.8, style="italic", color="#475569",
    )
    out = OUT_DIR / "fig04_albedo_crosscheck.png"
    fig.savefig(out, dpi=200)
    plt.close(fig)
    return out


def make_fig05(df: pd.DataFrame, prev_df: pd.DataFrame) -> Path:
    """Fig 05: Old vs new coordinates, distance shifted, and LST/albedo/relief shifts for 4 fixed sites."""
    targets = [
        ("earth_etna_cisternazza", "Etna\n(Cistern.)"),
        ("earth_suphan_south_apron", "Süphan\n(Alt Etek)"),
        ("earth_pinacate_el_elegante", "Pinacate\n(Elegante)"),
        ("earth_agri_dogubayazit_flow", "Ağrı\n(NASADEM)"),
    ]
    cur = df.set_index("site_id")
    prv = prev_df.set_index("site_id")

    rows = []
    for sid, label in targets:
        o, n = prv.loc[sid], cur.loc[sid]
        dist_km = haversine_km(float(o["lat"]), float(o["lon"]), float(n["lat"]), float(n["lon"]))
        rows.append(
            {
                "site_id": sid,
                "label": label,
                "dist_km": dist_km,
                "old_lst": float(o["temp_amplitude"]),
                "new_lst": float(n["temp_amplitude"]),
                "old_alb": float(o["albedo"]),
                "new_alb": float(n["albedo"]),
                "old_rel": float(o["relief"]),
                "new_rel": float(n["relief"]),
            }
        )
    rdf = pd.DataFrame(rows)

    fig, axes = plt.subplots(1, 4, figsize=(15.4, 6.4))
    fig.subplots_adjust(left=0.05, right=0.98, top=0.79, bottom=0.22, wspace=0.31)
    x = np.arange(len(rdf))
    w = 0.36

    # Panel 1: Distance moved
    bars = axes[0].bar(x, rdf["dist_km"], width=0.52, color="#7C3AED", edgecolor="#0F172A", linewidth=0.8)
    for b, d in zip(bars, rdf["dist_km"]):
        axes[0].text(b.get_x() + b.get_width() / 2, d + 0.4, f"{d:.2f} km", ha="center", va="bottom", fontsize=8.5, fontweight="bold", color="#4C1D95")
    axes[0].set_ylim(0, max(rdf["dist_km"]) * 1.18)
    axes[0].set_ylabel("Mesafe (km)", fontweight="bold")
    axes[0].set_title("Konum Kaydırma Mesafesi", fontweight="bold")

    panels = [
        (axes[1], "old_lst", "new_lst", "K", "temp_amplitude (Geçici Tanım)", ".1f", "#94A3B8", "#EA580C"),
        (axes[2], "old_alb", "new_alb", "", "Albedo (MCD43A3.061)", ".3f", "#94A3B8", "#059669"),
        (axes[3], "old_rel", "new_rel", "m", "Rölyef (relief, r = 1 km)", ".0f", "#94A3B8", "#2563EB"),
    ]
    for ax, c_old, c_new, unit, title, fmt, col_o, col_n in panels:
        b1 = ax.bar(x - w / 2, rdf[c_old], width=w, color=col_o, edgecolor="#0F172A", lw=0.7, label=f"Eski ({PREV_PARQUET_REV})")
        b2 = ax.bar(x + w / 2, rdf[c_new], width=w, color=col_n, edgecolor="#0F172A", lw=0.7, label="Yeni (final)")
        ymax = max(rdf[c_old].max(), rdf[c_new].max())
        ax.set_ylim(0, ymax * 1.28)
        for i, row in rdf.iterrows():
            delta = row[c_new] - row[c_old]
            top_v = max(row[c_old], row[c_new])
            ax.text(i, top_v + ymax * 0.04, f"Δ={delta:+{fmt}}{(' ' + unit) if unit else ''}", ha="center", va="bottom", fontsize=7.4, fontweight="bold", color="#0F172A")
        ax.set_title(title, fontweight="bold")
        if unit:
            ax.set_ylabel(unit, fontweight="bold")
        ax.legend(loc="upper right", fontsize=7.4, frameon=True, facecolor="#FFFFFF")
        _ = (b1, b2)

    for ax in axes:
        ax.set_xticks(x)
        ax.set_xticklabels(rdf["label"], fontsize=7.8)
        ax.grid(True, axis="y", linestyle=":", color="#CBD5E1", linewidth=0.8)
        ax.spines["top"].set_visible(False)
        ax.spines["right"].set_visible(False)

    fig.suptitle(
        "Koordinat Doğrulamasıyla Güncellenen 4 Saha: Mesafe, LST Genliği, Albedo ve Rölyef Değişimi",
        fontsize=13.5, fontweight="bold", y=0.95, color="#0F172A",
    )
    fig.text(
        0.5, 0.88,
        f"Git geçmişindeki {PREV_PARQUET_REV} (eski konum) vs güncel features_earth.parquet (yeni konum) karşılaştırması",
        ha="center", fontsize=9.5, color="#475569",
    )
    fig.text(
        0.04, 0.025,
        "Not 1: temp_amplitude tanımı geçicidir (docs/data_notes.md f33d0a4).\n"
        "Not 2: Ağrı sahası N39E044 GLO-30 eksiği nedeniyle NASADEM (EGM96) fallback kullanır; rölyef pencere içi fark olduğundan datumdan etkilenmez.",
        fontsize=8, style="italic", color="#475569",
    )
    out = OUT_DIR / "fig05_coordinate_fixes.png"
    fig.savefig(out, dpi=200)
    plt.close(fig)
    return out


def make_fig06() -> Path:
    """Fig 06: ESA WorldCover 10m land cover shares for the 5 MIXED_* sites."""
    mixed = [r for r in MADDE3_AUDITED_RECORDS if r.is_mixed]
    classes = [
        ("wc_bare_pct", "Çıplak Kaya / Toprak / Tuz", "#D6D3D1"),
        ("wc_veg_pct", "Doğal Bitki / Tundra / Step", "#16A34A"),
        ("wc_crop_pct", "Tarım / Nadas", "#EAB308"),
        ("wc_water_pct", "Açık / Sığ Su", "#0284C7"),
        ("wc_snow_pct", "Kalıcı / Mevsimsel Kar-Buz", "#BAE6FD"),
        ("wc_built_pct", "Yapılaşma / Yol", "#475569"),
    ]

    fig, ax = plt.subplots(figsize=(13.5, 6.2))
    fig.subplots_adjust(left=0.22, right=0.73, top=0.81, bottom=0.19)

    y = np.arange(len(mixed))
    left = np.zeros(len(mixed))
    for attr, cname, color in classes:
        vals = np.array([float(getattr(r, attr)) for r in mixed])
        ax.barh(y, vals, left=left, height=0.56, color=color, edgecolor="#0F172A", linewidth=0.6, label=cname)
        for i, v in enumerate(vals):
            if v >= 7.5:
                txt_c = "#FFFFFF" if attr in {"wc_water_pct", "wc_veg_pct", "wc_built_pct"} else "#0F172A"
                ax.text(left[i] + v / 2, i, f"%{v:.1f}", ha="center", va="center", fontsize=8.3, fontweight="bold", color=txt_c)
        left += vals

    ylabels = [f"{SITE_SHORT_TR[r.site_id]}\n[{r.mixed_pixel_flag}]" for r in mixed]
    ax.set_yticks(y)
    ax.set_yticklabels(ylabels, fontsize=9, fontweight="bold")
    ax.invert_yaxis()
    ax.set_xlim(0, 102)
    ax.set_xlabel("ESA WorldCover 10m (2021 v200) Alan Payı (%, r = 1000 m)", fontweight="bold")
    ax.grid(True, axis="x", linestyle=":", color="#CBD5E1", linewidth=0.8)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)

    # Audit notes cleanly aligned to the right of each bar
    s2_notes = {
        "earth_salda_terrace": "Yaz S2 SCL=5: %93.1 çıplak;\nMODIS göl kıyı tarım/stepi ortalama alır.",
        "earth_tuz_golu_south": "26.8% sığ tuzlu su;\nS2 SCL=11 (%17.6) parlak halit YANLIŞ kar!",
        "earth_svalbard_bockfjorden": "Fiyort suyu (%15.5 WC / %29.8 S2)\n+ Arktik tundra (%43.1 WC) karışımı.",
        "earth_suphan_south_apron": "Haziran NDVI=0.251 (yeşil step),\nEylül S2 SCL=5 %99.8 (kurumuş bozkır).",
        "earth_meteor_crater_arizona": "Ağustos S2 %99.9 çıplak görünse de\nWC %41.9 seyrek çöl çalısı içerir.",
    }
    for i, r in enumerate(mixed):
        ax.text(104.5, i, s2_notes[r.site_id], ha="left", va="center", fontsize=8.0, color="#1E293B")

    ax.legend(
        loc="upper center", bbox_to_anchor=(0.45, -0.15), ncol=3,
        frameon=True, facecolor="#FFFFFF", edgecolor="#CBD5E1", fontsize=8.3,
    )
    fig.suptitle(
        "1 km Piksel Temsiliyet Denetimi: 5 MIXED_* Sahasının WorldCover 10m Sınıf Payları",
        fontsize=13.5, fontweight="bold", y=0.95, color="#0F172A",
    )
    fig.text(
        0.5, 0.89,
        "src/earth/mixed_pixel.py (MADDE3_AUDITED_RECORDS) verileri | Eşik: su≥%10, kar≥%10, tarım≥%10 veya bitki≥%25",
        ha="center", fontsize=9.5, color="#475569",
    )
    fig.text(
        0.03, 0.02,
        "Not: Süphan'da yuvarlama toplamı %100.1'dir. MODIS 1 km/500 m pikselinde karışım yüksek olsa da features_earth.parquet sözleşmesi gereği bu 5 saha değiştirilmemiştir.",
        fontsize=8, style="italic", color="#475569",
    )
    out = OUT_DIR / "fig06_mixed_pixel.png"
    fig.savefig(out, dpi=200)
    plt.close(fig)
    return out


def make_fig07(df: pd.DataFrame, meta3d: dict[str, Any]) -> Path:
    """Fig 07: 3D shaded relief surfaces from earth_3d_grids.npz for 4 sites."""
    targets = [
        "earth_meteor_crater_arizona",
        "earth_karapinar_meke",
        "earth_etna_cisternazza",
        "earth_svalbard_bockfjorden",
    ]
    npz = np.load(GRIDS_PATH)
    meta_map = {s["site_id"]: s for s in meta3d["sites"]}
    df_idx = df.set_index("site_id")
    ls = LightSource(azdeg=315, altdeg=35)

    res_m = float(meta3d["grid_res_m"])
    half = (74 - 1) * res_m / 2.0
    xs = np.linspace(-half, half, 74)
    ys = np.linspace(half, -half, 74)
    X, Y = np.meshgrid(xs, ys)

    fig = plt.figure(figsize=(13.2, 10.6))
    fig.subplots_adjust(left=0.03, right=0.97, top=0.87, bottom=0.07, wspace=0.08, hspace=0.22)

    for idx, sid in enumerate(targets, start=1):
        ax = fig.add_subplot(2, 2, idx, projection="3d")
        Z = npz[sid].astype(np.float64)
        rgb = ls.shade(Z, cmap=plt.cm.terrain, vert_exag=1.6, blend_mode="soft", dx=res_m, dy=res_m)
        ax.plot_surface(X, Y, Z, facecolors=rgb, rstride=1, cstride=1, linewidth=0, antialiased=True, shade=False)
        ax.view_init(elev=32, azim=-130)
        ax.set_box_aspect((1.0, 1.0, 0.42))

        m = meta_map[sid]
        p = df_idx.loc[sid]
        emin = int(round(float(m["elev_min_m"]))) or 0
        emax = int(round(float(m["elev_max_m"]))) or 0
        ax.set_title(
            f"{SITE_SHORT_TR[sid]} ({m['vertical_datum']}, {res_m:.0f} m/px)\n"
            f"Rakım: {emin}–{emax} m | "
            f"Rölyef (r=1 km): {p['relief']:.1f} m | Ort. eğim: {p['slope_mean']:.1f}°",
            fontsize=9.5, fontweight="bold", pad=4, color="#0F172A",
        )
        ax.set_xlabel("Doğu–Batı (m)", fontsize=7.8, labelpad=4)
        ax.set_ylabel("Kuzey–Güney (m)", fontsize=7.8, labelpad=4)
        ax.set_zlabel("Rakım (m)", fontsize=7.8, labelpad=4)
        ax.tick_params(labelsize=7.2)

    fig.suptitle(
        "Seçili 4 Sahada E7 3B DEM Yüzey Kabartmaları (74×74 Grid, 2220×2220 m)",
        fontsize=13.5, fontweight="bold", y=0.96, color="#0F172A",
    )
    fig.text(
        0.5, 0.915,
        "Kaynak: data/processed/earth_3d_grids.npz + earth_3d_meta.json (Copernicus DEM GLO-30, 30 m/px, 1.6x düşey abartı)",
        ha="center", fontsize=9.5, color="#475569",
    )
    fig.text(
        0.04, 0.02,
        "Not: 3B gridler E5 Sentinel-2 görsel yamasıyla merkez hizalı görselleştirme içindir; features_earth.parquet içindeki sayısal skor özelliklerini değiştirmez.",
        fontsize=8, style="italic", color="#475569",
    )
    out = OUT_DIR / "fig07_3d_examples.png"
    fig.savefig(out, dpi=200)
    plt.close(fig)
    return out


def make_fig08(df: pd.DataFrame, atlas_meta: dict[str, Any]) -> Path:
    """Fig 08: 8-site Sentinel-2 visual mosaic from earth_atlas/ with r=1 km circle."""
    selected = [
        "earth_etna_cisternazza",
        "earth_meteor_crater_arizona",
        "earth_atacama_yungay",
        "earth_haughton_crater",
        "earth_karapinar_meke",
        "earth_salda_terrace",
        "earth_karacadag_summit",
        "earth_askja_holuhraun",
    ]
    atlas_map = {s["site_id"]: s for s in atlas_meta["sites"]}
    df_idx = df.set_index("site_id")
    res_m = float(atlas_meta["resolution_m"])
    fp_raw = atlas_meta["footprint_m"]
    fp_w, fp_h = (float(fp_raw[0]), float(fp_raw[1])) if isinstance(fp_raw, list) else (float(fp_raw), float(fp_raw))

    fig, axes = plt.subplots(2, 4, figsize=(15.4, 8.7))
    fig.subplots_adjust(left=0.02, right=0.98, top=0.84, bottom=0.08, wspace=0.14, hspace=0.25)

    for ax, sid in zip(axes.flat, selected):
        info = atlas_map[sid]
        p = df_idx.loc[sid]
        img = Image.open(ATLAS_DIR / info["file"]).convert("RGB")
        w_px, h_px = img.size
        ax.imshow(img)
        # r = 1000 m analysis radius ring centered at image middle
        ring = mpatches.Circle(
            (w_px / 2.0, h_px / 2.0), radius=1000.0 / res_m,
            fill=False, edgecolor="#FFFFFF", linestyle="--", linewidth=1.3, alpha=0.95,
        )
        ax.add_patch(ring)
        ax.plot(w_px / 2.0, h_px / 2.0, marker="+", color="#FACC15", markersize=8, markeredgewidth=1.4)

        # 1 km scale bar (bottom-left)
        bar_px = 1000.0 / res_m
        bx, by = 22, h_px - 26
        ax.plot([bx, bx + bar_px], [by, by], color="#FFFFFF", linewidth=2.8)
        ax.text(bx + bar_px / 2, by - 9, "1 km", color="#FFFFFF", fontsize=7.5, fontweight="bold", ha="center", va="bottom",
                bbox=dict(boxstyle="round,pad=0.12", fc="#0F172A", ec="none", alpha=0.6))

        role_tr = "Doğrulama" if info["role"] == "validation" else "Aday"
        lith_tr = LITHOLOGY_TR[str(p["lithology_class"])]
        acq = str(info["acquisition_date"])[:10]
        cld = float(info["local_cloud_pct"])
        ax.set_title(
            f"{SITE_SHORT_TR[sid]}\n{role_tr} · {lith_tr} | {acq} (bulut %{cld:.1f})",
            fontsize=8.1, fontweight="bold", pad=4, color="#0F172A",
        )
        ax.set_xticks([])
        ax.set_yticks([])

    fig.suptitle(
        f"Sentinel-2 L2A Görsel Atlas Örnekleri: 8 Saha Mozaiği ({fp_w:.0f}×{fp_h:.0f} m @ {res_m:.0f} m/px)",
        fontsize=13.5, fontweight="bold", y=0.95, color="#0F172A",
    )
    fig.text(
        0.5, 0.895,
        "Kesikli beyaz daire: r = 1000 m analiz penceresi | Sarı artı: saha merkez koordinatı | Kaynak: data/processed/earth_atlas/metadata.json",
        ha="center", fontsize=9.5, color="#475569",
    )
    fig.text(
        0.02, 0.02,
        "Üst sıra: 4 küresel doğrulama sahası. Alt sıra: 3 Türkiye + 1 İzlanda aday sahası. E5 atlası yalnızca görsel inceleme içindir.",
        fontsize=8, style="italic", color="#475569",
    )
    out = OUT_DIR / "fig08_atlas_mosaic.png"
    fig.savefig(out, dpi=200)
    plt.close(fig)
    return out


def parse_validation_matrix() -> tuple[pd.DataFrame, dict[str, tuple[str, str]]]:
    """Parse 10x3 expectation matrix (§2) and E8 inventory (§4) from validation_expectations.md."""
    lines = (DOCS_DIR / "validation_expectations.md").read_text(encoding="utf-8").splitlines()
    rows: list[dict[str, str]] = []
    e8: dict[str, tuple[str, str]] = {}
    section = None
    for line in lines:
        if line.startswith("## 2."):
            section = "sec2"
            continue
        if line.startswith("## 3."):
            section = None
        elif line.startswith("## 4."):
            section = "sec4"
            continue
        if section == "sec2" and line.startswith("| `earth_"):
            parts = [c.strip() for c in line.strip().strip("|").split("|")]
            sid, axis, kesin, _, _, kaynak = parts[:6]
            sid = sid.strip("`")
            axis = axis.strip("`")
            if "kaynak doğrulanamadı" not in kesin.lower():
                cat = "kesin"
            elif "http" in kaynak:
                cat = "aday"
            else:
                cat = "kaynak_yok"
            rows.append({"site_id": sid, "axis": axis, "cat": cat})
        elif section == "sec4" and line.startswith("| `earth_"):
            parts = [c.strip() for c in line.strip().strip("|").split("|")]
            sid = parts[0].strip("`")
            status = parts[1].strip("`")
            e8[sid] = (status, parts[2])
    return pd.DataFrame(rows), e8


def make_fig09() -> Path:
    """Fig 09: 10x3 validation expectation heatmap + separated E8 ice/permafrost strip."""
    vdf, e8 = parse_validation_matrix()
    site_order = list(dict.fromkeys(vdf["site_id"].tolist()))
    axes_order = ["mobility", "thermal", "surface"]
    axes_tr = ["Mobilite\n(slope/rough/relief)", "Termal\n(temp_amp; inertia NaN)", "Yüzey\n(albedo)"]

    code_map = {"kesin": 2, "aday": 1, "kaynak_yok": 0}
    mat = np.zeros((len(site_order), 3), dtype=int)
    for i, sid in enumerate(site_order):
        for j, axn in enumerate(axes_order):
            c = vdf.loc[(vdf["site_id"] == sid) & (vdf["axis"] == axn), "cat"].iloc[0]
            mat[i, j] = code_map[c]

    n_kesin = int((mat == 2).sum())
    n_aday = int((mat == 1).sum())
    n_yok = int((mat == 0).sum())
    assert (mat.size, n_kesin, n_aday, n_yok) == (30, 10, 14, 6), (mat.size, n_kesin, n_aday, n_yok)

    fig, (ax_main, ax_e8) = plt.subplots(
        1, 2, figsize=(13.6, 8.4), gridspec_kw={"width_ratios": [3.2, 1.15]}
    )
    fig.subplots_adjust(left=0.20, right=0.96, top=0.78, bottom=0.17, wspace=0.12)

    cmap = ListedColormap(["#E2E8F0", "#FDE68A", "#0F766E"])
    ax_main.imshow(mat, cmap=cmap, aspect="auto", vmin=0, vmax=2)

    cell_tags = {
        ("earth_etna_cisternazza", "mobility"): "KESİN\n(Ay rover: ARCHES/ROBEX)",
        ("earth_atacama_yungay", "mobility"): "KESİN\n(Mars Zoë traverse)",
        ("earth_atacama_yungay", "thermal"): "KESİN\n(4-yıllık hiperkurak rejim)",
        ("earth_haughton_crater", "mobility"): "KESİN\n(HMP krater rover/EVA)",
        ("earth_haughton_crater", "thermal"): "KESİN\n(Arktik permafrost / buz)",
        ("earth_mauna_loa_hiseas", "mobility"): "KESİN\n(HI-SEAS bazalt EVA)",
        ("earth_mcmurdo_wright_valley", "thermal"): "KESİN\n(Soğuk çöl / poligonlar)",
        ("earth_lanzarote_timanfaya", "mobility"): "KESİN\n(ESA PANGAEA / bazalt)",
        ("earth_meteor_crater_arizona", "mobility"): "KESİN\n(Krater eğim & Apollo)",
        ("earth_craters_of_the_moon", "mobility"): "KESİN\n(NASA BASALT / FINESSE)",
    }

    for i, sid in enumerate(site_order):
        for j, axn in enumerate(axes_order):
            val = mat[i, j]
            if val == 2:
                txt = cell_tags[(sid, axn)]
                fg = "#FFFFFF"
            elif val == 1:
                if sid == "earth_lunar_crater_nevada":
                    txt = "Aday (indirildi)\narka plan yayını"
                else:
                    txt = "Aday beklenti\n(arka plan kaynaklı)"
                fg = "#78350F"
            else:
                txt = "Kaynak\ndoğrulanamadı"
                fg = "#334155"
            ax_main.text(j, i, txt, ha="center", va="center", fontsize=8.0, fontweight="bold" if val == 2 else "normal", color=fg)

    ax_main.set_xticks(range(3))
    col_sums = [int((mat[:, j] == 2).sum()) for j in range(3)]
    ax_main.set_xticklabels([f"{lbl}\n[Kesin: {cnt}/10]" for lbl, cnt in zip(axes_tr, col_sums)], fontsize=9, fontweight="bold")
    ax_main.xaxis.tick_top()
    ax_main.set_yticks(range(len(site_order)))
    ax_main.set_yticklabels([SITE_SHORT_TR[s] for s in site_order], fontsize=9.2, fontweight="bold")
    ax_main.set_xticks(np.arange(-0.5, 3, 1), minor=True)
    ax_main.set_yticks(np.arange(-0.5, len(site_order), 1), minor=True)
    ax_main.grid(which="minor", color="#FFFFFF", linewidth=2.0)
    ax_main.tick_params(which="minor", length=0)
    ax_main.set_title(f"3 Sayısal Eksen Beklentisi (Kesin: {n_kesin}/30 | Aday: {n_aday}/30 | Doğrulanamadı: {n_yok}/30)", fontsize=10, fontweight="bold", pad=12)

    # Separated E8 qualitative permafrost/ice sidebar
    e8_code_map = {"var": 3, "yok": 2, "veri yok": 1, "kaynak doğrulanamadı": 0}
    e8_mat = np.array([[e8_code_map[e8[s][0]]] for s in site_order])
    e8_cmap = ListedColormap(["#FECACA", "#F1F5F9", "#BFDBFE", "#0369A1"])
    ax_e8.imshow(e8_mat, cmap=e8_cmap, aspect="auto", vmin=0, vmax=3)
    for i, sid in enumerate(site_order):
        st = e8[sid][0]
        fg = "#FFFFFF" if st == "var" else ("#991B1B" if st == "kaynak doğrulanamadı" else "#1E293B")
        extra = "\n(Oliva 2018 teyitsiz)" if st == "kaynak doğrulanamadı" else ""
        ax_e8.text(0, i, f"{st}{extra}", ha="center", va="center", fontsize=8.0, fontweight="bold" if st in {"var", "kaynak doğrulanamadı"} else "normal", color=fg)
    ax_e8.set_xticks([0])
    ax_e8.set_xticklabels(["E8 Buz / Permafrost\n(Nitel; skora girmez)"], fontsize=8.8, fontweight="bold")
    ax_e8.xaxis.tick_top()
    ax_e8.set_yticks([])
    ax_e8.set_yticks(np.arange(-0.5, len(site_order), 1), minor=True)
    ax_e8.grid(which="minor", color="#FFFFFF", linewidth=2.0)
    ax_e8.tick_params(which="minor", length=0)
    ax_e8.set_title("Nitel Envanter (10 Saha)", fontsize=10, fontweight="bold", pad=12)

    legend_handles = [
        mpatches.Patch(facecolor="#0F766E", edgecolor="#0F172A", label=f"Kesin beklenti ({n_kesin}/30)"),
        mpatches.Patch(facecolor="#FDE68A", edgecolor="#0F172A", label=f"Aday / İndirildi — arka plan kaynaklı ({n_aday}/30)"),
        mpatches.Patch(facecolor="#E2E8F0", edgecolor="#0F172A", label=f"Kaynak doğrulanamadı — arka plan DOI yok ({n_yok}/30)"),
        mpatches.Patch(facecolor="#0369A1", edgecolor="#0F172A", label="E8: var (3) | yok (1, mavi) | veri yok (5, gri) | teyitsiz (1, pembe)"),
    ]
    fig.legend(
        handles=legend_handles, loc="lower center", bbox_to_anchor=(0.56, 0.065),
        ncol=2, frameon=True, facecolor="#FFFFFF", edgecolor="#CBD5E1", fontsize=8.2,
    )

    fig.suptitle(
        f"Ön-Kayıtlı Doğrulama Beklenti Matrisi (10 Saha × 3 Eksen = 30 Çift, Kesin {n_kesin}/30)",
        fontsize=13.5, fontweight="bold", y=0.962, color="#0F172A",
    )
    fig.text(
        0.5, 0.916,
        "Tanım: Betimsel sıra tanısı, rol etiketlerinden habersiz (bağımsız holdout doğrulaması değildir; 40 sahanın tamamı Z-ölçeklemesine katılır).",
        ha="center", fontsize=9.5, fontweight="bold", color="#B45309",
    )
    fig.text(
        0.03, 0.018,
        "Not: thermal_inertia tüm sahalarda veri yok (40/40 NaN); temp_amplitude geçici tanımdır (docs/data_notes.md f33d0a4). Kaynak: docs/validation_expectations.md.",
        fontsize=8, style="italic", color="#475569",
    )
    out = OUT_DIR / "fig09_validation_matrix.png"
    fig.savefig(out, dpi=200)
    plt.close(fig)
    return out


def main() -> None:
    """Generate all 9 figures into report/p3_earth/figures/ from local artifacts."""
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    setup_rc()

    df = pd.read_parquet(PARQUET_PATH)
    prev_df = load_prev_parquet()
    meta3d = json.loads(META3D_PATH.read_text(encoding="utf-8"))
    atlas_meta = json.loads((ATLAS_DIR / "metadata.json").read_text(encoding="utf-8"))

    outputs = [
        make_fig01(df),
        make_fig02(df, meta3d, atlas_meta),
        make_fig03(df),
        make_fig04(df),
        make_fig05(df, prev_df),
        make_fig06(),
        make_fig07(df, meta3d),
        make_fig08(df, atlas_meta),
        make_fig09(),
    ]
    for p in outputs:
        print(f"OK | {p.relative_to(REPO_ROOT)} | {p.stat().st_size} bytes")


if __name__ == "__main__":
    main()
