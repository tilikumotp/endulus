# Live Demo Walkthrough (Person 4, Jury Presentation)

**Pre-demo checklist (do NOT skip):**
- Verified `data/processed/` parquets loaded (`python scripts/validate_all.py --fail-on-mock`).
- Streamlit running: `streamlit run app/main.py`; browser zoom 100%,
  dark background window; Moon reference selected (`Shackleton Crater Rim`).
- Have repo links ready in a browser tab.

---

## Step 1 — The problem & the single-score fallacy
- Open on the **title + Map tab**: "Every mission plan asks *where on
  Earth do we rehearse for the Moon?* The usual answer is one
  'best analog'. That's the trap."
- Show the Scores & Portfolio tab: "No place on Earth matches the Moon in
  *every* respect — Etna excels on volcanic slope/roughness, McMurdo Wright
  Valley matches bright cold surfaces, and Anatolian volcanics like
  Karapınar Meke (`0.528 [0.406–0.569]`) or Hasandağı bring complementary
  strengths."
- Point at the Axis Charts tab captions: "In v1, two numeric axes are active —
  **Mobility** and **Surface** — while **Thermal** is explicitly suspended
  (`NaN` on Moon per `Karar #30` until full-day PDS TBOL integration in v2).
  Every active axis displays 5th–95th Monte Carlo uncertainty percentiles.
  These are not confidence intervals, and the scores are not probabilities."

## Step 2 — Live map + mission re-weighting
- Switch mission from **Balanced** (`#1 Karapınar Meke 0.528`) to **Rover
  Mobility Test**: rankings visibly reorder (**#1 Hasandağı Keçikaleçik `0.446`**) —
  "the same 40 sites, re-ranked for the equipment we actually test."
- Switch to **Resource / Ice Prospecting**: point out the explicit honesty
  banner (*v1: ice is qualitative via E8; thermal is suspended — surface
  brightness weighted instead*).
- Hover a site on the map: tooltip shows role, score, and **lithology**
  (qualitative column, never in the numeric score). Blue ring (`[37, 99, 235]`)
  = 10 validation analogues, green→red fill = overall index across all 40 sites.
- Briefly open **3D Terrain**: inspect real **5 m/px LRO LOLA** Moon relief vs
  real **30 m/px Copernicus GLO-30** Earth topography (`~2.2 km` window, zero stubs).

## Step 3 — Breakdown card: Karacadağ & resolution honesty
- Open **Axis Profiles (`📡 Eksen Grafikleri`)** briefly to show the **2D
  physical scatter (`slope_mean` vs `albedo`)**, then switch to **Limits of
  the Analogy (`⚠️ Analojinin Sınırları`)** and select **Karacadağ**
  (`Karacadağ Summit`, `0.419` overall; `surface 0.736`, `mobility 0.103`) in
  "Inspect candidate site".
- Highlight the **8-Dimension Challenge Scorecard** (separating field-testable
  axes from `1/6 g`, vacuum, radiation, `29.5`-day cycles, and suspended
  `Thermal`), walk the offline-first 3-panel **Visual & Topographic Context Inspector**
  (local `5 m/px` LOLA hillshade + LOLA slope-hazard map beside local `10 m/px`
  Sentinel-2 L2A optical imagery with capture date & cloud cover, plus expandable
  LOLA overview) and the top rows of the gap table (`z_diff` sorts the largest
  physical mismatches first, e.g. `albedo` or `slope_mean`/`relief`).
- Highlight `ref_src / cand_src / res_m` columns and suspended thermal notice:
  "A 5 m Moon DEM vs 30 m Earth DEM, or 1000 m vs 500 m albedo, are never
  mixed silently — we show native resolution next to every number and leave
  suspended features empty (`NaN`)."
- One line on the qualitative list: "E8 water ice/permafrost, lava tubes, and
  electrostatic dust are tracked qualitatively — never silently added to the score."

## Step 4 — Rank diagnostic + Compact Portfolio
- **Rank Diagnostic (`🧭 Sıra Tanısı`):** "The scorer never sees role labels.
  Across all 40 Earth sites, we join each of the 10 validation sites with its
  pre-registered DOI expectations (`docs/validation_expectations.md`, plus E8
  ice status). For instance, Mount Etna ranks **#3 / 40** on Mobility (`#1`
  among validation sites), and McMurdo Wright Valley ranks **#2 / 40** on
  Surface (`albedo`), whereas broad top-5 aggregation across all active pairs
  is only `2/20`. Because all 40 sites enter pool Z-scaling, this is a
  **descriptive rank diagnostic, not an independent holdout validation**."
- **Scores & Portfolio (`📊 Skor & Portföy`):** Scroll directly to the
  **Compact Portfolio Card** under the score table: "Greedy set-cover at the
  `0.70` similarity-index setting yields the smallest set covering active axes
  (threshold is a heuristic setting, not a probability), while `thermal` and
  uncovered axes are explicitly routed to lunar simulation/lab chambers."
- Close: "Per-axis scores, honest uncertainty, citation-backed rank diagnostics,
  real 5m/30m 3D DEMs, a compact portfolio — and an explicit list of what Earth
  can't teach. That's the product."
