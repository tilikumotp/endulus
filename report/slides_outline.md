# Pitch slides outline (6–7 slides, Person 4)

Rule: every number on a slide carries its source (`*_src`) and, where
relevant, its native resolution (`*_res_m`). Full tables: `report/final_report_tr.md`.

---

## Slide 1 — One score is a trap
- No Earth site matches the Moon south pole in every respect.
- Blended "best analog" scores hide which skill each place teaches.
- We grade **per active axis**: **Mobility** · **Surface** (while **Thermal**
  stays intentionally `NaN` / suspended until equivalent full-day PDS TBOL
  cycles align in v2).
- *Visual: Title + Harita tab (pure-black `#000000`, blue validation rings vs
  red–green score fill across 40 sites).*

## Slide 2 — The method & mission re-weighting
- Uncapped RMS standardized-distance similarity index `exp(-D)`, 0–1, per axis.
- 200 independent Gaussian Monte Carlo draws; P5–P95 intervals
  (`expanded_interval`). Roles never enter the scorer.
- Mission presets re-weight active axes: on `Shackleton Krateri Kenarı`, Balanced
  puts **Karapınar Meke** first (`0.528 [0.406–0.569]`), whereas **Rover Hareket
  Testi** promotes **Hasandağı Keçikaleçik** (`0.446`) first.
- *Visual: Eksen Grafikleri tab (active Mobility & Surface bars + P5–P95 ranges).*

## Slide 3 — Real 3D terrain & offline orbital evidence
- Physics Earth can't reproduce: 1/6 g, vacuum, radiation, 29.5-day lunar day.
- Qualitative-only factors: E8 water ice/permafrost, lava tubes, electrostatic dust.
- Resolution honesty: `5 m` Moon LOLA DEM (`LRO_LOLA_PGDA_*`) vs `30 m` Earth
  `Copernicus_DEM_GLO-30` / `NASADEM_HGT_v001`; `1000 m` LOLA broadband-eq.
  albedo vs `500 m` MODIS `MCD43A3.061`.
- *Visual: 3D Arazi side-by-side (`5 m` LOLA vs `30 m` Copernicus GLO-30) or
  Analojinin Sınırları offline 3-panel inspector (`5 m` LOLA + `10 m` Sentinel-2 L2A).*

## Slide 4 — Descriptive rank diagnostic (not holdout validation)
- Scorer runs blind across all 40 sites against pre-registered DOI-cited
  expectations (`docs/validation_expectations.md`, 10 validation sites).
- Under Shackleton, **Mount Etna** ranks **#3 / 40** on Mobility and **McMurdo
  Wright Valley** ranks **#2 / 40** on Surface (`albedo`), explaining physically
  why steep bright craters split validation rankings.
- Candidates != confirmed analogues: **Karacadağ** stays a candidate
  (`Summit 0.419` on Shackleton; `#2 = 0.761` on gentler Faustini), a hypothesis
  for field verification rather than a confirmed match.
- *Visual: Sıra Tanısı (Doğrulama) tab sorted by Mobilite Sırası with E8 ice & DOIs.*

## Slide 5 — Multi-site portfolio synthesis (scoring engine & report)
- Core set-cover solver (`src/scoring/portfolio.py::select_portfolio`) identifies
  the smallest Earth set covering active axes at heuristic threshold `0.70`:
  - `Bağlantı Sırtı`: 2 sites (`karapinar_meke` + `puna_campo_piedra_pomez`) cover both active axes.
  - `Faustini` / `Shackleton Yakını Zirve`: 1 site clears `0.70` across both active axes.
  - `Shackleton Kenarı`: Mobility stays below `0.70` -> routed to simulation/lab chambers.
- Full quantitative matrices across all 5 Moon regions: `report/final_report_tr.md`.

## Slide 6 — What the jury can inspect today
- Clean pure-black 6-tab Streamlit app (TR/EN, zero emojis, localized crater names).
- Complete academic provenance: Emirhan's NASA PGDA/LOLA/Diviner papers
  (`docs/data_sources_moon.md`) + Eray's 40-site citations & DOI benchmarks
  (`docs/data_sources_earth.md`, `docs/data_sources.md`) accessible directly
  inside `Analojinin Sınırları`.
- Zero mock data: `python scripts/validate_all.py --fail-on-mock` passes with
  0 errors and 0 warnings across 40 Earth + 5 Moon rows.

## Slide 7 (optional) — Roadmap to v2
- Full-day PDS LRO Diviner `ltim01..96` diurnal modeling alongside MODIS.
- RADARSAT-1 SAR × Mini-RF subsurface lava-tube scoring.
- Mars integration (`features_mars.parquet`: MGS MOLA + Odyssey THEMIS/TES).
