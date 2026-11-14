# Live Demo Walkthrough (Person 4, Jury Presentation)

**Pre-demo checklist (do NOT skip):**
- Verified `data/processed/` parquets loaded (`python scripts/validate_all.py --fail-on-mock`).
- Streamlit running: `streamlit run app/main.py`; browser zoom 100%,
  dark background window; Moon reference selected.
- Have repo links ready in a browser tab.

---

## Step 1 — The problem & the single-score fallacy
- Open on the **title + map tab**: "Every mission plan asks *where on
  Earth do we rehearse for the Moon?* The usual answer is one
  'best analog'. That's the trap."
- Show the score table: "No place on Earth matches the Moon in *every*
  respect — Atacama wins on dryness, Iceland on lava mobility, Dry
  Valleys on cold. A single blended score hides that."
- Point at the radar captions: "So we score **per axis** — mobility,
  thermal, surface — and attach an uncertainty band to every number."

## Step 2 — Live map + mission re-weighting
- Switch mission to **Rover Mobility Test**: rankings visibly reorder —
  "the same sites, re-ranked for the equipment we actually test."
- Switch to **ISRU / Ice Prospecting**: "thermal axes dominate; a rover
  course and an ice-prospecting dress rehearsal need different
  venues."
- Hover a site: tooltip shows role, score and **lithology** (qualitative
  column, never in the numeric score). Blue ring = validated analogues,
  green→red = candidates.

## Step 3 — Breakdown card: Karacadağ & resolution honesty
- Open **Analogy Limits** tab; select **Karacadağ** in "Inspect
  candidate site".
- Walk the 3-panel **Visual & Topographic Context Inspector** (LRO WAC +
  LOLA shaded relief + Esri World Imagery) and the top 2 rows of the gap
  table: reference value vs candidate, z_diff sorts the biggest physical
  mismatches first.
- Highlight `ref_src / cand_src / res_m` columns: "a ~1 km MODIS-class
  thermal product cannot resolve a 500 m site even when the DEM is
  30 m — we show the native resolution next to every number."
- One line on the qualitative list: "Ice/PSR, lava tubes, electrostatic
  dust are tracked — never silently mixed into the score."

## Step 4 — Blind validation + portfolio
- **Validation tab:** "Run blind — the scorer never sees roles. Known
  analogues (Etna, Atacama, Haughton, McMurdo) rank in the top-5 per axis.
  This is the self-check that keeps us honest."
- **Portfolio tab:** "Greedy set-cover heuristic at the 0.70 threshold
  gives a compact portfolio of Earth sites covering the most axes —
  plus the axes no
  Earth site can cover: those go to lab/simulation."
- Close: "Per-axis scores, honest uncertainty, blind validation, a
  compact multi-site test portfolio — and an explicit list of what
  Earth can't teach. That's the product."
