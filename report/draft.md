# DRAFT report — Moon/Mars ↔ Earth analog scoring (Person 4)

**STATUS: DRAFT — all numbers currently come from `data/mock/` (see
disclaimer below). Final numbers are produced from real parquets in
`data/processed/` before submission; this text is updated after each
real-data drop.**

## 1. Method (one paragraph)
No place on Earth analogs the Moon south pole (Shackleton rim area)
in every respect, so we score Earth sites **per axis** — mobility
(slope, roughness, relief), thermal (temp amplitude, thermal inertia),
surface (albedo) — using the leader's standardized-distance kernel
similarity `exp(-distance)` [0–1] with bootstrap 5–95% CIs attached to
every score (leader's `src/scoring/similarity.py`; the app writes no
scoring math of its own). Scores are combined with mission-weighted
presets, known analogues are recovered blind (role labels never enter
the scorer), and a greedy set cover recommends the minimal portfolio
of Earth test sites. Qualitative factors (lithology class, ice/PSR,
lava tubes, electrostatic dust) are displayed but never enter the
numeric score (AGENTS.md §2, §5).

## 2. Where the analogy breaks down
- Gravity: Moon ~1/6 g, Mars ~3/8 g — regolith mechanics, dust settling.
- Vacuum / thin atmosphere; radiation; 29.5-day lunar day.
- Regolith composition and mineralogy.
- Qualitative v1 factors: water ice / PSR, lava tubes / subsurface
  caves, electrostatic dust — tracked in the app, not scored.
- Resolution honesty: thermal products (~1 km, MODIS-class) cannot
  resolve a 500 m site; DEM features are 30 m. `*_src` / `*_res_m`
  columns are shown per feature in the app's Analogy Limits tab.

## 3. Validation (§8.4)
Blind check: sites with role `validation` (known analogues) must rank
near the top per axis (rank ≤ 5 of all scored sites). App tab shows
per-axis ranks + recovery metric. **Mock note:** with mock data the
recovery is random; real `features_earth.parquet` (pending, PR #2)
makes this meaningful.

## 4. Portfolio (§8.5)
Greedy set cover over per-axis scores at a coverage threshold (default
0.70): smallest set of Earth sites covering the most axes; axes no
site covers are listed as "validate in lab/simulation".

## 5. Data sources (filled from `*_src` when real data lands)
| Feature | Dataset (planned/actual) | Native res |
|---|---|---|
| slope_mean/p90, roughness, relief | Copernicus DEM GLO-30 (Earth, PR #2) | 30 m |
| temp_amplitude | MODIS MOD11A2.061, annual diurnal cycle | ~1 km |
| albedo | MCD43A3.061 (pending EARTHDATA_TOKEN step) | ~1 km |
| thermal_inertia | No global product → NaN, no invented numbers | — |

## 6. App deliverable
`app/main.py` (Streamlit + pydeck + plotly): reference-site selector,
per-axis scores with CI, mission presets, blind validation tab,
portfolio tab, analogy-limits card with inspect-site picker, and an
AGENTS.md rule-10 MOCK banner that names exactly which parts of the
current view are synthetic.

## 7. Disclaimer (must remain in the final deck/report until 100% real)
Results shown with the MOCK banner are development data
(`scripts/make_mock.py`), not scientific findings.
