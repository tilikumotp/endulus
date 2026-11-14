# Pitch slides outline (6–7 slides, Person 4)

Rule: every number on a slide carries its source (`*_src`) and, where
relevant, its native resolution (`*_res_m`).

---

## Slide 1 — One score is a trap
- No Earth site matches the Moon south pole in every respect.
- Blended "best analog" scores hide which skill each place teaches.
- We grade **per axis**: mobility · thermal · surface.
🖼 *Screenshot: title + Map tab (blue validation ring vs green→red candidates).*

## Slide 2 — The method
- Uncapped RMS standardized-distance similarity index `exp(-D)`, 0–1, per axis.
- 200 independent Gaussian Monte Carlo draws; show 5th–95th percentiles,
  not confidence intervals. Roles never enter the scorer.
- Mission presets re-weight axes (rover mobility vs ISRU-ice vs radar).
🖼 *Screenshot: Radar Charts tab with 5th/95th percentile lines (upper dashed / lower dotted).*

## Slide 3 — Where the analogy breaks down
- Physics Earth can't reproduce: 1/6 g, vacuum, radiation, 29.5-day day.
- Qualitative-only factors: ice/PSR, lava tubes, electrostatic dust.
- Resolution honesty: ~1 km thermal vs 30 m DEM — shown per feature.
🖼 *Screenshot: Analogy Limits tab — Visual Context Inspector (LRO WAC/LOLA + Esri imagery) with Karacadağ selected, src/res columns visible.*

## Slide 4 — Blind ranking diagnostic (not yet validation)
- Scorer runs blind; current all-site/all-axis diagnostic is 4/30 top-5
  for Shackleton and is not a pass/fail validation.
- Define citation-backed expected site–axis pairs before any validation claim.
- Candidates ≠ confirmed analogues: a high index is a hypothesis to test.
- Karacadağ stays a candidate; current default ranking is stronger on
  surface than mobility, not a confirmed cross-axis match.
🖼 *Screenshot: Validation tab (ranks + "Recovered X/Y").*

## Slide 5 — The compact portfolio
- Greedy set-cover portfolio: exact minimum site count for the current
  three axes; heuristic for larger axis sets.
- The 0.70 coverage threshold is a similarity-index setting, not calibrated.
- No per-feature z clipping; feature gaps and ranking use the same raw
  standardized differences.
- Output = shopping list + uncovered-axes list (→ lab/simulation).
🖼 *Screenshot: Portfolio tab (pick order, covered axes, uncovered list).*

## Slide 6 — What the jury can click today
- Live Streamlit app: reference selector, mission re-weighting, radar,
  validation, portfolio, breakdown card.
- Every feature column carries `source` + `res_m` + uncertainty `sd`.
- Thermal inertia is unavailable in current Moon/Earth data; thermal
  scores use `temp_amplitude` only.
- Data contract (AGENTS.md §5) makes Moon/Mars/Earth numbers comparable.
🖼 *Screenshot: Score Table tab (role filter + Lithology ✓ column).*

## Slide 7 (optional) — Roadmap
- RADARSAT-1 SAR × Mini-RF: subsurface lava-tube axis on real instruments.
- Mars: MOLA/TES integration for Mars-referenced scoring.
- Replace flat mission presets with measured instrument tolerances.
🖼 *Screenshot: none — text slide with repo/PR QR code.*
