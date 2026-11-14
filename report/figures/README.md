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

- `25_title_map_tr_clean.jpeg`: Revised title and framing ("Ay ↔ Dünya
  Benzer Koşullar Analizi"; all Mars references removed), plain subtitle
  explaining exactly what the app does, portfolio tab removed, role filter
  removed, continent-based region filter (Asia / Europe / Africa / Americas
  / Oceania / Antarctica) and split map captions (dot size & colour vs
  blue-ringed known analogues).

- `26_validation_new_chart_table.jpeg`: Redesigned validation tab: simple
  one-bar-per-criterion summary chart (count of known analogues reaching
  the top 5 out of 10 comparisons per criterion, labels on bars) plus a
  plain-language table with Saha / Ölçüt / Sıralama / Değerlendirme columns.

- `27_3d_terrain_stub.jpeg`: New "3D Arazi" tab: side-by-side Plotly 3D
  surfaces (left Moon reference, right selected Earth site) coloured by
  hillshade (NW light, 45° altitude), with an honest vertical-exaggeration
  slider (1×–4×, default 2×, "Dikey ölçek abartılı gösteriliyor" note), a
  0–360° camera orbit slider and an r=1 km measurement ring. Until the real
  DEM tiles land (M6/E7), each card uses generated sample terrain shaped by
  the site's own measured slope/roughness/relief statistics and is labelled
  "Örnek arazi verisi" with its stats source + resolution + window in one
  line; cards switch to real tiles automatically when
  `data/processed/dem_tiles/{site_id}.npz` appears.
