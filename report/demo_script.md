# Live Demo Walkthrough (Person 4, Jury Presentation)

**Pre-demo checklist (do NOT skip):**
- Verified `data/processed/` parquets loaded (`python scripts/validate_all.py --fail-on-mock`).
- Streamlit running: `streamlit run app/main.py`; browser zoom 100%,
  pure-black high-contrast layout; Moon reference selected (`Shackleton Krateri Kenarı`).
- Keep `report/final_report_tr.md` and `docs/data_sources.md` ready for deep technical questions.

---

## Step 1 — The problem & the single-score fallacy
- Open on the **title + Harita tab**: "Every mission plan asks *where on
  Earth do we rehearse for the Moon?* The usual answer is one 'best analog'.
  That's the trap."
- Switch briefly to **Skor Tablosu**: "No place on Earth matches the Moon in
  *every* respect — Etna excels on volcanic slope/roughness (`#3 / 40` Mobility),
  McMurdo Wright Valley matches bright surfaces (`#2 / 40`), and Anatolian
  candidates like Karapınar Meke (`0.528 [0.406–0.569]`) or Hasandağı bring
  complementary strengths."
- Point at **Eksen Grafikleri**: "Two numeric axes are active — **Mobilite** and
  **Yüzey** — while **Termal** is kept `NaN` (suspended) until equivalent
  full-day PDS TBOL curves align in v2. Every active axis shows 5th–95th
  Monte Carlo uncertainty percentiles (`expanded_interval`). These are
  similarity indices, not probabilities."

## Step 2 — Live map, mission re-weighting & real 3D terrain
- Switch mission from **Dengeli** (`#1 Karapınar Meke 0.528`) to **Rover
  Hareket Testi**: rankings visibly reorder (**#1 Hasandağı Keçikaleçik `0.446`**) —
  "the same 40 sites, re-ranked for the equipment we actually test."
- Briefly check **Kaynak / Buz Araştırması (v1'de buz verisi içermez)** to show
  honest scope disclosure.
- Hover a site on **Harita**: blue ring (`[37, 99, 235]`) = 10 known validation
  analogues, red-green fill = active score across all 40 sites, tooltip shows
  intervals and qualitative lithology.
- Open **3D Arazi**: inspect real **5 m/px LRO LOLA** Moon relief vs real
  **30 m/px Copernicus GLO-30** Earth topography (`~2.2 km` window, zero stubs).

## Step 3 — Analojinin Sınırları, Visual Context & Kaynakça
- Open **Analojinin Sınırları** and select a candidate such as **Karacadağ Shield
  Volcano** (`0.419` overall on Shackleton; `surface 0.736`, `mobility 0.103`).
- Highlight the **8 Boyutlu Kapsam ve Sınır Tablosu** separating field-testable
  axes from `1/6 g`, vacuum, radiation, `29.5`-day lunar day, qualitative E8 ice,
  and suspended thermal cycles.
- Walk the offline-first 3-panel **Visual & Topographic Context Inspector**
  (local `5 m/px` LOLA hillshade + LOLA slope-hazard map beside local `10 m/px`
  Sentinel-2 L2A imagery with capture date & cloud cover) and the `z_diff` gap
  table with `ref_src / cand_src / res_m`.
- Expand **Veri Kaynakları ve Akademik Kaynakça (Ay & Dünya)** at the bottom to
  show peer-reviewed Moon DOIs (Barker 2021, Lucey 2014, Lemelin 2016) alongside
  all 40 verified Earth site citations (`src/earth/sites.py`).

## Step 4 — Descriptive Rank Diagnostic & Portfolio Synthesis
- **Sıra Tanısı (Doğrulama):** "The scorer never sees role labels. Sorted by
  integer Mobilite Sırası by default against pre-registered DOI expectations
  (`docs/validation_expectations.md` + E8 ice status): Mount Etna ranks **#3 / 40**
  on Mobility (`#1` among validation sites), while dark mare-like albedo (`0.047`)
  separates it on bright highland Shackleton (`0.147`). Because all 40 sites
  enter pooled Z-scaling, this is a **descriptive rank diagnostic, not an
  independent holdout validation**."
- Note orally (backed by `report/final_report_tr.md` §4.2): our core greedy
  set-cover engine (`src/scoring/portfolio.py`) computes the minimal site group
  per Moon region while routing suspended or unreachable axes to simulation/lab
  chambers.
- Close: "Per-axis scores, honest uncertainty, citation-backed rank diagnostics,
  real 5m/30m 3D DEMs, verified Moon & Earth bibliographies, and an explicit list
  of what Earth can't teach. That's the product."
