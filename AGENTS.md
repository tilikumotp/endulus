# AGENTS.md: NASA Space Apps 2026, "Permanent Moon Base Locations and Mars"

Read this file fully before doing anything. Every team member uses an AI coding agent on this repo. This file is the single source of truth so that four different agents produce compatible code.

## 1. Project in one paragraph
No place on Earth analogs a Moon base or Mars site in every respect. We therefore score Earth sites **per axis** (mobility, thermal, surface), attach **uncertainty** to every score, state **where each analogy breaks down**, link each axis to a **mission/equipment use case**, and recommend a **minimal portfolio of Earth test sites** that covers the most axes. We **validate** the method by checking that well-known analogs (Atacama, Etna/Mauna Loa, Haughton) rank high when the method is run blind. Lesser-studied places (e.g. Karacadağ basalt field, Turkey) are presented as **candidates**, never as confirmed analogs.

Deliverables: (1) interactive map/app, (2) short written report, (3) pitch slides. Hackathon ends the evening of Sunday 2026-11-15. Feature freeze: Sunday 14:00.

## 2. Scope (do not expand without the leader's approval)
- Reference body for v1: **Moon south pole** (Shackleton rim area first). Mars only if the core pipeline already works.
- Core axes (numeric): **mobility** (slope, roughness, relief), **thermal** (temp_amplitude, thermal_inertia), **surface** (albedo).
- Qualitative only in v1: lithology class (basalt, evaporite, ...), ice, lava tubes, dust/wind. Do NOT put mineral spectra from different instruments into a numeric score.
- Out of scope until the leader says so: 3D globe, chatbot/LLM features, new databases, extra backend services.

## 3. Stack (default; change only with leader approval)
- Python 3.11 only. `numpy`, `pandas`, `geopandas`, `rasterio`, `xarray`, `scikit-learn`, `scipy`, `streamlit`, `pydeck`, `plotly`, `pyarrow`.
- No FastAPI, no separate frontend build, no database. Data is a few thousand rows in parquet; numpy is enough.
- Pin new dependencies in `requirements.txt` when you add them.

## 4. Repo layout and ownership
```
data/raw/            big downloads. gitignored. NEVER read into the chat/context.
data/processed/      small parquet outputs defined in section 5. committed.
src/moon_mars/       Person 2 (Moon/Mars feature extraction)
src/earth/           Person 3 (Earth features + candidate curation)
src/scoring/         Leader (similarity, uncertainty, portfolio, validation)
app/                 Person 4 (Streamlit app)
report/              Person 4 (written report, figures)
scripts/make_mock.py generates mock data that follows the contract
```
Each person edits only their own folder. Need a change elsewhere? Ask the owner or the leader. Work on your own branch (`p2-moonmars`, `p3-earth`, `p4-app`, `leader`). Only the leader merges to `main`. Commit small and often. Commit before asking the agent to do anything large.

## 5. DATA CONTRACT (do not deviate)
One parquet file per body: `data/processed/features_moon.parquet`, `features_mars.parquet`, `features_earth.parquet`.

**Identity columns**
| column | type | meaning |
|---|---|---|
| site_id | str | unique, snake_case, e.g. `moon_shackleton_rim` |
| name | str | human-readable |
| body | str | `moon`, `mars`, `earth` |
| role | str | `reference`, `validation`, `candidate`, `grid` |
| lat, lon | float | WGS84-style degrees (planetocentric for Moon/Mars), EPSG:4326 for display |
| radius_m | float | analysis radius around the point (default 1000) |

**Feature columns** (float, NaN if unavailable, never 0 as a placeholder)
| column | unit | definition |
|---|---|---|
| slope_mean | degrees | mean slope inside radius_m |
| slope_p90 | degrees | 90th percentile slope |
| roughness | meters | std of detrended elevation inside radius_m |
| relief | meters | max minus min elevation inside radius_m |
| temp_amplitude | kelvin | max minus min surface temperature over one diurnal cycle (state in `_src` if annual mean) |
| thermal_inertia | J m^-2 K^-1 s^-1/2 | if available |
| albedo | 0 to 1 | broadband albedo |
| lithology_class | str | qualitative class, optional |

**For every feature `X` also provide:** `X_sd` (uncertainty, 1 sigma, best estimate), `X_src` (dataset name + version), `X_res_m` (native resolution in meters). If you cannot estimate `X_sd`, put NaN and say so in `docs/data_notes.md`. Never invent a value.

Rules:
- Compute every feature with the SAME definition on Moon, Mars and Earth. If a definition has to differ, write it in `docs/data_notes.md` and tell the leader.
- Resample/aggregate to the site radius before comparing. Note the native resolution; coarse data (e.g. MODIS ~1 km) must not be presented as resolving a 500 m site.
- Reproject to an appropriate projected CRS (e.g. polar stereographic for the lunar south pole) BEFORE computing slope or distances. Slope on unprojected degrees is wrong.

## 6. Rules for AI agents (all four of you)
1. **Plan first only for shared or structural work.** Write a short plan and wait for approval only when a task (a) changes the data contract or a shared interface, (b) touches another person's folder, or (c) adds a new dependency or module. Inside your own folder, for contained tasks, build it end to end, test it, and report.
2. **Never invent data, coordinates, dataset names, URLs or citations.** If you do not know a coordinate or a dataset's exact product name, say so and leave a `TODO(verify)` marker. A human checks every site coordinate on a map.
3. **Every number must carry its source** (`_src` columns). No source, no number.
4. **Sanity-check outputs visually and numerically** (plot it, print min/max/units). Slope maps: flat plateaus low, flanks high. Temperature in kelvin. Albedo between 0 and 1.
5. **Never load rasters or big files into context.** Print shapes, CRS, bounds and summary stats only.
6. **No silent changes** to the data contract, column names or units. Propose, get approval.
7. **Do not touch folders you do not own.**
8. **No secrets in git** (Earthdata tokens, Earth Engine keys). Use environment variables, `.env` is gitignored.
9. **Keep it simple.** No new frameworks, services, or abstractions. Small functions, type hints, one docstring line each.
10. **Mark mock data.** Anything generated by `make_mock.py` has `*_src == "MOCK"`. The app must show a visible warning banner when any MOCK row is displayed.
11. After each task: run it once end to end, report what ran, what did not, and what assumptions you made.

## 7. Roles
- **Leader:** methodology, `src/scoring/` (per-axis similarity, bootstrap uncertainty, portfolio selection, blind validation), integration, final story. Owns merges.
- **Person 2 (Moon/Mars data):** DEM-derived slope/roughness/relief, temperature products, albedo for the reference sites; writes `features_moon.parquet` (and Mars if time).
- **Person 3 (Earth data + candidates):** the SAME features for Earth validation sites and a curated list of 30 to 50 candidate sites (each with a verified source, e.g. a paper or geology map), plus a coarse global grid if time allows; writes `features_earth.parquet`. Also a 15-minute literature check on each Turkish candidate so we never claim novelty falsely.
- **Person 4 (App + report + pitch):** Streamlit app built on MOCK data first, then real data; per-site radar chart; "where the analogy breaks down" card; mission use-case mapping; written report; slides; 3-minute demo script.

## 8. Required app features (in priority order)
1. Pick a Moon/Mars reference site, see ranked Earth sites on a map with per-axis scores and uncertainty.
2. "Where it breaks down" card: per-axis match plus the physical limits Earth cannot reproduce (gravity, vacuum, radiation, thin atmosphere).
3. Mission selector (e.g. rover mobility test, ISRU/ice, subsurface radar calibration) that reweights axes.
4. Validation tab: known analogs recovered when the method is run blind.
5. Portfolio view: smallest set of Earth sites that covers the most axes, and which axes remain uncovered.

## 9. Timeline
- Hour 0 to 1: this file, repo, `make_mock.py`, everyone installs the environment.
- Hour 1 to 4: each person gets ONE feature (slope) working end to end for their part.
- Hour 4: checkpoint. Everyone pushes real outputs in contract format. App shows real data.
- Hour 4 to 10: remaining features, scoring, uncertainty.
- Before anyone stops for the night: everyone pushes their branch in a working state and runs `scripts/validate_contract.py` on their outputs. Then sleep. No new integration work on little sleep.
- Sunday morning: portfolio, validation, polish. Sunday afternoon: report, slides, demo rehearsal. No new features after 14:00.
