# English copies of the deck charts.
# Generated ONLY from the verified web data JSON (same tables the React app renders). No recomputation.
import json
import pathlib

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

ROOT = pathlib.Path(__file__).resolve().parents[3]
DATA = json.loads((ROOT / "web/public/data/app_data.json").read_text(encoding="utf-8"))
OUT = pathlib.Path(__file__).resolve().parent

PAPER, INK, INK2, INK3 = "#ffffff", "#22252a", "#565b64", "#8a8f98"
GRAY, ACCENT, HAIR, ORANGE = "#c3c7ce", "#2b5aa6", "#e4e2dd", "#d9822b"
plt.rcParams.update({
    "font.family": "Segoe UI", "text.color": INK, "axes.edgecolor": INK3, "axes.labelcolor": INK2,
    "xtick.color": INK2, "ytick.color": INK, "figure.facecolor": PAPER, "axes.facecolor": PAPER,
    "savefig.facecolor": PAPER, "axes.grid": True, "grid.color": HAIR, "grid.linewidth": 0.8,
    "axes.spines.top": False, "axes.spines.right": False, "axes.spines.left": False, "font.size": 13,
})

EN_NAMES = {
    "earth_haughton_crater": "Haughton Crater",
    "earth_cappadocia_kavakkoy": "Cappadocia Kavakköy",
    "earth_tendurek_shield": "Tendürek Shield",
    "earth_tuz_golu_south": "Tuz Gölü South",
    "earth_salda_terrace": "Lake Salda terrace",
    "earth_chajnantor_plateau": "Chajnantor Plateau",
    "earth_kilauea_kau_desert": "Kīlauea Kaʻū Desert",
    "earth_suphan_south_apron": "Süphan south apron",
    "earth_nemrut_caldera_flank": "Nemrut Caldera",
    "earth_karacadag_summit": "Karacadağ Kollubaba",
}


def name(sid: str) -> str:
    if sid in EN_NAMES:
        return EN_NAMES[sid]
    for s in DATA["earth_sites"]:
        if s["site_id"] == sid:
            return s["short"].replace(" (TR)", "")
    return sid


def is_tr(sid: str) -> bool:
    return next((s["is_tr"] for s in DATA["earth_sites"] if s["site_id"] == sid), False)


def role(sid: str) -> str:
    return next((s["role"] for s in DATA["earth_sites"] if s["site_id"] == sid), "")


rows = DATA["comparisons"]["moon_shackleton_rim"]["default"]
top10 = sorted(rows, key=lambda r: r["rank"])[:10]

# A: top-10 for Shackleton Rim with axis split
fig, (ax, ax2) = plt.subplots(1, 2, figsize=(12, 5.6), dpi=200, gridspec_kw={"width_ratios": [1.25, 1]})
fig.subplots_adjust(left=0.19, right=0.98, top=0.93, bottom=0.2, wspace=0.08)
y = list(range(len(top10)))[::-1]
for yi, r in zip(y, top10):
    c = ACCENT if role(r["site_id"]) == "validation" else ORANGE
    ax.barh(yi, r["score"], height=0.62, color=c, zorder=3)
    lo, hi = r["ci_lo"] or r["score"], r["ci_hi"] or r["score"]
    ax.errorbar(r["score"], yi, xerr=[[r["score"] - lo], [hi - r["score"]]], fmt="none", ecolor=INK, elinewidth=1.1, capsize=3, zorder=4)
    ax.text(hi + 0.012, yi, f"#{r['rank']}  {r['score']:.3f}", va="center", fontsize=11.5, fontfamily="Consolas", color=INK)
ax.set_yticks(y, [name(r["site_id"]) + (" (TR)" if is_tr(r["site_id"]) else "") for r in top10], fontsize=12.5)
ax.set_xlim(0, 0.8)
ax.grid(axis="y", visible=False)
ax.set_xlabel("Overall similarity index exp(−D), 0–1  ·  bar = Monte Carlo 5–95 % (n=200)", fontsize=11)
ax.set_title("Overall rank (Balanced profile)", fontsize=14, fontweight=600, loc="left")
from matplotlib.patches import Patch
ax.legend(handles=[Patch(color=ORANGE, label="Candidate site"), Patch(color=ACCENT, label="Known validation analog")],
          loc="lower left", bbox_to_anchor=(0.0, -0.26), ncols=2, frameon=False, fontsize=11.5)
h = 0.34
for yi, r in zip(y, top10):
    ax2.barh(yi + h / 2, r["mob"], height=h, color="#8c6bd6", zorder=3)
    ax2.barh(yi - h / 2, r["surf"], height=h, color="#2fb584", zorder=3)
    ax2.text(r["mob"] + 0.01, yi + h / 2, f"{r['mob']:.2f} (#{r['mob_rank']})", va="center", fontsize=10, fontfamily="Consolas", color=INK2)
    ax2.text(r["surf"] + 0.01, yi - h / 2, f"{r['surf']:.2f} (#{r['surf_rank']})", va="center", fontsize=10, fontfamily="Consolas", color=INK2)
ax2.set_yticks(y, [""] * len(y))
ax2.set_xlim(0, 1.25)
ax2.set_xticks([0, 0.25, 0.5, 0.75, 1.0])
ax2.grid(axis="y", visible=False)
ax2.legend(handles=[Patch(color="#8c6bd6", label="Mobility (4 DEM metrics)"), Patch(color="#2fb584", label="Surface (albedo)")],
           loc="lower left", bbox_to_anchor=(0.0, -0.26), ncols=2, frameon=False, fontsize=11.5)
ax2.set_title("Axis split  (Thermal = NaN in v1)", fontsize=14, fontweight=600, loc="left")
ax2.set_xlabel("Axis score (rank among 40)", fontsize=11)
fig.savefig(OUT / "en_top10_shackleton.png")
plt.close(fig)

# C: mission re-ranking
MISSIONS = [("default", "Balanced\n(Mob 1 : Surf 1)"), ("rover_mobility", "Rover mobility\n(Mob 2 : Surf 1)"), ("optical_survey", "Optical / solar\n(Mob 1 : Surf 2)")]
TRACK = ["earth_hasandagi_kecekalecik", "earth_karapinar_meke", "earth_etna_cisternazza"]
COL = {"earth_hasandagi_kecekalecik": "#d6455d", "earth_karapinar_meke": ORANGE, "earth_etna_cisternazza": ACCENT}
fig, ax = plt.subplots(figsize=(8, 5.6), dpi=200)
fig.subplots_adjust(left=0.11, right=0.74, top=0.95, bottom=0.17)
for sid in TRACK:
    ranks = [next(r for r in DATA["comparisons"]["moon_shackleton_rim"][mk] if r["site_id"] == sid)["rank"] for mk, _ in MISSIONS]
    ax.plot(range(3), ranks, color=COL[sid], linewidth=2.6, marker="o", markersize=7, zorder=3,
            linestyle="--" if role(sid) == "validation" else "-")
    for j, rk in enumerate(ranks):
        ax.annotate(f"#{rk}", (j, rk), textcoords="offset points", xytext=(0, {"earth_karapinar_meke": 10, "earth_hasandagi_kecekalecik": -20}.get(sid, -20)),
                    ha="center", fontsize=12, fontfamily="Consolas", color=COL[sid])
    lbl = name(sid) + (" (TR)" if is_tr(sid) else " [validation]")
    ax.text(2.1, ranks[-1], lbl, va="center", fontsize=12, color=COL[sid])
ax.set_xticks(range(3), [m[1] for m in MISSIONS], fontsize=12)
ax.set_ylim(36, -1)
ax.set_yticks([1, 5, 10, 15, 20, 25, 30, 35])
ax.set_ylabel("Overall rank among 40 (#1 best)", fontsize=12)
ax.grid(axis="x", visible=False)
fig.savefig(OUT / "en_mission_reweighting.png")
plt.close(fig)

# D: reference geometry sensitivity
FLIP = ["earth_svalbard_bockfjorden", "earth_mauna_loa_hiseas", "earth_haughton_crater", "earth_atacama_yungay"]
fig, ax = plt.subplots(figsize=(8, 4.6), dpi=200)
fig.subplots_adjust(left=0.22, right=0.97, top=0.9, bottom=0.17)
for k, sid in enumerate(FLIP):
    sh = next(r for r in rows if r["site_id"] == sid)["mob_rank"]
    fa = next(r for r in DATA["comparisons"]["moon_faustini_rim"]["default"] if r["site_id"] == sid)["mob_rank"]
    ax.plot([sh, fa], [k, k], color=HAIR, linewidth=3, zorder=2)
    ax.scatter([sh], [k], s=70, color=GRAY, zorder=3)
    ax.scatter([fa], [k], s=80, color=ACCENT, zorder=4)
    ax.annotate(f"Shackleton #{sh}", (sh, k), textcoords="offset points", xytext=(0, -19), ha="center", fontsize=11, fontfamily="Consolas", color=INK2)
    ax.annotate(f"Faustini #{fa}", (fa, k), textcoords="offset points", xytext=(0, 11), ha="center", fontsize=11, fontfamily="Consolas", color=ACCENT)
ax.set_yticks(range(len(FLIP)), [name(s) for s in FLIP], fontsize=12.5)
ax.set_ylim(-0.7, len(FLIP) - 0.3)
ax.set_xlim(31, 0)
ax.set_xticks([1, 5, 10, 15, 20, 25, 30])
ax.grid(axis="y", visible=False)
ax.set_xlabel("Mobility rank among 40 (#1 best →)", fontsize=12)
ax.set_title("Known analogs: steep Shackleton Rim vs gentle Faustini Rim", fontsize=13.5, fontweight=600, loc="left")
fig.savefig(OUT / "en_reference_sensitivity.png")
plt.close(fig)

for sid in FLIP:
    print(sid, next(r for r in rows if r["site_id"] == sid)["mob_rank"],
          next(r for r in DATA["comparisons"]["moon_faustini_rim"]["default"] if r["site_id"] == sid)["mob_rank"])
print("etna shack mob_rank", next(r for r in rows if r["site_id"] == "earth_etna_cisternazza")["mob_rank"])
print("OK", sorted(p.name for p in OUT.glob("en_*.png")))
