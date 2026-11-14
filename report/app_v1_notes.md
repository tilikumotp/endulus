# App Architecture Notes (Person 4, `app/main.py`)

Status: Production minimalist UI — runs end-to-end on verified orbital
datasets in `data/processed/` (`features_moon.parquet` and `features_earth.parquet`).

## Feature Summary
- **Single high-contrast pure-black UI (`.streamlit/config.toml` + `app/main.py`):**
  All 6 tabs (`Harita`, `Eksen Grafikleri`, `3D Arazi`, `Skor Tablosu`,
  `Sıra Tanısı (Doğrulama)`, `Analojinin Sınırları`) render over a pure `#000000`
  canvas with crisp white typography, zero emojis, dark Carto pydeck basemaps,
  and dark Plotly canvases. Moon crater reference names are localized cleanly
  without raw `Site XX ROI` labels (`i18n.moon_ref_name`).
- **Core scoring integration:** ref-site selector, mission preset selector
  (with explicit note when `isru_ice` runs without ice data and weights active
  axes), two-layer pydeck map (blue ring `[37, 99, 235]` = validation analogues,
  always shown alongside top-N when checked; green-red score fill; tooltip shows
  Overall + Mobility + Surface + qualitative lithology), active axis uncertainty
  bars (horizontal P5–P95 intervals for active `mobility` and `surface`), and
  role-filterable `Skor Tablosu`. Scores come 100% from leader's `src/scoring/`
  (`axis_scores_with_draws` -> `axis_pivot` -> `combine_axes_with_uncertainty`;
  `axis_gaps` for breakdown). Display bounds use `scoring.display.expanded_interval`
  across bar cards, tooltips, score table, and gap breakdown.
- **Descriptive Rank Diagnostic:** `Sıra Tanısı (Doğrulama)` tab calls
  `run_blind_validation` and joins the 10 validation rows with pre-registered
  DOI expectations (`app/expectations.py` / `docs/validation_expectations.md`)
  plus qualitative E8 ice labels. Numeric `NumberColumn(format="#%d / 40")`
  formatting keeps Mobility / Overall / Surface header sorting strictly integer,
  default-ordered by Mobility rank.
- **Real 3D Terrain (M6 + E7):** `app/terrain.py` loads `moon_3d/{site_id}_3d.npz`
  (`5 m/px` LOLA PGDA) and `earth_3d_grids.npz` (`30 m/px` Copernicus GLO-30 /
  NASADEM) with exact local window sizes (`~2.21 km` / `2.22 km`).
- **Provenance, Limits & Consolidated Bibliography:** `Analojinin Sınırları`
  includes the 8-Dimension Scope & Limits Scorecard, candidate selector, offline
  3-panel Visual & Topographic Context Inspector (`data/processed/moon_atlas/`
  + `data/processed/earth_atlas/` with `metadata.json`), per-feature
  `*_src` / `*_res_m` gaps, and a collapsible **Veri Kaynakları ve Akademik
  Kaynakça (Ay & Dünya)** section pulling Moon literature (`docs/data_sources_moon.md`)
  and all 40 Earth site citations (`src/earth/sites.py`). Portfolio optimization
  (`src/scoring/portfolio.py`) is documented in `report/final_report_tr.md`
  rather than adding an extra widget card to the minimal UI.
