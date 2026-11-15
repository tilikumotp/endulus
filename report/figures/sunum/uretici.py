# Jury-facing simple charts, generated ONLY from the verified web data JSON
# (the same precomputed tables the React site renders). No recomputation.
import json
import pathlib

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

ROOT = pathlib.Path(r"T:\Endülüs")
DATA = json.loads((ROOT / "web/public/data/app_data.json").read_text(encoding="utf-8"))
OUT = ROOT / "report/figures/sunum"
OUT.mkdir(parents=True, exist_ok=True)

# -- style: quiet chrome, one accent ------------------------------------------------
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


rows = DATA["comparisons"]["moon_shackleton_rim"]["default"]
rows_by_id = {r["site_id"]: r for r in rows}
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
ax.set_axisbelow(True)
header(fig, "Shackleton Krateri Kenarı · ilk 10 Dünya sahası",
       "Dengeli rover testi (50/50). Çubuk: ortalama puan · çizgi: Monte Carlo %90 aralığı (n=200).")
src(fig, "Kaynak: data/processed/features_*.parquet · LOLA PGDA 5 m/px · GLO-30 30 m/px · MCD43A3.061 500 m")
fig.savefig(OUT / "figA_top10_shackleton.png")
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
ax.barh([i + h / 2 + 0.02 for i in yy], mob, height=h, color=[ACCENT if m else GRAY for m in is_meke], label="Mobilite", zorder=3)
ax.barh([i - h / 2 - 0.02 for i in yy], surf, height=h, color=[ACCENT if m else "#9fa6b1" for m in is_meke], label="Yüzey (albedo)", zorder=3)
for i, (m, mr, s, sr) in enumerate(zip(mob, mob_rank, surf, surf_rank)):
    ax.text(m + 0.012, i + h / 2 + 0.02, f"{m:.2f}  (#{mr})", va="center", fontsize=9.5, fontfamily="Consolas", color=INK2)
    ax.text(s + 0.012, i - h / 2 - 0.02, f"{s:.2f}  (#{sr})", va="center", fontsize=9.5, fontfamily="Consolas", color=INK2)
ax.set_yticks(list(yy), labels, fontsize=11)
ax.set_xlim(0, 1.28)
ax.set_xticks([0, 0.25, 0.5, 0.75, 1.0])
ax.grid(axis="x", zorder=0)
ax.grid(axis="y", visible=False)
ax.legend(loc="upper right", bbox_to_anchor=(1.0, 1.04), ncols=2, frameon=False, fontsize=10.5)
header(fig, "Neden #1? Puanın iki bileşeni",
       "Karapınar Meke'yi (mavi) Yüzey ekseni taşıyor; mobilitede #11. Puan bir sıralama indeksidir, güvence değil.")
src(fig, "Kaynak: comparisons[moon_shackleton_rim][default] · eksen puanları S = exp(−D), z-skor uzaklığı")
fig.savefig(OUT / "figB_eksen_ayrimi.png")
plt.close(fig)

# -- C: Mission profile re-ranking ---------------------------------------------------
MISSIONS = [("default", "Dengeli\n(50/50)"), ("rover_mobility", "Tırmanma\n(67/33)"), ("optical_survey", "Optik\n(33/67)")]
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
ax.set_ylabel("Genel sıra (#1 en iyi)", fontsize=10.5)
ax.grid(axis="y", zorder=0)
ax.grid(axis="x", visible=False)
header(fig, "Görev profili değişince sıralama değişir",
       "Aynı veri, aynı sahalar; yalnızca eksen ağırlıkları değişti. Hasandağı tırmanma profilinde #3 → #1.")
src(fig, "Kaynak: comparisons[moon_shackleton_rim][default | rover_mobility | optical_survey]")
fig.savefig(OUT / "figC_gorev_profilleri.png")
plt.close(fig)

# -- D: Reference geometry sensitivity (Faustini flip) -------------------------------
FLIP = ["earth_svalbard", "earth_mauna_loa", "earth_haughton_crater", "earth_atacama_yungay"]


def find_id(fragment):
    for s in DATA["earth_sites"]:
        if fragment in s["site_id"]:
            return s["site_id"]
    return None


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
ax.set_xlabel("Mobilite sırası (#1 en iyi, sola doğru)", fontsize=10.5)
header(fig, "Referans geometrisine duyarlılık",
       "Dik krater kenarı (Shackleton) yerine yatık referans (Faustini) seçilince bilinen analoglar mobilitede yükselir.")
src(fig, "Kaynak: comparisons[moon_shackleton_rim | moon_faustini_rim][default] · mob_rank")
fig.savefig(OUT / "figD_faustini_degisimi.png")
plt.close(fig)

# -- E: One physical space, all 40 sites ---------------------------------------------
earth = DATA["earth_sites"]
fig, ax = plt.subplots(figsize=(9, 5.6), dpi=200)
fig.subplots_adjust(left=0.09, right=0.95, top=0.8, bottom=0.16)
ax.scatter([s["slope_mean"] for s in earth], [s["albedo"] for s in earth],
           s=30, color=GRAY, alpha=0.85, zorder=3, label="Dünya sahası (40)")
moon = DATA["moon_refs"]
ax.scatter([m["slope_mean"] for m in moon], [m["albedo"] for m in moon],
           s=95, color=ACCENT, marker="D", zorder=4, label="Ay referans bölgesi (5)")
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
ax.set_xlabel("Ortalama eğim (derece)", fontsize=10.5)
ax.set_ylabel("Albedo", fontsize=10.5)
ax.set_xlim(0, None)
ax.set_ylim(0, 0.75)
ax.legend(loc="upper right", frameon=False, fontsize=10.5)
header(fig, "40 saha, tek fiziksel uzayda",
       "Ay referans bölgeleri (mavi eşkenar dörtgen) karanlık albedoda toplanır; adayların çoğu daha parlak ve daha az eğimli.")
src(fig, "Kaynak: features_earth.parquet · features_moon.parquet · r = 1000 m toplulaştırma")
fig.savefig(OUT / "figE_fiziksel_uzay.png")
plt.close(fig)

print("OK:", [p.name for p in sorted(OUT.glob("*.png"))])
