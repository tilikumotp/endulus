# figures/

App screenshots captured during development (2026-11-14). **All were
taken while the app displayed MOCK data** (the MOCK banner is visible
in most frames) — do not present as scientific findings. Replace with
real-data captures after `data/processed/` parquets merge.

Files `12`–`19` are the v3.1 full re-test (2026-11-14): Option A Mars
lock + enriched reference table (12), two-layer map + legend (13),
radar lithology captions (14), score-table role filter (15),
Validation (16) and Portfolio (17) tabs, Analogy Limits default (18)
and after changing the inspect-site picker to "MOCK Earth Validation
09" (19) — proving the picker re-renders the comparison.

Files `20`–`21` add the v3.2 Visual Context Inspector (2026-11-14):
three-panel imagery evidence view (LRO WAC + LOLA via USGS Astrogeology
WMS, Esri World Imagery) with the quantitative score/CI context box.
Imagery is evidence/context only — it never creates or changes a score.

File `22` is the same panel after PR #2 merged real Earth data
(28 verified sites): the Earth panel now shows Meteor Crater
(Arizona) at real coordinates with the crater visibly resolved, and
the quantitative box shows the leader's real scores (e.g. Mobility
0.21 [0.11–0.30]) — mock's inflated 0.94s are gone. Moon reference is
still MOCK (banner shown) until Person 2's parquet lands.

File `23` is the milestone frame: p2's real Moon parquet landed
(`features_moon.parquet`, 5 LRO/PGDA sites, no MOCK rows) — the MOCK
banner is gone and the panel shows the real Shackleton Crater
(Site 04 ROI): WAC orthomosaic with the dark PSR floor and bright rim,
LOLA shaded relief, and McMurdo Dry Valleys side-by-side, with the
leader's real scores in the context box (Mobility 0.09 [0.08–0.11]).
Only Mars (optional preview) remains mock.
