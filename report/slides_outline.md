# Pitch slides outline (6–7 slides, Person 4)

Rule: every number on a slide carries its source (`*_src`) and, where
relevant, its native resolution (`*_res_m`).

---

## Slide 1 — One score is a trap
- No Earth site matches the Moon south pole in every respect.
- Blended "best analog" scores hide which skill each place teaches.
- In v1 we grade **per active axis**: **mobility** · **surface** (while
  **thermal** is explicitly suspended at `NaN` until v2 full-day PDS TBOL).
🖼 *Screenshot: title + Map tab (blue `[37, 99, 235]` validation rings vs green→red score fill across 40 sites).*

## Slide 2 — The method
- Uncapped RMS standardized-distance similarity index `exp(-D)`, 0–1, per axis.
- 200 independent Gaussian Monte Carlo draws; show 5th–95th percentiles,
  not confidence intervals. Roles never enter the scorer.
- Mission presets re-weight axes: e.g. Shackleton Balanced puts **Karapınar Meke**
  first (`0.528 [0.406–0.569]`), while **Rover Mobility** promotes **Hasandağı
  Keçikaleçik** (`0.446`) first.
🖼 *Screenshot: Axis Charts tab with 5th–95th percentile intervals (active Mobility & Surface + Thermal suspended note).*

## Slide 3 — Where the analogy breaks down & real 3D orbital views
- Physics Earth can't reproduce: 1/6 g, vacuum, radiation, 29.5-day day.
- Qualitative-only factors: E8 water ice/permafrost, lava tubes, electrostatic dust.
- Resolution honesty: `5 m` Moon LOLA DEM vs `30 m` Earth Copernicus GLO-30;
  `1000 m` Moon albedo vs `500 m` MODIS — shown per feature with offline visuals.
🖼 *Screenshot: Analogy Limits tab — offline 3-panel Visual Context Inspector (`5 m` LOLA hillshade + slope hazard + `10 m` Sentinel-2 L2A WebP) & Limits/Breakdown table (or 3D Terrain side-by-side M6+E7 DEM).*

## Slide 4 — Descriptive rank diagnostic (not independent holdout validation)
- Scorer runs blind across all 40 sites against pre-registered DOI-cited
  expectations (`docs/validation_expectations.md`, 10 validation sites).
- Under Shackleton, Mount Etna ranks **#3 / 40** on Mobility and McMurdo
  ranks **#2 / 40** on Surface (`albedo`); broad active top-5 overlap is `2/20`
  pairs (`bağımsız holdout değildir` — pool Z-scaling uses all 40 sites).
- Candidates != confirmed analogues: **Karacadağ** stays a candidate
  (`Summit 0.419`: stronger on `surface 0.736` than `mobility 0.103`), a
  hypothesis for field investigation rather than confirmed geology match.
🖼 *Screenshot: Rank Diagnostic tab (10-row expectation + active ranks + E8 ice + clickable DOI sources).*

## Slide 5 — The compact portfolio
- Greedy set-cover portfolio integrated directly under Score Table:
  exact minimum site count over the 2 active axes (`mobility`, `surface`);
  uncovered/suspended axes route to lab & lunar simulation.
- The `0.70` coverage threshold is a similarity-index setting, not calibrated
  (for Shackleton Rim default, neither active axis hits `0.70` — e.g.
  Connecting Ridge or Faustini Rim reach >`0.70` with 1–2 sites; `thermal`
  remains uncovered in v1).
- Output = compact Earth test portfolio + simulation backlog.
🖼 *Screenshot: Scores & Portfolio tab (role filter, lithology ✓ column, and Compact Portfolio Card below table).*

## Slide 6 — What the jury can click today
- Live Streamlit app (TR/EN): reference selector, mission re-weighting, active
  axis charts, real 3D M6/E7 DEMs, score table + portfolio card, 10-row rank
  diagnostic, and offline LOLA + Sentinel-2 analogy limits.
- Every feature column carries `source` + `res_m` + uncertainty `sd`.
- Thermal (`temp_amplitude` and `thermal_inertia`) is cleanly suspended (`NaN`
  on Moon in v1 per `Karar #30`) rather than filled with incompatible definitions.
- Data contract (`AGENTS.md` §5) passes `validate_all.py --fail-on-mock` (`0 MOCK`).
🖼 *Screenshot: 3D Terrain or Scores & Portfolio tab showing clean provenance.*

## Slide 7 (optional) — Roadmap
- **v2 Thermal completion:** derive full lunar diurnal amplitude from PDS
  LRO Diviner TBOL local-time bins alongside MODIS diurnal/annual thermal products.
- RADARSAT-1 SAR × Mini-RF: subsurface lava-tube axis on real instruments.
- Mars: MOLA/TES integration for Mars-referenced scoring.
🖼 *Screenshot: none — text slide with repo/PR QR code.*
