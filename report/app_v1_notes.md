# App notes (Person 4, branch p4-app)

Status: v2 — runs end-to-end on MOCK data (`streamlit run app/main.py`,
Python 3.11 venv). Verified with browser screenshots on 2026-11-14.
PR: tilikumotp/endulus#3 (draft).

## What v1 does
- Sidebar: Moon/Mars reference body, reference site selectbox (role =
  `reference`), mission selector (leader's `MISSION_PRESETS`), top-N slider.
- Scores: computed exclusively by `src/scoring/similarity.py`
  (`axis_scores` -> `axis_pivot` -> `combine_axes`). App writes no scoring
  math of its own.
- Tabs: pydeck map (size/colour = mission-weighted score), plotly radar
  charts with 95% CI high/low lines, score table with `[ci_low-ci_high]`
  per axis, analogy-limits card using leader's `axis_gaps` (sorted by
  |z_diff|).
- MOCK banner (top warning + title tag + footer error) whenever any
  `*_src == "MOCK"` row is displayed (AGENTS.md rule 10).

## What v2 adds on top of v1
- Validation tab: leader's `run_blind_validation` — rank table + grouped
  bar chart per axis, "Recovered X/Y" metric, explicit MOCK note (random
  draws → recovery is random until real data lands).
- Portfolio tab: leader's `select_portfolio` (greedy set cover) — pick
  order, covered axes per site, uncovered-axes list; threshold slider in
  sidebar.
- Review fixes: file-mtime cache key (auto-refresh when processed
  parquets land), "kernel similarity exp(-distance)" wording everywhere
  (leader's score is exp(-d), not Gaussian exp(-d^2)), no-op rename
  removed.

## Known v1 limitations (by design, feature freeze 2026-11-15 14:00)
- All numbers are MOCK until real parquets land in `data/processed/`.
- Radar is a 3-point triangle (mobility/thermal/surface axes).
- Validation-tab blind-run check and portfolio view are leader-side;
  app shows their inputs but not their outputs yet.
- `use_container_width` replaced by `width="stretch"` (streamlit 1.67).

## Env quirks
- Machine had only Python 3.14; installed 3.11.9 via `py install 3.11`
  (AGENTS.md stack rule).
- `.venv/` is ignored via local `.git/info/exclude` (no shared-file edit);
  move to `.gitignore` if the leader prefers.
