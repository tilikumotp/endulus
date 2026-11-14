"""Run validate_contract on every features_*.parquet under data/processed.

Usage: python scripts/validate_all.py [--include-mock] [--fail-on-mock]
Exit code 1 if any checked file has contract errors, 0 otherwise.
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(Path(__file__).resolve().parent))

from validate_contract import validate  # noqa: E402


def _check_dir(directory: Path, fail_on_mock: bool) -> tuple[int, int]:
    """Validate all parquet files in one directory; return (files, errors)."""
    files, error_total = 0, 0
    for path in sorted(directory.glob("features_*.parquet")):
        files += 1
        errors, warnings, infos = validate(path, fail_on_mock=fail_on_mock)
        for line in errors:
            print(f"HATA    {line}")
        for line in warnings:
            print(f"UYARI   {line}")
        for line in infos:
            print(f"BILGI   {line}")
        error_total += len(errors)
        status = "GECTI" if not errors else "BASARISIZ"
        print(f"-> {path.relative_to(REPO_ROOT)}: {status} "
              f"({len(errors)} hata, {len(warnings)} uyari)")
    return files, error_total


def main() -> int:
    """Validate all real (and optionally mock) outputs; exit 1 on any error."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--include-mock", action="store_true",
                        help="data/mock altindaki dosyalari da kontrol et")
    parser.add_argument("--fail-on-mock", action="store_true",
                        help="tek bir MOCK satiri bile hata say (final demodan once)")
    args = parser.parse_args()

    total_files, total_errors = 0, 0
    processed = REPO_ROOT / "data" / "processed"
    if not any(processed.glob("features_*.parquet")):
        print(f"BILGI   {processed.relative_to(REPO_ROOT)} altinda features_*.parquet yok "
              f"(gercek cikti henuz gelmedi)")
    files, errors = _check_dir(processed, args.fail_on_mock)
    total_files, total_errors = total_files + files, total_errors + errors
    if args.include_mock:
        files, errors = _check_dir(REPO_ROOT / "data" / "mock", args.fail_on_mock)
        total_files, total_errors = total_files + files, total_errors + errors

    if total_files == 0:
        print("SONUC: kontrol edilecek dosya yok")
        return 0
    verdict = "GECTI" if total_errors == 0 else "BASARISIZ"
    print(f"SONUC: {verdict} - {total_files} dosya, {total_errors} hata")
    return 1 if total_errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
