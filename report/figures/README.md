# figures/

Verified application screenshots running on `data/processed/features_moon.parquet`
(NASA LRO LOLA 5 m DEM, Diviner 240 m TBOL, LOLA 1000 m broadband albedo) and
`data/processed/features_earth.parquet` (ESA Copernicus DEM GLO-30, NASA Terra
MODIS MOD11A2.061, NASA MODIS MCD43A3.061).

- `23_real_moon_earth_visual_panel_shackleton.jpeg`: Three-panel Visual &
  Topographic Context Inspector showing Shackleton Crater Rim (`moon_shackleton_rim`,
  Site 04 ROI: LRO WAC orthomosaic with dark PSR floor and illuminated rim +
  LOLA shaded relief via USGS Astrogeology WMS) alongside McMurdo Dry Valleys
  (`earth_mcmurdo_wright_valley`, Esri World Imagery) and quantitative per-axis
  similarity indices with 5th–95th Monte Carlo uncertainty percentiles
  (not confidence intervals).

- `24_i18n_tr_default_clean_ui.jpeg`: Plain-language (i18n) pass, Turkish
  default view. Every user-visible string lives in `app/i18n.py` (TR default
  + English toggle in the sidebar); developer jargon (module/function names,
  internal-doc references) is removed from the screen; the reference-site
  label reads "Referans saha (Ay'dan)", measurements use readable Turkish
  column headers, and the score table gains ground-type (lithology) and
  region (Türkiye / other) filters. English view verified manually across
  all tabs.
