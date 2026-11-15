# English re-generation of the five app gallery figures (fig01..fig05).
# Data: ONLY the verified web/public/data/app_data.json + served atlas imagery.
# Replaces the Turkish-labelled gallery PNGs in web/public/figures (same filenames).
import json
import pathlib
from textwrap import wrap

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from PIL import Image

ROOT = pathlib.Path(__file__).resolve().parents[1]
DATA = json.loads((ROOT / "web/public/data/app_data.json").read_text(encoding="utf-8"))
PUB = ROOT / "web/public"
OUT = PUB / "figures"

BG, PANEL = "#07080d", "#0e1118"
INK, INK2, INK3 = "#eef0f5", "#a3a9b8", "#7a8296"
ORANGE, BLUE, RED, GREEN, PURPLE, CYAN = "#e8a13c", "#58b6f0", "#f06a7e", "#2fbf8f", "#a48bf0", "#59e6e6"

plt.rcParams.update({
    "font.family": "DejaVu Sans",
    "text.color": INK, "axes.edgecolor": "#2a2f3a", "axes.labelcolor": INK2,
    "xtick.color": INK2, "ytick.color": INK2,
    "figure.facecolor": BG, "axes.facecolor": PANEL, "savefig.facecolor": BG,
    "axes.grid": True, "grid.color": "#1d222c", "grid.linewidth": 0.8,
    "axes.spines.top": False, "axes.spines.right": False,
    "font.size": 11,
})

C = DATA["comparisons"]["moon_shackleton_rim"]
REG = DATA["comparisons"]
SITES = DATA["earth_sites"]
MOON = DATA["moon_refs"]
BYID = {s["site_id"]: s for s in SITES}
MOONBYID = {m["site_id"]: m for m in MOON}

COL_EN = {
    "moon_shackleton_rim": "Shackleton\nCrater Rim",
    "moon_connecting_ridge": "Connecting Ridge\n(Shack.-de Gerl.)",
    "moon_de_gerlache_rim": "de Gerlache\nCrater Rim",
    "moon_shackleton_peak": "Shackleton\nPeak (nearby)",
    "moon_faustini_rim": "Faustini\nCrater Rim",
}
PROF_EN = {"default": "Balanced\n(Mob 1 : Surf 1)",
           "rover_mobility": "Rover Mobility\n(Mob 2 : Surf 1)",
           "optical_survey": "Optical / Surface\n(Mob 1 : Surf 2)"}


def src(fig, text):
    fig.text(0.012, 0.012, text, fontsize=8, color=INK3, va="bottom", ha="left")


# ------------------------------------------------------------------ fig01
rows = sorted(C["default"], key=lambda r: r["rank"])[:15]
fig, (a, b) = plt.subplots(1, 2, figsize=(13.6, 6.6), dpi=150)
fig.suptitle("Shackleton Crater Rim — Top 15 Earth Sites and Axis Breakdown",
             fontsize=16, fontweight="bold", y=0.97)
fig.subplots_adjust(left=0.19, right=0.985, top=0.87, bottom=0.26, wspace=0.42)
y = np.arange(len(rows))[::-1]
labels, scores, lo, hi, mob, surf, cols = [], [], [], [], [], [], []
for r in rows:
    s = BYID[r["site_id"]]
    labels.append(s["short"])
    scores.append(r["score"]); lo.append(r["score"] - r["ci_lo"]); hi.append(r["ci_hi"] - r["score"])
    mob.append(r["mob"]); surf.append(r["surf"])
    cols.append(ORANGE if s["role"] == "candidate" else BLUE)
a.barh(y, scores, height=0.62, color=cols, zorder=3)
a.errorbar(scores, y, xerr=[lo, hi], fmt="none", ecolor=INK, elinewidth=1.0, capsize=3, zorder=4)
for yi, r in zip(y, rows):
    a.text(r["ci_hi"] + 0.012, yi, f"#{r['rank']}  {r['score']:.3f}",
           va="center", fontsize=10, color=INK, fontweight="bold")
a.set_yticks(y, labels, fontsize=9.5)
a.set_xlim(0, 0.78); a.grid(axis="x", zorder=0); a.grid(axis="y", visible=False)
a.set_xlabel("Overall Similarity Index [0-1] + P5-P95 Monte Carlo", fontsize=10)
a.set_title("A. Overall ranking (Balanced) & uncertainty", fontsize=12, pad=8)
h1 = a.bar([], [], color=ORANGE, label="Candidate test site")
h2 = a.bar([], [], color=BLUE, label="Documented validation analogue")
a.legend(handles=[h1, h2], loc="upper center", bbox_to_anchor=(0.5, -0.115), ncols=2, frameon=False, fontsize=9.5)
xb = np.arange(len(rows))
b.bar(xb - 0.2, mob, width=0.38, color=PURPLE, label="Mobility (4 DEM metrics)", zorder=3)
b.bar(xb + 0.2, surf, width=0.38, color=GREEN, label="Surface (albedo)", zorder=3)
for xi, r in zip(xb, rows):
    b.text(xi - 0.2, r["mob"] + 0.015, f"{r['mob']:.2f}", ha="center", fontsize=7.5, color=INK2)
    b.text(xi + 0.2, r["surf"] + 0.015, f"{r['surf']:.2f}", ha="center", fontsize=7.5, color=INK2)
b.set_xticks(xb, labels, rotation=60, ha="right", fontsize=8)
b.set_ylim(0, 1.05); b.grid(axis="y", zorder=0); b.grid(axis="x", visible=False)
b.legend(loc="upper right", frameon=False, fontsize=9)
b.set_title("B. Axis separation: Mobility vs Surface", fontsize=12, pad=8)
b.legend(loc="upper right", frameon=False, fontsize=9)
src(fig, "Source: NASA GSFC LRO LOLA PGDA (5 m/px) & LOLA 1064 nm albedo (1,000 m, x0.38) vs Copernicus GLO-30 / NASADEM (30 m/px) & MODIS MCD43A3 (500 m) | exp(-D), 200 MC draws | active axis scores only; thermal axis suspended in v1 (NaN)")
fig.savefig(OUT / "fig01_shackleton_top15_axes.png"); plt.close(fig)

# ------------------------------------------------------------------ fig02
TRACK = ["earth_karapinar_meke", "earth_hasandagi_kecekalecik", "earth_agri_dogubayazit_flow",
         "earth_erciyes_kojugedigi", "earth_kula_divlit", "earth_lunar_crater_nevada",
         "earth_deccan_mahabaleshwar", "earth_karacadag_summit", "earth_etna_cisternazza",
         "earth_mcmurdo_wright_valley"]
fig, ax = plt.subplots(figsize=(13.6, 7.4), dpi=150)
fig.subplots_adjust(left=0.205, right=0.795, top=0.88, bottom=0.11)
for sid in TRACK:
    s = BYID[sid]
    ranks = [next(r for r in C[p] if r["site_id"] == sid)["rank"] for p in ("default", "rover_mobility", "optical_survey")]
    solid = s["role"] == "candidate"
    hot = sid in ("earth_karapinar_meke", "earth_hasandagi_kecekalecik")
    col = RED if sid == "earth_hasandagi_kecekalecik" else (ORANGE if hot else (CYAN if not solid else "#5fd3a3"))
    ls = "-" if solid else "--"
    lw = 2.6 if hot else 1.6
    ax.plot(range(3), ranks, color=col, linestyle=ls, linewidth=lw, marker="o", markersize=5, zorder=3)
    ax.annotate(f"{s['short']} (#{ranks[0]}, {next(r for r in C['default'] if r['site_id']==sid)['score']:.3f})",
                (0, ranks[0]), textcoords="offset points", xytext=(-8, 0), ha="right",
                fontsize=8.8, color=col, fontweight="bold" if hot else "normal")
    if sid in ("earth_karapinar_meke", "earth_hasandagi_kecekalecik", "earth_mcmurdo_wright_valley", "earth_etna_cisternazza"):
        ax.annotate(f"#{ranks[1]} ({next(r for r in C['rover_mobility'] if r['site_id']==sid)['score']:.3f})",
                    (1, ranks[1]), textcoords="offset points", xytext=(0, 10), ha="center", fontsize=8.2,
                    color=INK, fontweight="bold")
    ax.annotate(f"#{ranks[2]} ({next(r for r in C['optical_survey'] if r['site_id']==sid)['score']:.3f}) {s['short']}",
                (2, ranks[2]), textcoords="offset points", xytext=(8, 0), ha="left",
                fontsize=8.8, color=col, fontweight="bold" if hot else "normal")
ax.set_xticks(range(3), [PROF_EN[p] for p in ("default", "rover_mobility", "optical_survey")], fontsize=11)
ax.invert_yaxis()
ax.set_ylim(34, 0)
ax.set_yticks([1, 5, 10, 15, 20, 25, 30, 35, 40])
ax.set_ylabel("Overall rank (#1 best)", fontsize=10.5)
ax.grid(axis="y", zorder=0); ax.grid(axis="x", visible=False)
ax.set_title("Shackleton Crater Rim — How the ranking shifts when the mission profile changes\n"
             "(solid line: candidate site · dashed line: documented validation analogue)",
             fontsize=14.5, fontweight="bold")
src(fig, "Under Rover Mobility, Hasandagi climbs #3 -> #1; Etna rises to #17 overall (mobility #3 / 40). Under Optical, weights match the Surface-axis emphasis.")
fig.savefig(OUT / "fig02_mission_reweighting.png"); plt.close(fig)

# ------------------------------------------------------------------ fig03
cand_top8 = sorted((r for r in C["default"] if BYID[r["site_id"]]["role"] == "candidate"),
                   key=lambda r: -r["score"])[:8]
val = sorted((r for r in C["default"] if BYID[r["site_id"]]["role"] == "validation"),
             key=lambda r: -r["score"])
sel = cand_top8 + val
regions = list(COL_EN)
A = np.array([[next(r for r in REG[reg]["default"] if r["site_id"] == s["site_id"])["score"] for reg in regions] for s in sel])
B = np.array([[next(r for r in REG[reg]["default"] if r["site_id"] == s["site_id"])["mob"] for reg in regions] for s in sel])
fig, (a, b) = plt.subplots(1, 2, figsize=(15.5, 9.2), dpi=150)
fig.suptitle("18 Earth Sites vs the 5 Lunar South Pole Regions (8 top Turkish candidates + 10 documented analogues)",
             fontsize=15, fontweight="bold", y=0.97)
fig.subplots_adjust(left=0.185, right=0.945, top=0.87, bottom=0.13, wspace=0.34)
rowlbl = [BYID[s["site_id"]]["short"].replace("Haughton Krateri", "Haughton Crater") for s in sel]
for axx, M, t, cm in ((a, A, "A. Overall Similarity Index (Balanced)", "Blues"),
                      (b, B, "B. Mobility axis only (4 DEM metrics)", "inferno")):
    im = axx.imshow(M, cmap=cm, vmin=0.02, vmax=0.9, aspect="auto")
    for i in range(M.shape[0]):
        for j in range(M.shape[1]):
            v = M[i, j]
            axx.text(j, i, f"{v:.2f}", ha="center", va="center", fontsize=8.5,
                     color="white" if (0.35 < v < 0.75 or cm == "inferno") else "black",
                     fontweight="bold")
    axx.set_xticks(range(5), [COL_EN[r] for r in regions], rotation=30, ha="right", fontsize=9)
    axx.set_yticks(range(len(sel)), rowlbl, fontsize=9)
    for lbl in axx.get_yticklabels():
        if "[Val]" in lbl.get_text():
            lbl.set_color(BLUE)
        elif "(TR)" in lbl.get_text():
            lbl.set_color(ORANGE)
    axx.set_title(t, fontsize=12, pad=8)
    axx.grid(visible=False)
    axx.axhline(7.5, color=INK, linestyle="--", linewidth=1.2, alpha=0.6)
a.texts[-1].set_color(INK2)
fig.text(0.012, 0.985, "", fontsize=1)
src(fig, "Steep Shackleton (18.5 deg) vs flat Faustini (5.2 deg): Etna leads on the steep wall (Mob #3), Atacama/Haughton/Svalbard lead on the flat rim; Karacadag is a test candidate.")
fig.savefig(OUT / "fig03_moon_regions_heatmap.png"); plt.close(fig)

# ------------------------------------------------------------------ fig04
fig, (a, b) = plt.subplots(1, 2, figsize=(14.6, 7.2), dpi=150)
fig.suptitle("Descriptive Rank Diagnostic — Why Documented Analogues Diverge with the Reference",
             fontsize=15, fontweight="bold", y=0.97)
fig.subplots_adjust(left=0.075, right=0.97, top=0.86, bottom=0.12, wspace=0.28)
ec = [(s["slope_mean"], s["albedo"], s["roughness"], s["role"], s["short"]) for s in SITES]
xa = [e[0] for e in ec if e[3] == "candidate"]; ya = [e[1] for e in ec if e[3] == "candidate"]
sa = [12 + 55 * np.sqrt(max(e[2], 0)) for e in ec if e[3] == "candidate"]
xb_ = [e[0] for e in ec if e[3] == "validation"]; yb = [e[1] for e in ec if e[3] == "validation"]
sb = [16 + 70 * np.sqrt(max(e[2], 0)) for e in ec if e[3] == "validation"]
a.scatter(xa, ya, s=sa, color=ORANGE, alpha=0.75, zorder=3, label="Candidate Earth site (n=30)")
a.scatter(xb_, yb, s=sb, color=BLUE, alpha=0.85, zorder=4, label="Validation analogue (n=10)")
xm = [m["slope_mean"] for m in MOON]; ym = [m["albedo"] for m in MOON]
a.scatter(xm, ym, s=340, color=RED, marker="*", edgecolor="white", linewidth=0.7,
          zorder=5, label="Moon south-pole region (n=5)")
a.axhspan(0.136, 0.147, color=RED, alpha=0.10, zorder=1)
a.text(0.4, 0.1525, "Moon south-pole albedo band (0.136-0.147)", fontsize=8, color=RED)
for frag, off in (("earth_haughton_crater", (10, 6)), ("earth_atacama_yungay", (10, 4)),
                  ("earth_hasandagi_kecekalecik", (8, 8)), ("earth_karapinar_meke", (8, -10)),
                  ("earth_mcmurdo_wright_valley", (-6, 12)), ("earth_etna_cisternazza", (8, -10)),
                  ("earth_mauna_loa_hiseas", (8, -8)), ("earth_karacadag_summit", (-4, -14))):
    s = next(x for x in SITES if x["site_id"] == frag)
    a.annotate(f"{s['short'].replace('Haughton Krateri', 'Haughton Crater')} ({s['slope_mean']:.1f}, {s['albedo']:.3f})",
               (s["slope_mean"], s["albedo"]), textcoords="offset points", xytext=off, fontsize=8.4, color=INK2)
for m in MOON:
    if m["site_id"] in ("moon_shackleton_rim", "moon_faustini_rim"):
        a.annotate(f"{m['name_en']} ({m['slope_mean']:.1f}, {m['albedo']:.3f})",
                   (m["slope_mean"], m["albedo"]), textcoords="offset points", xytext=(10, 6),
                   fontsize=8.6, color=RED, fontweight="bold")
a.set_xlabel("Mean slope (deg)", fontsize=10.5)
a.set_ylabel("Broadband albedo [0-1]", fontsize=10.5)
a.set_xlim(0, 24.5); a.set_ylim(0, 0.29)
a.legend(loc="upper right", framealpha=0.25, facecolor=PANEL, fontsize=8.6)
a.set_title("A. Physical feature space (size = roughness)", fontsize=12, pad=8)

vals = sorted((x for x in SITES if x["role"] == "validation"), key=lambda x: x["short"])
names, rsh, rfa = [], [], []
for s in vals:
    rsh.append(next(r for r in REG["moon_shackleton_rim"]["default"] if r["site_id"] == s["site_id"])["mob_rank"])
    rfa.append(next(r for r in REG["moon_faustini_rim"]["default"] if r["site_id"] == s["site_id"])["mob_rank"])
    names.append(s["short"].replace(" [Val]", "").replace("Haughton Krateri", "Haughton Crater"))
for n, r1, r2 in zip(names, rsh, rfa):
    colr = GREEN if r2 < r1 else RED
    b.plot([0, 1], [r1, r2], color=colr, linewidth=1.6, marker="o", markersize=4.5, zorder=3)
    b.annotate(f"{n} (#{r1})", (0, r1), xytext=(-8, 0), textcoords="offset points",
               ha="right", va="center", fontsize=8.4, color=INK2)
    b.annotate(f"#{r2} {n}", (1, r2), xytext=(8, 0), textcoords="offset points",
               ha="left", va="center", fontsize=8.4, color=colr, fontweight="bold")
b.set_xlim(-0.72, 1.85)
b.set_xticks([0, 1], ["Shackleton Rim\n(18.50 deg, steep wall)", "Faustini Rim\n(5.20 deg, flat ridge)"], fontsize=10.5)
b.invert_yaxis(); b.set_ylim(42, 0)
b.set_yticks([1, 5, 10, 15, 20, 25, 30, 35, 40])
b.set_ylabel("Mobility rank within the same 40 sites (#1 best)", fontsize=10)
b.grid(axis="y", zorder=0); b.grid(axis="x", visible=False)
b.set_title("B. Slope-regime effect across validation sites", fontsize=12, pad=8)
src(fig, "Same 40-site pool, same features, only the reference geometry changes: rank order is a property of the reference, which we report openly rather than claim as validation.")
fig.savefig(OUT / "fig04_physical_space_validation.png"); plt.close(fig)

# ------------------------------------------------------------------ fig05
sh = MOONBYID["moon_shackleton_rim"]
meke = BYID["earth_karapinar_meke"]
hasa = BYID["earth_hasandagi_kecekalecik"]
etna = BYID["earth_etna_cisternazza"]
krcd = BYID["earth_karacadag_summit"]
fa_row = next(r for r in REG["moon_faustini_rim"]["default"] if r["site_id"] == "earth_karacadag_summit")
sh_row = next(r for r in REG["moon_shackleton_rim"]["default"] if r["site_id"] == "earth_karapinar_meke")
rm_hasa = next(r for r in C["rover_mobility"] if r["site_id"] == "earth_hasandagi_kecekalecik")
rm_etna = next(r for r in C["rover_mobility"] if r["site_id"] == "earth_etna_cisternazza")

# Moon panels recomputed in English from the verified 3-D grid
# (embedded LOLA/hazard PNGs carry Turkish text, so we rebuild them from data/processed/moon_3d).
from matplotlib.colors import ListedColormap

z3d = np.load(ROOT / "data/processed/moon_3d/moon_shackleton_rim_3d.npz")
elev = z3d["elev_m"].astype(np.float64)
dxg = float(z3d["dx_m"])
dyg = -abs(float(z3d["dy_m"]))  # y decreases with row index (row 0 = north)
XG, YG = np.meshgrid(z3d["xs_rel_m"], z3d["ys_rel_m"])
incirc = np.hypot(XG, YG) <= float(z3d["radius_m"])
gyg, gxg = np.gradient(elev, dyg, dxg)
slope_grid = np.degrees(np.arctan(np.hypot(gxg, gyg)))
extent = [float(z3d["xs_rel_m"].min()), float(z3d["xs_rel_m"].max()),
          float(z3d["ys_rel_m"].min()), float(z3d["ys_rel_m"].max())]
azg, altg = np.radians(315.0), np.radians(45.0)
slope_r = np.arctan(np.hypot(gxg, gyg))
down_bearing = np.arctan2(-gxg, -gyg)  # compass bearing of the downhill direction
shade = np.clip(np.cos(altg) * np.cos(slope_r)
                + np.sin(altg) * np.sin(slope_r) * np.cos(azg - down_bearing), 0, 1)
cls = np.select([slope_grid < 10, slope_grid < 20], [0, 1], default=2)
CLS_CMAP = ListedColormap([GREEN, ORANGE, RED])


def npz_panel(spec, grid, cmap, title, caption, vmin=None, vmax=None):
    ax = fig.add_subplot(spec)
    ax.imshow(np.where(incirc, grid, np.nan), cmap=cmap, extent=extent,
              vmin=vmin, vmax=vmax, interpolation="nearest")
    ax.add_patch(plt.Circle((0, 0), 1000, fill=False, ls="--", lw=1.4, color=CYAN, zorder=5))
    yb = extent[2] + 0.055 * (extent[3] - extent[2])
    ax.plot([extent[0] + 120, extent[0] + 620], [yb, yb], color="white", lw=2.5, zorder=6)
    ax.text(extent[0] + 370, yb + 55, "500 m", color="white", fontsize=8.5,
            ha="center", va="bottom", zorder=6)
    ax.set_xticks([]); ax.set_yticks([])
    ax.set_xlim(extent[0], extent[1]); ax.set_ylim(extent[2], extent[3])
    ax.set_title("\n".join(wrap(title, 46)), fontsize=10.5, fontweight="bold", pad=6)
    ax.text(0.5, -0.045, "\n".join(wrap(caption, 52)), transform=ax.transAxes,
            ha="center", va="top", fontsize=8.8, color=INK2)
    ax.grid(visible=False)
    for sp in ax.spines.values():
        sp.set_color("#2a2f3a")
    return ax

fig = plt.figure(figsize=(14.2, 9.6), dpi=150)
fig.suptitle("Verified Orbital Evidence Gallery (offline atlas — imagery is NOT included in any numerical score)",
             fontsize=14.5, fontweight="bold", y=0.985)
gs = fig.add_gridspec(2, 6, left=0.035, right=0.975, top=0.855, bottom=0.055,
                      hspace=0.42, wspace=1.6)


def image_panel(spec, img_path, title, caption, span=1):
    ax = fig.add_subplot(spec)
    if span != 1:
        pass
    img = Image.open(PUB / img_path.lstrip("/"))
    ax.imshow(np.asarray(img.convert("RGB")))
    ax.set_xticks([]); ax.set_yticks([])
    ax.set_title("\n".join(wrap(title, 46)), fontsize=10.5, fontweight="bold", pad=6)
    ax.text(0.5, -0.045, "\n".join(wrap(caption, 52)), transform=ax.transAxes,
            ha="center", va="top", fontsize=8.8, color=INK2)
    ax.grid(visible=False)
    for sp in ax.spines.values():
        sp.set_color("#2a2f3a")


npz_panel(gs[0, 0:2], shade, "gray",
          "Shackleton Crater Rim — LRO LOLA relief\n(5 m/px PGDA · r = 1,000 m)",
          f"Mean slope {sh['slope_mean']:.2f} deg | p90 {sh['slope_p90']:.2f} deg | "
          f"relief {sh['relief']:.0f} m | albedo {sh['albedo']:.3f}")
npz_panel(gs[0, 2:4], cls, CLS_CMAP,
          f"Shackleton Crater Rim — slope classes\n(<10 deg {sh['pct_lt10deg']:.1f}% | "
          f"10-20 deg {sh['pct_10_20deg']:.1f}% | >20 deg {sh['pct_gt20deg']:.1f}%)",
          "Illustrative slope bins — not a landing-safety assessment")
ax_cls = fig.axes[-1]
ax_cls.legend(handles=[plt.Rectangle((0, 0), 1, 1, color=c, label=l) for c, l in
                       ((GREEN, "<10 deg (flat)"), (ORANGE, "10-20 deg"), (RED, ">20 deg (steep)"))],
              loc="lower right", framealpha=0.55, facecolor=PANEL, fontsize=7.8, borderpad=0.5)
image_panel(gs[0, 4:6], meke["atlas_img"],
            "Karapınar Meke Crater (Candidate #1 overall)\n(Sentinel-2 L2A 10 m/px)",
            f"Date: {meke['s2_date'][:10]} | Cloud: {meke['s2_cloud_pct']:.1f}% | Score: {sh_row['score']:.3f}")
image_panel(gs[1, 0:2], hasa["atlas_img"],
            "Hasandağı Keçikalecik (Mobility #1)\n(Sentinel-2 L2A 10 m/px)",
            f"Date: {hasa['s2_date'][:10]} | Cloud: {hasa['s2_cloud_pct']:.1f}% | Mobility score: {rm_hasa['mob']:.3f}")
image_panel(gs[1, 2:4], etna["atlas_img"],
            "Mount Etna Cisternazza (Validation, Mob #3)\n(Sentinel-2 L2A 10 m/px)",
            f"Date: {etna['s2_date'][:10]} | Cloud: {etna['s2_cloud_pct']:.1f}% | Mobility score: {rm_etna['mob']:.3f}")
image_panel(gs[1, 4:6], krcd["atlas_img"],
            "Karacadağ Kollubaba (Candidate test site)\n(Sentinel-2 L2A 10 m/px)",
            f"Date: {krcd['s2_date'][:10]} | Cloud: {krcd['s2_cloud_pct']:.1f}% | Faustini Mob #{fa_row['mob_rank']} ({fa_row['mob']:.3f})")
fig.savefig(OUT / "fig05_orbital_evidence_gallery.png"); plt.close(fig)

print("OK: fig01..fig05 regenerated in English")
