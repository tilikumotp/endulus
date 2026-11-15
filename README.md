# Moon/Mars Analogue Scorer — NASA Space Apps 2026

No place on Earth analogues a Moon base or Mars site in every respect. We score
Earth sites **per axis** (mobility, thermal, surface), attach uncertainty to
every score, show *where the analogy breaks down*, and recommend a minimal
portfolio of Earth test sites. Known analogues (Atacama, Etna/Mauna Loa,
Haughton) provide a descriptive rank diagnostic, not a holdout validation;
lesser-studied places are candidates, never
confirmed analogues. Deliverables: interactive map app, short report, pitch.
Full team rules: see **[AGENTS.md](AGENTS.md)** (data contract in section 5).

## Setup

```bash
python -m venv .venv
.venv\Scripts\activate        # Windows (bash: source .venv/bin/activate)
pip install -r requirements.txt
```

Python 3.11+.

## Repo layout

```
data/raw/            raw orbital downloads (gitignored; never commit)
data/processed/      verified feature parquets (committed; the data contract)
scripts/             validate_contract.py, validate_all.py
src/moon_mars/       Person 2: Lunar South Pole feature extraction (LRO LOLA / Diviner)
src/earth/           Person 3: Earth features + candidate curation (Copernicus GLO-30 / MODIS)
src/scoring/         Leader: similarity, uncertainty, portfolio, validation
app/                 Person 4: Streamlit application
web/                 React + Vite interactive observatory (Leaflet GIS + 3D DEM)
report/              Person 4: written report, figures, demo & slide outlines
```

Each person works in their own folder on their own branch; only the leader
merges to `main`.

## Running the Web Observatory (React / Vite)

Requires Node.js 18+.

```bash
git pull origin main
cd web
npm install
npm run dev          # opens http://127.0.0.1:5173
```

To test the production build locally:

```bash
cd web
npm run build
npm run preview      # serves dist/ at http://127.0.0.1:4173
```

To regenerate static JSON/figure assets from `data/processed/`:

```bash
python web/scripts/export_web_data.py
```

## Running the Streamlit application

```bash
streamlit run app/main.py
```

## Contract validation & tests

```bash
python scripts/validate_all.py --fail-on-mock
python scripts/validate_contract.py data/processed/features_moon.parquet --fail-on-mock
python scripts/validate_contract.py data/processed/features_earth.parquet --fail-on-mock
pytest
```

`--fail-on-mock` verifies that all committed parquets contain only documented orbital instrument observations with zero synthetic rows. Exit code 1 on errors, 0 otherwise.
