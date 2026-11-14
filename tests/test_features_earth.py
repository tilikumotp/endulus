"""Comprehensive data integrity and audit test suite for features_earth.parquet (MADDE 1–6)."""

from __future__ import annotations

import csv
import re
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

from scripts.validate_contract import count_mock, validate
from src.earth.sites import VERIFIED_EARTH_SITES

PARQUET_PATH = Path("data/processed/features_earth.parquet")
ARCHIVE_PARQUET_PATH = Path("data/processed/archive/features_earth_20261114.parquet")
DOCS_PATH = Path("docs/data_sources_earth.md")
CONFLICTS_CSV_PATH = Path("lithology_conflicts.csv")

TURKEY_CANDIDATE_IDS = {
    "earth_karacadag_summit",
    "earth_karacadag_ovabag",
    "earth_kula_divlit",
    "earth_tendurek_shield",
    "earth_erciyes_kojugedigi",
    "earth_hasandagi_kecekalecik",
    "earth_acigol_guneydag",
    "earth_cappadocia_kavakkoy",
    "earth_tuz_golu_south",
    "earth_salda_terrace",
}

GLOBAL_CANDIDATE_IDS = {
    "earth_askja_holuhraun",
    "earth_harrat_rahat_madinah",
    "earth_pinacate_el_elegante",
    "earth_puna_campo_piedra_pomez",
    "earth_deccan_mahabaleshwar",
    "earth_harrat_ash_shaam",
    "earth_kilbourne_hole_nm",
    "earth_qaidam_dalangtan",
}

# Geographic bounding boxes (lat_min, lat_max, lon_min, lon_max) for all 28 sites
SITE_REGION_BOUNDS: dict[str, tuple[float, float, float, float]] = {
    "earth_etna_cisternazza": (37.5, 38.0, 14.8, 15.2),
    "earth_atacama_yungay": (-25.0, -23.0, -70.5, -69.5),
    "earth_haughton_crater": (75.0, 75.8, -90.5, -89.0),
    "earth_mauna_loa_hiseas": (19.2, 19.9, -155.8, -155.2),
    "earth_mcmurdo_wright_valley": (-78.0, -77.0, 160.5, 163.0),
    "earth_lanzarote_timanfaya": (28.8, 29.3, -13.9, -13.4),
    "earth_meteor_crater_arizona": (34.8, 35.3, -111.3, -110.8),
    "earth_craters_of_the_moon": (43.1, 43.7, -113.9, -113.2),
    "earth_svalbard_bockfjorden": (79.0, 79.8, 12.5, 14.5),
    "earth_lunar_crater_nevada": (38.0, 38.7, -116.5, -115.7),
    "earth_karacadag_summit": (37.4, 37.9, 39.5, 40.0),
    "earth_karacadag_ovabag": (37.5, 38.0, 39.8, 40.3),
    "earth_kula_divlit": (38.3, 38.8, 28.3, 28.9),
    "earth_tendurek_shield": (39.1, 39.6, 43.6, 44.2),
    "earth_erciyes_kojugedigi": (38.3, 38.7, 35.3, 35.8),
    "earth_hasandagi_kecekalecik": (38.0, 38.4, 33.9, 34.4),
    "earth_acigol_guneydag": (38.3, 38.7, 34.3, 34.8),
    "earth_cappadocia_kavakkoy": (38.4, 38.9, 34.6, 35.1),
    "earth_tuz_golu_south": (38.3, 39.1, 33.2, 33.9),
    "earth_salda_terrace": (37.4, 37.7, 29.5, 29.8),
    "earth_askja_holuhraun": (64.5, 65.2, -17.3, -16.3),
    "earth_harrat_rahat_madinah": (24.0, 24.7, 39.4, 40.2),
    "earth_pinacate_el_elegante": (31.5, 32.1, -113.8, -113.1),
    "earth_puna_campo_piedra_pomez": (-27.0, -26.2, -67.8, -67.1),
    "earth_deccan_mahabaleshwar": (17.6, 18.2, 73.5, 74.1),
    "earth_harrat_ash_shaam": (31.8, 32.6, 36.7, 37.6),
    "earth_kilbourne_hole_nm": (31.7, 32.2, -107.3, -106.7),
    "earth_qaidam_dalangtan": (38.1, 38.9, 91.0, 91.9),
}


@pytest.fixture(scope="module")
def df_earth() -> pd.DataFrame:
    """Load the processed Earth features parquet."""
    assert PARQUET_PATH.exists(), f"Missing {PARQUET_PATH}"
    return pd.read_parquet(PARQUET_PATH)


def test_backup_archive_exists() -> None:
    """Pre-rule: Verify backup parquet exists in data/processed/archive/."""
    assert ARCHIVE_PARQUET_PATH.exists()
    assert ARCHIVE_PARQUET_PATH.stat().st_size > 0


def test_madde1_temp_amplitude_consistency(df_earth: pd.DataFrame) -> None:
    """MADDE 1: Verify single annual MOD11A2.061 definition and |amplitude - (day_mean - night_mean)| < 0.1 K."""
    assert (df_earth["temp_amplitude_src"] == "MOD11A2.061_annual_mean").all()
    assert (df_earth["temp_amplitude_res_m"] == 1000.0).all()
    assert df_earth["temp_amplitude"].notna().all()
    assert df_earth["lst_day_mean_k"].notna().all()
    assert df_earth["lst_night_mean_k"].notna().all()

    diff = (df_earth["temp_amplitude"] - (df_earth["lst_day_mean_k"] - df_earth["lst_night_mean_k"])).abs()
    assert (diff < 0.1).all(), f"Max |amp - (day - night)| = {diff.max():.4f} K >= 0.1 K"


def test_madde2_albedo_source_and_physical_bounds(df_earth: pd.DataFrame) -> None:
    """MADDE 2: Verify real MODIS albedo source, [0, 1] bounds, and basalt vs evaporite separation."""
    assert df_earth["albedo"].notna().all()
    assert ((df_earth["albedo"] >= 0.0) & (df_earth["albedo"] <= 1.0)).all()
    valid_srcs = {"MCD43A3.061", "MCD43A4.061_Liang2001"}
    assert set(df_earth["albedo_src"].unique()).issubset(valid_srcs)
    assert (df_earth["albedo_res_m"] == 500.0).all()

    by_id = df_earth.set_index("site_id")["albedo"]
    # Fresh dark basalts (Askja, Mauna Loa, Etna, Lanzarote, Craters of the Moon, Harrat Rahat)
    for sid in ("earth_askja_holuhraun", "earth_mauna_loa_hiseas", "earth_etna_cisternazza"):
        assert 0.02 <= by_id[sid] <= 0.10, f"Unexpected fresh basalt albedo for {sid}: {by_id[sid]}"

    # Hyperarid evaporite flats (Atacama, Qaidam, Tuz Gölü)
    for sid in ("earth_atacama_yungay", "earth_qaidam_dalangtan", "earth_tuz_golu_south"):
        assert 0.18 <= by_id[sid] <= 0.45, f"Unexpected evaporite albedo for {sid}: {by_id[sid]}"


def test_madde3_no_mock_and_validator_rejects_mock(df_earth: pd.DataFrame, tmp_path: Path) -> None:
    """MADDE 3: Verify 0 MOCK rows in features_earth.parquet and test that MOCK injection triggers error."""
    src_cols = [c for c in df_earth.columns if c.endswith("_src")]
    for col in src_cols:
        n_col_mock = int((df_earth[col].astype(str) == "MOCK").sum())
        assert n_col_mock == 0, f"Found {n_col_mock} MOCK values in {col}"

    n_mock, per_col = count_mock(df_earth, PARQUET_PATH)
    assert n_mock == 0
    assert all(v == 0 for v in per_col.values())

    errors, warnings, infos = validate(PARQUET_PATH, fail_on_mock=True)
    assert errors == []
    assert warnings == []
    assert any("0/28 satirda en az bir src == MOCK" in inf for inf in infos)

    # Inject MOCK into one row and verify validate() flags it as an error/info
    df_mock = df_earth.copy()
    df_mock.loc[0, "albedo_src"] = "MOCK"
    mock_parquet = tmp_path / "features_earth_mock_test.parquet"
    df_mock.to_parquet(mock_parquet, index=False)

    err_strict, _, info_strict = validate(mock_parquet, fail_on_mock=True)
    assert any("1/28 satirda en az bir src == MOCK" in inf for inf in info_strict)
    assert any("MOCK" in e for e in err_strict)

    err_soft, _, info_soft = validate(mock_parquet, fail_on_mock=False)
    assert err_soft == []
    assert any("MOCK kaynakli satirlar var" in inf for inf in info_soft)


def test_madde4_lithology_src_and_conflicts_csv(df_earth: pd.DataFrame) -> None:
    """MADDE 4: Verify non-empty lithology_src column and lithology_conflicts.csv structure."""
    assert "lithology_src" in df_earth.columns
    assert (df_earth["lithology_src"].astype(str).str.strip().str.len() > 10).all()
    assert not (df_earth["lithology_src"].astype(str) == "MOCK").any()

    assert CONFLICTS_CSV_PATH.exists(), "Missing lithology_conflicts.csv"
    with CONFLICTS_CSV_PATH.open(encoding="utf-8") as f:
        reader = csv.DictReader(f)
        assert reader.fieldnames == ["site_id", "mevcut_etiket", "onerilen_etiket", "kaynak"]
        rows = list(reader)
    conflict_ids = {r["site_id"] for r in rows}
    for expected in (
        "earth_tongariro_rangipo",
        "earth_erciyes_kojugedigi",
        "earth_hasandagi_kecekalecik",
        "earth_salda_terrace",
    ):
        assert expected in conflict_ids


def test_madde5_high_uncertainty_flag(df_earth: pd.DataFrame) -> None:
    """MADDE 5: Verify high_uncertainty boolean column matches CV > 0.30 rule without dropping rows."""
    assert len(df_earth) == 28
    assert "high_uncertainty" in df_earth.columns
    assert df_earth["high_uncertainty"].dtype == bool

    cv_temp = df_earth["temp_amplitude_sd"] / df_earth["temp_amplitude"]
    cv_alb = df_earth["albedo_sd"] / df_earth["albedo"]
    expected_flag = (cv_temp > 0.30) | (cv_alb > 0.30)
    assert (df_earth["high_uncertainty"] == expected_flag).all()


def test_madde6_site_counts_invariants_and_cross_table_consistency(df_earth: pd.DataFrame) -> None:
    """MADDE 6: Verify 10 validation + 18 candidate (10 TR + 8 global), physical invariants, and cross-table match."""
    assert len(df_earth) == 28
    assert df_earth["site_id"].is_unique

    val_df = df_earth[df_earth["role"] == "validation"]
    cand_df = df_earth[df_earth["role"] == "candidate"]
    assert len(val_df) == 10
    assert len(cand_df) == 18

    cand_ids = set(cand_df["site_id"])
    assert cand_ids == TURKEY_CANDIDATE_IDS | GLOBAL_CANDIDATE_IDS
    assert len(cand_ids & TURKEY_CANDIDATE_IDS) == 10
    assert len(cand_ids & GLOBAL_CANDIDATE_IDS) == 8

    # Physical invariants
    assert (df_earth["slope_p90"] >= df_earth["slope_mean"]).all()
    assert (df_earth["relief"] >= 0.0).all()
    assert (df_earth["roughness"] >= 0.0).all()
    assert ((df_earth["albedo"] >= 0.0) & (df_earth["albedo"] <= 1.0)).all()

    # Cross-table consistency: parquet vs sites.py vs docs/data_sources_earth.md
    sites_py_ids = [s["site_id"] for s in VERIFIED_EARTH_SITES]
    assert list(df_earth["site_id"]) == sites_py_ids

    md_text = DOCS_PATH.read_text(encoding="utf-8")
    md_ids = re.findall(r"\|\s*\d+\s*\|\s*`(earth_[a-z0-9_]+)`\s*\|", md_text)
    assert md_ids == sites_py_ids

    # Coordinate bounding-box verification for all 28 sites
    for _, row in df_earth.iterrows():
        sid = row["site_id"]
        assert sid in SITE_REGION_BOUNDS, f"Missing region bounds for {sid}"
        lat_min, lat_max, lon_min, lon_max = SITE_REGION_BOUNDS[sid]
        assert lat_min <= row["lat"] <= lat_max, f"{sid} lat={row['lat']} outside [{lat_min}, {lat_max}]"
        assert lon_min <= row["lon"] <= lon_max, f"{sid} lon={row['lon']} outside [{lon_min}, {lon_max}]"


def test_satellite_thumbnails_and_zip(df_earth: pd.DataFrame) -> None:
    """Extra deliverable: Verify 28 5x5 km Sentinel-2 RGB thumbnails, metadata JSONs, and zip archive."""
    thumbs_dir = Path("outputs/satellite_thumbs")
    zip_path = Path("outputs/satellite_thumbs.zip")
    assert thumbs_dir.exists()
    assert zip_path.exists() and zip_path.stat().st_size > 1_000_000

    for sid in df_earth["site_id"]:
        png_p = thumbs_dir / f"{sid}.png"
        meta_p = thumbs_dir / f"{sid}_meta.json"
        assert png_p.exists() and png_p.stat().st_size > 1000, f"Missing/empty thumbnail {png_p}"
        assert meta_p.exists() and meta_p.stat().st_size > 50, f"Missing/empty metadata {meta_p}"
