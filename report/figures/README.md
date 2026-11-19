# figures/

Verified visual evidence and analysis figures generated from `data/processed/features_moon.parquet` (NASA LRO LOLA 5 m DEM + PGDA error maps, LOLA 1000 m broadband albedo) and `data/processed/features_earth.parquet` (ESA Copernicus DEM GLO-30 / NASADEM fallback, NASA MODIS MCD43A3.061, MOD11A2.061, ESA WorldCover + Sentinel-2 L2A), 
## Publication Figures (report & pitch deck)
- `fig01_shackleton_top15_axes.png`: Top 15 Earth sites for Shackleton Crater Rim (`moon_shackleton_rim`) with balanced scores, `P5–P95` Monte Carlo percentile intervals, and Mobility vs Surface axis separation (`Karapınar Meke #1`, `McMurdo #2`, `Hasandağı #3`, `Etna` Mobility `#3`).
- `fig02_mission_reweighting.png`: Slopegraph of rank shifts across Active Mission Profiles (`Balanced -> Rover Mobility -> Radar Calibration`), highlighting `Hasandağı` (`#3 -> #1`) and `Etna` (`#26 -> #17 -> #32`).
- `fig03_moon_regions_heatmap.png`: Multi-region heatmap across all 5 Lunar South Pole reference sites (`Overall`, `Mobility`, `Surface`, and top candidates + validation sites).
- `fig04_physical_space_validation.png`: Two-panel physical space (`slope_mean` vs `albedo` colored by role with Lunar reference markers) alongside pre-registered role-blind rank diagnostics (`Mob #` vs `Surf #`) for all 10 validation sites.
- `fig05_orbital_evidence_gallery.png`: Offline orbital & Earth imagery mosaic combining real `5 m/px` LRO LOLA shaded-relief/hazard tiles (`moon_atlas/`) with real `10 m/px` Sentinel-2 L2A imagery (`earth_atlas/`) and capture metadata.

## Pitch deck figures

`sunum_en/` holds the seven-slide English deck figures (plus `deck_uretici.py`) behind `report/endulus_moon_analogue_scorer.pdf`, the submitted report.

