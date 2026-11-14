# Live Demo Walkthrough (Person 4, Jury Presentation — v1 Final)

**Pre-demo checklist (do NOT skip):**
- Verified `data/processed/` parquets and local assets loaded (`python scripts/validate_all.py --fail-on-mock` → 0 errors, 0 warnings).
- Streamlit running: `streamlit run app/main.py` (default language: Turkish; instant English switch in sidebar).
- Default Moon reference selected: **Shackleton Krateri Kenarı / Shackleton Crater Rim** (`moon_shackleton_rim`).

---

## Step 1 — The Problem, Scope & Decision #30 Transparency
- Open on the **title + `🗺️ Harita` tab**:
  - Highlight the 5 NASA Artemis III Lunar South Pole reference regions and 40 curated Earth sites (10 validation + 30 candidates).
  - Point to the **Decision #30 (`Karar #30`) banner**: explain that v1 numeric scoring runs on **2 active numeric axes (`Mobility + Surface`)** while the **`Thermal` axis is suspended (`NaN`)** because lunar LRO Diviner polar `ltim` local-time slices and Earth `MOD11A2.061` annual-mean day–night ΔT do not share an equivalent diurnal definition.
  - Show that both validation sites (blue ring, `color_val`) and candidate sites (`color`) encode the mission-weighted similarity score in dot colour and radius.

## Step 2 — Visual Comparison (`📊 Görsel Karşılaştırma & Eksenler`) & 3D Terrain (`⛰️ 3D Arazi`)
- Switch to **`📊 Görsel Karşılaştırma & Eksenler`**:
  - Show the **2D Physical Feature Space scatter (`slope_mean` vs `albedo`)** with all 40 Earth sites and the gold star ⭐ for the selected Moon reference.
  - Walk the horizontal per-axis bar cards (`Mobility`, `Surface`, `Overall`) with `expanded_interval` Monte Carlo uncertainty bands and explicit `Thermal: Suspended (NaN)` status.
- Switch to **`⛰️ 3D Arazi`**:
  - Show the side-by-side interactive Plotly 3D hillshade surfaces built offline from committed `5 m/px` LRO LOLA (`data/processed/moon_3d/`) and `30 m/px` Copernicus GLO-30 (`data/processed/earth_3d_grids.npz`) elevation grids, with the `r = 1 km` measurement ring, `1×–4×` vertical exaggeration slider, and `0–360°` camera orbit.

## Step 3 — Score Table & Compact Multi-Site Portfolio Card (`📊 Skor Tablosu & Portföy`)
- Open **`📊 Skor Tablosu & Portföy`**:
  - Show the filterable 40-site score table (`Overall`, `Mobility`, `Surface` with `expanded_interval` bounds; dead `Thermal` column removed with clear note).
  - Scroll to the **Compact Portfolio Card (`select_portfolio`)** right below the table:
    - For Shackleton Rim (`Balanced`), **Karapınar Meke Maar (`0.53`, Surface `0.90 >= 0.70`)** covers `Surface`, while `Mobility` (led across all 40 sites by **Hasan Dağı** at `0.335`) and suspended `Thermal` (`NaN`) are routed to targeted steep-slope trials and lab/simulation.
    - Point out the explicit `0.70` heuristic threshold caveat.

## Step 4 — Descriptive Rank Diagnostic (`✅ Betimsel Sıra Tanısı`)
- Open **`✅ Betimsel Sıra Tanısı`**:
  - Emphasize that all 40 Earth sites participate in Z-standardization, so this screen is a **descriptive rank diagnostic (`betimsel sıra tanısı`), not an independent holdout pass/fail test**.
  - Walk the **10-row single table** (`docs/validation_expectations.md`): pre-registered expected axes (`Confirmed` / `Candidate`), raw blind ranks (`/40`) on **Mobility** and **Surface** (`Thermal: Suspended / NaN`), E8 qualitative ice/permafrost status, single-sentence rationale, and verified DOIs/URLs (e.g., **Mount Etna `Mobility #3/40`**, **Lunar Crater Nevada `Mobility #7/40`**, **Meteor Crater `Mobility #8/40`**, **McMurdo Dry Valleys `Surface #2/40`**).

## Step 5 — Limits of the Analogy, 8-Dimension Scorecard & Local Orbital Evidence (`⚠️ Analojinin Sınırları`)
- Open **`⚠️ Analojinin Sınırları`**:
  - Walk the physical limits (`1/6 g`, vacuum, radiation, `29.5`-day synodic cycle) and technical limits (`5 m/px` LOLA vs `30 m/px` GLO-30 DEM scale difference, `Karar #30` suspended thermal axis).
  - Show the **8-Dimension Challenge Scorecard** (`Numeric Active`, `Suspended in v1`, `Qualitative`, `Field-Independent Lab/Simulation`).
  - Inspect a site in the **Verified Orbital Visual & Topographic Evidence Card** (`LRO LOLA 5 m/px` hillshade & slope classes beside cloudless `Sentinel-2 L2A 10 m/px` imagery with `collection`, `scene_id`, `acquisition_date`, `local_cloud_pct`) and the standardized feature-gap table (`axis_gaps`).
