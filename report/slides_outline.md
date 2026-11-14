# Pitch Slides Outline (7 Slides — `Ay ↔ Dünya Benzer Koşullar Analizi`)

Rule: Every number on a slide carries its orbital source (`*_src`), native spatial resolution (`*_res_m`), and explicit physical/technical boundaries (`docs/data_notes.md`).

---

## Slide 1 — One Score Is a Trap (Scope & Framing)
- No place on Earth matches a Lunar South Pole base site in every respect.
- v1 Scope: **5 NASA Artemis III Lunar South Pole Reference Regions** ↔ **40 Curated Earth Sites** (10 literature validation analogues + 30 candidates, including 10 Anatolian volcanic/evaporite sites).
- We evaluate 3 axes: **2 Active Numeric Axes (`Mobility` + `Surface`)** + **1 Suspended Axis (`Thermal = NaN` in v1 under Decision #30)**.
🖼 *Visual: App title (`🌕 Ay ↔ Dünya Benzer Koşullar Analizi`) + Map tab showing blue-ringed validation sites (`color_val`) and candidate sites (`color`) sized/coloured by mission score.*

## Slide 2 — The Method & Uncertainty Propagation
- Standardized-distance kernel similarity index `exp(-D)` in `[0, 1]`, where `D = sqrt(mean(z_diff^2))` over `r = 1000 m` metric windows (not a calibrated probability).
- **200 independent Gaussian Monte Carlo draws** from each feature's `*_sd`; 5th–95th percentiles (`q05–q95`) displayed via `scoring.display.expanded_interval`.
- **Independent Verification:** All 600 site×axis pairs and 200 mission-weighted totals cross-checked with **0 deviation**.
🖼 *Visual: `📊 Görsel Karşılaştırma & Eksenler` tab — 2D Physical Feature Space scatter (`slope_mean` vs `albedo` + Moon ⭐) and horizontal per-axis uncertainty bar cards.*

## Slide 3 — 3D Orbital Topography (`5 m/px` Moon vs `30 m/px` Earth)
- Side-by-side interactive 3D hillshade surfaces built from committed orbital DEM tiles (`data/processed/moon_3d/` & `earth_3d_grids.npz`).
- **Moon:** `LRO_LOLA_PGDA_5mpp_v2021` (`5 m/px`, `2.2×2.2 km`).
- **Earth:** `Copernicus_DEM_GLO30_v2023_1` / `NASADEM_HGT_v001` (`30 m/px`, `2.22×2.22 km`).
- Honest vertical exaggeration slider (`1×–4×`, default `2×`), `0–360°` camera orbit, and `r = 1 km` measurement ring.
🖼 *Visual: `⛰️ 3D Arazi` tab comparing Shackleton Crater Rim (`5 m` LOLA) and Mount Etna / Karapınar Meke Maar (`30 m` GLO-30).*

## Slide 4 — Score Table & Compact Multi-Site Portfolio Card
- Score Table shows **Overall (2 Active Axes)**, **Mobility**, and **Surface** with `expanded_interval` bounds; **Thermal** is omitted with Decision #30 transparency note.
- Directly below the table, the **Compact Portfolio Card (`select_portfolio`)** finds the minimal set of Earth sites covering axes at the `0.70` heuristic threshold (`<= 3` axes exact minimum), routing uncovered/suspended axes to targeted steep-slope trials or lab/simulation.
- Default Shackleton Rim (`Balanced`): **Karapınar Meke Maar (`0.53`, Surface `0.90`)** covers `Surface >= 0.70`; **Hasan Dağı (`Mobility = 0.335`, #1/40)** leads steep volcanic mobility.
🖼 *Visual: `📊 Skor Tablosu & Portföy` tab showing top rows + Compact Portfolio Card + `0.70` heuristic threshold note.*

## Slide 5 — Descriptive Rank Diagnostic (`Betimsel Sıra Tanısı`)
- **Not an independent holdout test:** All 40 Earth sites participate in Z-standardization (`docs/data_notes.md` §2b).
- Single **10-row table** (`docs/validation_expectations.md`) pairing pre-registered expected axes (`Confirmed` / `Candidate`), single-sentence rationale, **E8 qualitative ice/permafrost status**, and **verified DOIs/URLs** with raw blind ranks (`/40`) on **Mobility** and **Surface** (`Thermal: Suspended / NaN`).
- Shackleton Rim highlights: **Mount Etna (`Mobility #3/40`)**, **Lunar Crater Nevada (`Mobility #7/40`, `Surface #11/40`)**, **Meteor Crater (`Mobility #8/40`)**, **McMurdo Dry Valleys (`Surface #2/40`)**.
🖼 *Visual: `✅ Betimsel Sıra Tanısı` 10-row table with DOIs and raw ranks.*

## Slide 6 — Where the Analogy Breaks Down & 8-Dimension Scorecard
- **Physical limits (Lab/Simulation only):** `1/6 g` gravity, vacuum, radiation, `29.5`-day synodic cycle, agglutinate regolith.
- **Technical limits (`docs/data_notes.md`):** `5 m/px` LOLA vs `30 m/px` GLO-30 DEM scale difference; `Karar #30` suspended `Thermal` (`NaN`) due to LRO Diviner `ltim` polar slice vs Earth MODIS annual mean day–night ΔT definition mismatch.
- **Local Orbital Visual Evidence Card:** Committed `LRO LOLA 5 m/px` hillshade & slope-class maps beside cloudless `Sentinel-2 L2A 10 m/px` imagery (`collection`, `scene_id`, `acquisition_date`, `local_cloud_pct`).
🖼 *Visual: `⚠️ Analojinin Sınırları` tab — 8-Dimension Scorecard + LOLA/Sentinel-2 Evidence Card + Feature Gaps table.*

## Slide 7 — Challenge Alignment Matrix & v2 Roadmap
- Every sentence of the NASA Space Apps challenge prompt mapped to a verified deliverable (`draft.md` §8).
- **v2 Roadmap:** (1) 24-hour `ltim01..ltim96` diurnal thermal harmonization (`Karar #30` Option a), (2) multi-thousand-cell global screening layer upstream of `30 m` site analysis, (3) RADARSAT-1 × LRO Mini-RF lava-tube radar axis, (4) Mars MOLA/THEMIS reference integration.
