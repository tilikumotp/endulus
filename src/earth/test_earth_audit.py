"""Audit and AGENTS.md §5 contract verification tests for the 40-site Earth dataset."""

from __future__ import annotations

import json
import re
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

from scripts.validate_contract import count_mock, validate
from src.earth.dem_pipeline import (
    CONTRACT_COLS,
    COPERNICUS_DEM_SRC,
    NASADEM_DEM_SRC,
    get_dem_source,
)
from src.earth.mixed_pixel import (
    MADDE3_AUDITED_RECORDS,
    build_diagnostic_rows,
    classify_mixed_pixel,
)
from src.earth.modis_pipeline import _make_retrying_session
from src.earth.sites import VERIFIED_EARTH_SITES

PARQUET_PATH = Path("data/processed/features_earth.parquet")
DOCS_PATH = Path("docs/data_sources_earth.md")
RAW_EARTH_DIR = Path("data/raw/earth")

EXPECTED_VALIDATION_IDS = {
    "earth_etna_cisternazza",
    "earth_atacama_yungay",
    "earth_haughton_crater",
    "earth_mauna_loa_hiseas",
    "earth_mcmurdo_wright_valley",
    "earth_lanzarote_timanfaya",
    "earth_meteor_crater_arizona",
    "earth_craters_of_the_moon",
    "earth_svalbard_bockfjorden",
    "earth_lunar_crater_nevada",
}

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
    "earth_karapinar_meke",
    "earth_suphan_south_apron",
    "earth_nemrut_caldera_flank",
    "earth_agri_dogubayazit_flow",
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
    "earth_payunia_pampa_negra",
    "earth_chajnantor_plateau",
    "earth_waw_an_namus_apron",
    "earth_tibesti_tarso_voon",
    "earth_paricutin_lava_field",
    "earth_tolbachik_apron",
    "earth_kilauea_kau_desert",
    "earth_tongariro_rangipo",
}

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
    "earth_karapinar_meke": (37.4, 38.0, 33.4, 34.0),
    "earth_suphan_south_apron": (38.6, 39.2, 42.5, 43.2),
    "earth_nemrut_caldera_flank": (38.4, 38.9, 42.0, 42.6),
    "earth_agri_dogubayazit_flow": (39.4, 39.9, 43.6, 44.3),
    "earth_payunia_pampa_negra": (-36.5, -35.8, -69.5, -68.8),
    "earth_chajnantor_plateau": (-23.3, -22.7, -68.0, -67.4),
    "earth_waw_an_namus_apron": (24.6, 25.3, 17.4, 18.1),
    "earth_tibesti_tarso_voon": (20.6, 21.3, 16.9, 17.6),
    "earth_paricutin_lava_field": (19.2, 19.8, -102.5, -101.9),
    "earth_tolbachik_apron": (55.4, 56.1, 159.9, 160.7),
    "earth_kilauea_kau_desert": (19.1, 19.7, -155.6, -155.0),
    "earth_tongariro_rangipo": (-39.6, -39.0, 175.4, 176.0),
}


@pytest.fixture(scope="module")
def df_earth() -> pd.DataFrame:
    """Load the 40-site processed Earth features parquet."""
    assert PARQUET_PATH.exists(), f"Missing {PARQUET_PATH}"
    return pd.read_parquet(PARQUET_PATH)


def test_exact_36_column_contract_schema(df_earth: pd.DataFrame) -> None:
    """Verify exact 36-column AGENTS.md §5 schema, order, and thermal_inertia contract."""
    assert list(df_earth.columns) == CONTRACT_COLS
    assert len(df_earth.columns) == 36
    assert (df_earth["body"] == "earth").all()
    assert df_earth["thermal_inertia"].isna().all()
    assert df_earth["thermal_inertia_sd"].isna().all()
    assert (df_earth["thermal_inertia_src"] == "").all()
    assert (df_earth["thermal_inertia_res_m"] == 1000.0).all()

    required_non_nan = (
        "slope_mean",
        "slope_p90",
        "roughness",
        "relief",
        "temp_amplitude",
        "albedo",
    )
    for col in required_non_nan:
        assert df_earth[col].notna().all(), f"Unexpected NaN in {col}"
        assert df_earth[f"{col}_sd"].notna().all(), f"Unexpected NaN in {col}_sd"


def test_site_counts_and_region_bounds(df_earth: pd.DataFrame) -> None:
    """Verify 40 sites (10 validation + 30 candidate [14 TR + 16 global]) and region boxes."""
    assert len(df_earth) == 40
    assert df_earth["site_id"].is_unique

    val_ids = set(df_earth[df_earth["role"] == "validation"]["site_id"])
    cand_ids = set(df_earth[df_earth["role"] == "candidate"]["site_id"])
    assert val_ids == EXPECTED_VALIDATION_IDS
    assert len(val_ids) == 10
    assert len(cand_ids) == 30
    assert cand_ids == TURKEY_CANDIDATE_IDS | GLOBAL_CANDIDATE_IDS
    assert len(cand_ids & TURKEY_CANDIDATE_IDS) == 14
    assert len(cand_ids & GLOBAL_CANDIDATE_IDS) == 16

    for _, row in df_earth.iterrows():
        sid = row["site_id"]
        lat_min, lat_max, lon_min, lon_max = SITE_REGION_BOUNDS[sid]
        assert lat_min <= row["lat"] <= lat_max, f"{sid} lat={row['lat']} out of bounds"
        assert lon_min <= row["lon"] <= lon_max, f"{sid} lon={row['lon']} out of bounds"


def test_temp_amplitude_annual_mean_and_raw_cache(df_earth: pd.DataFrame) -> None:
    """Verify MOD11A2.061_annual_mean source and |amp - (day - night)| < 0.1 K when raw cache exists."""
    assert (df_earth["temp_amplitude_src"] == "MOD11A2.061_annual_mean").all()
    assert (df_earth["temp_amplitude_res_m"] == 1000.0).all()
    assert (df_earth["temp_amplitude"] > 0.0).all()

    cached = [RAW_EARTH_DIR / f"{sid}_mod11a2_061_annual_2024.json" for sid in df_earth["site_id"]]
    if all(p.exists() for p in cached):
        for _, row in df_earth.iterrows():
            data = json.loads(
                (RAW_EARTH_DIR / f"{row['site_id']}_mod11a2_061_annual_2024.json").read_text(
                    encoding="utf-8"
                )
            )
            diff = abs(
                float(row["temp_amplitude"])
                - (float(data["lst_day_mean_k"]) - float(data["lst_night_mean_k"]))
            )
            assert diff < 0.1, f"{row['site_id']} diff={diff:.4f} K >= 0.1 K"


def test_albedo_and_physical_invariants(df_earth: pd.DataFrame) -> None:
    """Verify real MODIS albedo bounds, dark basalt vs evaporite separation, and slope invariants."""
    assert set(df_earth["albedo_src"].unique()).issubset({"MCD43A3.061", "MCD43A4.061_Liang2001"})
    assert (df_earth["albedo_res_m"] == 500.0).all()
    assert ((df_earth["albedo"] >= 0.0) & (df_earth["albedo"] <= 1.0)).all()
    assert (df_earth["slope_p90"] >= df_earth["slope_mean"]).all()
    assert (df_earth["relief"] >= 0.0).all()
    assert (df_earth["roughness"] >= 0.0).all()

    by_id = df_earth.set_index("site_id")["albedo"]
    for sid in ("earth_askja_holuhraun", "earth_mauna_loa_hiseas", "earth_etna_cisternazza", "earth_tolbachik_apron"):
        assert 0.02 <= by_id[sid] <= 0.10, f"Unexpected dark basalt albedo for {sid}: {by_id[sid]}"
    for sid in ("earth_atacama_yungay", "earth_qaidam_dalangtan", "earth_tuz_golu_south"):
        assert 0.18 <= by_id[sid] <= 0.45, f"Unexpected evaporite albedo for {sid}: {by_id[sid]}"


def test_validator_no_mock_and_mock_rejection(df_earth: pd.DataFrame, tmp_path: Path) -> None:
    """Verify validate_contract passes cleanly with 0/40 MOCK and flags injected MOCK."""
    n_mock, per_col = count_mock(df_earth, PARQUET_PATH)
    assert n_mock == 0
    assert all(v == 0 for v in per_col.values())

    errors, warnings, infos = validate(PARQUET_PATH, fail_on_mock=True)
    assert errors == []
    assert warnings == []
    assert any("0/40 satirda en az bir src == MOCK" in inf for inf in infos)

    df_mock = df_earth.copy()
    df_mock.loc[0, "albedo_src"] = "MOCK"
    mock_parquet = tmp_path / "features_earth_mock.parquet"
    df_mock.to_parquet(mock_parquet, index=False)

    err_strict, _, info_strict = validate(mock_parquet, fail_on_mock=True)
    assert any("1/40 satirda en az bir src == MOCK" in inf for inf in info_strict)
    assert any("MOCK" in e for e in err_strict)


def test_cross_table_consistency_with_docs(df_earth: pd.DataFrame) -> None:
    """Verify exact 40-site consistency across parquet, sites.py, and docs/data_sources_earth.md."""
    sites_py_ids = [s["site_id"] for s in VERIFIED_EARTH_SITES]
    assert list(df_earth["site_id"]) == sites_py_ids

    md_text = DOCS_PATH.read_text(encoding="utf-8")
    sec4_ids = re.findall(r"\|\s*\d+\s*\|\s*`(earth_[a-z0-9_]+)`\s*\|", md_text)
    assert sec4_ids == sites_py_ids

    sec5_ids = re.findall(
        r"^\|\s*`(earth_[a-z0-9_]+)`\s*\|\s*\d+\.\d+\s*\|\s*\d+\.\d+\s*\|",
        md_text,
        flags=re.MULTILINE,
    )
    assert sec5_ids == sites_py_ids

    # Ensure CV > 0.30 high-uncertainty audit table and 7 lithology conflict nuances are documented
    assert "earth_mcmurdo_wright_valley" in md_text
    for conflict_sid in (
        "earth_tongariro_rangipo",
        "earth_erciyes_kojugedigi",
        "earth_hasandagi_kecekalecik",
        "earth_salda_terrace",
        "earth_tendurek_shield",
        "earth_suphan_south_apron",
        "earth_paricutin_lava_field",
    ):
        assert conflict_sid in md_text


def test_dem_fallback_source_and_agri_nasadem(df_earth: pd.DataFrame) -> None:
    """Verify NASADEM fallback is restricted to missing Copernicus tiles (N39E044 at Agri)."""
    assert get_dem_source(Path("site_copdem30_wgs84.tif")) == COPERNICUS_DEM_SRC
    assert get_dem_source(Path("site_nasadem30_wgs84.tif")) == NASADEM_DEM_SRC

    by_id = df_earth.set_index("site_id")
    assert by_id.loc["earth_agri_dogubayazit_flow", "slope_mean_src"] == NASADEM_DEM_SRC
    other_mask = df_earth["site_id"] != "earth_agri_dogubayazit_flow"
    assert (df_earth.loc[other_mask, "slope_mean_src"] == COPERNICUS_DEM_SRC).all()

    for _, row in df_earth.iterrows():
        expected = row["slope_mean_src"]
        for feat in ("slope_p90", "roughness", "relief"):
            assert row[f"{feat}_src"] == expected


def test_modis_retrying_session_config() -> None:
    """Verify MADDE 4 retry/backoff adapter policy for resilient MODIS/Earthdata fetching."""
    sess = _make_retrying_session()
    retry = sess.get_adapter("https://").max_retries
    assert retry.total == 5
    assert retry.connect == 5
    assert retry.read == 5
    assert retry.backoff_factor == pytest.approx(0.8)
    assert {429, 500, 502, 503, 504}.issubset(set(retry.status_forcelist))


def test_mixed_pixel_diagnostic_rules_and_schema(df_earth: pd.DataFrame) -> None:
    """Verify MADDE 3 mixed-pixel diagnostic rules remain decoupled from the 36-col contract."""
    assert "mixed_pixel_flag" not in df_earth.columns
    assert classify_mixed_pixel(0.0, 0.0, 0.0, 1.5) == (False, "PURE_TARGET")
    assert classify_mixed_pixel(26.8, 0.0, 0.0, 0.0) == (True, "MIXED_WATER")
    assert classify_mixed_pixel(15.5, 0.3, 0.0, 43.1) == (True, "MIXED_WATER+VEG")
    assert classify_mixed_pixel(0.1, 0.0, 40.2, 55.9) == (True, "MIXED_CROP+VEG")

    diag_rows = build_diagnostic_rows()
    diag_ids = {r["site_id"] for r in diag_rows}
    expected_ids = {
        "earth_salda_terrace",
        "earth_tuz_golu_south",
        "earth_svalbard_bockfjorden",
        "earth_suphan_south_apron",
        "earth_meteor_crater_arizona",
        "earth_etna_cisternazza",
        "earth_etna_cand1_cisternazza",
        "earth_etna_cand2_pianolago_w",
    }
    assert expected_ids.issubset(diag_ids)
    assert len(MADDE3_AUDITED_RECORDS) == len(diag_rows)
    for row in diag_rows:
        assert row["mixed_pixel_flag"] == row["rule_flag"]
        assert row["is_mixed"] == row["rule_is_mixed"]


def test_earth_3d_grids_e7_integrity(df_earth: pd.DataFrame) -> None:
    """Verify E7 compact 74x74 DEM archive and E5-aligned metadata stay < 1 MB and match parquet *_src."""
    npz_path = Path("data/processed/earth_3d_grids.npz")
    meta_path = Path("data/processed/earth_3d_meta.json")
    atlas_meta_path = Path("data/processed/earth_atlas/metadata.json")

    assert npz_path.exists() and meta_path.exists()
    assert 0 < npz_path.stat().st_size < 1_000_000

    meta = json.loads(meta_path.read_text(encoding="utf-8"))
    atlas_by_id = {s["site_id"]: s for s in json.loads(atlas_meta_path.read_text(encoding="utf-8"))["sites"]}
    parquet_src = df_earth.set_index("site_id")["slope_mean_src"].to_dict()
    expected_ids = [s["site_id"] for s in VERIFIED_EARTH_SITES]

    assert meta["window_side_m"] == 2220.0
    assert meta["grid_res_m"] == 30.0
    assert meta["grid_shape"] == [74, 74]
    assert meta["site_count"] == 40
    assert meta["source_counts"] == {COPERNICUS_DEM_SRC: 39, NASADEM_DEM_SRC: 1}
    assert [r["site_id"] for r in meta["sites"]] == expected_ids

    with np.load(npz_path) as npz:
        assert list(npz.files) == expected_ids
        for rec in meta["sites"]:
            sid = rec["site_id"]
            grid = npz[sid]
            assert grid.shape == (74, 74)
            assert grid.dtype == np.float32
            assert np.all(np.isfinite(grid))
            assert rec["e5_scene_id"] == atlas_by_id[sid]["scene_id"]
            assert rec["dem_source"] == parquet_src[sid]
            assert rec["center_offset_from_site_m"] <= 7.5
            expected_sigma = 1.0 if rec["dem_source"] == COPERNICUS_DEM_SRC else None
            assert rec["sigma_z_rel_m"] == expected_sigma

