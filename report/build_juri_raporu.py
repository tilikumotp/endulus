"""Build the unslopped Turkish jury technical report (figures, HTML, PDF)."""
from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.colors import LightSource
import matplotlib.patches as mpatches
import numpy as np
import pandas as pd
from PIL import Image

ROOT = Path(__file__).resolve().parent.parent
SRC_DIR = ROOT / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from scoring.config import AXES, MISSION_PRESETS
from scoring.display import expanded_interval
from scoring.portfolio import select_portfolio
from scoring.similarity import (
    axis_gaps,
    axis_pivot,
    axis_scores_with_draws,
    combine_axes_with_uncertainty,
)
from scoring.validation import run_blind_validation
from moon_mars.albedo_sensitivity import run_albedo_sensitivity
from earth.mixed_pixel import build_diagnostic_rows

FIG_DIR = ROOT / "report" / "figures" / "juri"
HTML_PATH = ROOT / "report" / "juri_raporu_tr.html"
PDF_PATH = ROOT / "report" / "juri_raporu_tr.pdf"

TURKISH_CANDIDATE_IDS = {
    "earth_karacadag_summit",
    "earth_karacadag_ovabag",
    "earth_kula_divlit",
    "earth_tendurek_shield",
    "earth_erciyes_kojugedigi",
    "earth_hasandagi_kecekalecik",
    "earth_acigol_guneydag",
    "earth_cappadocia_kavakkoy",
    "earth_tuz_golu_south",
    "earth_salda_terrace",
    "earth_karapinar_meke",
    "earth_suphan_south_apron",
    "earth_nemrut_caldera_flank",
    "earth_agri_dogubayazit_flow",
}

SHORT_NAME_TR: dict[str, str] = {
    "moon_shackleton_rim": "Shackleton Kenarı",
    "moon_connecting_ridge": "Bağlantı Sırtı",
    "moon_de_gerlache_rim": "de Gerlache Kenarı",
    "moon_shackleton_peak": "Shackleton Yakını Tepe",
    "moon_faustini_rim": "Faustini Kenarı A",
    "earth_karapinar_meke": "Karapınar Meke (TR)",
    "earth_mcmurdo_wright_valley": "McMurdo Wright V. [Doğr.]",
    "earth_hasandagi_kecekalecik": "Hasandağı Keçekalecik (TR)",
    "earth_agri_dogubayazit_flow": "Ağrı Doğubayazıt (TR)",
    "earth_erciyes_kojugedigi": "Erciyes Koçdağ (TR)",
    "earth_kula_divlit": "Kula Divlit (TR)",
    "earth_lunar_crater_nevada": "Lunar Crater NV [Doğr.]",
    "earth_nemrut_caldera_flank": "Nemrut Kaldera (TR)",
    "earth_deccan_mahabaleshwar": "Deccan Platosu",
    "earth_karacadag_summit": "Karacadağ Zirve (TR)",
    "earth_karacadag_ovabag": "Karacadağ Ovabağ (TR)",
    "earth_tendurek_shield": "Tendürek Kalkanı (TR)",
    "earth_acigol_guneydag": "Acıgöl Güneydağ (TR)",
    "earth_cappadocia_kavakkoy": "Kapadokya Kavakköy (TR)",
    "earth_suphan_south_apron": "Süphan Güney Eteği (TR)",
    "earth_salda_terrace": "Salda Gölü Terası (TR)",
    "earth_tuz_golu_south": "Tuz Gölü Güney (TR)",
    "earth_etna_cisternazza": "Etna Cisternazza [Doğr.]",
    "earth_atacama_yungay": "Atacama Yungay [Doğr.]",
    "earth_haughton_crater": "Haughton Krateri [Doğr.]",
    "earth_mauna_loa_hiseas": "Mauna Loa HI-SEAS [Doğr.]",
    "earth_lanzarote_timanfaya": "Lanzarote [Doğr.]",
    "earth_meteor_crater_arizona": "Meteor Crater AZ [Doğr.]",
    "earth_craters_of_the_moon": "Craters of Moon [Doğr.]",
    "earth_svalbard_bockfjorden": "Svalbard AMASE [Doğr.]",
    "earth_puna_campo_piedra_pomez": "Puna Piedra Pómez",
    "earth_kilbourne_hole_nm": "Kilbourne Hole NM",
    "earth_chajnantor_plateau": "Chajnantor Platosu",
    "earth_harrat_ash_shaam": "Harrat Ash Shaam",
    "earth_payunia_pampa_negra": "Payunia Pampa Negra",
    "earth_tibesti_tarso_voon": "Tibesti Tarso Voon",
    "earth_qaidam_dalangtan": "Qaidam Dalangtan",
    "earth_pinacate_el_elegante": "Pinacate El Elegante",
    "earth_harrat_rahat_madinah": "Harrat Rahat",
    "earth_waw_an_namus_apron": "Waw an Namus",
    "earth_tongariro_rangipo": "Tongariro Rangipo",
    "earth_tolbachik_apron": "Tolbachik Kamçatka",
    "earth_paricutin_lava_field": "Parícutin Lav Alanı",
    "earth_kilauea_kau_desert": "Kīlauea Kaʻū Çölü",
    "earth_askja_holuhraun": "Askja Holuhraun",
}

LITH_TR: dict[str, str] = {
    "basalt": "Bazalt",
    "pyroclastic_tuff": "Piroklastik tüf",
    "evaporite": "Evaporit / karbonat",
    "impact_breccia": "Çarpma breşi",
    "regolith_permafrost": "Regolit / permafrost",
    "regolith": "Ay regoliti",
    "anorthosite": "Anortozit",
}

INK_BLACK = "#111111"
INK_PRIMARY = "#171717"
INK_SECONDARY = "#525252"
INK_MUTED = "#737373"
GRID_GRAY = "#e5e5e5"
SURFACE_GRAY = "#f5f5f5"
ACCENT_RUST = "#9a3412"


def setup_matplotlib() -> None:
    """Configure uniform white-paper scientific typography and neutral spines."""
    plt.rcParams.update({
        "figure.facecolor": "#ffffff",
        "axes.facecolor": "#ffffff",
        "savefig.facecolor": "#ffffff",
        "font.family": "sans-serif",
        "font.sans-serif": ["Segoe UI", "DejaVu Sans", "Arial"],
        "axes.edgecolor": "#a3a3a3",
        "axes.linewidth": 0.7,
        "axes.labelcolor": INK_PRIMARY,
        "axes.titlecolor": INK_BLACK,
        "xtick.color": INK_SECONDARY,
        "ytick.color": INK_SECONDARY,
        "text.color": INK_PRIMARY,
        "grid.color": GRID_GRAY,
        "grid.linewidth": 0.6,
        "axes.spines.top": False,
        "axes.spines.right": False,
    })


def short_label(site_id: str) -> str:
    """Return concise localized chart/table label for any site_id."""
    return SHORT_NAME_TR.get(site_id, site_id)


def compute_all_metrics() -> dict[str, Any]:
    """Run scoring, uncertainty, validation, portfolio, and sensitivity pipelines."""
    moon_df = pd.read_parquet(ROOT / "data" / "processed" / "features_moon.parquet")
    earth_df = pd.read_parquet(ROOT / "data" / "processed" / "features_earth.parquet")
    meta_by_id = earth_df.set_index("site_id").to_dict(orient="index")

    per_moon: dict[str, dict[str, Any]] = {}
    for _, mrow in moon_df.iterrows():
        mid = str(mrow["site_id"])
        scores_df, draws_df = axis_scores_with_draws(mrow, earth_df, n_boot=200, seed=0)
        piv = axis_pivot(scores_df).set_index("site_id")

        by_preset: dict[str, pd.DataFrame] = {}
        for pname, weights in MISSION_PRESETS.items():
            if pname == "isru_ice":
                continue
            comb = combine_axes_with_uncertainty(scores_df, draws_df, axis_weights=weights)
            comb["mobility"] = comb["site_id"].map(piv["score_mobility"])
            comb["surface"] = comb["site_id"].map(piv["score_surface"])
            comb["role"] = comb["site_id"].map(lambda s: meta_by_id[s]["role"])
            comb["lithology_class"] = comb["site_id"].map(lambda s: meta_by_id[s]["lithology_class"])
            comb["slope_mean"] = comb["site_id"].map(lambda s: meta_by_id[s]["slope_mean"])
            comb["albedo"] = comb["site_id"].map(lambda s: meta_by_id[s]["albedo"])
            comb["albedo_sd"] = comb["site_id"].map(lambda s: meta_by_id[s]["albedo_sd"])
            exp_bounds = [
                expanded_interval(float(r.score), float(r.q05), float(r.q95))
                for r in comb.itertuples()
            ]
            comb["exp_lo"] = [b[0] for b in exp_bounds]
            comb["exp_hi"] = [b[1] for b in exp_bounds]
            comb["was_expanded"] = [b[2] for b in exp_bounds]
            comb = comb.sort_values(["score", "site_id"], ascending=[False, True]).reset_index(drop=True)
            comb["rank"] = np.arange(1, len(comb) + 1)
            by_preset[pname] = comb

        selected, uncovered = select_portfolio(scores_df, min_score=0.70, axes=["mobility", "surface"])
        bval = run_blind_validation(scores_df, earth_df, top_k=5)
        gaps_df = axis_gaps(mrow, earth_df)
        per_moon[mid] = {
            "moon_row": mrow,
            "scores_df": scores_df,
            "piv": piv,
            "by_preset": by_preset,
            "portfolio_selected": selected,
            "portfolio_uncovered": uncovered,
            "blind_val": bval,
            "gaps_df": gaps_df,
        }

    sens_df = run_albedo_sensitivity(moon_df, earth_df)
    mixed_rows = build_diagnostic_rows()
    ea_meta = json.loads((ROOT / "data" / "processed" / "earth_atlas" / "metadata.json").read_text(encoding="utf-8"))
    e3_meta = json.loads((ROOT / "data" / "processed" / "earth_3d_meta.json").read_text(encoding="utf-8"))

    return {
        "moon_df": moon_df,
        "earth_df": earth_df,
        "meta_by_id": meta_by_id,
        "per_moon": per_moon,
        "sens_df": sens_df,
        "mixed_rows": mixed_rows,
        "ea_meta": ea_meta,
        "e3_meta": e3_meta,
    }


def make_fig1_orbital_plate(data: dict[str, Any]) -> None:
    """Create Fig 1: White-paper orbital cartography plate (LOLA 5 m + Sentinel-2 10 m)."""
    npz = np.load(ROOT / "data" / "processed" / "moon_3d" / "moon_shackleton_rim_3d.npz")
    elev = npz["elev_m"].astype(np.float32)
    xs = npz["xs_rel_m"]
    ys = npz["ys_rel_m"]
    wx = npz["profile_we_x_m"]
    wdz = npz["profile_we_dz_m"]

    ls = LightSource(azdeg=315, altdeg=38)
    hill = ls.hillshade(elev, vert_exag=1.2, dx=float(npz["dx_m"]), dy=float(npz["dy_m"]))

    fig = plt.figure(figsize=(11.2, 3.30), dpi=300)
    outer = fig.add_gridspec(1, 2, width_ratios=[2.35, 2.70], wspace=0.16)
    gs_l = outer[0, 0].subgridspec(1, 2, width_ratios=[1.05, 1.0], wspace=0.46)
    gs_r = outer[0, 1].subgridspec(1, 3, wspace=0.12)

    # Panel A: LOLA 5 m/px hillshade + r = 1000 m boundary
    ax0 = fig.add_subplot(gs_l[0, 0])
    extent = [float(xs[0]), float(xs[-1]), float(ys[0]), float(ys[-1])]
    ax0.imshow(hill, cmap="Greys_r", origin="lower", extent=extent, vmin=0.08, vmax=0.95)
    levels = np.linspace(float(np.nanmin(elev)), float(np.nanmax(elev)), 9)
    ax0.contour(xs, ys, elev, levels=levels, colors="#404040", linewidths=0.45, alpha=0.65)
    circ = mpatches.Circle((0, 0), 1000.0, fill=False, edgecolor=INK_BLACK, linewidth=1.3, linestyle="--")
    ax0.add_patch(circ)
    ax0.plot([xs[0] * 0.9, xs[-1] * 0.9], [0, 0], color=ACCENT_RUST, linewidth=0.95, linestyle=":")
    ax0.scatter([0], [0], s=18, color=INK_BLACK, zorder=5)
    ax0.set_xlim(-1100, 1100)
    ax0.set_ylim(-1100, 1100)
    ax0.set_aspect("equal")
    ax0.set_xticks([-1000, 0, 1000])
    ax0.set_yticks([-1000, 0, 1000])
    ax0.tick_params(labelsize=6.8)
    ax0.set_xlabel("Metre (kesik: r=1 km, kırmızı: D-B)", fontsize=7.0)
    ax0.set_title("A · LRO LOLA 5 m/px Shackleton", fontsize=8.3, fontweight="semibold", pad=6, loc="left")

    # Panel B: W-E topographic elevation cross-section
    ax1 = fig.add_subplot(gs_l[0, 1])
    ax1.fill_between(wx, np.min(wdz) - 20, wdz, color="#f0f0f0", edgecolor="none")
    ax1.plot(wx, wdz, color=INK_BLACK, linewidth=1.4)
    ax1.axvline(-1000, color="#737373", linestyle="--", linewidth=0.8)
    ax1.axvline(1000, color="#737373", linestyle="--", linewidth=0.8)
    ax1.axhline(0, color="#a3a3a3", linestyle=":", linewidth=0.7)
    ax1.set_xlim(-1100, 1100)
    ax1.set_ylim(float(np.min(wdz)) - 25, float(np.max(wdz)) + 45)
    ax1.grid(True, axis="y", alpha=0.7)
    ax1.tick_params(labelsize=7)
    ax1.set_xlabel("Merkeze göre uzaklık (m)", fontsize=7.5)
    ax1.set_ylabel("Göreceli kot farkı (m)", fontsize=7.5)
    ax1.set_title("B · Doğu–Batı Topoğrafik Kesiti", fontsize=8.5, fontweight="semibold", pad=6, loc="left")
    ax1.text(0.04, 0.89, f"Rölyef: 501.4 m\nOrt. eğim: 18.5° (P90: 30.8°)",
             transform=ax1.transAxes, fontsize=7, va="top",
             bbox=dict(boxstyle="square,pad=0.25", facecolor="#ffffff", edgecolor="#d4d4d4"))

    # Panels C, D, E: 10 m/px Sentinel-2 L2A orthophotos on crisp white frames
    tiles = [
        ("earth_karapinar_meke.webp", "C · Karapınar Meke", "Yüzey: 0.903 (#1)\nGenel: 0.528 (#1)"),
        ("earth_hasandagi_kecekalecik.webp", "D · Hasandağı Eteği", "Hareket: 0.335 (#1)\nGenel: 0.502 (#3)"),
        ("earth_etna_cisternazza.webp", "E · Etna Cisternazza", "Hareket: 0.299 (#3)\nSaf tefra %99.4"),
    ]
    for idx, (fname, title, subtitle) in enumerate(tiles):
        ax = fig.add_subplot(gs_r[0, idx])
        img = Image.open(ROOT / "data" / "processed" / "earth_atlas" / fname).convert("RGB")
        ax.imshow(img, extent=[-1110, 1110, -1110, 1110])
        c_earth = mpatches.Circle((0, 0), 1000.0, fill=False, edgecolor="#ffffff", linewidth=1.2, linestyle="--")
        ax.add_patch(c_earth)
        ax.set_xticks([])
        ax.set_yticks([])
        for sp in ("top", "right", "bottom", "left"):
            ax.spines[sp].set_visible(True)
            ax.spines[sp].set_color("#d4d4d4")
            ax.spines[sp].set_linewidth(0.8)
        ax.set_title(title, fontsize=8.2, fontweight="semibold", pad=6, loc="left")
        ax.set_xlabel(subtitle, fontsize=7.0, labelpad=5, color=INK_SECONDARY)

    fig.subplots_adjust(left=0.055, right=0.99, top=0.87, bottom=0.19)
    fig.savefig(FIG_DIR / "fig1_orneklem_arazi.png", dpi=300)
    plt.close(fig)


def make_fig2_shackleton_axes(data: dict[str, Any]) -> None:
    """Create Fig 2: Shackleton Top 15 scores + intervals (left) and axis split incl. Etna (right)."""
    bal = data["per_moon"]["moon_shackleton_rim"]["by_preset"]["default"].copy()
    top15 = bal.head(15).copy()
    etna_row = bal[bal["site_id"] == "earth_etna_cisternazza"].copy()
    right_df = pd.concat([top15, etna_row], ignore_index=True)

    fig, (ax_l, ax_r) = plt.subplots(1, 2, figsize=(11.0, 4.05), dpi=300, gridspec_kw={"width_ratios": [1.0, 1.05], "wspace": 0.42})

    # Left: Top 15 overall score + expanded interval [exp_lo, exp_hi]
    y_l = np.arange(len(top15))[::-1]
    for i, (_, row) in enumerate(top15.iterrows()):
        y = y_l[i]
        is_val = row["role"] == "validation"
        col = INK_MUTED if is_val else INK_BLACK
        ax_l.barh(y, float(row["score"]), height=0.56, color="#e5e5e5" if is_val else "#d4d4d4", edgecolor=col, linewidth=0.8)
        ax_l.plot([float(row["exp_lo"]), float(row["exp_hi"])], [y, y], color=ACCENT_RUST if float(row["albedo_sd"]) > 0.04 else INK_BLACK, linewidth=1.5)
        ax_l.scatter([float(row["score"])], [y], color=INK_BLACK, s=16, zorder=4)
        ax_l.text(float(row["exp_hi"]) + 0.012, y, f"{row['score']:.3f}", va="center", fontsize=7.2, color=INK_PRIMARY)

    ax_l.set_yticks(y_l)
    ax_l.set_yticklabels([f"#{int(r['rank'])}  {short_label(str(r['site_id']))}" for _, r in top15.iterrows()], fontsize=7.5)
    ax_l.set_xlim(0.0, 0.74)
    ax_l.grid(True, axis="x", alpha=0.65)
    ax_l.tick_params(axis="x", labelsize=7.5)
    ax_l.set_xlabel("Dengeli benzerlik skoru ve P5–P95 belirsizlik aralığı", fontsize=8)
    ax_l.set_title("A · Shackleton İlk 15 (Genişletilmiş Monte Carlo Bandı)", fontsize=8.8, fontweight="semibold", loc="left", pad=8)
    h_cand = mpatches.Patch(facecolor="#d4d4d4", edgecolor=INK_BLACK, label="Aday saha")
    h_val = mpatches.Patch(facecolor="#e5e5e5", edgecolor=INK_MUTED, label="Doğrulama sahası")
    ax_l.legend(handles=[h_cand, h_val], loc="upper center", bbox_to_anchor=(0.48, -0.17), ncol=2, frameon=False, fontsize=7.0)

    # Right: Mobility vs Surface decoupled bars (Top 15 + #26 Etna)
    y_r = np.arange(len(right_df))[::-1]
    for i, (_, row) in enumerate(right_df.iterrows()):
        y = y_r[i]
        sid = str(row["site_id"])
        mob = float(row["mobility"])
        surf = float(row["surface"])
        mob_col = ACCENT_RUST if sid in ("earth_hasandagi_kecekalecik", "earth_etna_cisternazza") else INK_BLACK
        surf_col = "#d4d4d4"
        ax_r.barh(y - 0.17, surf, height=0.31, color=surf_col, edgecolor="#737373", linewidth=0.6)
        ax_r.barh(y + 0.17, mob, height=0.31, color=mob_col, edgecolor=mob_col, linewidth=0.5)
        ax_r.text(max(mob, surf) + 0.015, y, f"H:{mob:.2f}  Y:{surf:.2f}", va="center", fontsize=6.8, color=INK_SECONDARY)

    # Dotted separator before Etna row at index 15
    ax_r.axhline(0.55, color="#737373", linestyle=":", linewidth=0.9)
    ax_r.set_yticks(y_r)
    ylabels_r = [f"#{int(r['rank'])}  {short_label(str(r['site_id']))}" for _, r in right_df.iterrows()]
    ax_r.set_yticklabels(ylabels_r, fontsize=7.3)
    ax_r.set_xlim(0.0, 1.14)
    ax_r.grid(True, axis="x", alpha=0.65)
    ax_r.tick_params(axis="x", labelsize=7.5)
    ax_r.set_xlabel("Bağımsız eksen skoru (0 = uyumsuz, 1 = özdeş)", fontsize=8)
    ax_r.set_title("B · Eksen Ayrıştırma: Hareket vs Yüzey (ve #26 Etna Örneği)", fontsize=8.8, fontweight="semibold", loc="left", pad=8)

    h_mob = mpatches.Patch(facecolor=INK_BLACK, label="Hareket")
    h_mob_hi = mpatches.Patch(facecolor=ACCENT_RUST, label="Yüksek hareket (#1, #3)")
    h_surf = mpatches.Patch(facecolor="#d4d4d4", edgecolor="#737373", label="Yüzey (albedo)")
    ax_r.legend(handles=[h_mob, h_mob_hi, h_surf], loc="upper center", bbox_to_anchor=(0.48, -0.17), ncol=3, frameon=False, fontsize=6.9, handlelength=1.2, columnspacing=1.0)

    fig.subplots_adjust(left=0.22, right=0.985, top=0.90, bottom=0.20)
    fig.savefig(FIG_DIR / "fig2_shackleton_eksenler.png", dpi=300)
    plt.close(fig)


def _spread_positions(raw_ys: list[float], min_gap: float = 1.65) -> list[float]:
    """Iteratively separate vertically crowded text anchors while preserving order."""
    order = np.argsort(raw_ys)
    pos = np.array(raw_ys, dtype=float)
    sorted_pos = pos[order].copy()
    for _ in range(12):
        for i in range(1, len(sorted_pos)):
            if sorted_pos[i] - sorted_pos[i - 1] < min_gap:
                diff = min_gap - (sorted_pos[i] - sorted_pos[i - 1])
                sorted_pos[i - 1] -= diff * 0.45
                sorted_pos[i] += diff * 0.55
    pos[order] = sorted_pos
    return pos.tolist()


def make_fig3_mission_slopegraph(data: dict[str, Any]) -> None:
    """Create Fig 3: Slopegraph across Balanced -> Rover Mobility -> Radar/Surface on Shackleton."""
    presets = data["per_moon"]["moon_shackleton_rim"]["by_preset"]
    d_df = presets["default"].set_index("site_id")
    m_df = presets["rover_mobility"].set_index("site_id")
    r_df = presets["radar_calibration"].set_index("site_id")

    track_ids = [
        "earth_karapinar_meke",
        "earth_mcmurdo_wright_valley",
        "earth_hasandagi_kecekalecik",
        "earth_agri_dogubayazit_flow",
        "earth_erciyes_kojugedigi",
        "earth_kula_divlit",
        "earth_lunar_crater_nevada",
        "earth_deccan_mahabaleshwar",
        "earth_karacadag_summit",
        "earth_etna_cisternazza",
    ]
    focus_black = {"earth_hasandagi_kecekalecik", "earth_karapinar_meke", "earth_erciyes_kojugedigi"}
    focus_rust = {"earth_etna_cisternazza", "earth_deccan_mahabaleshwar"}

    fig, ax = plt.subplots(figsize=(10.6, 3.60), dpi=300)
    xs = [0.0, 1.0, 2.0]

    rks = {sid: [int(d_df.loc[sid, "rank"]), int(m_df.loc[sid, "rank"]), int(r_df.loc[sid, "rank"])] for sid in track_ids}
    scs = {sid: [float(d_df.loc[sid, "score"]), float(m_df.loc[sid, "score"]), float(r_df.loc[sid, "score"])] for sid in track_ids}
    y_left = dict(zip(track_ids, _spread_positions([rks[s][0] for s in track_ids], min_gap=1.85)))
    y_mid = dict(zip(track_ids, _spread_positions([rks[s][1] for s in track_ids], min_gap=1.95)))
    y_right = dict(zip(track_ids, _spread_positions([rks[s][2] for s in track_ids], min_gap=1.85)))

    for sid in track_ids:
        rk = rks[sid]
        sc = scs[sid]
        if sid in focus_rust:
            col, lw, ls_style, z = ACCENT_RUST, 1.85, "-" if sid == "earth_etna_cisternazza" else "--", 5
        elif sid in focus_black:
            col, lw, ls_style, z = INK_BLACK, 1.75, "-", 4
        else:
            col, lw, ls_style, z = "#a3a3a3", 1.05, "-", 2

        ax.plot(xs, rk, color=col, linewidth=lw, linestyle=ls_style, marker="o", markersize=4.2, zorder=z)
        lbl = short_label(sid)
        ax.text(-0.04, y_left[sid], f"{lbl}  #{rk[0]} ({sc[0]:.3f})", ha="right", va="center", fontsize=7.2,
                color=col if col != "#a3a3a3" else INK_SECONDARY,
                fontweight="semibold" if col != "#a3a3a3" else "normal")
        ax.text(1.0, y_mid[sid], f"{lbl.split()[0]} #{rk[1]} ({sc[1]:.3f})", ha="center", va="center", fontsize=6.6,
                color=col if col != "#a3a3a3" else INK_SECONDARY,
                fontweight="semibold" if col != "#a3a3a3" else "normal",
                bbox=dict(boxstyle="square,pad=0.14", facecolor="#ffffff", edgecolor="none", alpha=0.90), zorder=z + 2)
        ax.text(2.04, y_right[sid], f"#{rk[2]} ({sc[2]:.3f})  {lbl}", ha="left", va="center", fontsize=7.2,
                color=col if col != "#a3a3a3" else INK_SECONDARY,
                fontweight="semibold" if col != "#a3a3a3" else "normal")

    for x in xs:
        ax.axvline(x, color="#d4d4d4", linewidth=0.9, zorder=1)

    max_rk = max(max(v) for v in rks.values())
    ax.invert_yaxis()
    ax.set_ylim(max_rk + 3.0, -1.5)
    ax.set_xlim(-0.92, 2.92)
    ax.set_xticks(xs)
    ax.set_xticklabels(["Dengeli (1 : 1)", "Rover Hareket (2 : 1)", "Radar / Yüzey (1 : 2)"], fontsize=8.5, fontweight="semibold", color=INK_BLACK)
    ax.set_yticks([1, 5, 10, 15, 20, 25, 30, 35])
    ax.tick_params(axis="y", labelsize=7.5)
    ax.set_ylabel("40 saha içindeki sıralama (#1 en iyi)", fontsize=8)
    ax.spines["bottom"].set_visible(False)
    ax.set_title("Görev Profili Ağırlıklandırmasının Shackleton Sıralamasına Etkisi", fontsize=9.0, fontweight="semibold", loc="left", pad=10)

    fig.subplots_adjust(left=0.07, right=0.98, top=0.89, bottom=0.10)
    fig.savefig(FIG_DIR / "fig3_gorev_duyarliligi.png", dpi=300)
    plt.close(fig)


def make_fig4_multiregion_heatmap(data: dict[str, Any]) -> None:
    """Create Fig 4: Clean neutral heatmap across all 5 Moon South Pole references."""
    moon_order = [
        ("moon_shackleton_rim", "Shackleton\n18.5°"),
        ("moon_de_gerlache_rim", "de Gerlache\n10.8°"),
        ("moon_connecting_ridge", "Bağlantı Sırtı\n9.4°"),
        ("moon_shackleton_peak", "Tepe\n8.1°"),
        ("moon_faustini_rim", "Faustini A\n5.2°"),
    ]
    site_order = [
        "earth_karapinar_meke",
        "earth_hasandagi_kecekalecik",
        "earth_erciyes_kojugedigi",
        "earth_agri_dogubayazit_flow",
        "earth_salda_terrace",
        "earth_karacadag_summit",
        "earth_mcmurdo_wright_valley",
        "earth_lunar_crater_nevada",
        "earth_puna_campo_piedra_pomez",
        "earth_deccan_mahabaleshwar",
        "earth_etna_cisternazza",
        "earth_atacama_yungay",
    ]

    mat_gen = np.zeros((len(site_order), len(moon_order)))
    mat_mob = np.zeros((len(site_order), len(moon_order)))
    for c, (mid, _) in enumerate(moon_order):
        bal = data["per_moon"][mid]["by_preset"]["default"].set_index("site_id")
        for r, sid in enumerate(site_order):
            mat_gen[r, c] = float(bal.loc[sid, "score"])
            mat_mob[r, c] = float(bal.loc[sid, "mobility"])

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(10.8, 4.15), dpi=300, sharey=True, gridspec_kw={"wspace": 0.10})
    for ax, mat, title in [
        (ax1, mat_gen, "A · Dengeli Genel Skor (0 – 1)"),
        (ax2, mat_mob, "B · Bağımsız Hareket Ekseni (0 – 1)"),
    ]:
        ax.imshow(mat, cmap="Greys", vmin=0.02, vmax=0.92, aspect="auto")
        for r in range(mat.shape[0]):
            for c in range(mat.shape[1]):
                val = mat[r, c]
                txt_col = "#ffffff" if val >= 0.48 else INK_PRIMARY
                ax.text(c, r, f"{val:.2f}", ha="center", va="center", fontsize=7.4,
                        color=txt_col, fontweight="semibold" if val >= 0.65 else "normal")
        ax.set_xticks(np.arange(len(moon_order)))
        ax.set_xticklabels([lbl for _, lbl in moon_order], fontsize=7.5)
        ax.set_title(title, fontsize=8.8, fontweight="semibold", loc="left", pad=8)
        for sp in ("top", "right", "bottom", "left"):
            ax.spines[sp].set_visible(True)
            ax.spines[sp].set_color("#d4d4d4")

    ax1.set_yticks(np.arange(len(site_order)))
    ax1.set_yticklabels([short_label(s) for s in site_order], fontsize=7.6)
    ax1.axhline(5.5, color=INK_BLACK, linewidth=1.1, linestyle="--")
    ax2.axhline(5.5, color=INK_BLACK, linewidth=1.1, linestyle="--")

    fig.subplots_adjust(left=0.22, right=0.985, top=0.88, bottom=0.14)
    fig.savefig(FIG_DIR / "fig4_bes_bolge_isi.png", dpi=300)
    plt.close(fig)


def make_fig5_physical_and_validation(data: dict[str, Any]) -> None:
    """Create Fig 5: Physical space scatter (slope vs albedo) + Blind validation slope shift."""
    earth_df = data["earth_df"]
    moon_df = data["moon_df"]

    fig, (ax_l, ax_r) = plt.subplots(1, 2, figsize=(11.0, 3.35), dpi=300, gridspec_kw={"width_ratios": [1.08, 1.0], "wspace": 0.40})

    # Left: slope_mean vs albedo physical space
    alb_min, alb_max = float(moon_df["albedo"].min()), float(moon_df["albedo"].max())
    ax_l.axvspan(alb_min, alb_max, color="#e5e5e5", alpha=0.85, zorder=1, label=f"Ay albedo bandı ({alb_min:.3f}–{alb_max:.3f})")

    for _, row in earth_df.iterrows():
        sid = str(row["site_id"])
        x, y = float(row["albedo"]), float(row["slope_mean"])
        if row["role"] == "validation":
            ax_l.scatter(x, y, s=34, facecolors="#ffffff", edgecolors=INK_BLACK, linewidths=1.1, zorder=4)
        elif sid in TURKISH_CANDIDATE_IDS:
            ax_l.scatter(x, y, s=30, color=ACCENT_RUST, marker="D", alpha=0.9, zorder=3)
        else:
            ax_l.scatter(x, y, s=26, color="#8c8c8c", alpha=0.8, zorder=2)

    for _, row in moon_df.iterrows():
        ax_l.scatter(float(row["albedo"]), float(row["slope_mean"]), s=46, color=INK_BLACK, marker="s", zorder=5)

    annots = [
        ("moon_shackleton_rim", "Shackleton", (-6, 5), "right"),
        ("moon_faustini_rim", "Faustini", (6, -5), "left"),
        ("earth_etna_cisternazza", "Etna", (6, 2), "left"),
        ("earth_hasandagi_kecekalecik", "Hasandağı", (6, 2), "left"),
        ("earth_karapinar_meke", "Karapınar", (5, 4), "left"),
        ("earth_haughton_crater", "Haughton", (-6, 3), "right"),
        ("earth_atacama_yungay", "Atacama", (-6, -4), "right"),
        ("earth_karacadag_summit", "Karacadağ Z.", (-6, 1), "right"),
    ]
    all_pts = pd.concat([earth_df[["site_id", "albedo", "slope_mean"]], moon_df[["site_id", "albedo", "slope_mean"]]], ignore_index=True).set_index("site_id")
    for sid, txt, (dx, dy), ha in annots:
        px, py = float(all_pts.loc[sid, "albedo"]), float(all_pts.loc[sid, "slope_mean"])
        ax_l.annotate(txt, (px, py), xytext=(dx, dy), textcoords="offset points", fontsize=6.9, ha=ha,
                      color=ACCENT_RUST if sid in TURKISH_CANDIDATE_IDS else INK_BLACK)

    ax_l.set_xlim(0.01, 0.285)
    ax_l.set_ylim(-0.5, 25.0)
    ax_l.grid(True, alpha=0.6)
    ax_l.tick_params(labelsize=7.5)
    ax_l.set_xlabel("Geniş bant albedo (0–1)", fontsize=8)
    ax_l.set_ylabel("Ortalama eğim (°)", fontsize=8)
    ax_l.set_title("A · Fiziksel Uzay: Eğim ve Albedo Dağılımı", fontsize=8.8, fontweight="semibold", loc="left", pad=8)

    lg_handles = [
        plt.Line2D([0], [0], marker="s", color="w", markerfacecolor=INK_BLACK, markersize=6, label="Ay referansları (5)"),
        plt.Line2D([0], [0], marker="o", color="w", markerfacecolor="#ffffff", markeredgecolor=INK_BLACK, markersize=5.5, label="Doğrulama (10)"),
        plt.Line2D([0], [0], marker="D", color="w", markerfacecolor=ACCENT_RUST, markersize=5, label="Türkiye adayları (14)"),
        plt.Line2D([0], [0], marker="o", color="w", markerfacecolor="#8c8c8c", markersize=5, label="Küresel adaylar (16)"),
    ]
    ax_l.legend(handles=lg_handles, loc="upper right", frameon=True, facecolor="#ffffff", edgecolor="#e5e5e5", fontsize=6.7)

    # Right: Role-blind validation slope regime shift (Mobility rank /40: Shackleton 18.5° vs Faustini 5.2°)
    sh_bv_df = data["per_moon"]["moon_shackleton_rim"]["blind_val"]
    fa_bv_df = data["per_moon"]["moon_faustini_rim"]["blind_val"]
    sh_mob = sh_bv_df[sh_bv_df["axis"] == "mobility"].set_index("site_id")["rank"]
    fa_mob = fa_bv_df[fa_bv_df["axis"] == "mobility"].set_index("site_id")["rank"]
    val_df = pd.DataFrame({
        "sh_mob_rank": sh_mob.astype(int),
        "fa_mob_rank": fa_mob.astype(int),
    }).sort_values("sh_mob_rank")

    y_v = np.arange(len(val_df))[::-1]
    for i, (sid, r) in enumerate(val_df.iterrows()):
        y = y_v[i]
        s_rk, f_rk = int(r["sh_mob_rank"]), int(r["fa_mob_rank"])
        ax_r.plot([s_rk, f_rk], [y, y], color="#a3a3a3", linewidth=1.2, zorder=2)
        ax_r.scatter([s_rk], [y], color=INK_BLACK, s=28, zorder=4, label="Shackleton (18.5°)" if i == 0 else None)
        ax_r.scatter([f_rk], [y], color=ACCENT_RUST, marker="s", s=26, zorder=4, label="Faustini (5.2°)" if i == 0 else None)

    ax_r.set_yticks(y_v)
    ax_r.set_yticklabels([short_label(str(sid)).replace(" [Doğr.]", "") for sid in val_df.index], fontsize=7.4)
    ax_r.set_xlim(0.0, 42.5)
    ax_r.axvline(5.5, color="#d4d4d4", linestyle="--", linewidth=0.9)
    ax_r.grid(True, axis="x", alpha=0.6)
    ax_r.tick_params(axis="x", labelsize=7.5)
    ax_r.set_xlabel("Rol-kör Hareket sırası (40 saha içinde #1 = en yakın)", fontsize=8)
    ax_r.set_title("B · Doğrulama Sıra Kayması: Dik Shackleton vs Düz Faustini", fontsize=8.8, fontweight="semibold", loc="left", pad=8)
    ax_r.legend(loc="lower right", frameon=True, facecolor="#ffffff", edgecolor="#e5e5e5", fontsize=7.0)

    fig.subplots_adjust(left=0.075, right=0.985, top=0.89, bottom=0.14)
    fig.savefig(FIG_DIR / "fig5_fiziksel_uzay_dogrulama.png", dpi=300)
    plt.close(fig)


def make_fig6_robustness_and_audit(data: dict[str, Any]) -> None:
    """Create Fig 6: Albedo c-factor sensitivity curve (left) + Data quality audit bars (right)."""
    sens_df = data["sens_df"]
    earth_df = data["earth_df"]
    mixed_rows = data["mixed_rows"]
    # Count unique Earth sites that are MIXED_* (5 confirmed mixed sites in features_earth)
    mixed_earth_ids = {r["site_id"] for r in mixed_rows if r["rule_is_mixed"] and r["site_id"] in data["meta_by_id"]}

    fig, (ax_l, ax_r) = plt.subplots(1, 2, figsize=(10.8, 3.4), dpi=300, gridspec_kw={"width_ratios": [1.05, 1.0], "wspace": 0.34})

    ax_l.axvspan(0.34, 0.42, color="#f0f0f0", zorder=1, label="Kararlı çekirdek bandı (0.34–0.42)")
    styles = [
        ("moon_shackleton_rim", INK_BLACK, "-", "o", "Shackleton Kenarı"),
        ("moon_connecting_ridge", "#525252", "--", "s", "Bağlantı Sırtı"),
        ("moon_de_gerlache_rim", "#737373", "-.", "^", "de Gerlache Kenarı"),
        ("moon_shackleton_peak", "#a3a3a3", ":", "D", "Shackleton Tepe"),
        ("moon_faustini_rim", ACCENT_RUST, "-", "v", "Faustini Kenarı A"),
    ]
    for mid, col, ls_s, mk, lbl in styles:
        sub = sens_df[sens_df["ref_site_id"] == mid].sort_values("factor")
        ax_l.plot(sub["factor"], sub["spearman_rho_overall"], color=col, linestyle=ls_s, marker=mk, markersize=4.2, linewidth=1.3, label=lbl, zorder=3)

    ax_l.set_xticks([0.30, 0.34, 0.38, 0.42, 0.46])
    ax_l.set_ylim(0.62, 1.03)
    ax_l.grid(True, alpha=0.65)
    ax_l.tick_params(labelsize=7.5)
    ax_l.set_xlabel("LOLA 1064 nm -> geniş bant dönüşüm çarpanı (c)", fontsize=8)
    ax_l.set_ylabel("Baz (c = 0.38) ile Spearman ρ", fontsize=8)
    ax_l.set_title("A · Albedo Kalibrasyon Çarpanı Duyarlılığı (ρ = 0.866–0.944)", fontsize=8.6, fontweight="semibold", loc="left", pad=8)
    ax_l.legend(loc="lower center", ncol=2, frameon=True, facecolor="#ffffff", edgecolor="#e5e5e5", fontsize=6.6)

    # Right: Stacked horizontal proportions of dataset integrity / audit status
    dem_glo = int((earth_df["slope_mean_src"] == "Copernicus_DEM_GLO-30").sum())
    dem_nasa = len(earth_df) - dem_glo
    n_mixed = len(mixed_earth_ids)
    n_pure = len(earth_df) - n_mixed
    cv_hi = int((earth_df["albedo_sd"] / earth_df["albedo"] > 0.30).sum())
    cv_ok = len(earth_df) - cv_hi
    s2_ok = int(data["ea_meta"]["included_count"])

    categories = [
        ("DEM kaynağı\n(40 Dünya)", dem_glo, dem_nasa, f"{dem_glo} GLO-30", f"{dem_nasa} NASADEM"),
        ("10 m piksel saflığı\n(WorldCover/S2)", n_pure, n_mixed, f"{n_pure} PURE_TARGET", f"{n_mixed} MIXED_*"),
        ("Albedo CV <= 0.30\n(MCD43A3 500 m)", cv_ok, cv_hi, f"{cv_ok} kararlı", f"{cv_hi} CV > 0.30"),
        ("Sözleşme denetimi\n(Ay + Dünya)", 45, 0, "45/45 Doğrulanmış (0 MOCK)", ""),
        ("10 m görsel atlas\n(Sentinel-2 L2A)", s2_ok, 0, f"{s2_ok}/40 Bulutsuz/Seçili", ""),
    ]
    y_c = np.arange(len(categories))[::-1]
    for i, (lbl, p1, p2, t1, t2) in enumerate(categories):
        y = y_c[i]
        tot = p1 + p2
        w1 = 100.0 * p1 / tot
        w2 = 100.0 * p2 / tot
        ax_r.barh(y, w1, height=0.52, color="#e5e5e5", edgecolor=INK_BLACK, linewidth=0.7)
        if w2 > 0:
            ax_r.barh(y, w2, left=w1, height=0.52, color=ACCENT_RUST, edgecolor=ACCENT_RUST, linewidth=0.6)
        ax_r.text(2.5, y, t1, va="center", ha="left", fontsize=7.2, color=INK_BLACK, fontweight="semibold")
        if t2:
            ax_r.text(min(w1 + 1.5, 82), y - 0.34, t2, va="top", ha="left" if w1 < 80 else "right", fontsize=6.7, color=ACCENT_RUST)

    ax_r.set_yticks(y_c)
    ax_r.set_yticklabels([c[0] for c in categories], fontsize=7.3)
    ax_r.set_xlim(0, 102)
    ax_r.set_ylim(-0.65, len(categories) - 0.3)
    ax_r.set_xticks([0, 25, 50, 75, 100])
    ax_r.set_xticklabels(["%0", "%25", "%50", "%75", "%100"], fontsize=7.3)
    ax_r.grid(True, axis="x", alpha=0.55)
    ax_r.set_title("B · Veri Doğruluğu ve Karışık Piksel Denetimi", fontsize=8.6, fontweight="semibold", loc="left", pad=8)

    fig.subplots_adjust(left=0.06, right=0.985, top=0.87, bottom=0.15)
    fig.savefig(FIG_DIR / "fig6_albedo_ve_belirsizlik.png", dpi=300)
    plt.close(fig)


def build_html(data: dict[str, Any]) -> str:
    """Assemble clean 8-page unslopped HTML report using verified computed metrics."""
    sh = data["per_moon"]["moon_shackleton_rim"]
    sh_bal = sh["by_preset"]["default"]
    top10 = sh_bal.head(10)

    # Top 10 rows for Shackleton
    top10_rows_html = []
    for _, r in top10.iterrows():
        sid = str(r["site_id"])
        role_txt = "Doğrulama" if r["role"] == "validation" else ("Aday (TR)" if sid in TURKISH_CANDIDATE_IDS else "Aday (Küresel)")
        gap_tr = "Hareket" if float(r["mobility"]) < float(r["surface"]) else "Yüzey"
        top10_rows_html.append(
            f"<tr>"
            f"<td class='num'>{int(r['rank'])}</td>"
            f"<td>{short_label(sid).replace(' [Doğr.]', '')}</td>"
            f"<td>{role_txt}</td>"
            f"<td>{LITH_TR.get(str(r['lithology_class']), str(r['lithology_class']))}</td>"
            f"<td class='num strong'>{r['score']:.3f}</td>"
            f"<td class='num'>[{r['exp_lo']:.3f}–{r['exp_hi']:.3f}]</td>"
            f"<td class='num'>{r['mobility']:.3f}</td>"
            f"<td class='num'>{r['surface']:.3f}</td>"
            f"<td>{gap_tr}</td>"
            f"</tr>"
        )

    # Portfolio summary across all 5 Moon references
    port_rows_html = []
    moon_order = [
        ("moon_shackleton_rim", "18.50° / 90.4 m"),
        ("moon_de_gerlache_rim", "10.83° / 45.0 m"),
        ("moon_connecting_ridge", "9.43° / 42.5 m"),
        ("moon_shackleton_peak", "8.11° / 32.3 m"),
        ("moon_faustini_rim", "5.20° / 12.3 m"),
    ]
    for mid, topo_str in moon_order:
        pm = data["per_moon"][mid]
        sel_str = ", ".join(short_label(s).replace(" [Doğr.]", "") for s in pm["portfolio_selected"])
        unc_str = "Yok (tüm eksenler >= 0.70)" if not pm["portfolio_uncovered"] else "Hareket (< 0.70)"
        if "earth_salda_terrace" in pm["portfolio_selected"]:
            note = "Salda, WorldCover'da MIXED_CROP+VEG bayraklıdır"
        elif "earth_mcmurdo_wright_valley" in pm["portfolio_selected"]:
            note = "McMurdo albedo_sd=0.096 ile geniş bantlıdır"
        elif not pm["portfolio_uncovered"]:
            note = "Seçilen iki saha iki aktif ekseni de >= 0.70 kapsar"
        else:
            note = "Dünya havuzunda >= 0.70 hareket eşiği yok"
        port_rows_html.append(
            f"<tr>"
            f"<td>{short_label(mid)}</td>"
            f"<td class='num'>{topo_str}</td>"
            f"<td>{sel_str}</td>"
            f"<td>{unc_str}</td>"
            f"<td>{note}</td>"
            f"</tr>"
        )

    # Moon 5 reference summary
    moon_tbl_rows = []
    for _, mr in data["moon_df"].iterrows():
        sid = str(mr["site_id"])
        moon_tbl_rows.append(
            f"<tr>"
            f"<td>{short_label(sid)}</td>"
            f"<td class='num'>{mr['lat']:.2f}°, {mr['lon']:.2f}°</td>"
            f"<td class='num'>{mr['slope_mean']:.2f} ± {mr['slope_mean_sd']:.2f}°</td>"
            f"<td class='num'>{mr['slope_p90']:.2f}°</td>"
            f"<td class='num'>{mr['roughness']:.2f} m</td>"
            f"<td class='num'>{mr['relief']:.1f} m</td>"
            f"<td class='num'>{mr['albedo']:.3f} ± {mr['albedo_sd']:.3f}</td>"
            f"</tr>"
        )

    # Top TR candidate highlights across Moon targets
    tr_keys = [
        ("earth_karapinar_meke", "Konya (Maar/Cüruf)"),
        ("earth_hasandagi_kecekalecik", "Aksaray (Andezit-Bazalt)"),
        ("earth_erciyes_kojugedigi", "Kayseri (Koçdağ Yamacı)"),
        ("earth_agri_dogubayazit_flow", "Ağrı (NASADEM Fallback)"),
        ("earth_karacadag_summit", "Diyarbakır-Şanlıurfa (Bazalt)"),
        ("earth_karacadag_ovabag", "Diyarbakır (Düz Bazalt)"),
        ("earth_salda_terrace", "Burdur (Hidromanyezit)"),
    ]
    sh_idx = sh_bal.set_index("site_id")
    fa_idx = data["per_moon"]["moon_faustini_rim"]["by_preset"]["default"].set_index("site_id")
    ed_idx = data["earth_df"].set_index("site_id")
    tr_rows_html = []
    for sid, loc in tr_keys:
        er = ed_idx.loc[sid]
        sr = sh_idx.loc[sid]
        fr = fa_idx.loc[sid]
        lit_status = "Bilinen Mars analogu (Horgan 2020)" if sid == "earth_salda_terrace" else (
            "Bilinen maar sahası (Keller 1974)" if sid == "earth_karapinar_meke" else "Yeni nicel test adayı (volkanoloji ref.)"
        )
        tr_rows_html.append(
            f"<tr>"
            f"<td>{short_label(sid).replace(' (TR)', '')}</td>"
            f"<td>{loc}</td>"
            f"<td class='num'>{er['slope_mean']:.2f}° / {er['roughness']:.1f} m</td>"
            f"<td class='num'>{er['albedo']:.3f}</td>"
            f"<td class='num'>{sr['score']:.3f} (#{int(sr['rank'])})</td>"
            f"<td class='num'>{fr['score']:.3f} (#{int(fr['rank'])})</td>"
            f"<td>{lit_status}</td>"
            f"</tr>"
        )

    css = """
    @page {
      size: A4;
      margin: 0;
    }
    * {
      box-sizing: border-box;
      margin: 0;
      padding: 0;
    }
    html, body {
      background: #ffffff;
      color: #171717;
      font-family: "Segoe UI", -apple-system, BlinkMacSystemFont, Arial, sans-serif;
      font-size: 9.2pt;
      line-height: 1.46;
      -webkit-font-smoothing: antialiased;
    }
    @media screen {
      body {
        background: #ededed;
        padding: 20px 0;
      }
      .page {
        margin: 0 auto 20px auto;
        box-shadow: 0 1px 4px rgba(0, 0, 0, 0.08);
      }
    }
    .page {
      width: 210mm;
      height: 297mm;
      padding: 13mm 15mm 13mm 15mm;
      background: #ffffff;
      display: flex;
      flex-direction: column;
      justify-content: space-between;
      break-after: page;
      page-break-after: always;
      overflow: hidden;
    }
    .page:last-child {
      break-after: auto;
      page-break-after: auto;
    }
    .page-body {
      flex: 1 1 auto;
    }
    .header-rule {
      border-top: 2px solid #111111;
      padding-top: 10px;
      margin-bottom: 10px;
    }
    .running-head {
      display: flex;
      justify-content: space-between;
      align-items: baseline;
      border-bottom: 1px solid rgba(23, 23, 23, 0.14);
      padding-bottom: 5px;
      margin-bottom: 10px;
      font-size: 8pt;
      color: #737373;
    }
    .running-head span:first-child {
      color: #111111;
      font-weight: 600;
    }
    h1 {
      font-size: 20pt;
      line-height: 1.18;
      font-weight: 600;
      color: #111111;
      letter-spacing: -0.015em;
      margin-bottom: 6px;
    }
    h2 {
      font-size: 12.2pt;
      line-height: 1.25;
      font-weight: 600;
      color: #111111;
      margin-top: 10px;
      margin-bottom: 6px;
      padding-bottom: 3px;
      border-bottom: 1px solid rgba(23, 23, 23, 0.14);
    }
    h3 {
      font-size: 9.8pt;
      line-height: 1.3;
      font-weight: 600;
      color: #111111;
      margin-top: 8px;
      margin-bottom: 3px;
    }
    p {
      margin-bottom: 7px;
      color: #262626;
    }
    .lead {
      font-size: 9.8pt;
      line-height: 1.48;
      color: #171717;
      margin-bottom: 10px;
    }
    .meta-line {
      font-size: 8.2pt;
      color: #525252;
      margin-bottom: 8px;
    }
    .kpi-grid {
      display: grid;
      grid-template-columns: repeat(4, 1fr);
      border-top: 1px solid #111111;
      border-bottom: 1px solid rgba(23, 23, 23, 0.16);
      margin: 8px 0 12px 0;
    }
    .kpi-cell {
      padding: 8px 10px 8px 0;
    }
    .kpi-cell + .kpi-cell {
      padding-left: 12px;
      border-left: 1px solid rgba(23, 23, 23, 0.12);
    }
    .kpi-val {
      font-size: 15pt;
      font-weight: 600;
      color: #111111;
      font-variant-numeric: tabular-nums;
      line-height: 1.15;
    }
    .kpi-lbl {
      font-size: 7.8pt;
      color: #525252;
      margin-top: 2px;
    }
    .fig-wrap {
      margin: 6px 0 10px 0;
    }
    .fig-wrap img {
      display: block;
      width: 100%;
      height: auto;
    }
    .fig-cap {
      font-size: 7.8pt;
      color: #525252;
      margin-top: 4px;
      line-height: 1.35;
    }
    .two-col {
      display: grid;
      grid-template-columns: 1fr 1fr;
      gap: 14px;
      margin-top: 4px;
    }
    .card-plain {
      border: 1px solid rgba(23, 23, 23, 0.14);
      padding: 9px 11px;
      background: #ffffff;
      margin-bottom: 8px;
    }
    .card-tint {
      border-left: 2px solid #111111;
      background: #f5f5f5;
      padding: 8px 11px;
      margin: 7px 0 9px 0;
    }
    .formula-box {
      font-family: "Consolas", "Cascadia Mono", monospace;
      font-size: 8.2pt;
      background: #f5f5f5;
      border: 1px solid rgba(23, 23, 23, 0.12);
      padding: 6px 9px;
      margin: 5px 0 7px 0;
      color: #111111;
    }
    table {
      width: 100%;
      border-collapse: collapse;
      margin: 5px 0 9px 0;
      font-size: 8pt;
    }
    th {
      text-align: left;
      font-weight: 600;
      color: #111111;
      border-top: 1px solid #111111;
      border-bottom: 1px solid #111111;
      padding: 4.5px 6px;
      background: #f5f5f5;
    }
    td {
      padding: 4px 6px;
      border-bottom: 1px solid rgba(23, 23, 23, 0.10);
      vertical-align: top;
      color: #262626;
    }
    th.num, td.num {
      text-align: right;
      font-family: "Consolas", "Cascadia Mono", monospace;
      font-variant-numeric: tabular-nums;
      white-space: nowrap;
    }
    td.strong {
      font-weight: 600;
      color: #111111;
    }
    .compact-table {
      font-size: 7.5pt;
      margin: 4px 0 6px 0;
    }
    .compact-table th {
      padding: 3.2px 5px;
    }
    .compact-table td {
      padding: 2.8px 5px;
    }
    ul {
      padding-left: 15px;
      margin: 3px 0 7px 0;
    }
    li {
      margin-bottom: 4px;
      color: #262626;
    }
    code {
      font-family: "Consolas", "Cascadia Mono", monospace;
      font-size: 8pt;
      background: #f5f5f5;
      padding: 0 3px;
      color: #111111;
    }
    .ref-list {
      column-count: 2;
      column-gap: 16px;
      font-size: 7.4pt;
      line-height: 1.38;
      color: #404040;
      padding-left: 14px;
    }
    .ref-list li {
      margin-bottom: 3.5px;
      break-inside: avoid;
    }
    .footer {
      border-top: 1px solid rgba(23, 23, 23, 0.14);
      padding-top: 5px;
      display: flex;
      justify-content: space-between;
      font-size: 7.6pt;
      color: #737373;
      font-variant-numeric: tabular-nums;
      margin-top: 8px;
    }
    """

    def page_wrap(page_num: int, section_title: str, body_html: str) -> str:
        header = "" if page_num == 1 else (
            f"<div class='running-head'>"
            f"<span>{section_title}</span>"
            f"<span>Ay Güney Kutbu Çok-Eksenli Test Sahası Değerlendirmesi</span>"
            f"</div>"
        )
        footer = (
            f"<div class='footer'>"
            f"<span>NASA Space Apps 2026 · Doğrulanmış Uydu Çıktısı (0 MOCK)</span>"
            f"<span>{page_num} / 8</span>"
            f"</div>"
        )
        return f"<section class='page'><div class='page-body'>{header}{body_html}</div>{footer}</section>"

    # Page 1: Executive Overview, Core Premise & Orbital Specimen Plate
    p1_body = f"""
    <div class='header-rule'>
      <div class='meta-line'>NASA Space Apps 2026 · Teknik Değerlendirme ve Yöntem Raporu</div>
      <h1>Ay Güney Kutbu İçin Çok-Eksenli Yeryüzü Test Sahası Değerlendirmesi</h1>
      <p class='lead'>Yeryüzünde tek başına hiçbir saha Ay'ı veya Mars'ı tümüyle kopyalayamaz. Bu çalışma, tekil puan ortalamaları yerine fiziksel eksenleri ayırarak her sonuca ölçüm belirsizliği, kırılma sınırı ve görev profili bağlayan şeffaf bir test sahası seçim ve portföy sistemi sunar</p>
    </div>

    <div class='kpi-grid'>
      <div class='kpi-cell'><div class='kpi-val'>5</div><div class='kpi-lbl'>Artemis III Güney Kutbu referansı (5 m/px)</div></div>
      <div class='kpi-cell'><div class='kpi-val'>40</div><div class='kpi-lbl'>Yeryüzü sahası (10 doğrulama, 30 aday)</div></div>
      <div class='kpi-cell'><div class='kpi-val'>2 + 1</div><div class='kpi-lbl'>v1 aktif eksen: Hareket, Yüzey (Termal askıda)</div></div>
      <div class='kpi-cell'><div class='kpi-val'>0 / 51</div><div class='kpi-lbl'>Sentetik (MOCK) veri / geçen birim test</div></div>
    </div>

    <div class='fig-wrap'>
      <img src='figures/juri/fig1_orneklem_arazi.png' alt='Shackleton Kenarı 5 m LOLA rölyef ve 10 m Sentinel-2 Yeryüzü sahaları'>
      <div class='fig-cap'>Şekil 1: Sol — LRO LOLA 5 m/px Shackleton Krater Kenarı (Site 04, r = 1000 m analiz çemberi) ve 501.4 m rölyefli D–B kesiti. Sağ — 10 m/px Sentinel-2 L2A uydu görüntüleriyle Karapınar Meke (Yüzey 0.903), Hasandağı (Hareket #1) ve Etna Cisternazza (%99.4 çıplak tefra)</div>
    </div>

    <h2>Yöntemsel Sorunlar ve Geliştirilen Çözüm Mimarisi</h2>
    <table>
      <thead>
        <tr>
          <th style='width:24%'>Klasik Yaklaşım Sorunu</th>
          <th style='width:28%'>Uygulanan Algoritmik Çözüm</th>
          <th style='width:48%'>Sağlanan Mühendislik Kazanımı</th>
        </tr>
      </thead>
      <tbody>
        <tr>
          <td class='strong'>Ortalama skor aldatmacası</td>
          <td>Eksen ayrıştırma (<code>Hareket</code>, <code>Yüzey</code>, <code>Termal</code>)</td>
          <td>Örneğin Etna Cisternazza, Hareket ekseninde 40 saha içinde #3 (0.299) iken koyu albedosu (0.047) yüzünden dengeli skorda #26'ya düşer; ayrıştırma bu sahayı görünür kılar</td>
        </tr>
        <tr>
          <td class='strong'>Coğrafi grid & makro eğim hatası</td>
          <td>Metrik CRS + <code>lstsq</code> düzlem arındırma</td>
          <td>Kutupta derece gridi eğimi bozar; ham yükseklik standart sapması ise tepe eğimini pürüzlülük sanır. Düzlem eğimi çıkarılarak yalnızca yerel mikro-rölyef ölçülür</td>
        </tr>
        <tr>
          <td class='strong'>Belirsizliği gizleyen nokta skor</td>
          <td>200 çekimli Monte Carlo + <code>expanded_interval</code></td>
          <td>Her özelliğin ölçüm hatası (<code>X_sd</code>) skora taşınır; McMurdo gibi kar sınırında kararsız sahalar geniş P5–P95 bandıyla ([0.088–0.513]) dürüstçe ayrılır</td>
        </tr>
        <tr>
          <td class='strong'>Fiziksel rejim tutarsızlığı</td>
          <td>Bilinçli Termal Askıya Alma (Karar #30)</td>
          <td>Ay'daki 29.53 günlük vakumlu döngü (~187 K) ile Dünya'nın 24 saatlik atmosferli günlük döngüsü (2.7–29.3 K) aynı sayısal skorda birleştirilmedi</td>
        </tr>
        <tr>
          <td class='strong'>Tek "en iyi" saha saplantısı</td>
          <td>Açgözlü küme örtme (<code>select_portfolio</code>)</td>
          <td>Tek sahaya sıkışmak yerine en az aday ile tüm ulaşılabilir eksenleri örter ve Yeryüzünde hiç ulaşılamayan eşikleri açıkta bırakır</td>
        </tr>
      </tbody>
    </table>
    """

    # Page 2: Mathematical & Algorithmic Architecture Justifications
    p2_body = f"""
    <h2>1. Algoritmik Tasarım ve Matematiksel Gerekçeler</h2>
    <p>Her algoritmik karar, gezegensel yüzey analojilerinde sık görülen istatistiksel ve fiziksel yanılgıları engellemek üzere seçilmiştir. Aşağıda boru hattındaki çekirdek yöntemlerin neden seçildiği ve hangi problemi çözdüğü özetlenir</p>

    <div class='two-col'>
      <div>
        <h3>1.1 Çok-Eksenli Ayrıştırma ve Ağırlıklı Birleşim</h3>
        <p>Yedi sayısal özellik üç bağımsız fiziksel eksende toplanır: <strong>Hareket</strong> (<code>slope_mean</code>, <code>slope_p90</code>, <code>roughness</code>, <code>relief</code>), <strong>Yüzey</strong> (<code>albedo</code>) ve v1'de bilinçli askıda tutulan <strong>Termal</strong> (<code>temp_amplitude</code>, <code>thermal_inertia</code>). Bir sahanın eğim profili mükemmelken parlaklığı uyumsuz olabilir; eksen skorları ayrı ayrı raporlanmadan genel sıralama yapılmaz</p>

        <h3>1.2 Neden Metrik Projeksiyon ve Düzlem Arındırma</h3>
        <p>Shackleton Krater Kenarı <code>89.78°S</code> enlemindedir. <code>EPSG:4326</code> derece gridinde meridyensel piksel genişliği kutupta sıfıra yaklaşır ve türev tabanlı eğimi yapay büyütür. Bu nedenle Ay sahaları doğrudan <strong>Güney Kutbu Polar Stereografik</strong> (<code>R = 1737.4 km</code>) CRS'de, Dünya sahaları ise merkez koordinata göre yerel <strong>UTM / UPS</strong> metre projeksiyonunda işlenir. Eğim tüm sahalarda ortak <code>np.gradient</code> formülüyle (<code>arctan(hypot(dz_dx, dz_dy))</code>) türetilir</p>
        <p><strong>Çözdüğü kritik sorun:</strong> Ham <code>std(elev)</code> hesaplamak, düzgün fakat eğimli bir krater yamacını "aşırı pürüzlü" gösterir. Bunu önlemek için her <code>r = 1000 m</code> çemberdeki <code>(dx, dy, z)</code> noktalarına <code>np.linalg.lstsq</code> ile en küçük kareler düzlemi uydurulup makro yamaç eğimi çıkarılır; yalnızca düzlem kalıntısının standart sapması (<code>ddof=1</code>) pürüzlülük olarak alınır</p>
      </div>

      <div>
        <h3>1.3 Üst-Sınırsız Z-Skoru ve Üstel Dönüşüm</h3>
        <p>Dünya referans evreninin 40 sahalık dağılımında her özellik önce <code>ddof=0</code> popülasyon ortalaması ve standart sapmasıyla Z-skoruna çevrilir; Ay ile Dünya arasındaki öklidyen eksen uzaklığı ve benzerlik puanı şu formülle üretilir:</p>
        <div class='formula-box'>D_axis = sqrt( mean_f( ((x_earth_f - x_ref_f) / sigma_earth_f)^2 ) )<br>S_axis = exp(-D_axis)    in (0, 1]<br>S_overall = sum_a(w_a * S_a) / sum_a(w_a)</div>
        <ul>
          <li><strong>Neden min-max yerine Z-skoru:</strong> Min-max ölçekleme uç bir aykırı sahaya (ör. Shackleton 501 m rölyef) tüm diğer farkları sıkıştırır; Z-skoru ise varyans birimi cinsinden dengeli ölçek kurar</li>
          <li><strong>Neden sabit üst-kesimsiz <code>exp(-D)</code>:</strong> Bazı çalışmalarda büyük farklar sabit eşikte sıfırlanır ve sıralama türevi ölür. <code>exp(-D)</code> her aday için kesin azalan ve pürüzsüz bir skor verir. <strong>Önemli uyarı:</strong> <code>S_axis</code> bir olasılık ya da yüzde güven değeri değil, yalnızca sıralama indeksidir</li>
        </ul>

        <h3>1.4 Bilinçli Termal Askıya Alma (Lider Kararı #30)</h3>
        <p><code>AGENTS.md §5</code> veri sözleşmesi tüm gök cisimlerinde ortak fiziksel tanım şartı koşar. Ay Güney Kutbu'nda LRO Diviner (240 m) sıyırıcı güneş açısı (~1.5°) ve vakum altında 29.53 Dünya günlük sinodik döngüde <code>Shackleton ~187 K</code> hücre içi salınım ölçerken, Dünya <code>MOD11A2.061</code> 24 saatlik atmosferli döngünün yıllık ortalamasını (2.7–29.3 K) verir. Aynı tanımı zorlamak sahte bir "termal eşleşme" üreteceği için termal eksen v1'de <code>NaN</code> bırakılmıştır</p>
      </div>
    </div>

    <h2>Referans Alınan 5 Artemis III Ay Güney Kutbu Sahası (LRO LOLA 5 m/px, r = 1000 m)</h2>
    <table>
      <thead>
        <tr>
          <th>Referans Saha</th>
          <th class='num'>Koordinat</th>
          <th class='num'>Ort. Eğim ± sd</th>
          <th class='num'>P90 Eğim</th>
          <th class='num'>Pürüzlülük</th>
          <th class='num'>Rölyef</th>
          <th class='num'>Albedo ± sd</th>
        </tr>
      </thead>
      <tbody>
        {''.join(moon_tbl_rows)}
      </tbody>
    </table>
    """

    # Page 3: Uncertainty Propagation, Albedo Calibration & Portfolio Logic
    p3_body = f"""
    <h2>2. Belirsizlik Yayılımı, Kalibrasyon Duyarlılığı ve Görev Portföyü</h2>
    <div class='two-col'>
      <div>
        <h3>2.1 Deterministik <code>blake2b</code> Monte Carlo Yayılımı</h3>
        <p>Uydu ürünlerinin kendi hata haritalarından gelen 1-sigma belirsizlikler (<code>X_sd</code>; örn. PGDA klon ansamblı <code>slperr</code>/<code>toterr</code> ve GLO-30 <code>sigma_z_rel = 1.0 m</code>) skorun dışına itilmez. Her (referans, aday) çifti için <code>n_boot = 200</code> normal dağılımlı çekim yapılır. Farklı Python/OS sürümlerinde rastgelelik kaymasını önlemek amacıyla tohum değeri gömülü <code>hashlib.blake2b</code> anahtarından deterministik üretilir</p>
        <p><strong><code>expanded_interval</code> gerekçesi:</strong> Ay ve Dünya ölçüm hataları doğrusal olmayan <code>exp(-D)</code> içinden geçerken dağılım çarpıklaşır; örneğin yüksek albedo varyanslı (<code>albedo_sd = 0.0961</code>) <strong>McMurdo</strong> veya asimetrik Shackleton Tepe skorlarında nominal nokta skor bazen 5.–95. yüzdelik dışına kayar. <code>display.py</code> içindeki <code>expanded_interval</code> fonksiyonu <code>[min(score, q05), max(score, q95)]</code> zarfını alarak noktanın kendi bandı dışında görünmesini önler</p>
      </div>

      <div>
        <h3>2.2 LOLA 1064 nm -> Geniş Bant Kalibrasyonu (<code>×0.38</code>)</h3>
        <p>LRO LOLA aktif lazer altimetresi <code>LDAM_50S_1000M</code> sıfır faz açısında (<code>α = 0°</code>, karşıtlık parlaması dahil, ~0.358–0.387) monokromatik yansıma ölçer; Dünya <code>MCD43A3.061</code> ise kısa dalga güneş albedosudur (0.028–0.264). Doğrudan kıyaslama için LRO literatürü doğrultusunda <code>×0.38</code> ölçeği uygulanmıştır. Bu proje katsayısının sıralamayı aşırı hassaslaştırıp hassaslaştırmadığını görmek üzere <code>c ∈ [0.30, 0.46]</code> taraması çalıştırıldı (Şekil 2a)</p>

        <h3>2.3 Görev Ağırlıklandırma ve Açgözlü Portföy</h3>
        <p>Mühendislik ekibinin test amacı değiştikçe ağırlık vektörü değişir: <code>Dengeli (1:1)</code>, <code>Rover Hareket (2:1)</code> ve <code>Radar / Yüzey (1:2)</code> (Streamlit'te <code>isru_ice</code> ön ayarı ekli olup v1'de buz verisi olmadığı için Web arayüzünde sadeleştirilmiştir). <code>select_portfolio</code> algoritması ise verilen eşikte (<code>min_score = 0.70</code>) en çok kapsanmamış ekseni ekleyen adayı adım adım seçer</p>
      </div>
    </div>

    <div class='fig-wrap'>
      <img src='figures/juri/fig6_albedo_ve_belirsizlik.png' alt='Albedo kalibrasyon duyarlılığı ve veri denetim özeti'>
      <div class='fig-cap'>Şekil 2: Sol — Geniş bant dönüşüm çarpanı c değiştikçe 5 Ay bölgesinde baz (c = 0.38) ile korunan Spearman sıralama korelasyonu (0.34–0.42 çekirdek bandında ρ = 0.866–0.944). Sağ — 40 Dünya sahasının DEM kaynağı, 10 m piksel saflığı ve belirsizlik dağılımı</div>
    </div>

    <div class='card-tint'>
      <strong>Kalibrasyon Sonucu:</strong> Çarpan <code>c</code> değeri %±10 aralığında (<code>0.34–0.42</code>) oynadığında Shackleton için sıralama korelasyonu <code>ρ = 0.886–0.889</code>, Bağlantı Sırtı için <code>0.892–0.940</code> ve de Gerlache için <code>0.926–0.937</code> düzeyinde korunur. Ancak aşırı uçlarda (<code>c = 0.30</code> → Ay albedosu <code>0.116</code>) Deccan/Tendürek gibi daha koyu sahalar öne geçer; bu sınır <code>data_sources_moon.md</code> içinde açıkça kayıtlıdır
    </div>
    """

    # Page 4: Data Integrity, Orbital Products & Mixed-Pixel Audit
    p4_body = """
    <h2>3. Verilerin Doğruluğu, Uydu Kaynakları ve Ölçek Denetimi</h2>
    <p>Projedeki her sayısal hücre, doğrulanmış açık NASA / ESA / Copernicus uydu ürünlerinden otomatik çekilir. Sözleşme denetleyicisi <code>scripts/validate_all.py --fail-on-mock</code> çalıştırıldığında hem <code>features_moon.parquet</code> (5 satır) hem de <code>features_earth.parquet</code> (40 satır) için <strong>0/45 MOCK, 0 hata, 0 uyarı</strong> verir ve tüm <strong>51 birim test (pytest)</strong> sıfır hatayla geçer</p>

    <table>
      <thead>
        <tr>
          <th>Cisim</th>
          <th>Değişkenler</th>
          <th>Doğrulanmış Uydu Ürünü (<code>_src</code>)</th>
          <th class='num'>Yerel Çözünürlük</th>
          <th>Doğrulama ve Özel Teknik Not</th>
        </tr>
      </thead>
      <tbody>
        <tr>
          <td>Ay</td>
          <td>Eğim, P90, Pürüzlülük, Rölyef</td>
          <td><code>LRO_LOLA_PGDA_*_5mpp_v2021</code></td>
          <td class='num'>5.0 m</td>
          <td>NASA GSFC PGDA Ürün 78 (Barker vd., 2021); piksel hata haritaları (<code>slperr</code>, <code>toterr</code>) + 200 bootstrap</td>
        </tr>
        <tr>
          <td>Ay</td>
          <td>Albedo</td>
          <td><code>LRO-L-LOLA-4-GDR-V1.0 (LDAM_50S)</code></td>
          <td class='num'>1000.0 m</td>
          <td>1064 nm sıfır faz yansıması; Earth ile birim uyumu için <code>×0.38</code> geniş bant dönüşümü</td>
        </tr>
        <tr>
          <td>Dünya</td>
          <td>Eğim, P90, Pürüzlülük, Rölyef (39 saha)</td>
          <td><code>Copernicus_DEM_GLO-30</code></td>
          <td class='num'>30.0 m</td>
          <td>Airbus DGED EGM2008; resmi <code>LE90 &lt; 2.0 m</code> spesifikasyonundan <code>sigma_z_rel = 1.0 m</code></td>
        </tr>
        <tr>
          <td>Dünya</td>
          <td>DEM Yedeği (1/40 saha)</td>
          <td><code>NASADEM_HGT_v001</code></td>
          <td class='num'>30.0 m</td>
          <td>Ağrı (<code>N39 E044</code>) GLO-30 arşivinde 404 döndüğü için EGM96 yedeği tetiklendi; göreli türev etkilenmez</td>
        </tr>
        <tr>
          <td>Dünya</td>
          <td>Albedo (40 saha)</td>
          <td><code>MODIS MCD43A3.061</code></td>
          <td class='num'>500.0 m</td>
          <td><code>Albedo_BSA_shortwave</code> (5×5 piksel); ayrıca 6 sahada <code>MCD43A4.061</code> (Liang 2001, <code>NDSI &lt; 0.40</code>) ile çapraz doğrulandı</td>
        </tr>
        <tr>
          <td>Dünya</td>
          <td>Sıcaklık (Arşiv, v1'de skora girmez)</td>
          <td><code>MOD11A2.061_annual_mean</code></td>
          <td class='num'>1000.0 m</td>
          <td>2024 tam yıl 24 kompozit (<code>QC &lt;= 1</code>, yarımküre yanlılıksız); thermal eksen Karar #30 gereği askıda</td>
        </tr>
      </tbody>
    </table>

    <h2>Ölçek Farkı Sınırı ve 10 m Karışık Piksel Denetimi (WorldCover + Sentinel-2 SCL)</h2>
    <p>Veri doğruluğu yalnızca ürün adıyla bitmez: <strong>(1) Çözünürlük uçurumu:</strong> Ay DEM'i <code>5 m/px</code> iken Dünya DEM'i <code>30 m/px</code>'dir (6× örnekleme farkı). 30 m piksel Ay ölçeğindeki 5–15 m'lik bloklu mikro-rölyefi yumuşatır. <strong>(2) Karışık piksel etkisi:</strong> 500 m MODIS albedo ve 1 km LST penceresi heterojen kıyı/step sahalarında çevredeki su, tarım veya çöl çalısı örtüsünü de ortalamaya katar. Bu nedenle 40 sahanın tamamı <code>10 m ESA WorldCover v200</code> ve <code>Sentinel-2 L2A</code> ile denetlenmiş, aşağıdaki <strong>5 saha</strong> açıkça <code>MIXED_*</code> bayrağıyla işaretlenmiştir</p>

    <table>
      <thead>
        <tr>
          <th>Saha</th>
          <th>Teşhis Bayrağı</th>
          <th>10 m Örtü Dağılımı (WorldCover / S2)</th>
          <th>Fiziksel Yorum ve Dikkat Notu</th>
        </tr>
      </thead>
      <tbody>
        <tr>
          <td>Salda Gölü Terası (TR)</td>
          <td><code>MIXED_CROP+VEG</code></td>
          <td>Çıplak %2.0 · Tarım %40.2 · Doğal bitki %55.9</td>
          <td>Hidromanyezit kıyı barı (~150 m) 500 m MODIS'te serpantin/kıyı bitkisiyle karışır (albedo 0.127)</td>
        </tr>
        <tr>
          <td>Tuz Gölü Güney (TR)</td>
          <td><code>MIXED_WATER</code></td>
          <td>Çıplak/tuz %73.2 · Sığ su %26.8</td>
          <td>S2'de %17.6 <code>SCL=11</code> parlak tuz yanlış kar pozitifi verir; parquet <code>MCD43A3 (0.206)</code> NDSI maskesiz olduğu için etkilenmez</td>
        </tr>
        <tr>
          <td>Svalbard Bockfjorden</td>
          <td><code>MIXED_WATER+VEG</code></td>
          <td>Çıplak %41.1 · Fiyort suyu %15.5 · Tundra %43.1</td>
          <td>1 km pencerede fiyort suyu ve Arktik tundra hem albedoyu hem arşiv LST genliğini bastırır</td>
        </tr>
        <tr>
          <td>Süphan Güney Eteği (TR)</td>
          <td><code>MIXED_CROP+VEG</code></td>
          <td>Mera %79.2 · Tarım %18.4 · Çıplak %2.3</td>
          <td>Haziran'da yeşil (NDVI 0.251), Eylül'de kuru anız (<code>bare_5 %99.8</code>); 5 km taramada daha çıplak etek dik koni olduğundan konum korundu</td>
        </tr>
        <tr>
          <td>Meteor Crater (AZ)</td>
          <td><code>MIXED_VEG</code></td>
          <td>Çıplak %57.3 · Çöl çalısı %41.9</td>
          <td>Yaz S2'de %99.9 çıplak görünse de WorldCover %41.9 seyrek çöl çalısı tanımlar</td>
        </tr>
        <tr>
          <td class='strong'>Etna Cisternazza (Kontrol)</td>
          <td class='strong'><code>PURE_TARGET</code></td>
          <td class='strong'>Çıplak tefra %99.4 · Bitki %0.6 (Yaz kar %0)</td>
          <td>OSM gerçek Cisternazza kraterine (<code>37.7257, 15.0084</code>) taşınarak Şubat kar payı %36.5'tan %22.0'a indirildi</td>
        </tr>
      </tbody>
    </table>
    """

    kz = ed_idx.loc["earth_karacadag_summit"]
    ko = ed_idx.loc["earth_karacadag_ovabag"]
    kz_sh = sh_idx.loc["earth_karacadag_summit"]
    kz_fa = fa_idx.loc["earth_karacadag_summit"]
    ko_sh = sh_idx.loc["earth_karacadag_ovabag"]

    sh_bv_df = data["per_moon"]["moon_shackleton_rim"]["blind_val"]
    fa_bv_df = data["per_moon"]["moon_faustini_rim"]["blind_val"]
    sh_mob_r = sh_bv_df[sh_bv_df["axis"] == "mobility"].set_index("site_id")["rank"]
    fa_mob_r = fa_bv_df[fa_bv_df["axis"] == "mobility"].set_index("site_id")["rank"]

    sh_mob_preset = sh["by_preset"]["rover_mobility"].set_index("site_id")
    sh_rad_preset = sh["by_preset"]["radar_calibration"].set_index("site_id")
    sh_hasan_m = sh_mob_preset.loc["earth_hasandagi_kecekalecik"]
    sh_erciyes_m = sh_mob_preset.loc["earth_erciyes_kojugedigi"]
    sh_etna_m = sh_mob_preset.loc["earth_etna_cisternazza"]
    sh_kara_r = sh_rad_preset.loc["earth_karapinar_meke"]

    # Page 5: Shackleton Crater Rim Results & Mission Sensitivity
    p5_body = f"""
    <h2>4. Shackleton Krater Kenarı Sonuçları ve Görev Duyarlılığı</h2>
    <p>Artemis III aday bölgesi <strong>Shackleton Krater Kenarı</strong> (<code>18.50°</code> ort. eğim, <code>90.43 m</code> pürüzlülük, <code>501.4 m</code> rölyef, <code>0.147</code> albedo) için 40 Yeryüzü sahası sıralandığında, Dünya üzerindeki çok dik ve koyu bir krater kenarı bile Shackleton'un iki eksenini aynı anda yüksek puanda kapatamaz</p>

    <table class='compact-table'>
      <thead>
        <tr>
          <th class='num'>Sıra</th>
          <th>Yeryüzü Sahası</th>
          <th>Rol / Bölge</th>
          <th>Litoloji</th>
          <th class='num'>Genel</th>
          <th class='num'>P5–P95 Zarfı</th>
          <th class='num'>Hareket</th>
          <th class='num'>Yüzey</th>
          <th>Zayıf Eksen</th>
        </tr>
      </thead>
      <tbody>
        {''.join(top10_rows_html)}
      </tbody>
    </table>

    <div class='fig-wrap'>
      <img src='figures/juri/fig2_shackleton_eksenler.png' alt='Shackleton İlk 15 genel skorlar ve eksen ayrışması'>
      <div class='fig-cap'>Şekil 3: Shackleton Krater Kenarı için Dengeli İlk 15 saha (sol) ile Hareket vs Yüzey ayrışması ve #26 Etna karşılaştırması (sağ)</div>
    </div>

    <div class='fig-wrap'>
      <img src='figures/juri/fig3_gorev_duyarliligi.png' alt='Görev profiline göre sıralama değişimi'>
      <div class='fig-cap'>Şekil 4: Görev ağırlıkları değiştikçe sıralamanın evrimi — Rover Hareket modunda Hasandağı (#{int(sh_idx.loc['earth_hasandagi_kecekalecik','rank'])} → #{int(sh_hasan_m['rank'])}, {sh_hasan_m['score']:.3f}), Erciyes (#{int(sh_idx.loc['earth_erciyes_kojugedigi','rank'])} → #{int(sh_erciyes_m['rank'])}, {sh_erciyes_m['score']:.3f}) ve Etna (#{int(sh_idx.loc['earth_etna_cisternazza','rank'])} → #{int(sh_etna_m['rank'])}, {sh_etna_m['score']:.3f}) yükselir; Radar/Yüzey modunda Karapınar Meke ({sh_kara_r['score']:.3f}) liderliğini pekiştirir</div>
    </div>
    """

    # Page 6: 5 Moon References + Turkish Candidates & Literature Position
    p6_body = f"""
    <h2>5. Beş Ay Güney Kutbu Bölgesi ve Türkiye Adaylarının Konumlandırılması</h2>
    <p>Proje yalnızca tek bir kratere kilitlenmez. Beş farklı Artemis III referans bölgesinin ortalama eğimi <code>18.50°</code>'den (Shackleton) <code>5.20°</code>'ye (Faustini) indikçe Dünya sahalarının eksen profilleri sistematik biçimde yer değiştirir</p>

    <div class='fig-wrap'>
      <img src='figures/juri/fig4_bes_bolge_isi.png' alt='5 Ay bölgesi genel ve hareket ısı haritası'>
      <div class='fig-cap'>Şekil 5: Beş Ay referans bölgesinde Türkiye vurguları (üst 6) ve küresel doğrulama/aday sahalarının (alt 6) Dengeli ve Hareket skorları. Eğim azaldıkça (soldan sağa) Hareket uyumu keskin biçimde artar</div>
    </div>

    <h3>Türkiye Adaylarının Bilimsel Statüsü (Özgünlük Sınırı ve Karacadağ Yorumu)</h3>
    <p><code>AGENTS.md</code> gereği Türkiye'den seçilen 14 aday sahanın mevcut literatür durumu denetlenmiş, halihazırda bilinen Mars/gezegen analoglarında asılsız "ilk keşif" iddiasından kaçınılmıştır. Kalkan volkanı ve volkanik plato sahaları ise "doğrulanmış analog" olarak değil, eksen skorlarıyla değerlendirilen <strong>aday test sahaları</strong> olarak sunulur:</p>

    <table>
      <thead>
        <tr>
          <th>Türkiye Adayı</th>
          <th>Bölge ve Yapı</th>
          <th class='num'>Eğim / Pürüzlülük</th>
          <th class='num'>Albedo</th>
          <th class='num'>Shackleton (18.5°)</th>
          <th class='num'>Faustini (5.2°)</th>
          <th>Literatür Statüsü ve Yorum</th>
        </tr>
      </thead>
      <tbody>
        {''.join(tr_rows_html)}
      </tbody>
    </table>

    <div class='card-tint'>
      <strong>Karacadağ Bulgusu (Abartısız Gerçekçi Değerlendirme):</strong> Güneydoğu Anadolu'daki bazaltik Karacadağ kalkan volkanının iki noktası keskin biçimde ayrılır. Zirve platosu (<code>Kollubaba</code>, eğim <code>{kz['slope_mean']:.2f}°</code>, pürüzlülük <code>{kz['roughness']:.1f} m</code>, albedo <code>{kz['albedo']:.3f}</code>) dik Shackleton'da #{int(kz_sh['rank'])} sırada (<code>{kz_sh['score']:.3f}</code>) yer alırken düz Faustini'de #{int(kz_fa['rank'])} sıraya (<code>{kz_fa['score']:.3f}</code>) yükselir. Buna karşılık <code>Ovabağ</code> eteği son derece düz olduğu için (<code>{ko['slope_mean']:.2f}°</code>, pürüzlülük <code>{ko['roughness']:.1f} m</code>) dik Ay krater kenarlarıyla düşük hareket uyumu gösterir (Shackleton #{int(ko_sh['rank'])}, <code>{ko_sh['score']:.3f}</code>) ve düz iniş platosu testleri dışında önerilmez
    </div>
    """

    # Page 7: Blind Validation Diagnostic, Portfolio & Physical Breakdown Limits
    p7_body = f"""
    <h2>6. Rol-Kör Sıra Tanısı, Açgözlü Portföy ve Fiziksel Sınırlar</h2>

    <div class='fig-wrap'>
      <img src='figures/juri/fig5_fiziksel_uzay_dogrulama.png' alt='Fiziksel uzay dağılımı ve rol-kör doğrulama sıra kayması'>
      <div class='fig-cap'>Şekil 6: Sol — 40 Dünya sahası ve 5 Ay hedefinin (koyu kareler) eğim–albedo dağılımı; gri şerit Ay Güney Kutbu geniş bant albedo bandıdır (0.136–0.147). Sağ — 10 bilinen doğrulama sahasının dik Shackleton vs düz Faustini üzerindeki Hareket sıra kayması</div>
    </div>

    <div class='two-col'>
      <div>
        <h3>6.1 Rol-Kör Sıra Tanısı (Bilimsel Kapsam Sınırı)</h3>
        <p><code>validation</code> etiketi hesaplamada gizlendiğinde sistem fiziksel olarak hangi bilinen analogları öne çıkarır? Bu kontrol ikili sınıflandırıcı (ROC/AUC) değildir; <code>validation_expectations.md</code> içinde önceden kayıtlı 11 kesin hücreyle tutarlılığı ölçen <strong>betimleyici bir sıra tanısıdır</strong>:</p>
        <ul>
          <li><strong>Dik krater (Shackleton 18.50°):</strong> Engebeli krater/lav eğitim sahaları <code>Etna (#{int(sh_mob_r['earth_etna_cisternazza'])})</code>, <code>Lunar Crater NV (#{int(sh_mob_r['earth_lunar_crater_nevada'])})</code> ve <code>Meteor Crater (#{int(sh_mob_r['earth_meteor_crater_arizona'])})</code> Hareket ilk 8'ine girer; düz kutup/çöl sahaları <code>Haughton (#{int(sh_mob_r['earth_haughton_crater'])})</code> ve <code>Atacama (#{int(sh_mob_r['earth_atacama_yungay'])})</code> doğal olarak geride kalır</li>
          <li><strong>Düz plato (Faustini 5.20°):</strong> Tam tersine <code>Svalbard (#{int(fa_mob_r['earth_svalbard_bockfjorden'])})</code>, <code>Mauna Loa (#{int(fa_mob_r['earth_mauna_loa_hiseas'])})</code>, <code>Haughton (#{int(fa_mob_r['earth_haughton_crater'])})</code> ve <code>Atacama (#{int(fa_mob_r['earth_atacama_yungay'])})</code> Hareket İlk 8'ine yükselir; dik <code>Etna (#{int(fa_mob_r['earth_etna_cisternazza'])})</code> son sıraya iner</li>
        </ul>
      </div>

      <div>
        <h3>6.2 Analojinin Kırıldığı Fiziksel Sınırlar</h3>
        <table class='compact-table'>
          <thead>
            <tr>
              <th>Parametre</th>
              <th>Ay Güney Kutbu</th>
              <th>Dünya Limiti / Kırılma Etkisi</th>
            </tr>
          </thead>
          <tbody>
            <tr>
              <td class='strong'>Yerçekimi</td>
              <td><code>1.62 m/s^2</code> (0.165 g)</td>
              <td>1 g (6× fazla); tekerlek batması ve şasi yükü Dünya'da farklı sapma verir</td>
            </tr>
            <tr>
              <td class='strong'>Vakum &amp; Toz</td>
              <td><code>~10^-12 torr</code></td>
              <td>Hava sönümlemesi, rüzgar ve aşınmayan nemli/kil toz Dünya'da kaçınılmazdır</td>
            </tr>
            <tr>
              <td class='strong'>Termal Döngü</td>
              <td>29.53 gün (~144–187 K)</td>
              <td>24 saat ve konveksiyon (~3–29 K); termal şok yalnızca vakum odasında sınanır</td>
            </tr>
            <tr>
              <td class='strong'>Ölçek &amp; Buz</td>
              <td>5 m LOLA; PSR 40–100 K</td>
              <td>30 m GLO-30 alt-piksel kayaları yumuşatır; v1'de sayısal buz verisi yoktur</td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <h3>6.3 Açgözlü Portföy Seçimi (<code>select_portfolio</code>, Eşik = 0.70)</h3>
    <table class='compact-table'>
      <thead>
        <tr>
          <th>Ay Hedefi</th>
          <th class='num'>Eğim / Pürüzlülük</th>
          <th>Seçilen Portföy</th>
          <th>Kapanmayan Eksen</th>
          <th>Denetim ve Fiziksel Limit Notu</th>
        </tr>
      </thead>
      <tbody>
        {''.join(port_rows_html)}
      </tbody>
    </table>
    <p><strong>Portföy sonucu:</strong> <code>Shackleton</code> ve <code>de Gerlache</code> için Dünya havuzundaki hiçbir saha tek başına <code>Hareket >= 0.70</code> eşiğine ulaşamaz (Shackleton azami Hareket <code>0.335</code>, Hasandağı). Sistem sahte yüksek skor üretmek yerine bu eksiği açıkça raporlar</p>
    """

    # Page 8: Dual Observatory Architecture & Consolidated References
    p8_body = """
    <h2>7. İki Tamamlayıcı Karar Arayüzü ve Doğrulanmış Yazılım Mimari Bütünlüğü</h2>
    <p>Tüm çıktı parquet dosyaları (<code>features_moon.parquet</code> ve <code>features_earth.parquet</code>) doğrudan iki ayrı arayüzü besler; her iki arayüz de aynı sabit sözleşme ve metriklerle çalışır</p>

    <div class='two-col'>
      <div class='card-plain'>
        <h3>Web Observatory (React 18 + Vite + Leaflet + WebGL)</h3>
        <ul>
          <li>İstemci taraflı TypeScript skor motoru (<code>web/src/scoring.ts</code>) ile anlık <strong>eksen ağırlık sürgüleri</strong> ve dinamik portföy eşiği simülasyonu</li>
          <li>Leaflet GIS uydu/topografya haritası, çok-eksenli D3 radar karşılaştırması, yükseklik kesit grafikleri ve <code>51×51</code> boyutunda etkileşimli Three.js 3B arazi ağı</li>
          <li><code>web/</code> arayüzünde yalnızca aktif veriyle desteklenen 3 görev ön ayarı ve serbest ağırlık modu sunulur; v1 buz verisi olmadığı için ISRU ön ayarı bilinçli olarak ayrıştırılmıştır</li>
        </ul>
      </div>
      <div class='card-plain'>
        <h3>Araştırma Workbench'i (Streamlit + PyDeck + Plotly)</h3>
        <ul>
          <li>Python backend üzerinden doğrudan <code>src/scoring/</code> modülünü çalıştıran 6 sekmeli teknik inceleme ortamı (<code>app/</code>)</li>
          <li>LRO LOLA <code>5 m/px</code> hillshade &amp; tehlike haritaları, <code>10 m/px</code> Sentinel-2 L2A görsel atlası, Kör Doğrulama matrisi ve <code>select_portfolio</code> analizi</li>
          <li><code>default</code>, <code>rover_mobility</code>, <code>radar_calibration</code> ve <code>isru_ice</code> ön ayarlarının tamamını kaynak kod referansı olarak taşır</li>
        </ul>
      </div>
    </div>

    <h3>Yinelemeli Yeniden Üretim ve Denetim Zinciri</h3>
    <div class='formula-box'>python scripts/validate_all.py --fail-on-mock   # -> 0 hata, 0 uyari, 0/45 MOCK<br>pytest -q                                     # -> 51 passed (skor, belirsizlik, portfoy, dogrulama, Earth/Moon boru hatlari)</div>

    <h2>Birincil Uydu Veri Setleri ve Temel Literatür Kaynakçası</h2>
    <ol class='ref-list'>
      <li><strong>NASA GSFC PGDA Product 78:</strong> Barker, M. K. vd. (2021). Improved LOLA elevation models for south pole landing sites. <em>Planet. Space Sci.</em> 203:105119 (5 m/px DEM, <code>slperr</code>, <code>toterr</code>)</li>
      <li><strong>Mazarico, E. vd. (2011).</strong> Illumination conditions of the lunar polar regions using LOLA topography. <em>Icarus</em> 211:1066–1081</li>
      <li><strong>Zuber, M. T. vd. (2012) &amp; Spudis, P. D. vd. (2008).</strong> Shackleton Crater topography, LOLA reflectance (<em>Nature</em> 486) &amp; south pole geology (<em>GRL</em> 35)</li>
      <li><strong>LOLA GDR LDAM 1064 nm:</strong> Lemelin, M. vd. (2016), <em>Icarus</em> 273:315–328; Lucey, P. G. vd. (2014), <em>JGR Planets</em> 119:1665–1679</li>
      <li><strong>Geniş Bant Kalibrasyon &amp; Diviner Referansları:</strong> Vasavada, A. R. vd. (2012), <em>JGR</em> 117; Hayne, P. O. vd. (2017), <em>JGR Planets</em> 122; Williams, J.-P. vd. (2019), <em>JGR Planets</em> 124 (<code>LRO-L-DLRE-5-PCP-V1.0</code>)</li>
      <li><strong>Copernicus DEM GLO-30 DGED:</strong> Airbus &amp; ESA Product Handbook <code>GEO.2018-1988-2</code> §4.2 (<code>LE90 &lt; 2.0 m</code> → <code>sigma_z_rel = 1.0 m</code>); fallback: <code>NASADEM_HGT_v001</code> (LP DAAC)</li>
      <li><strong>MODIS Albedo &amp; LST Ürünleri:</strong> <code>MCD43A3.061</code> (500 m BSA), <code>MCD43A4.061</code> + Liang, S. (2001, <em>RSE</em> 76 Eq. 9) &amp; Hall, D. K. vd. (2002) <code>NDSI &lt; 0.40</code>; <code>MOD11A2.061</code> (1 km, 2024 yıllık 24 kompozit)</li>
      <li><strong>Piksel Saflığı &amp; Görsel Atlas:</strong> ESA WorldCover 10 m <code>v200</code> &amp; Copernicus Sentinel-2 L2A (10/20 m <code>SCL</code>)</li>
      <li><strong>Doğrulama Sahaları (Seçme):</strong> Wedler vd. (2017) &amp; Schuster vd. (2020) Etna; Navarro-González vd. (2003) Atacama; Osinski vd. (2005) Haughton; Marchant &amp; Head (2007) McMurdo; Binsted vd. (2016) HI-SEAS; Kring (2007) Meteor Crater; Steele vd. (2011) Svalbard AMASE; Greeley vd. (1972) Lunar Crater NV; Sauro vd. (2020) Lanzarote; Hughes vd. (2019) Craters of the Moon</li>
      <li><strong>Türkiye ve Küresel Aday Kaynakları (Seçme):</strong> Lustrino vd. (2010, <em>Lithos</em> 117) &amp; Ekici vd. (2014) Karacadağ; Horgan vd. (2020, <em>Icarus</em> 339) Salda-Jezero; Keller (1974) &amp; Reid vd. (2017) Karapınar Meke; Deniel vd. (1998) Hasandağı; Şen vd. (2003) Erciyes; Yılmaz vd. (1998) Ağrı/Süphan/Tendürek; Ersoy vd. (2010) Kula; Lebedev vd. (2016) Tendürek; de Silva vd. (2010) Puna de Atacama; Self vd. (2006) Deccan; Salisbury vd. (2011) Chajnantor; MTA 1:500.000 Türkiye Jeoloji Haritaları</li>
    </ol>
    """

    pages = [
        page_wrap(1, "", p1_body),
        page_wrap(2, "1. Algoritmik Tasarım ve Referanslar", p2_body),
        page_wrap(3, "2. Belirsizlik, Kalibrasyon ve Portföy", p3_body),
        page_wrap(4, "3. Veri Bütünlüğü ve Ölçek Denetimi", p4_body),
        page_wrap(5, "4. Shackleton Sonuçları ve Görev Duyarlılığı", p5_body),
        page_wrap(6, "5. Beş Ay Bölgesi ve Türkiye Adayları", p6_body),
        page_wrap(7, "6. Doğrulama Tanısı, Portföy ve Fiziksel Sınırlar", p7_body),
        page_wrap(8, "7. Arayüz Mimarisi ve Birincil Kaynakça", p8_body),
    ]

    return (
        "<!DOCTYPE html>\n"
        "<!-- Typography & restraint conventions informed by unslop (Damir Sokolovsky, CC BY 4.0) -->\n"
        "<html lang='tr'>\n<head>\n<meta charset='utf-8'>\n"
        "<title>Ay Güney Kutbu Çok-Eksenli Yeryüzü Test Sahası Değerlendirmesi</title>\n"
        f"<style>{css}</style>\n</head>\n<body>\n{''.join(pages)}\n</body>\n</html>\n"
    )


def export_pdf_and_check() -> None:
    """Export HTML to A4 PDF via headless Chromium and assert zero page overflow."""
    from playwright.sync_api import sync_playwright

    with sync_playwright() as pw:
        browser = pw.chromium.launch()
        page = browser.new_page(viewport={"width": 1240, "height": 1754})
        page.goto(HTML_PATH.resolve().as_uri(), wait_until="networkidle")

        overflow_report = page.evaluate(
            """() => {
              const pages = [...document.querySelectorAll('.page')];
              return pages.map((el, i) => ({
                page: i + 1,
                scrollH: el.scrollHeight,
                clientH: el.clientHeight,
                overflowPx: Math.max(0, el.scrollHeight - el.clientHeight)
              }));
            }"""
        )
        print("DOM_OVERFLOW_CHECK:", json.dumps(overflow_report))
        for item in overflow_report:
            if item["overflowPx"] > 2:
                raise RuntimeError(f"Page {item['page']} overflows by {item['overflowPx']} px")

        page.pdf(
            path=str(PDF_PATH),
            format="A4",
            print_background=True,
            prefer_css_page_size=True,
            margin={"top": "0mm", "right": "0mm", "bottom": "0mm", "left": "0mm"},
        )
        browser.close()

    import fitz
    doc = fitz.open(str(PDF_PATH))
    print("PDF_PAGE_COUNT:", len(doc))
    if len(doc) != 8:
        raise RuntimeError(f"Expected 8 PDF pages, got {len(doc)}")
    scratch_dir = Path(r"C:\Users\ASUS\.gemini\antigravity\brain\a87bc1f2-c8f4-46ac-9084-98d1166941ca\scratch\new_pdf_pages")
    scratch_dir.mkdir(parents=True, exist_ok=True)
    for idx, p in enumerate(doc, start=1):
        pix = p.get_pixmap(dpi=150)
        pix.save(str(scratch_dir / f"page_{idx}.png"))
    doc.close()


def main() -> None:
    """Generate figures, build HTML report, render PDF, and rasterize verification PNGs."""
    FIG_DIR.mkdir(parents=True, exist_ok=True)
    setup_matplotlib()
    data = compute_all_metrics()
    make_fig1_orbital_plate(data)
    make_fig2_shackleton_axes(data)
    make_fig3_mission_slopegraph(data)
    make_fig4_multiregion_heatmap(data)
    make_fig5_physical_and_validation(data)
    make_fig6_robustness_and_audit(data)

    html = build_html(data)
    HTML_PATH.write_text(html, encoding="utf-8")
    export_pdf_and_check()
    print("BUILD_OK:", HTML_PATH, PDF_PATH)


if __name__ == "__main__":
    main()
