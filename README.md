# Moon/Mars Analogue Scorer — NASA Space Apps 2026

No place on Earth analogues a Moon base or Mars site in every respect. We score
Earth sites **per axis** (mobility, thermal, surface), attach uncertainty to
every score, show *where the analogy breaks down*, and recommend a minimal
portfolio of Earth test sites. Known analogues (Atacama, Etna/Mauna Loa,
Haughton) validate the method; lesser-studied places are candidates, never
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
data/raw/            big downloads (gitignored; never commit)
data/mock/           mock parquet files from scripts/make_mock.py
data/processed/      real feature parquets (committed; the data contract)
scripts/             make_mock.py, validate_contract.py
src/moon_mars/       Person 2: Moon/Mars feature extraction
src/earth/           Person 3: Earth features + candidate curation
src/scoring/         Leader: similarity, uncertainty, portfolio, validation
app/                 Person 4: Streamlit app
report/              Person 4: written report, figures
```

Each person works in their own folder on their own branch; only the leader
merges to `main`.

## Mock data

```bash
python scripts/make_mock.py [--out data/mock]
```

Writes `features_moon.parquet` (5 ref), `features_mars.parquet` (3 ref),
`features_earth.parquet` (10 validation + 30 candidate) matching the contract,
with fixed seed. **scripts/make_mock.py yalnızca geliştirme sırasında arayüzü
veri gelmeden test etmek içindir; sunulan sonuçlar gerçek veriyle
üretilmiştir.**

## Contract validation

```bash
python scripts/validate_contract.py data/processed/features_moon.parquet
python scripts/validate_contract.py data/processed/features_earth.parquet --fail-on-mock
```

`--fail-on-mock` turns any `*_src == "MOCK"` row into a hard error — run it on
real outputs right before the final demo. Exit code 1 on errors, 0 otherwise.
