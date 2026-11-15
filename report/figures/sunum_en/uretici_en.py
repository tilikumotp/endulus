# English versions of the jury charts, generated ONLY from the verified web data JSON.
# Same generator logic as report/figures/sunum/uretici.py, English labels only.
import json
import pathlib

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

ROOT = pathlib.Path(r"T:\Endülüs")
DATA = json.loads((ROOT / "web/public/data/app_data.json").read_text(encoding="utf-8"))
OUT = ROOT / "report/figures/sunum_en"
OUT.mkdir(parents=True, exist_ok=True)

PAPER, INK, INK2, INK3 = "#faf9f6", "#22252a", "#565b64", "#8a8f98"
GRAY, ACCENT, HAIR = "#c3c7ce", "#2b5aa6", "#e4e2dd"
plt.rcParams.update({
    "font.family": "Segoe UI",
    "text.color": INK, "axes.edgecolor": INK3, "axes.labelcolor": INK2,
    "xtick.color": INK2, "ytick.color": INK,
    "figure.facecolor": PAPER, "axes.facecolor": PAPER, "savefig.facecolor": PAPER,
    "axes.grid": True, "grid.color": HAIR, "grid.linewidth": 0.8,
    "axes.spines.top": False, "axes.spines.right": False, "axes.spines.left": False,
    "font.size": 11.5,
})
MONO = {"family": "Consolas", "size": 8.0, "color": INK3}


def strip_tr(name: str) -> str:
    return name.replace(" (TR)", "")


def short_of(site_id: str) -> str:
    for s in DATA["earth_sites"]:
        if s["site_id"] == site_id:
            return strip_tr(s["short"])
    return site_id


def header(fig, title, sub):
    fig.text(0.02, 0.97, title, fontsize=15.5, fontweight=600, va="top", ha="left")
    fig.text(0.02, 0.905, sub, fontsize=10.5, color=INK2, va="top", ha="left")


def src(fig, text):
    fig.text(0.02, 0.012, text, **MONO, va="bottom", ha="left")


def find_id(fragment):
    for s in DATA["earth_sites"]:
        if fragment in s["site_id"]:
            return s["site_id"]
    return None


rows = DATA["comparisons"]["moon_shackleton_rim"]["default"]
top10 = sorted(rows, key=lambda r: r["rank"])[:10]

# -- A: Top 10 for Shackleton --------------------------------------------------------
fig, ax = plt.subplots(figsize=(9, 5.4), dpi=200)
fig.subplots_adjust(left=0.24, right=0.93, top=0.82, bottom=0.14)
labels = [short_of(r["site_id"]) for r in top10][::-1]
scores = [r["score"] for r in top10][::-1]
lo = [r["score"] - (r["ci_lo"] or r["score"]) for r in top10][::-1]
hi = [(r["ci_hi"] or r["score"]) - r["score"] for r in top10][::-1]
colors = [ACCENT if r["site_id"] == "earth_karapinar_meke" else GRAY for r in top10][::-1]
y = range(len(top10))
ax.barh(y, scores, height=0.62, color=colors, zorder=3)
ax.errorbar(scores, y, xerr=[lo, hi], fmt="none", ecolor=INK2, elinewidth=1.1, capsize=3, zorder=4)
for i, r in enumerate(top10[::-1]):
    ax.text((r["ci_hi"] or r["score"]) + 0.014, i, f"{r['score']:.3f}",
            va="center", fontsize=10.5, fontfamily="Consolas",
            color=ACCENT if r["site_id"] == "earth_karapinar_meke" else INK2)
ax.set_yticks(list(y), labels, fontsize=11)
ax.set_xlim(0, 0.78)
ax.set_xticks([0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7])
ax.grid(axis="x", zorder=0)
ax.grid(axis="y", visible=False)
header(fig, "Shackleton crater rim · top 10 Earth sites",
       "Balanced rover profile (50/50). Bar: mean score · line: Monte Carlo 90% interval (n=200 draws).")
src(fig, "Source: data/processed/features_*.parquet · LOLA PGDA 5 m/px · GLO-30 30 m/px · MCD43A3.061 500 m")
fig.savefig(OUT / "figA_top10_shackleton_en.png")
plt.close(fig)

# -- B: Why #1? axis split -----------------------------------------------------------
top6 = sorted(rows, key=lambda r: r["rank"])[:6]
fig, ax = plt.subplots(figsize=(9, 5.2), dpi=200)
fig.subplots_adjust(left=0.235, right=0.93, top=0.82, bottom=0.14)
labels = [short_of(r["site_id"]) for r in top6][::-1]
yy = range(len(top6))
h = 0.32
mob = [r["mob"] for r in top6][::-1]
surf = [r["surf"] for r in top6][::-1]
mob_rank = [r["mob_rank"] for r in top6][::-1]
surf_rank = [r["surf_rank"] for r in top6][::-1]
is_meke = [r["site_id"] == "earth_karapinar_meke" for r in top6][::-1]
ax.barh([i + h / 2 + 0.02 for i in yy], mob, height=h, color=[ACCENT if m else GRAY for m in is_meke], label="Mobility", zorder=3)
ax.barh([i - h / 2 - 0.02 for i in yy], surf, height=h, color=[ACCENT if m else "#9fa6b1" for m in is_meke], label="Surface (albedo)", zorder=3)
for i, (m, mr, s, sr) in enumerate(zip(mob, mob_rank, surf, surf_rank)):
    ax.text(m + 0.012, i + h / 2 + 0.02, f"{m:.2f}  (#{mr})", va="center", fontsize=9.5, fontfamily="Consolas", color=INK2)
    ax.text(s + 0.012, i - h / 2 - 0.02, f"{s:.2f}  (#{sr})", va="center", fontsize=9.5, fontfamily="Consolas", color=INK2)
ax.set_yticks(list(yy), labels, fontsize=11)
ax.set_xlim(0, 1.28)
ax.set_xticks([0, 0.25, 0.5, 0.75, 1.0])
ax.grid(axis="x", zorder=0)
ax.grid(axis="y", visible=False)
ax.legend(loc="upper right", bbox_to_anchor=(1.0, 1.04), ncols=2, frameon=False, fontsize=10.5)
header(fig, "Why #1? The two score components",
       "Meke (blue) is carried by the Surface axis; it ranks #11 on Mobility. The score is a ranking index, not a guarantee.")
src(fig, "Source: comparisons[moon_shackleton_rim][default] · axis scores S = exp(-D), z-score distance")
fig.savefig(OUT / "figB_axis_split_en.png")
plt.close(fig)

# -- C: Mission profile re-ranking ---------------------------------------------------
MISSIONS = [("default", "Balanced\n(50/50)"), ("rover_mobility", "Climbing\n(67/33)"), ("optical_survey", "Optical\n(33/67)")]
TRACK = ["earth_hasandagi_kecekalecik", "earth_karapinar_meke", "earth_etna_cisternazza"]
fig, ax = plt.subplots(figsize=(9, 5.4), dpi=200)
fig.subplots_adjust(left=0.09, right=0.82, top=0.82, bottom=0.16)
for sid in TRACK:
    ranks = []
    for mk, _ in MISSIONS:
        row = next(r for r in DATA["comparisons"]["moon_shackleton_rim"][mk] if r["site_id"] == sid)
        ranks.append(row["rank"])
    accent = sid == "earth_hasandagi_kecekalecik"
    ax.plot(range(3), ranks, color=ACCENT if accent else GRAY, linewidth=2.2 if accent else 1.6,
            marker="o", markersize=5.5, zorder=3)
    for j, rk in enumerate(ranks):
        ax.annotate(f"#{rk}", (j, rk), textcoords="offset points",
                    xytext=(0, 8 if sid != "earth_etna_cisternazza" else -14),
                    ha="center", fontsize=10, fontfamily="Consolas",
                    color=ACCENT if accent else INK2)
    ax.text(2.06, ranks[-1], short_of(sid), va="center", fontsize=10.5,
            color=ACCENT if accent else INK2)
ax.set_xticks(range(3), [m[1] for m in MISSIONS], fontsize=11)
ax.invert_yaxis()
ax.set_ylim(40, 0)
ax.set_yticks([1, 5, 10, 15, 20, 25, 30, 35, 40])
ax.set_ylabel("Overall rank (#1 best)", fontsize=10.5)
ax.grid(axis="y", zorder=0)
ax.grid(axis="x", visible=False)
header(fig, "Rankings change with the mission profile",
       "Same data, same sites; only the axis weights changed. Hasandagi climbs #3 -> #1 in the climbing profile.")
src(fig, "Source: comparisons[moon_shackleton_rim][default | rover_mobility | optical_survey]")
fig.savefig(OUT / "figC_mission_profiles_en.png")
plt.close(fig)

# -- D: Reference geometry sensitivity (Faustini flip) -------------------------------
FLIP = ["earth_svalbard", "earth_mauna_loa", "earth_haughton_crater", "earth_atacama_yungay"]
fig, ax = plt.subplots(figsize=(9, 4.9), dpi=200)
fig.subplots_adjust(left=0.185, right=0.9, top=0.8, bottom=0.15)
yy = []
for k, frag in enumerate(FLIP):
    sid = find_id(frag)
    if sid is None:
        continue
    sh = next(r for r in rows if r["site_id"] == sid)["mob_rank"]
    fa = next(r for r in DATA["comparisons"]["moon_faustini_rim"]["default"] if r["site_id"] == sid)["mob_rank"]
    yy.append((short_of(sid), sh, fa))
    ax.plot([sh, fa], [k, k], color=HAIR, linewidth=2.5, zorder=2)
    ax.scatter([sh], [k], s=52, color=GRAY, zorder=3)
    ax.scatter([fa], [k], s=62, color=ACCENT, zorder=4)
    ax.annotate(f"Shackleton #{sh}", (sh, k), textcoords="offset points", xytext=(0, -16),
                ha="center", fontsize=9.5, fontfamily="Consolas", color=INK2)
    ax.annotate(f"Faustini #{fa}", (fa, k), textcoords="offset points", xytext=(0, 10),
                ha="center", fontsize=9.5, fontfamily="Consolas", color=ACCENT)
ax.set_yticks(range(len(yy)), [t[0] for t in yy], fontsize=11)
ax.set_xlim(31, 0)
ax.set_xticks([1, 5, 10, 15, 20, 25, 30])
ax.grid(axis="x", zorder=0)
ax.grid(axis="y", visible=False)
ax.set_xlabel("Mobility rank (#1 best, leftward)", fontsize=10.5)
header(fig, "Reference-geometry sensitivity",
       "With the flat reference (Faustini) instead of the steep crater rim (Shackleton), known analogues rise in mobility.")
src(fig, "Source: comparisons[moon_shackleton_rim | moon_faustini_rim][default] · mob_rank")
fig.savefig(OUT / "figD_faustini_flip_en.png")
plt.close(fig)

# -- E: One physical space, all 40 sites ---------------------------------------------
earth = DATA["earth_sites"]
fig, ax = plt.subplots(figsize=(9, 5.6), dpi=200)
fig.subplots_adjust(left=0.09, right=0.95, top=0.8, bottom=0.16)
ax.scatter([s["slope_mean"] for s in earth], [s["albedo"] for s in earth],
           s=30, color=GRAY, alpha=0.85, zorder=3, label="Earth site (40)")
moon = DATA["moon_refs"]
ax.scatter([m["slope_mean"] for m in moon], [m["albedo"] for m in moon],
           s=95, color=ACCENT, marker="D", zorder=4, label="Moon reference region (5)")
ANNOT = [
    ("earth_karapinar_meke", (8, -14), "left"),
    ("earth_atacama_yungay", (7, 5), "left"),
    ("earth_haughton_crater", (7, 12), "left"),
    ("earth_etna_cisternazza", (-9, 4), "right"),
    ("earth_mcmurdo_wright_valley", (-4, 11), "center"),
]
for frag, off, halign in ANNOT:
    sid = find_id(frag)
    if sid is None:
        continue
    s = next(x for x in earth if x["site_id"] == sid)
    ax.annotate(short_of(sid), (s["slope_mean"], s["albedo"]),
                textcoords="offset points", xytext=off, fontsize=9.5, color=INK2, ha=halign)
ax.set_xlabel("Mean slope (degrees)", fontsize=10.5)
ax.set_ylabel("Albedo", fontsize=10.5)
ax.set_xlim(0, None)
ax.set_ylim(0, 0.75)
ax.legend(loc="upper right", frameon=False, fontsize=10.5)
header(fig, "40 sites in one physical space",
       "Moon reference regions (blue diamonds) cluster at dark albedo; most candidates are brighter and gentler.")
src(fig, "Source: features_earth.parquet · features_moon.parquet · r = 1000 m aggregation")
fig.savefig(OUT / "figE_physical_space_en.png")
plt.close(fig)

# -- F: Albedo sensitivity -----------------------------------------------------------
sens = [r for r in DATA["albedo_sensitivity"] if r["ref_site_id"] == "moon_shackleton_rim"]
sens.sort(key=lambda r: r["factor"])
fig, ax = plt.subplots(figsize=(9, 5.4), dpi=200)
fig.subplots_adjust(left=0.08, right=0.96, top=0.8, bottom=0.19)
facs = [r["factor"] for r in sens]
rhos = [r["spearman_rho_overall"] for r in sens]
center = 0.38
cols = [ACCENT if abs(f - center) < 1e-9 else GRAY for f in facs]
x = range(len(facs))
ax.bar(x, rhos, width=0.58, color=cols, zorder=3)
for i, (rho, r) in enumerate(zip(rhos, sens)):
    ax.text(i, rho + 0.025, f"{rho:.2f}", ha="center", fontsize=11, fontfamily="Consolas",
            color=ACCENT if abs(facs[i] - center) < 1e-9 else INK2)
    ax.text(i, -0.16, short_of(r["top1_site_id"]), ha="center", fontsize=9.5,
            color=ACCENT if abs(facs[i] - center) < 1e-9 else INK2)
ax.set_xticks(list(x), [f"x{f:.2f}" for f in facs], fontsize=11.5)
ax.set_ylim(0, 1.12)
ax.set_yticks([0, 0.25, 0.5, 0.75, 1.0])
ax.grid(axis="y", zorder=0)
ax.grid(axis="x", visible=False)
ax.set_ylabel("Spearman rho (overall rank)", fontsize=10.5)
header(fig, "Albedo-factor sensitivity",
       "Reference x0.38 (blue). A +/-10% factor change preserves the ranking across all 5 Moon regions (rho >= 0.87);\nthe leader changes at the extremes - we report that openly.")
src(fig, "Source: albedo_sensitivity · LOLA 1064 nm x0.38 broadband equivalent · below bars: the #1 site at that factor")
fig.savefig(OUT / "figF_albedo_sensitivity_en.png")
plt.close(fig)

print("OK:", [p.name for p in sorted(OUT.glob("*.png"))])
