"""Validate a features parquet file against the AGENTS.md section 5 data contract.

Usage: python scripts/validate_contract.py <parquet_path> [--fail-on-mock]
Exit code 1 on any error, 0 when at most warnings/informations are found.
"""
from __future__ import annotations

import argparse
import re
from pathlib import Path

import pandas as pd

IDENTITY_STR_COLS = ["site_id", "name", "body", "role"]
IDENTITY_NUM_COLS = ["lat", "lon", "radius_m"]
FEATURES = [
    "slope_mean",
    "slope_p90",
    "roughness",
    "relief",
    "temp_amplitude",
    "thermal_inertia",
    "albedo",
]
VALID_BODIES = {"moon", "mars", "earth"}
VALID_ROLES = {"reference", "validation", "candidate", "grid"}
ZERO_PLACEHOLDER_FRAC = 0.95
MOCK_SRC = "MOCK"


def _row_tag(df: pd.DataFrame, i: int) -> str:
    """Return a human-readable locator for row i."""
    sid = df["site_id"].iat[i] if "site_id" in df.columns else "?"
    return f"satir {i + 1} (site_id={sid})"


def _as_num(df: pd.DataFrame, col: str) -> pd.Series:
    """Return the column coerced to numeric (NaN on failure)."""
    return pd.to_numeric(df[col], errors="coerce")


def _src_mask(df: pd.DataFrame, col: str) -> pd.Series:
    """Return a bool mask of rows whose src column equals MOCK."""
    if col not in df.columns:
        return pd.Series(False, index=df.index)
    return (df[col].astype("string").fillna("") == MOCK_SRC).fillna(False)


def check_identity(df: pd.DataFrame, path: Path, errors: list[str], warnings: list[str]) -> None:
    """Check identity columns: presence, types, ranges, uniqueness."""
    missing = [c for c in IDENTITY_STR_COLS + IDENTITY_NUM_COLS if c not in df.columns]
    if missing:
        errors.append(f"{path.name}: zorunlu kimlik kolonlari yok: {missing}")
        return
    for col in IDENTITY_STR_COLS:
        bad = [i for i, v in enumerate(df[col].tolist()) if not isinstance(v, str)]
        for i in bad:
            errors.append(f"{path.name}:{col}: {_row_tag(df, i)} string degil veya bos")
        if col in ("body", "role"):
            valid = VALID_BODIES if col == "body" else VALID_ROLES
            for i, v in enumerate(df[col].tolist()):
                if isinstance(v, str) and v not in valid:
                    errors.append(f"{path.name}:{col}: {_row_tag(df, i)} gecersiz deger: '{v}'")
    if "body" in df.columns and df["body"].nunique() > 1:
        errors.append(f"{path.name}:body: tek dosyada birden fazla body var: "
                      f"{sorted(set(df['body'].tolist()))}")
    for col in IDENTITY_NUM_COLS:
        if not pd.api.types.is_numeric_dtype(df[col]):
            errors.append(f"{path.name}:{col}: sayisal kolon bekleniyor, dtype={df[col].dtype}")
        num = _as_num(df, col)
        for i in num.index[num.isna()]:
            errors.append(f"{path.name}:{col}: {_row_tag(df, i)} sayisal degil veya bos")
        if col == "radius_m":
            for i in num.index[num.notna() & (num <= 0)]:
                errors.append(f"{path.name}:{col}: {_row_tag(df, i)} radius_m pozitif olmali")
    lat = _as_num(df, "lat")
    for i in lat.index[lat.notna() & ~lat.between(-90.0, 90.0)]:
        errors.append(f"{path.name}:lat: {_row_tag(df, i)} -90..90 disinda: {lat.iat[i]}")
    lon = _as_num(df, "lon")
    for i in lon.index[lon.notna() & ~lon.between(-180.0, 180.0)]:
        errors.append(f"{path.name}:lon: {_row_tag(df, i)} -180..180 disinda: {lon.iat[i]} "
                      f"(EPSG:4326 konvansiyonu)")
    ids = df["site_id"].tolist()
    dupes = sorted({s for s in ids if isinstance(s, str) and ids.count(s) > 1})
    if dupes:
        errors.append(f"{path.name}:site_id: benzersiz degil: {dupes[:5]}")
    snake = re.compile(r"^[a-z0-9]+(_[a-z0-9]+)*$")
    for i, v in enumerate(ids):
        if isinstance(v, str) and not snake.fullmatch(v):
            warnings.append(f"{path.name}:site_id: {_row_tag(df, i)} snake_case degil: '{v}'")


def check_ranges(df: pd.DataFrame, path: Path, errors: list[str], warnings: list[str]) -> None:
    """Check physical ranges for the numeric feature columns."""
    missing = [f for f in FEATURES if f not in df.columns]
    if missing:
        errors.append(f"{path.name}: ozellik kolonlari yok: {missing}")
    slope_lo = _as_num(df, "slope_mean")
    slope_hi = _as_num(df, "slope_p90")
    pairs = [
        ("albedo", 0.0, 1.0),
        ("slope_mean", 0.0, 90.0),
        ("slope_p90", 0.0, 90.0),
    ]
    nonneg = ["roughness", "relief", "thermal_inertia"]
    for col, lo, hi in pairs:
        if col not in df.columns:
            continue
        num = _as_num(df, col)
        bad = num.notna() & ~num.between(lo, hi)
        for i in num.index[bad]:
            errors.append(f"{path.name}:{col}: {_row_tag(df, i)} {lo}..{hi} disinda: {num.iat[i]}")
    for col in nonneg:
        if col not in df.columns:
            continue
        num = _as_num(df, col)
        for i in num.index[num.notna() & (num < 0)]:
            errors.append(f"{path.name}:{col}: {_row_tag(df, i)} negatif: {num.iat[i]}")
    if "temp_amplitude" in df.columns:
        num = _as_num(df, "temp_amplitude")
        for i in num.index[num.notna() & (num <= 0)]:
            errors.append(f"{path.name}:temp_amplitude: {_row_tag(df, i)} pozitif olmali "
                          f"(kelvin genisligi): {num.iat[i]}")
    if "slope_mean" in df.columns and "slope_p90" in df.columns:
        bad = slope_lo.notna() & slope_hi.notna() & (slope_hi < slope_lo)
        for i in slope_lo.index[bad]:
            warnings.append(f"{path.name}:slope_p90: {_row_tag(df, i)} slope_p90 < slope_mean "
                            f"({slope_hi.iat[i]:.3f} < {slope_lo.iat[i]:.3f})")
    for col in FEATURES:
        if col not in df.columns:
            continue
        filled = _as_num(df, col).dropna()
        if len(filled) > 0 and (filled == 0).mean() >= ZERO_PLACEHOLDER_FRAC:
            warnings.append(f"{path.name}:{col}: dolu degerlerin >=%{ZERO_PLACEHOLDER_FRAC * 100:.0f}'i "
                            f"tam 0 -> 0 yer tutucu olarak kullanilmis olabilir")


def check_feature_meta(df: pd.DataFrame, path: Path, errors: list[str], warnings: list[str]) -> None:
    """Check that every feature X carries X_sd, X_src, X_res_m with sane values."""
    for f in FEATURES:
        if f not in df.columns:
            continue
        vals = _as_num(df, f)
        for suffix in ("sd", "src", "res_m"):
            col = f"{f}_{suffix}"
            if col not in df.columns:
                errors.append(f"{path.name}:{f}: yardimci kolon yok: {col}")
        if f"{f}_sd" in df.columns:
            sd = _as_num(df, f"{f}_sd")
            for i in sd.index[sd.notna() & (sd < 0)]:
                errors.append(f"{path.name}:{f}_sd: {_row_tag(df, i)} negatif: {sd.iat[i]}")
            for i in vals.index[vals.notna() & sd.isna()]:
                errors.append(f"{path.name}:{f}_sd: {_row_tag(df, i)} deger dolu ama sd NaN "
                              f"(belirsizlik olmadan skorlanamaz)")
        if f"{f}_src" in df.columns:
            src = df[f"{f}_src"]
            empty = src.isna() | src.astype("string").fillna("").str.strip().eq("")
            for i in vals.index[vals.notna() & empty]:
                errors.append(f"{path.name}:{f}_src: {_row_tag(df, i)} deger dolu ama kaynak "
                              f"bos (kaynagi olmayan sayi)")
        if f"{f}_res_m" in df.columns:
            res = _as_num(df, f"{f}_res_m")
            if not pd.api.types.is_numeric_dtype(df[f"{f}_res_m"]):
                errors.append(f"{path.name}:{f}_res_m: sayisal kolon bekleniyor")
            for i in res.index[res.isna()]:
                errors.append(f"{path.name}:{f}_res_m: {_row_tag(df, i)} bos")
            for i in res.index[res.notna() & (res <= 0)]:
                errors.append(f"{path.name}:{f}_res_m: {_row_tag(df, i)} pozitif olmali")


def count_mock(df: pd.DataFrame, path: Path) -> tuple[int, dict[str, int]]:
    """Return (rows with any MOCK source, MOCK counts per src column)."""
    src_cols = [c for c in df.columns if c.endswith("_src")]
    per_col = {c: int(_src_mask(df, c).sum()) for c in src_cols}
    any_mask = pd.Series(False, index=df.index)
    for c in src_cols:
        any_mask |= _src_mask(df, c)
    return int(any_mask.sum()), per_col


def validate(path: Path, fail_on_mock: bool = False) -> tuple[list[str], list[str], list[str]]:
    """Run all contract checks on one parquet file; return (errors, warnings, infos)."""
    errors: list[str] = []
    warnings: list[str] = []
    infos: list[str] = []
    try:
        df = pd.read_parquet(path)
    except Exception as exc:  # noqa: BLE001 - any load failure is a contract error
        errors.append(f"{path.name}: dosya yuklenemedi (parquet mi?): {type(exc).__name__}: {exc}")
        return errors, warnings, infos
    if df.empty:
        warnings.append(f"{path.name}: dosya 0 satir")
        return errors, warnings, infos

    check_identity(df, path, errors, warnings)
    check_ranges(df, path, errors, warnings)
    check_feature_meta(df, path, errors, warnings)

    n_mock, per_col = count_mock(df, path)
    for col, n in per_col.items():
        if n:
            infos.append(f"{path.name}:{col}: {n} satir src == MOCK")
    infos.append(f"{path.name}: toplam {n_mock}/{len(df)} satirda en az bir src == MOCK")
    if n_mock > 0:
        if fail_on_mock:
            errors.append(f"{path.name}: {n_mock} satirda MOCK kaynak var "
                          f"(final demodan once sahte veri temizlenmeli)")
        else:
            infos.append(f"{path.name}: MOCK kaynakli satirlar var (gelistirme verisi)")
    m = re.fullmatch(r"features_(moon|mars|earth)\.parquet", path.name)
    if m and "body" in df.columns:
        bodies = set(str(v) for v in df["body"].unique())
        if m.group(1) not in bodies:
            warnings.append(f"{path.name}: dosya adi '{m.group(1)}' imasi veriyor ama body={bodies}")
    return errors, warnings, infos


def main() -> int:
    """Validate one parquet file; exit 1 on errors, 0 otherwise."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("path", type=Path, help="kontrol edilecek parquet dosyasi")
    parser.add_argument("--fail-on-mock", action="store_true",
                        help="tek bir MOCK satiri bile hata say")
    args = parser.parse_args()

    errors, warnings, infos = validate(args.path, fail_on_mock=args.fail_on_mock)
    for line in errors:
        print(f"HATA    {line}")
    for line in warnings:
        print(f"UYARI   {line}")
    for line in infos:
        print(f"BILGI   {line}")
    if errors:
        print(f"SONUC: BASARISIZ - {len(errors)} hata, {len(warnings)} uyari")
        return 1
    print(f"SONUC: GECTI - {len(warnings)} uyari, {len(infos)} bilgi")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
