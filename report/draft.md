# Written Report — Lunar South Pole ↔ Earth Multi-Axis Analog Scoring (`Ay ↔ Dünya Benzer Koşullar Analizi`)

**All 5 Lunar South Pole reference regions (`data/processed/features_moon.parquet`) and 40 Earth validation/candidate sites (`data/processed/features_earth.parquet`) are computed from verified orbital datasets (`0 MOCK`, verified via `python scripts/validate_all.py --fail-on-mock`).**

## 1. Method (One Paragraph)
No place on Earth analogs a Lunar South Pole base site in every respect, so we score 40 curated Earth sites against 5 NASA Artemis III candidate Lunar South Pole regions **per axis** using the leader's standardized-distance kernel similarity index `exp(-D)` in `[0, 1]`, where `D = sqrt(mean(z_diff^2))` is the RMS of uncapped standardized feature differences over `r = 1000 m` circular windows. Under **Decision #30 (`Karar #30`)**, v1 numeric scoring operates on **2 active numeric axes**: **mobility** (`slope_mean`, `slope_p90`, `roughness`, `relief`) and **surface** (`albedo`), while the **thermal** axis (`temp_amplitude`, `thermal_inertia`) is **suspended (`NaN`)** because lunar LRO Diviner polar local-time (`ltim`) slices and Earth `MOD11A2.061` annual-mean day–night LST differences do not share an equivalent physical diurnal-cycle definition, and no uniform global `thermal_inertia` product exists at matching scale. Standardization uses the 40-site Earth pool plus the selected Moon reference, so index values are pool-dependent rankings rather than calibrated probabilities. Uncertainty is propagated through 200 independent Gaussian Monte Carlo draws from each feature's `*_sd`; reported bounds are the 5th and 95th percentiles (`q05–q95`, widened on display via `scoring.display.expanded_interval` when the point index falls outside raw percentile bounds so the UI never appears broken, while underlying scored values remain unchanged). All 600 site×axis pairs (5 Moon references × 40 Earth sites × 3 axes) and 200 mission-weighted totals were independently cross-checked against the documented formula with **zero deviation**. Qualitative factors (`lithology_class`, E8 ground ice/permafrost, lava tubes, electrostatic dust) are tracked explicitly and never mixed into the numeric score (`AGENTS.md` §2, §5).

## 1b. Scope & Rationale (Why Lunar South Pole in v1, Mars Path in v2)
The NASA Space Apps challenge prompt asks teams to compare Earth locations against **Moon or Mars** conditions. In v1, we focus exclusively on the **Lunar South Pole** (5 NASA Artemis III candidate regions: Shackleton Crater Rim, Shackleton–de Gerlache Connecting Ridge, de Gerlache Crater Rim, Peak Near Shackleton, and Faustini Crater Rim) to deliver deep, high-resolution (`5 m/px` LRO LOLA DEM), fully audited orbital provenance rather than a shallow multi-body prototype. The data contract (`AGENTS.md` §5) and `src/scoring/` engine are body-agnostic (`body in {"moon", "mars", "earth"}`); extending to Mars in v2 requires only ingesting MGS MOLA topography and Mars Odyssey THEMIS / MGS TES thermal/albedo products into `data/processed/features_mars.parquet`.

## 2. Where the Analogy Breaks Down & 8-Dimension Scorecard
- **Physical limits Earth cannot reproduce (routed to laboratory & simulation):**
  - Surface gravity: Moon `~1.62 m/s²` (`~1/6 g`) — governs regolith compaction, rover wheel sinkage, and dust settling.
  - Hard vacuum (`~10^-12 torr`), lack of magnetospheric/atmospheric radiation shielding, and the `29.5`-Earth-day lunar synodic cycle with grazing (`~1.5°`) polar solar illumination.
  - Impact-gardened, glass-welded regolith (agglutinates) vs. water/wind-weathered terrestrial soils.
- **Technical & scale limits affecting score interpretation (`docs/data_notes.md`):**
  - **DEM resolution scale difference (`5 m/px` Moon LOLA PGDA vs `30 m/px` Earth Copernicus GLO-30):** Both bodies use the same `r = 1000 m` window and metric-CRS `np.gradient → atan` slope calculation, but the `6×` native pixel-scale ratio makes `slope_mean`, `slope_p90`, and `roughness` scale-sensitive (proxy comparison).
  - **Suspended Thermal axis (`Karar #30`, `temp_amplitude = NaN`, `thermal_inertia = NaN`):** Official PDS3 `.lbl` inspection confirmed that LRO Diviner polar `ltim` slices (`240 m`) do not match the physical diurnal definition of Earth `MOD11A2.061` annual mean day–night LST difference (`1000 m`), and no uniform global `thermal_inertia` product exists at matching scale. Rather than presenting an apples-to-oranges thermal score, v1 suspends the thermal axis as `NaN` and documents the full 24-hour `ltim01..ltim96` polar series (`52.8–278.4 K`) in `docs/data_sources_moon.md`.
  - **Coarse surface sensors (`500 m`–`1000 m`):** Earth `MCD43A3.061` albedo (`500 m`) and Moon `LOLA GDR` albedo (`1000 m`, scaled by `× 0.38` phase-integral conversion to broadband solar hemispherical albedo) do not resolve sub-kilometer patches.

### 8-Dimension Challenge Scorecard
| # | Challenge Dimension | v1 Status | Orbital / Field Provenance |
|---|---|---|---|
| 1 | **Topography & Terrain** (`slope_mean`, `slope_p90`, `roughness`, `relief`) | **Numeric Axis (Active — Mobility)** | Moon: `LRO_LOLA_PGDA_*_5mpp_v2021` (`5 m`) · Earth: `Copernicus_DEM_GLO30_v2023_1` / `NASADEM_HGT_v001` (`30 m`) |
| 2 | **Surface Brightness** (`albedo`) | **Numeric Axis (Active — Surface)** | Moon: `LRO-L-LOLA-4-GDR-V1.0` `× 0.38` broadband eq. (`1000 m`) · Earth: `MCD43A3.061` (`500 m`) |
| 3 | **Temperature Swing & Thermal Inertia** (`temp_amplitude`, `thermal_inertia`) | **Suspended in v1 (`NaN` — Decision #30)** | Moon: `LRO Diviner PCP` (`240 m`, `NaN` in v1) · Earth: `MOD11A2.061_annual_mean` (`1000 m`) |
| 4 | **Surface Lithology** (`lithology_class`) | **Qualitative (Unscored)** | Curated geological literature & maps (`src/earth/sites.py`) |
| 5 | **Water Ice / PSR & Permafrost** (`E8`) | **Qualitative (Unscored)** | Pre-registered DOI-backed inventory across all 10 validation sites (`docs/validation_expectations.md` §4) |
| 6 | **Lava Tubes & Subsurface Cavities** | **Qualitative (Unscored — v2 SAR path)** | Literature channel (Lanzarote PANGAEA, Craters of the Moon); v2 RADARSAT-1 × Mini-RF extension |
| 7 | **Dust, Wind & Electrostatic Dust** | **Qualitative / Lab & Simulation** | Vacuum/plasma electrostatic dust levitation requires laboratory chambers |
| 8 | **Gravity (`1/6 g`), Vacuum, Radiation & `29.5`-Day Cycle** | **Field-Independent — Lab & Simulation** | Fundamental physical constants; never reproduced in terrestrial field sites |

## 3. Descriptive Rank Diagnostic (`Betimsel Sıra Tanısı`, §8.4)
The validation tab (`✅ Betimsel Sıra Tanısı`) is explicitly framed as a **descriptive rank diagnostic (`betimsel sıra tanısı`), not an independent holdout validation or top-5 pass/fail test**: although the scorer never sees `role` labels (`validation` vs `candidate`), all 40 Earth rows participate in the Z-standardization mean and standard deviation (`docs/data_notes.md` §2b). Instead of a blended pass/fail metric, the app presents a **10-row single table** linking each known validation site's raw blind rank (`1–40`) on the **2 active numeric axes (`Mobility` and `Surface`, with `Thermal` marked `Suspended / NaN`)** to its pre-registered expected axes (`Confirmed` / `Candidate`), single-sentence rationale, E8 qualitative ice/permafrost status, and verified DOIs/URLs from `docs/validation_expectations.md`.
- For the default **Shackleton Crater Rim** reference (`moon_shackleton_rim`), steep crater-rim/volcanic-flank mobility analogues rank near the top of the 40-site pool on **Mobility**: **Mount Etna (`#3/40`)**, **Lunar Crater Volcanic Field, Nevada (`#7/40`)**, and **Meteor Crater, Arizona (`#8/40`)**, while **McMurdo Dry Valleys** ranks **`#2/40`** on **Surface** (`#14/40` on Mobility). Flat desert/shield traverse sites such as **Atacama Yungay (`#28/40` Mobility)** naturally rank lower against Shackleton's `18.5°` mean crater-wall slope, illustrating why per-axis diagnostic context outperforms a single pass/fail threshold.

## 4. Compact Multi-Site Portfolio Card (§8.5)
Placed directly below the Score Table (`📊 Skor Tablosu & Portföy`), the **Compact Portfolio Card** runs `scoring.portfolio.select_portfolio` (greedy set cover) at a default `0.70` similarity-index threshold. With at most three axes, the greedy choice guarantees the minimum number of sites covering all reachable axes (`>= 0.70`).
- For the default **Shackleton Crater Rim** reference, **Karapınar Meke Maar (`earth_karapinar_meke`)** is selected (`Surface = 0.90 >= 0.70`), while **Mobility** (where the steepest/closest site in the 40-site pool at `30 m` GLO-30 scale is **Hasan Dağı Keçekalecik** at `0.335`, followed by **Parícutin** `0.311` and **Mount Etna** `0.299`) and the suspended **Thermal (`NaN`)** axis are flagged for targeted steep-slope testing and laboratory/simulation verification.
- **Explicit threshold caveat:** The `0.70` threshold is neither a probability nor a calibrated physical sufficiency bound; the minimal set size depends on this heuristic index setting (`docs/data_notes.md` §2b).

## 5. Data Sources (Verified Orbital Products in `*_src`)
| Body | Feature(s) / Asset | Dataset (`*_src` / Directory) | Native Res (`*_res_m`) |
|---|---|---|---|
| **Moon** | `slope_mean/p90, roughness, relief` | `LRO_LOLA_PGDA_<Site>_5mpp_v2021` (NASA GSFC PGDA LOLA DEM + co-registered `slperr`) | `5 m` |
| **Moon** | `albedo` | `LRO-L-LOLA-4-GDR-V1.0:LDAM_50S_1000M_V1.0_broadband_eq` (LOLA `1064 nm` normal albedo `× 0.38` broadband solar eq.) | `1000 m` |
| **Moon** | `temp_amplitude, thermal_inertia` | Suspended as `NaN` in v1 under Decision #30 (`_src = ""`, `_res_m = 240.0` retained per contract) | `240 m` |
| **Moon** | 2D Atlas & 3D DEM Grids (`M1/M6`) | `data/processed/moon_atlas/` & `data/processed/moon_3d/*_3d.npz` (`442×442` float32, `2.2×2.2 km`) | `5 m` |
| **Earth** | `slope_mean/p90, roughness, relief` | `Copernicus_DEM_GLO30_v2023_1` (39 sites) & `NASADEM_HGT_v001` (1 site: `earth_agri_dogubayazit_flow`) in local metric UTM/UPS | `30 m` |
| **Earth** | `temp_amplitude` | `MOD11A2.061_annual_mean` (NASA Terra MODIS 2024 full-year day–night ΔT; stored in Earth parquet, unscored in v1 while Moon thermal is `NaN`) | `1000 m` |
| **Earth** | `albedo` | `MCD43A3.061` (NASA MODIS shortwave black-sky broadband albedo) | `500 m` |
| **Earth** | `thermal_inertia` | No uniform global product at matching scale → `NaN` (`_src = ""`) | `1000 m` |
| **Earth** | 2D Cloudless Sentinel-2 Atlas (`E5`) | `data/processed/earth_atlas/*.webp` + `metadata.json` (`sentinel-2-l2a`, `512×512`, max local cloud `1.05%`) | `10 m` |
| **Earth** | 3D DEM Grids (`E7`) | `data/processed/earth_3d_grids.npz` (`40` sites, `74×74` float32, `2.22×2.22 km`, aligned to E5 patch centers) | `30 m` |

## 6. Interactive App Deliverable (`app/main.py`)
Built with Streamlit, PyDeck, and Plotly, fully bilingual (**Turkish default + English toggle** via `app/i18n.py`):
1. **Map Tab (`🗺️ Harita`):** Two-layer PyDeck map where both known validation sites (blue ring, `color_val`) and candidate sites (`color`) encode the selected Moon reference and mission-weighted 2-active-axis similarity score in dot colour and radius.
2. **Visual Comparison & Axes Tab (`📊 Görsel Karşılaştırma & Eksenler`):** 2D physical feature-space scatter (`slope_mean` vs `albedo` for all 40 Earth sites + gold star ⭐ for the selected Moon reference) paired with horizontal per-axis bar cards (`Mobility`, `Surface`, `Overall`) showing `expanded_interval` Monte Carlo uncertainty bands and explicit `Thermal: Suspended (NaN)` status.
3. **3D Terrain Tab (`⛰️ 3D Arazi`):** Side-by-side interactive Plotly 3D hillshade surfaces loaded offline from committed `5 m/px` LRO LOLA (`moon_3d/`) and `30 m/px` Copernicus GLO-30 (`earth_3d_grids.npz`) elevation grids, with honest vertical exaggeration (`1×–4×`, default `2×`), `0–360°` camera orbit slider, and `r = 1 km` measurement ring.
4. **Score Table & Portfolio Tab (`📊 Skor Tablosu & Portföy`):** Filterable 40-site table (`Overall`, `Mobility`, `Surface` with `expanded_interval` bounds; `Thermal` omitted with Decision #30 note) followed immediately by the **Compact Portfolio Card** (`select_portfolio` at `0.70` heuristic threshold).
5. **Descriptive Rank Diagnostic Tab (`✅ Betimsel Sıra Tanısı`):** 10-row DOI-backed expectation matrix (`docs/validation_expectations.md`) + E8 qualitative ice/permafrost inventory + raw blind ranks (`/40`).
6. **Limits of the Analogy Tab (`⚠️ Analojinin Sınırları`):** Physical & technical limits (`5 m` vs `30 m` DEM scale note, Decision #30 thermal note), 8-Dimension Challenge Scorecard, committed local orbital visual evidence card (`LRO LOLA 5 m/px` hillshade & slope classes beside `Sentinel-2 L2A 10 m/px` RGB with `collection`, `scene_id`, `acquisition_date`, `local_cloud_pct`), and standardized feature-gap table (`axis_gaps`).

## 7. Candidate vs. Confirmed Analog Strategy (Anatolian Candidates & Karacadağ)
Lesser-studied sites are presented strictly as **candidates**, never as confirmed analogues (`AGENTS.md` §1). For the default **Shackleton Crater Rim** reference (`Balanced` preset across the 2 active axes `Mobility + Surface`), the top-ranked Earth candidates are **Karapınar Meke Maar (`0.53 [0.41–0.57]`, Surface `0.90`, Mobility `0.15`)**, **McMurdo Dry Valleys (`0.51 [0.09–0.51]`, validation)**, **Hasan Dağı Keçekalecik (`0.50 [0.38–0.65]`, Mobility `0.335` — #1 on Mobility across all 40 sites)**, **Ağrı Doğubayazıt Lava Flow (`0.50`)**, and **Erciyes Koçdağı (`0.50`)**, while **Karacadağ Summit (`0.42 [0.36–0.48]`, Surface `0.74`, Mobility `0.10`)** and **Karacadağ Ovabağ (`0.35 [0.28–0.46]`)** match strongly on basaltic surface brightness (`albedo`) but break down on steep crater-wall mobility because Karacadağ is a low-angle shield volcano (`~2–7°` slopes vs Shackleton's `18.5°`).

## 8. Challenge Prompt ↔ Deliverable Alignment Matrix (`Görev Metni ↔ Teslimat Uyum Matrisi`)
| Challenge Prompt Requirement | Project Deliverable & Implementation |
|---|---|
| *"Identify what is similar, how similar it is, and what is different"* | Per-axis `exp(-D)` similarity index (`0–1`) + 200-draw Monte Carlo `q05–q95` intervals (`expanded_interval`) + standardized feature-gap table (`axis_gaps`) |
| *"Remember Earth's limitations"* | Dedicated `Limits of the Analogy` tab + 8-Dimension Scorecard separating field-testable axes from `1/6 g`, vacuum, radiation, and `29.5`-day synodic cycles |
| *"Look beyond well-known analogs / surprise us"* | 30 curated candidate sites (including 10 Anatolian volcanic/evaporite sites: Meke Maar, Hasan Dağı, Karacadağ, Kula, Tendürek, Erciyes, Süphan, Ağrı, Nemrut, Tuz Gölü) evaluated alongside 10 classic validation analogues |
| *"Use multiple datasets & consider scale"* | Multi-sensor orbital fusion (`5 m` LRO LOLA DEM, `1000 m` LOLA albedo, `30 m` Copernicus GLO-30 / NASADEM, `500 m` MODIS MCD43A3, `1000 m` MOD11A2, `10 m` Sentinel-2 L2A) on uniform `r = 1000 m` metric windows with explicit `5 m vs 30 m` scale notes |
| *"Connect the analogy to exploration"* | Mission selector (`Balanced`, `Rover mobility test`, `Thermal-weighted scenario`, `Subsurface radar calibration`) + Compact Multi-Site Test Portfolio Card (`select_portfolio`) |
| *"Go beyond visual similarity"* | Visuals (`moon_atlas/`, `earth_atlas/`, 3D DEM surfaces) are strictly evidence/context cards and never enter the numeric score |

## 9. Future Work (v2 Extensions)
- **Diurnal Thermal Harmonization (`Karar #30` Option a):** Combine the 24-hour `ltim01..ltim96` LRO Diviner polar time series with harmonized diurnal skin-temperature ranges on Earth to activate the numerical `Thermal` axis under a strict common physical definition.
- **Systematic Global Screening Layer:** Scale the generic coordinate-based pipeline to a multi-thousand-cell global screening grid as a coarse discovery layer upstream of `30 m` site-level characterization.
- **Subsurface Lava Tubes & Mars Integration:** Add CSA RADARSAT-1 × LRO Mini-RF radar roughness/void metrics and ingest Mars MOLA/THEMIS reference sites (`features_mars.parquet`).
