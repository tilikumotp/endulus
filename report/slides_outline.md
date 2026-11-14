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
- Standardized-distance kernel similarity `exp(-distance)`, 0–1, per axis.
- Bootstrap 5–95% CI attached to every score; roles never enter the scorer.
- Mission presets re-weight axes (rover mobility vs ISRU-ice vs radar).
🖼 *Screenshot: Radar Charts tab with CI bands (CI high green dashed / low red dotted).*

## Slide 3 — Where the analogy breaks down
- Physics Earth can't reproduce: 1/6 g, vacuum, radiation, 29.5-day day.
- Qualitative-only factors: ice/PSR, lava tubes, electrostatic dust.
- Resolution honesty: ~1 km thermal vs 30 m DEM — shown per feature.
🖼 *Screenshot: Analogy Limits tab — Visual Context Inspector (LRO WAC/LOLA + Esri imagery) with Karacadağ selected, src/res columns visible.*

## Slide 4 — Validated, not assumed (blind check)
- Scorer runs blind; known analogues (Etna, Atacama, Haughton) must
  rank top-5 per axis.
- Candidates ≠ confirmed analogues: high axis score = hypothesis to test.
- Karacadağ case study: strong mobility/surface *test candidate* — scoped claim.
🖼 *Screenshot: Validation tab (ranks + "Recovered X/Y").*

## Slide 5 — The compact portfolio
- Greedy set-cover heuristic: a compact portfolio covering the most
  axes at the 0.70 threshold (heuristic, not a guaranteed minimum).
- Within-axis z-diffs clipped at ±3σ (`Z_CAP = 3.0`) before ranking.
- Output = shopping list + uncovered-axes list (→ lab/simulation).
🖼 *Screenshot: Portfolio tab (pick order, covered axes, uncovered list).*

## Slide 6 — What the jury can click today
- Live Streamlit app: reference selector, mission re-weighting, radar,
  validation, portfolio, breakdown card.
- Every feature column carries `source` + `res_m` + uncertainty `sd`.
- Data contract (AGENTS.md §5) makes Moon/Mars/Earth numbers comparable.
🖼 *Screenshot: Score Table tab (role filter + Lithology ✓ column).*

## Slide 7 (optional) — Roadmap
- RADARSAT-1 SAR × Mini-RF: subsurface lava-tube axis on real instruments.
- Mars: MOLA/TES integration for Mars-referenced scoring.
- Replace flat mission presets with measured instrument tolerances.
🖼 *Screenshot: none — text slide with repo/PR QR code.*
