# Written Report — Moon South Pole ↔ Earth Multi-Axis Analog Scoring

**All reference features (`data/processed/features_moon.parquet`) and Earth validation/candidate features (`data/processed/features_earth.parquet`) are computed from verified orbital datasets (`0 MOCK`, verified via `scripts/validate_all.py --fail-on-mock`).**

## 1. Method (one paragraph)
No place on Earth analogs the Moon south pole (Shackleton rim area)
in every respect, so we score Earth sites **per axis** — **mobility**
(slope mean/p90, roughness, relief) and **surface** (albedo) as active v1
numeric axes, while **thermal** (`temp_amplitude`, `thermal_inertia`) is
intentionally suspended (`NaN` on Moon per `Karar #30` until diurnal PDS
definition alignment) — using the leader's standardized-distance kernel
similarity index `exp(-D)` [0–1], where `D` is the RMS of the uncapped
standardized feature differences. Standardization uses all 40 Earth
sites plus the Moon reference, so index values are pool-dependent and are
not calibrated probabilities. Uncertainty is propagated through 200
independent Gaussian Monte Carlo draws using candidate and reference `*_sd`
values; reported bounds are the 5th and 95th percentiles, not bootstrap
confidence intervals. Unknown uncertainty is not treated as zero, and
mission-weighted total ranges are computed from the same axis draws. Role
labels do not enter scoring. Qualitative factors (lithology class, E8
water ice/permafrost, lava tubes, electrostatic dust) are displayed for
mission context and never enter the numeric score (`AGENTS.md` §2, §5).

## 1b. Scope & Rationale (Moon South Pole First in v1, Mars Path in v2)
The NASA Space Apps challenge asks teams to evaluate terrestrial analogues for
**Moon or Mars** exploration. In v1, we focus deliberately on the **Lunar South
Pole** (5 NASA Artemis III candidate regions: Shackleton Crater Rim,
Shackleton–de Gerlache Connecting Ridge, de Gerlache Crater Rim, Peak Near
Shackleton, and Faustini Crater Rim) so every row carries high-resolution
(`5 m/px` LRO LOLA DEM, `30 m/px` Copernicus GLO-30 / NASADEM) audited orbital
provenance rather than a shallow multi-body prototype. Both the data contract
(`AGENTS.md` §5) and `src/scoring/` are body-agnostic (`body in {"moon", "mars", "earth"}`);
extending v2 to Mars requires only ingesting MGS MOLA topography and Odyssey
THEMIS / TES thermal-albedo products into `data/processed/features_mars.parquet`.

## 2. Where the analogy breaks down
- Gravity: Moon ~1/6 g, Mars ~3/8 g — regolith mechanics, dust settling.
- Vacuum / thin atmosphere; radiation; 29.5-day lunar day.
- Regolith composition and mineralogy.
- Qualitative v1 factors: E8 water ice / permafrost, lava tubes /
  subsurface caves, electrostatic dust — tracked qualitatively in the app,
  not scored numerically.
- Thermal suspension & resolution honesty (`Karar #30`): Moon thermal
  metrics remain `NaN` in v1 rather than mixing non-comparable local-time
  products (`docs/data_notes.md`); DEM features compare `5 m` LOLA (Moon)
  against `30 m` Copernicus GLO-30 / NASADEM (Earth), and albedo compares
  `1000 m` LOLA against `500 m` MODIS, all labeled via `*_src` / `*_res_m`
  in the app's Limits of the Analogy tab.

## 3. Descriptive Rank Diagnostic (§8.4)
The Rank Diagnostic tab (`Sıra Tanısı (Doğrulama)`) is a **descriptive
diagnostic**, not an independent holdout validation (`bağımsız holdout
doğrulaması değildir`), because all 40 Earth sites contribute to the pooled
standard deviation scaling. It pairs the 10 blind-scored `validation` sites
with pre-registered DOI-backed expectations (`docs/validation_expectations.md`,
reproduced in `app/expectations.py`): 8 sites expected on `mobility`,
McMurdo Dry Valleys expected on `thermal_only` (suspended in v1) while
nonetheless aligning on bright snow-covered `surface` (`#2 / 40`), and
Svalbard Bockfjorden expected `none` on active v1 numeric axes (relevant
qualitatively via E8 permafrost). The diagnostic table sorts numerically via
integer column headers (default ordered by Mobility rank). Under
`moon_shackleton_rim` (`Balanced`), Mount Etna ranks **#3 / 40** on `mobility`
(`#1` among validation sites) and only `2/20` active site×axis pairs fall
inside the overall top 5 (`etna` on mobility, `mcmurdo` on surface) —
confirming why per-site expected-axis criteria matter far more than an
all-site/all-axis top-k count.

## 4. Multi-Site Portfolio Analysis (Scoring Engine & Technical Report)
Multi-site greedy set-cover selection (`src/scoring/portfolio.py::select_portfolio`)
remains part of the core scoring module and is reported across all 5 lunar
references in `report/final_report_tr.md`: at threshold `0.70` (a heuristic
index setting, not a calibrated physical sufficiency limit), no single Earth
site clears both active axes on `moon_shackleton_rim` (`mobility` stays below
`0.70`), whereas for `moon_connecting_ridge` a 2-site portfolio
(`earth_karapinar_meke` + `earth_puna_campo_piedra_pomez`) covers both active
axes (`mobility` and `surface`), and `moon_shackleton_peak` / `moon_faustini_rim`
clear `0.70` with 1 site (`mcmurdo` and `salda_terrace`, respectively). To keep
the Streamlit interface minimal and clutter-free, portfolio optimization is
documented in the technical report rather than shown as a separate UI widget.

## 5. Data sources (verified orbital products in `*_src`)
| Body | Feature(s) | Dataset (`*_src`) | Native res (`*_res_m`) |
|---|---|---|---|
| **Moon** | `slope_mean/p90, roughness, relief` | `LRO_LOLA_PGDA_<Site>_5mpp_v2021` (NASA GSFC PGDA LOLA DEM + `slperr`) | `5 m` |
| **Moon** | `albedo` | `LRO-L-LOLA-4-GDR-V1.0:LDAM_50S_1000M_V1.0_broadband_eq` (LOLA normal × 0.38 broadband solar eq.) | `1000 m` |
| **Moon** | `temp_amplitude, thermal_inertia` | Suspended in v1 (`NaN` per `Karar #30` / `docs/data_notes.md`) | — |
| **Earth** | `slope_mean/p90, roughness, relief` | `Copernicus_DEM_GLO-30` (39 sites) + `NASADEM_HGT_v001` (`earth_agri_dogubayazit_flow`) | `30 m` |
| **Earth** | `temp_amplitude` | `MOD11A2.061_annual_mean` (NASA Terra MODIS 2024 full-year day–night ΔT; retained on Earth for v2) | `1000 m` |
| **Earth** | `albedo` | `MCD43A3.061` (NASA MODIS shortwave black-sky broadband albedo) | `500 m` |
| **Earth** | `thermal_inertia` | No uniform global product at matching scale → `NaN` | — |
| **Moon & Earth (visual + 3D)** | `moon_3d/` (`5 m`), `earth_3d_grids.npz` (`30 m`), `moon_atlas/` (`5 m` LOLA hillshade/hazard), `earth_atlas/` (`10 m` Sentinel-2 L2A WebP) | Visual & 3D inspection only — never scored numerically | `5–30 m` |

## 6. App deliverable
`app/main.py` (Streamlit + pydeck + plotly, TR default / EN toggle, single
high-contrast pure-black `#000000` canvas, zero emojis, localized Moon crater
names without raw `ROI` codes): reference-site selector, mission re-weighting
(with explicit `isru_ice` `(no ice data in v1)` note), active axis
uncertainty bars (`expanded_interval`, `Eksen Grafikleri`), real 3D Moon/Earth
DEM terrain (`3D Arazi`), role-filterable `Skor Tablosu`, numeric-sorted
10-row `Sıra Tanısı (Doğrulama)`, and `Analojinin Sınırları` featuring the
**8-Dimension Challenge Scorecard**, offline 3-panel Visual Context Inspector,
standardized `axis_gaps`, and a collapsible **Veri Kaynakları ve Akademik
Kaynakça (Ay & Dünya)** section drawing directly on Emirhan's Moon citations
(`docs/data_sources_moon.md`) and Eray's 40 Earth site citations
(`src/earth/sites.py`, `docs/data_sources_earth.md`).

**Visual Context Inspector** (`Analojinin Sınırları` tab): an offline-first
three-panel evidence tool rendered from committed assets — local `5 m/px`
LRO LOLA hillshade and slope-hazard maps (`data/processed/moon_atlas/`, plus
optional full-context expander) beside local `10 m/px` Sentinel-2 L2A WebP
imagery (`data/processed/earth_atlas/` with `metadata.json` capture date and
cloud cover), with remote WMS/Esri kept solely as fallback. It is **context,
not a scoring channel**: imagery never creates or modifies a score.

## 7. Scientific Honesty & Uncertainty Policy
Every feature value carries its 1-sigma uncertainty (`*_sd`), exact
dataset version (`*_src`), and native spatial resolution (`*_res_m`).
Unavailable features (`thermal_inertia`) remain `NaN` and are skipped
transparently by the scoring engine rather than filled with placeholders.
If any scored feature lacks a valid standard deviation, its point score
remains available but its uncertainty interval is omitted; the same rule
applies to a total score if a positively weighted axis has incomplete
uncertainty. Negative or infinite standard deviations are rejected as
invalid inputs. Candidate, reference, feature and axis errors are treated
as independent; pooled standardization statistics stay fixed across draws.

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
The method in v1 is evaluated **descriptively rather than as an independent
validation**: across 40 Earth sites under `moon_shackleton_rim` with thermal
suspended (`20` active site×axis validation pairs), `2/20` pairs fall in
the overall top five (Mount Etna `#3 / 40` on mobility, McMurdo Wright Valley
`#2 / 40` on surface), and we intentionally do not tune weights or thresholds
to force known analogues higher. Lesser-studied terrains play a complementary
discovery role. Under `moon_shackleton_rim` (`Balanced`), Anatolian candidate
**Karapınar Meke Crater** leads the default balanced ranking (`0.528
[0.406–0.569]`, driven strongly by `surface 0.903`, `mobility 0.153`), while
**Hasandağı Keçikaleçik** leads under **Rover Mobility** (`0.446`); meanwhile
**Karacadağ** remains a **candidate** (`Karacadağ Summit 0.419`: `surface
0.736`, `mobility 0.103`; `Karacadağ Ovabağ 0.349`), not a confirmed analog.
A high surface or balanced index is a screening hypothesis reflecting measured
broadband albedo and coarse DEM statistics — never proof of matching regolith
mechanics or geology — and always requires field and literature verification.

## 10. Challenge Prompt ↔ Deliverable Alignment Matrix
| Challenge Prompt Requirement | v1 Implementation & Deliverable |
|---|---|
| *"Identify what is similar, how similar it is, and what is different"* | Per-axis `exp(-D)` index (`0–1`) + 200-draw Monte Carlo `q05–q95` intervals (`scoring.display.expanded_interval`) + standardized `axis_gaps` feature diffs |
| *"Remember Earth's limitations"* | Dedicated `Limits of the Analogy` tab + **8-Dimension Challenge Scorecard** separating field-testable axes (`Mobility`, `Surface`) from `1/6 g`, vacuum, radiation, `29.5`-day cycles, and suspended `Thermal` |
| *"Look beyond well-known analogs / surprise us"* | `30` curated candidate sites evaluated alongside `10` classic validation analogues (`40` Earth sites total) without feeding role labels into scoring |
| *"Use multiple datasets & consider scale"* | Multi-sensor orbital fusion (`5 m` LOLA DEM, `1000 m` LOLA albedo, `30 m` Copernicus GLO-30 / NASADEM, `500 m` MCD43A3, `10 m` Sentinel-2 L2A) on `r = 1000 m` metric windows with explicit `5 m` vs `30 m` scale disclosures |
| *"Connect the analogy to exploration"* | Mission selector (`Balanced`, `Rover mobility test`, `ISRU / ice prospect (no ice data in v1)`, `Subsurface radar calibration`) + core portfolio synthesis (`select_portfolio`, `report/final_report_tr.md`) |
| *"Go beyond visual similarity"* | Offline `moon_atlas/`, `earth_atlas/`, and 3D DEMs serve strictly as visual/topographic context and never enter the numeric score |

## 11. Future Work (v2 Extensions)
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

## 12. Consolidated Bibliography & Turkish Final Report
- Consolidated Moon (`docs/data_sources_moon.md`) and Earth
  (`docs/data_sources_earth.md`, `docs/validation_expectations.md`,
  `src/earth/sites.py`) citations are indexed in `docs/data_sources.md` and
  exposed inside the collapsible bibliography panel of `Analojinin Sınırları`.
- The full Turkish final technical report with 5-region comparisons and all
  14 Turkish candidate assessments is published in `report/final_report_tr.md`.

