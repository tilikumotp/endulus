# App notes (Person 4, branch p4-app)

Status: v3 — runs end-to-end on MOCK data (`streamlit run app/main.py`,
Python 3.11 venv). Verified with browser screenshots on 2026-11-14.
PR: tilikumotp/endulus#3 (draft).

## Version history
- **v1:** ref-site selector, pydeck map, radar + CI, score table, MOCK
  banner; scores 100% from leader's `src/scoring/` (axis_scores →
  axis_pivot → combine_axes; axis_gaps for the breakdown card).
- **v2:** Validation tab (`run_blind_validation`: rank table + grouped
  bars + "Recovered X/Y"), Portfolio tab (`select_portfolio`: pick
  order, covered axes, uncovered axes, threshold slider); review fixes:
  file-mtime cache key, "kernel similarity exp(-distance)" wording,
  no-op rename removed.
- **v3:** lithology shown everywhere (score-table column with ✓ when it
  matches the reference class, radar captions, map tooltip; qualitative
  only, never in the numeric score — AGENTS.md §2); Analogy Limits tab
  gained an "Inspect candidate site" selector (any site, e.g.
  Karacadağ) plus per-feature `_src` and `_res_m` transparency for both
  reference and candidate (a ~1 km MODIS product cannot resolve a
  500 m site even when the DEM is 30 m); qualitative v1 factors
  (water ice/PSR, lava tubes/subsurface caves, electrostatic dust)
  listed under "not in numeric score"; per-body MOCK flag — the banner
  now names exactly which parts are synthetic, so real Moon+Earth data
  is never masked by a mock Mars parquet; Mars radio labelled
  "Mars (v2 Mock Preview)" while its parquet is mock; top-N slider
  guard for tiny Earth tables (min_value=1).

## Known limitations (by design, feature freeze 2026-11-15 14:00)
- All numbers are MOCK until real parquets land in `data/processed/`;
  p3's real Earth parquet is pending merge (PR #2), Moon/Mars from p2.
- Radar is a 3-point triangle (mobility/thermal/surface axes).
- Validation and Portfolio read leader's modules; their narrative
  interpretation lives in the written report, not the app.

## Env quirks
- Machine had only Python 3.14; installed 3.11.9 via `py install 3.11`
  (AGENTS.md stack rule).
- `.venv/` is ignored via local `.git/info/exclude` (no shared-file edit);
  move to `.gitignore` if the leader prefers.
