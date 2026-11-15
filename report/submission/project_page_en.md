# NASA Space Apps 2026 – Project Page Text (copy/paste, English)

> Copy each section into the matching field on the Space Apps Project page.
> Fill `TODO` items before submitting.

---

## Project Name

**Moon Analogue Scorer**

---

## High-Level Project Summary

No single place on Earth matches a Moon base site in every respect, so ranking Earth analogs with one overall "similarity score" hides exactly what mission planners need to know. We built an open, interactive tool that compares 5 Lunar South Pole reference regions (Shackleton rim first) with 40 curated Earth sites (10 well-known analogs used as a diagnostic, 30 candidates) axis by axis: mobility (slope, roughness, relief) and surface (albedo), each with Monte Carlo uncertainty. For every site the app shows where the analogy breaks down (1/6 g, vacuum, radiation, 29.5-day lunar day; thermal scoring is kept non-numeric in v1 due to non-equivalent lunar/Earth definitions), lets the user re-weight the axes for a mission (balanced, rover mobility test, optical surface survey), and recommends a compact portfolio of Earth test sites that together cover the most axes. All numbers come from orbital data (NASA LRO LOLA, NASA MODIS, NASADEM, ESA Copernicus DEM) with their source and resolution attached. This helps agencies and teams choose cheaper, better-justified Earth test sites before sending hardware to the Moon.

---

## Link to Project Demo

https://github.com/tilikumotp/endulus/blob/main/report/nasa_submission_7slides.pptx

(7-slide English deck; opens anonymously, verified without login.)

## Link to Final Project

- Live web app: https://tilikumotp.github.io/endulus/
- Source code, data and documentation: https://github.com/tilikumotp/endulus

---

## Detailed Project Description

**What it does.**
The tool answers: *"Which Earth sites can we use to test equipment for a permanent base at the lunar south pole, for which purpose, and how sure are we?"* Instead of one overall score, it reports a separate similarity score per physical axis, each with an uncertainty band, and explicitly states which conditions Earth cannot reproduce.

**How it works.**
1. **Same feature definitions on both bodies.** For every site we compute, inside the same 1 km analysis radius and in a projected metric CRS (polar stereographic for the Moon, local UTM/UPS for Earth): mean slope, 90th-percentile slope, roughness (std of detrended elevation), relief and broadband albedo. Every value carries its uncertainty (`_sd`), its source product (`_src`) and its native resolution (`_res_m`).
2. **Moon reference regions.** 5 Lunar South Pole regions from NASA LRO LOLA 5 m/px PGDA DEMs (Barker et al., 2021) and LOLA 1064 nm albedo (scaled to broadband; the scaling factor is shown with a sensitivity analysis).
3. **Earth sites.** 40 sites from Copernicus DEM GLO-30 (NASADEM as fallback for one tile) and NASA MODIS MCD43A3 albedo; 10 literature-documented analogs (e.g. Etna, Atacama, Haughton, Mauna Loa, Meteor Crater, McMurdo Dry Valleys, Lanzarote, Lunar Crater Nevada) and 30 candidates, including Anatolian volcanic and evaporite sites. Candidates are presented as candidates, never as confirmed analogs.
4. **Scoring with uncertainty.** Features are standardized; per-axis similarity is `exp(-D)` of the standardized distance (a similarity index, not a probability). 200 Monte Carlo draws from each feature's uncertainty give a 5–95 % interval for every score.
5. **Mission reweighting and portfolio.** A mission selector (balanced / rover mobility / optical surface survey) re-weights the axes; a portfolio routine finds the smallest set of Earth sites that covers the most axes above a stated threshold, and lists which axes remain uncovered (to be handled in the lab or by simulation).
6. **Honest validation.** When run blind, known analogs rank high on the axes they are known for (e.g. Mount Etna #3/40 and Meteor Crater #8/40 on mobility, McMurdo Dry Valleys #2/40 on surface for the Shackleton rim). Because all sites share the standardization, we present this as a descriptive rank diagnostic, not as an independent holdout test.
7. **Transparency about limits.** The thermal axis is deliberately suspended in v1: lunar Diviner polar temperatures (29.5-day cycle, vacuum) and Earth MODIS day–night differences are not equivalent definitions, so we do not mix them into a number. Gravity, vacuum, radiation and regolith properties are shown as "Earth cannot reproduce" limits.

**Benefits.** Cheaper and better-justified analog campaigns; clear mapping from each Earth site to a concrete test (e.g. rover mobility on steep volcanic slopes); visible uncertainty; reproducible open pipeline with automated data-contract validation and unit tests.

**What we hope to achieve.** A reusable, open screening tool that agencies, universities and rover teams can extend to Mars reference sites and to more Earth candidates, so that analog testing is chosen by evidence rather than by habit.

**Tools.** Python 3.11 (numpy, pandas, geopandas, rasterio, xarray, scipy, scikit-learn, pyarrow), Streamlit + pydeck/plotly app, React + Vite + TypeScript + Leaflet web observatory with 3D DEM viewer, pytest, GitHub Actions / GitHub Pages.

---

## Use of Super Intelligence (SI)  *(data collection only, not shown to judges)*

Yes. AI coding assistants were used to speed up writing and refactoring code (data-processing scripts, the web/Streamlit app, tests), drafting documentation and translating text between Turkish and English. The idea, methodology, site selection, scoring decisions and validation were designed by the team. Every number in the project comes from documented orbital data products; AI was not used to generate data, coordinates or citations, and all generated code was reviewed and tested by the team (data-contract validation + pytest). No AI-generated images, video or audio are used in the project.

---

## NASA Data

- **NASA LRO LOLA – PGDA Product 78, 5 m/px south-pole DEMs and error maps (v2021)** – slope, roughness, relief for the 5 lunar reference regions (Barker et al., 2021, doi:10.1016/j.pss.2020.105119).
- **NASA LRO LOLA GDR LDAM 1064 nm normal albedo (LRO-L-LOLA-4-GDR-V1.0)** – lunar surface albedo (Lucey et al., 2014; Lemelin et al., 2016).
- **NASA LRO Diviner (LRO-L-DLRE-5-PCP-V1.0)** – lunar polar temperature context; used to justify suspending the thermal axis in v1.
- **NASA MODIS MCD43A3 v061 (LP DAAC)** – Earth broadband albedo for all 40 sites.
- **NASA MODIS MOD11A2 v061 (LP DAAC)** – Earth land-surface temperature, recorded but not scored in v1.
- **NASADEM_HGT v001 (LP DAAC)** – Earth elevation fallback where Copernicus GLO-30 is unavailable.
- NASA Earthdata search / CMR used for data discovery.

---

## Space Agency Partner & Other Data, Resources and References

**Space agency partner data**
- **ESA / Copernicus DEM GLO-30** (30 m) – primary Earth elevation source (39 of 40 sites).
- **ESA Copernicus Sentinel-2 L2A** (10 m) – cloud-free visual context images in the app.
- **ESA WorldCover v200** – mixed-pixel land-cover check.

**Data access:** AWS Open Data, Microsoft Planetary Computer STAC, NASA Earthdata / LP DAAC, NASA GSFC PGDA.

**Key references** (full list with DOIs in `docs/data_sources.md`, `docs/validation_expectations.md`)
- Barker et al. (2021) Planet. Space Sci. 203, 105119 – LOLA south-pole DEMs.
- Lucey et al. (2014) JGR Planets 119, 1665–1679; Lemelin et al. (2016) Icarus 273, 315–328 – LOLA albedo.
- Zuber et al. (2012) Nature 486, 378–381 – Shackleton crater.
- Paige et al. (2010) Science 330, 479–482; Williams et al. (2019) JGR Planets 124; Hayne et al. (2017) JGR Planets 122 – Diviner temperatures.
- Liang (2001) – broadband albedo conversion.
- Analog literature: Schuster et al. (2020) (Etna); Wettergreen et al. (2005), McKay et al. (2003) (Atacama); Lee & Osinski (2005) (Haughton); Shiro et al. (2022) (Mauna Loa); Marchant & Head (2007) (McMurdo); Sauro et al. (2020, 2023) (Lanzarote); Kring (2007) (Meteor Crater); Hughes et al. (2019) (Craters of the Moon); Evans et al. (1992) (Lunar Crater, Nevada).

**Open-source software:** numpy, pandas, geopandas, rasterio, xarray, scipy, scikit-learn, pyarrow, Streamlit, pydeck, plotly, React, Vite, Leaflet, Tailwind CSS, d3-geo, world-atlas / topojson (Natural Earth).

---

## Pre-submission checklist (from the official guide)

- [ ] All team members are confirmed at the same Local Event.
- [ ] Every required field filled, everything in English.
- [ ] Demo link and final project link open in a private/incognito window with no login.
- [ ] Demo ≤ 7 slides, English, shows team name, member names, challenge name.
- [ ] No images/video/audio of anyone under 18; no NASA logos or branding.
- [ ] Tick "Terms and Conditions" and "Confirm All Work is Original", then **Submit for Judging** before **Sunday Nov 15, 23:59 local time**.
- [ ] Check the confirmation banner; download the participant certificate from Profile.
