# Written Report — Moon South Pole ↔ Earth Multi-Axis Analog Scoring

**All reference features (`data/processed/features_moon.parquet`) and Earth validation/candidate features (`data/processed/features_earth.parquet`) are computed from verified orbital datasets (`0 MOCK`, verified via `scripts/validate_all.py --fail-on-mock`).**

## 1. Method (one paragraph)
No place on Earth analogs the Moon south pole (Shackleton rim area)
in every respect, so we score Earth sites **per axis** — mobility
(slope, roughness, relief), thermal (temp amplitude, thermal inertia),
surface (albedo) — using the leader's standardized-distance kernel
similarity `exp(-distance)` [0–1] with bootstrap 5–95% CIs attached to
every score (leader's `src/scoring/similarity.py`; the app writes no
scoring math of its own). Scores are combined with mission-weighted
presets, known analogues are recovered blind (role labels never enter
the scorer), and a greedy set-cover heuristic recommends a compact
multi-site test portfolio of Earth sites. Within-axis z-score
differences are capped at ±3σ (`Z_CAP = 3.0`, outlier clipping) so a
single anomalous feature cannot dominate a comparison. Qualitative
factors (lithology class, ice/PSR, lava tubes, electrostatic dust) are
displayed but never enter the numeric score (AGENTS.md §2, §5).

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
near the top per axis (rank ≤ 5 of all scored sites). Role labels never
enter the scorer; on verified LRO and Earth orbital observations, known
volcanic and polar analogues (`McMurdo Dry Valleys`, `Lunar Crater Volcanic Field`,
`Askja / Holuhraun`, `Craters of the Moon`, `Mauna Loa HI-SEAS`, `Mount Etna`)
rank in the Top-5 on their corresponding `mobility` and `surface` axes.

## 4. Portfolio (§8.5)
Compact multi-site test portfolio via greedy set-cover heuristic
(leader's `select_portfolio`) over per-axis scores at a coverage
threshold (default 0.70): a small set of Earth sites covering the most
axes. Greedy is a fast, transparent heuristic — it does not guarantee
the mathematically minimal set in every case; axes no site covers
(notably extreme lunar South Pole `thermal` swings of 114–151 K) are
explicitly flagged as "validate in lab/simulation".

## 5. Data sources (verified orbital products in `*_src`)
| Body | Feature(s) | Dataset (`*_src`) | Native res (`*_res_m`) |
|---|---|---|---|
| **Moon** | `slope_mean/p90, roughness, relief` | `LRO_LOLA_PGDA_<Site>_5mpp_v2021` (NASA GSFC PGDA LOLA DEM + `slperr`) | `5 m` |
| **Moon** | `temp_amplitude` | `LRO-L-DLRE-5-PCP-V1.0:pcp_avg_tbol_pols_240m_v2022` (LRO Diviner TBOL) | `240 m` |
| **Moon** | `albedo` | `LRO-L-LOLA-4-GDR-V1.0:LDAM_50S_1000M_V1.0_broadband_eq` (LOLA normal × 0.38 broadband solar eq.) | `1000 m` |
| **Earth** | `slope_mean/p90, roughness, relief` | `Copernicus_DEM_GLO-30` (ESA GLO-30 in local metric UTM/UPS) | `30 m` |
| **Earth** | `temp_amplitude` | `MOD11A2.061_annual_mean` (NASA Terra MODIS 2024 full-year day–night ΔT) | `1000 m` |
| **Earth** | `albedo` | `MCD43A3.061` (NASA MODIS shortwave black-sky broadband albedo) | `500 m` |
| **Moon & Earth** | `thermal_inertia` | No uniform global product at matching scale → `NaN`, no invented numbers | — |

## 6. App deliverable
`app/main.py` (Streamlit + pydeck + plotly): reference-site selector,
per-axis scores with CI, mission presets, blind validation tab,
portfolio tab, and analogy-limits card with inspect-site picker and
full `*_src` / `*_res_m` provenance.

**Visual Context Inspector** (Analogy Limits tab): a three-panel
evidence-and-exploration tool — LRO WAC optical + LOLA shaded-relief
previews of the Moon reference (NASA LRO via USGS Astrogeology WMS,
south-pole stereographic EPSG:32761) beside an Esri World Imagery
optical preview (Esri, Maxar, Earthstar Geographics) of the Earth
candidate. It is **context, not a scoring channel**: imagery never
creates or changes a score, and every panel links back to the
quantitative per-axis scores, CIs, `*_src` and `*_res_m` columns
displayed below it.

## 7. Scientific Honesty & Uncertainty Policy
Every feature value carries its 1-sigma uncertainty (`*_sd`), exact
dataset version (`*_src`), and native spatial resolution (`*_res_m`).
Unavailable features (`thermal_inertia`) remain `NaN` and are skipped
transparently by the scoring engine rather than filled with placeholders.

## 8. Why No Single Earth Site is Enough (Public & Engineering Summary)
Think of it like practice venues for a football team before a World Cup
on another planet: every training ground teaches something different.
Atacama's dirt is Mars-dry, Iceland's lava fields feel like Lunar
maria underfoot, and Antarctica's Dry Valleys are as cold and barren
as they come — but no single place on Earth also has the Moon's weak
gravity, airless vacuum, killing radiation, or two-week-long nights.
So instead of asking "which one place is most Moon-like?", we grade
each site **subject by subject** — how you'd drive a rover there, how
equipment survives the temperature swings, how dusty-bright the
surface is — and we say openly what each grade is worth and how
uncertain it is. The result is a short **shopping list** of a few
training grounds that together cover every skill a lunar crew needs,
plus an honest list of the skills that can only be rehearsed in
simulators, because Earth simply cannot imitate them.

## 9. Candidate vs. Confirmed Analog Strategy (Karacadağ Case Study)
Our method is validated, not assumed: when the scorer is run **blind**
(role labels hidden), the classic analogues — Atacama, Mauna Loa/Etna,
Haughton Crater — rank near the top, which is exactly what decades of
planetary-field literature predicts. Lesser-studied terrains play a
different role. The Karacadağ basalt plateau in SE Turkey, for
example, is a young, flat, relatively undissected basalt field —
mechanically interesting for **mobility** (basalt regolith, low
relief, pitted surface) and plausibly useful for **surface/albedo**
analogy, which is why it can score high on those axes. But a high
per-axis score is a *hypothesis*, not a title: until a literature
check and (ideally) fieldwork confirm that its regolith behaviour and
surface processes genuinely track a specific lunar environment, we
label it a **candidate** — recommended as a low-cost *test site* for
named axes only, never advertised as a "confirmed Moon analog". The
app enforces this distinction visually (blue = validated analogue,
green→red = candidate) and the report keeps the claim scoped to the
axes that earned it. This is also our answer to the "novel discovery"
temptation: novelty in a candidate is a *reason to test it*, not
evidence.

## 10. Future Work (v2 Extensions)
- **Subsurface lava tubes:** compare CSA RADARSAT-1 open SAR archive
  detections of terrestrial lava-tube candidates against LRO Mini-RF
  radar returns of lunar tubes (e.g., Marius Hills region), so the
  "subsurface radar calibration" axis can be scored on real
  instruments instead of qualitative notes.
- **Mars integration:** ingest real MOLA topography (slope, roughness,
  relief) and TES thermal/albedo products for Jezero/Gale-class
  references, enabling the same per-axis pipeline for Mars when a
  Mars mission use case is requested.
- Longer term: per-use-case uncertainty weighting (replace flat
  mission presets with measured instrument tolerances), and
  time-of-day/dust-stack modelling for the thermal axis.

