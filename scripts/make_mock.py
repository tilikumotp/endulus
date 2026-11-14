"""Generate mock parquet files that follow the AGENTS.md section 5 data contract.

Usage: python scripts/make_mock.py [--out DIR]  (default: data/mock/)
Every feature value carries *_sd, *_src ("MOCK") and *_res_m; all names and
coordinates are explicitly fake.
"""
from __future__ import annotations

import argparse
from pathlib import Path

import numpy as np
import pandas as pd

REPO_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_OUT = REPO_ROOT / "data" / "mock"
SEED = 42
MOCK_SRC = "MOCK"
DEFAULT_RADIUS_M = 1000.0

IDENTITY_COLS = ["site_id", "name", "body", "role", "lat", "lon", "radius_m"]
FEATURES = [
    "slope_mean",
    "slope_p90",
    "roughness",
    "relief",
    "temp_amplitude",
    "thermal_inertia",
    "albedo",
]
# Mock native resolutions (m): DEM-like features fine, thermal/radiometric coarse.
RES_M = {
    "slope_mean": 50.0,
    "slope_p90": 50.0,
    "roughness": 50.0,
    "relief": 50.0,
    "temp_amplitude": 500.0,
    "thermal_inertia": 100.0,
    "albedo": 500.0,
}
LITHOLOGY_CLASSES = ["basalt", "regolith", "evaporite", "sediment", "dust-mantle"]

N_MOON_REF = 5
N_MARS_REF = 3
N_EARTH_VAL = 10
N_EARTH_CAND = 27
N_EARTH_SIMILAR = 3
EARTH_TI_NAN_FRAC = 0.20  # ~20% of Earth sites lack thermal_inertia


def _ordered_columns() -> list[str]:
    """Return the full column list in contract display order."""
    cols = list(IDENTITY_COLS)
    for f in FEATURES:
        cols += [f, f"{f}_sd", f"{f}_src", f"{f}_res_m"]
    cols += ["lithology_class", "lithology_class_src"]
    return cols


def _draw_features(rng: np.random.Generator, n: int) -> dict[str, np.ndarray]:
    """Draw physically plausible feature values for n sites."""
    slope_mean = rng.uniform(0.0, 25.0, n)
    slope_p90 = np.minimum(slope_mean + rng.uniform(2.0, 30.0, n), 90.0)
    return {
        "slope_mean": slope_mean,
        "slope_p90": slope_p90,
        "roughness": rng.uniform(0.5, 50.0, n),
        "relief": rng.uniform(5.0, 500.0, n),
        "temp_amplitude": rng.uniform(1.0, 300.0, n),
        "thermal_inertia": rng.uniform(50.0, 3000.0, n),
        "albedo": rng.uniform(0.05, 0.5, n),
    }


def _make_frame(
    rng: np.random.Generator,
    body: str,
    role: str,
    prefix: str,
    n: int,
    lat_lo: float,
    lat_hi: float,
) -> pd.DataFrame:
    """Build one mock table: identity columns plus features, no meta yet."""
    feats = _draw_features(rng, n)
    df = pd.DataFrame(feats)
    df.insert(0, "site_id", [f"{prefix}_{i:02d}" for i in range(1, n + 1)])
    label = {"moon": "Moon", "mars": "Mars", "earth": "Earth"}[body]
    df.insert(1, "name", [f"MOCK {label} {role.title()} {i:02d}" for i in range(1, n + 1)])
    df.insert(2, "body", body)
    df.insert(3, "role", role)
    df.insert(4, "lat", rng.uniform(lat_lo, lat_hi, n))
    df.insert(5, "lon", rng.uniform(-180.0, 180.0, n))
    df.insert(6, "radius_m", DEFAULT_RADIUS_M)
    return df


def _add_feature_meta(df: pd.DataFrame, rng: np.random.Generator) -> None:
    """Append X_sd (5-20% of X), X_src and X_res_m for every feature."""
    for f in FEATURES:
        vals = df[f].to_numpy(dtype=float)
        # NaN value -> NaN sd and empty src (uncertainty only defined for real values).
        df[f"{f}_sd"] = vals * rng.uniform(0.05, 0.20, len(vals))
        df[f"{f}_src"] = np.where(np.isnan(vals), None, MOCK_SRC)
        df[f"{f}_res_m"] = RES_M[f]
    if "lithology_class" not in df.columns:
        df["lithology_class"] = None
    # Existing (non-null) lithology values are kept; the rest get a draw.
    draws = pd.Series(rng.choice(LITHOLOGY_CLASSES, len(df)), index=df.index)
    df["lithology_class"] = df["lithology_class"].fillna(draws)
    df["lithology_class_src"] = MOCK_SRC


def make_moon(rng: np.random.Generator) -> pd.DataFrame:
    """Create the 5 mock Moon reference sites (south-pole latitude band)."""
    return _make_frame(rng, "moon", "reference", "mock_moon_ref", N_MOON_REF, -90.0, -80.0)


def make_mars(rng: np.random.Generator) -> pd.DataFrame:
    """Create the 3 mock Mars reference sites."""
    return _make_frame(rng, "mars", "reference", "mock_mars_ref", N_MARS_REF, -60.0, 60.0)


def make_earth(rng: np.random.Generator, moon_ref: pd.Series) -> pd.DataFrame:
    """Create 10 validation + 30 candidate Earth sites, 3 tuned near a Moon ref."""
    df = pd.concat(
        [
            _make_frame(rng, "earth", "validation", "mock_earth_val", N_EARTH_VAL, -60.0, 60.0),
            _make_frame(rng, "earth", "candidate", "mock_earth_cand", N_EARTH_CAND, -60.0, 60.0),
        ],
        ignore_index=True,
    )
    # ~20% of Earth sites have no thermal_inertia (value, sd and src all empty).
    ti_nan = rng.random(len(df)) < EARTH_TI_NAN_FRAC
    df.loc[ti_nan, "thermal_inertia"] = np.nan

    similar_rows = []
    for i in range(1, N_EARTH_SIMILAR + 1):
        row = {
            "site_id": f"mock_earth_similar_{i:02d}",
            "name": f"MOCK Earth Similar {i:02d}",
            "body": "earth",
            "role": "candidate",
            "lat": float(rng.uniform(-60.0, 60.0)),
            "lon": float(rng.uniform(-180.0, 180.0)),
            "radius_m": DEFAULT_RADIUS_M,
            "lithology_class": moon_ref["lithology_class"],
        }
        for f in FEATURES:
            base = float(moon_ref[f])
            row[f] = base * (1.0 + float(rng.uniform(-0.05, 0.05)))
        similar_rows.append(row)
    df = pd.concat([df, pd.DataFrame(similar_rows)], ignore_index=True)
    return df


def _print_summary(out_dir: Path, written: dict[str, pd.DataFrame]) -> None:
    """Print row counts, roles, columns and per-feature ranges for sanity."""
    print(f"\n== OZET ==  {len(written)} dosya yazildi -> {out_dir}")
    for body, df in written.items():
        roles = df["role"].value_counts().to_dict()
        print(f"- features_{body}.parquet: {len(df)} satir, role: {roles}")
    print(f"Kolonlar ({len(written['moon'].columns)}): {_ordered_columns()}")
    print("Ozellik araliklari (min..max, tum dosyalar):")
    all_df = pd.concat(written.values(), ignore_index=True)
    for f in FEATURES:
        vals = all_df[f].dropna()
        print(f"  {f:18s} {vals.min():10.3f} .. {vals.max():10.3f}"
              f"  (NaN: {int(all_df[f].isna().sum())})")


def main() -> int:
    """Generate the three mock parquet files and print a summary."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", default=str(DEFAULT_OUT),
                        help="output directory (default: data/mock/)")
    args = parser.parse_args()
    out_dir = Path(args.out)
    out_dir.mkdir(parents=True, exist_ok=True)

    rng = np.random.default_rng(SEED)
    moon = make_moon(rng)
    _add_feature_meta(moon, rng)
    mars = make_mars(rng)
    _add_feature_meta(mars, rng)
    earth = make_earth(rng, moon.iloc[0])
    _add_feature_meta(earth, rng)
    written = {"moon": moon, "mars": mars, "earth": earth}
    for body, df in written.items():
        cols = [c for c in _ordered_columns() if c in df.columns]
        path = out_dir / f"features_{body}.parquet"
        df[cols].to_parquet(path)
        print(f"yazıldı: {path}")
    _print_summary(out_dir, written)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
