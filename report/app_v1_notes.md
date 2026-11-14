# App Architecture Notes (Person 4, `app/main.py`)

Status: Production v1 (synced with `main` `Karar #30`) — runs end-to-end on
verified orbital datasets in `data/processed/` (`features_moon.parquet` and
`features_earth.parquet`).

## Feature Summary
- **Pure-black base & Moon/Earth themes (`.streamlit/config.toml` + `app/main.py`):**
  Both visual presets render over a pure-black canvas (`#000000`) with dark
  Carto pydeck basemaps and dark Plotly canvases; sidebar selector lets users
  switch between **🌑 Moon · Black–Grey** (lunar regolith graphite/silver accents)
  and **🌍 Earth · Blue** (deep abyss navy + `#38BDF8`/`#2563EB` sapphire accents).
- **Core scoring integration:** ref-site selector, mission preset selector
  (with explicit note when `isru_ice` runs on qualitative ice + surface-weighted
  proxy while `thermal` is suspended), two-layer pydeck map (blue ring
  `[37, 99, 235]` = validation analogues, always shown alongside top-N when
  checked; green→red = score fill; tooltip shows Overall + Mobility + Surface),
  active axis uncertainty charts (horizontal P5–P95 bars for 2 active axes
  `mobility` + `surface`; polar radar automatically enabled when >=3 axes are
  active), and Score Table with role filter; scores come 100% from leader's
  `src/scoring/` (`axis_scores` → `axis_pivot` → `combine_axes`; `axis_gaps`
  for breakdown).
- **Rank Diagnostic & Compact Portfolio:** `🧭 Sıra Tanısı (Doğrulama)` tab
  (`run_blind_validation` joined with pre-registered `app/expectations.py` /
  `docs/validation_expectations.md` citations and E8 qualitative ice labels;
  integer `NumberColumn` formatting so column-header and radio sorting by
  Mobility / Overall / Surface rank stay strictly numeric `#%d / 40`; framed
  with an honest note explaining why dark basalt / flat Mars analogues rank
  differently on steep bright lunar South Pole craters, not holdout validation).
  Compact **Portfolio Card** (`select_portfolio`: greedy set-cover with
  threshold slider, `Order` / `Role` / covered active axes, uncovered/suspended
  axes, and highest-mobility note when Mobility stays uncovered) lives directly
  under the Score Table in `📊 Skor & Portföy`. Display uncertainty ranges use
  `scoring.display.expanded_interval` across bar cards, map tooltip, score table,
  and gap breakdown so point scores always sit inside reported bounds.
- **2D Physical Scatter (`📡 Eksen Grafikleri`):** Plots `slope_mean` vs `albedo`
  (marker size = `roughness`) across all 40 Earth sites against the Moon
  reference star before the per-axis bar cards.
- **Real 3D Terrain (M6 + E7):** `app/terrain.py` loads `moon_3d/{site_id}_3d.npz`
  (`5 m/px` LOLA PGDA) and `earth_3d_grids.npz` (`30 m/px` Copernicus GLO-30 /
  NASADEM) with real window dimensions (`2.21 km` / `2.22 km`).
- **Provenance & Analogy Limits:** lithology and E8 ice/permafrost status are
  shown qualitatively across table, tooltips, and breakdown cards (never in the
  numeric score — `AGENTS.md` §2); `⚠️ Analojinin Sınırları` includes the
  **8-Dimension Challenge Scorecard**, candidate selector, per-feature
  `*_src` / `*_res_m` provenance, and an offline-first 3-panel **Visual &
  Topographic Context Inspector** using local `data/processed/moon_atlas/`
  (`5 m/px` LOLA hillshade & slope hazard, plus overview atlas expander) and
  `data/processed/earth_atlas/` (`10 m/px` Sentinel-2 L2A WebP with
  `metadata.json` scene/date/cloud), keeping remote WMS/Esri calls solely as
  fallback.
