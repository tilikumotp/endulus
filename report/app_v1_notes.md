# App Architecture Notes (Person 4, `app/main.py`)

Status: Production v1 — runs end-to-end on verified orbital datasets in
`data/processed/` (`features_moon.parquet` and `features_earth.parquet`).

## Feature Summary
- **Core scoring integration:** ref-site selector, two-layer pydeck map
  (blue ring = validation analogues, green→red = candidates), radar + 5th–95th
  Monte Carlo uncertainty percentiles,
  score table with role filter; scores come 100% from leader's `src/scoring/`
  (`axis_scores` → `axis_pivot` → `combine_axes`; `axis_gaps` for the breakdown card).
- **Validation & Portfolio:** Validation tab (`run_blind_validation`: rank table +
  grouped bars + "Recovered X/Y"), Portfolio tab (`select_portfolio`: greedy
  set-cover heuristic, pick order, covered axes, uncovered axes, threshold slider).
- **Provenance & Analogy Limits:** lithology shown everywhere (score-table column
  with ✓ when it matches the reference class, radar captions, map tooltip;
  qualitative only, never in the numeric score — AGENTS.md §2); Analogy Limits tab
  includes an "Inspect candidate site" selector plus per-feature `_src` and `_res_m`
  transparency for both reference and candidate, and the 3-panel **Visual &
  Topographic Context Inspector** (NASA LRO WAC + LOLA via USGS Astrogeology WMS
  beside Esri World Imagery).
