# Written Report — Moon South Pole ↔ Earth Multi-Axis Analog Scoring

**All reference features (`data/processed/features_moon.parquet`) and Earth validation/candidate features (`data/processed/features_earth.parquet`) are computed from verified orbital datasets (`0 MOCK`, verified via `scripts/validate_all.py --fail-on-mock`).**

## 1. Method (one paragraph)
No place on Earth analogs the Moon south pole (Shackleton rim area)
in every respect, so we score Earth sites **per axis** — mobility
(slope, roughness, relief), thermal (temp amplitude, thermal inertia),
surface (albedo) — using the leader's standardized-distance kernel
similarity index `exp(-D)` [0–1], where `D` is the RMS of the uncapped
standardized feature differences. The standardization uses the current
Earth candidate pool plus the reference, so index values are
pool-dependent and are not calibrated probabilities. Uncertainty is
propagated through 200 independent Gaussian Monte Carlo draws using the
candidate and reference `*_sd` values; reported bounds are the 5th and
95th percentiles, not bootstrap confidence intervals. Unknown uncertainty
is not treated as zero, and mission-weighted total ranges are computed
from the same axis draws. Role labels do not enter scoring. The app also
offers a greedy set-cover portfolio heuristic. Qualitative factors
(lithology class, ice/PSR, lava tubes, electrostatic dust) are displayed
but never enter the numeric score (AGENTS.md §2, §5).

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
The current blind-ranking screen is a **descriptive diagnostic**, not a
pass/fail validation: it compares every validation site with every axis,
although a known analogue is not expected to match every axis. For the
default `moon_shackleton_rim` reference, 4 of 30 site×axis pairs rank in
the top five (mobility 1/10, thermal 2/10, surface 1/10). The scorer does
not see role labels, but this aggregate does not establish predictive
validity. Before making a validation claim, define expected
site–axis pairs from cited evidence before inspecting rankings; do not
tune the formula to this validation set. The current thermal ranking uses
`temp_amplitude` only because no `thermal_inertia` values are available.

## 4. Portfolio (§8.5)
Compact multi-site test portfolio via greedy set-cover heuristic
(leader's `select_portfolio`) over per-axis scores at a coverage
threshold (default 0.70 similarity-index value): a small set of Earth
sites covering the most axes. This threshold is an interface heuristic,
not a calibrated likelihood of a match. Greedy is fast and transparent,
and for this v1's three axes its maximum-new-axes choice gives the exact
minimum number of sites; ties are broken by score and then `site_id`.
For more than three axes it is only a heuristic. Axes no site covers
(notably extreme lunar South Pole `thermal` swings of 114–151 K) are
flagged for lab/simulation validation.

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
per-axis scores with Monte Carlo percentiles, mission presets, blind-ranking
diagnostic tab, portfolio tab, and analogy-limits card with inspect-site
picker and full `*_src` / `*_res_m` provenance.

**Visual Context Inspector** (Analogy Limits tab): a three-panel
evidence-and-exploration tool — LRO WAC optical + LOLA shaded-relief
previews of the Moon reference (NASA LRO via USGS Astrogeology WMS,
south-pole stereographic EPSG:32761) beside an Esri World Imagery
optical preview (Esri, Maxar, Earthstar Geographics) of the Earth
candidate. It is **context, not a scoring channel**: imagery never
creates or changes a score, and every panel links back to the
quantitative per-axis scores, Monte Carlo percentiles, `*_src` and `*_res_m` columns
displayed below it.

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
The current method is **not yet validated**: the blind diagnostic
compares all validation sites against all axes and recovers only 4/30
site×axis pairs in the top five for the default Shackleton reference.
This is not a fair per-analogue pass/fail score without a cited,
pre-registered expected-axis matrix, and we will not tune the method to
force known sites upward. Lesser-studied terrains play a different role.
Karacadağ remains a **candidate**, not a confirmed analog. In the
current default-reference ranking, its candidate entries score more
favorably on the surface axis than on mobility; this is a relative
index result, not evidence of matching geology or regolith mechanics.
Any site-specific claim requires a source-backed literature check and,
ideally, field validation. The app preserves the candidate label; novelty
is a reason to test a site, not evidence that it is analogous.

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

