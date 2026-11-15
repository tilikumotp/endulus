"""Smoke tests for app modules, verified 3D/atlas assets, and Streamlit UI."""
from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from app import expectations, terrain  # noqa: E402


def _load_processed() -> tuple[pd.DataFrame, pd.DataFrame]:
    moon = pd.read_parquet(ROOT / "data" / "processed" / "features_moon.parquet")
    earth = pd.read_parquet(ROOT / "data" / "processed" / "features_earth.parquet")
    return moon, earth


def test_terrain_loads_verified_3d_grids_for_all_sites() -> None:
    moon, earth = _load_processed()
    for _, row in moon.iterrows():
        z, is_stub, half_width_m = terrain.get_tile_data(row)
        assert not is_stub, f"Expected real Moon 3D grid for {row['site_id']}"
        assert z.shape == (442, 442)
        assert np.isfinite(z).all()
        assert half_width_m > 1000.0

    for _, row in earth.iterrows():
        z, is_stub, half_width_m = terrain.get_tile_data(row)
        assert not is_stub, f"Expected real Earth 3D grid for {row['site_id']}"
        assert z.shape == (74, 74)
        assert np.isfinite(z).all()
        assert np.isclose(half_width_m, 1110.0)


def test_validation_expectations_cover_all_validation_sites() -> None:
    _, earth = _load_processed()
    expected_ids = set(earth.loc[earth["role"] == "validation", "site_id"])
    assert len(expected_ids) == 10
    assert set(expectations.VALIDATION_EXPECTATIONS.keys()) == expected_ids

    for site_id, meta in expectations.VALIDATION_EXPECTATIONS.items():
        assert meta["expected_v1"] in {"mobility", "thermal_only", "none"}
        assert meta["ice_e8"] in {"var", "kısmi", "yok", "veri yok"}
        assert meta["source_url"].startswith("https://"), site_id


def test_offline_atlas_assets_present_for_all_sites() -> None:
    moon, earth = _load_processed()
    moon_atlas = ROOT / "data" / "processed" / "moon_atlas"
    earth_atlas = ROOT / "data" / "processed" / "earth_atlas"

    for site_id in moon["site_id"]:
        for suffix in ("hillshade", "hazard", "atlas"):
            assert (moon_atlas / f"{site_id}_{suffix}.png").exists()

    meta = json.loads((earth_atlas / "metadata.json").read_text(encoding="utf-8"))
    meta_ids = {item["site_id"] for item in meta["sites"]}
    assert meta_ids == set(earth["site_id"])
    for site_id in earth["site_id"]:
        assert (earth_atlas / f"{site_id}.webp").exists()


def test_streamlit_app_smoke_tr_and_en() -> None:
    from streamlit.testing.v1 import AppTest

    at = AppTest.from_file(str(ROOT / "app" / "main.py"), default_timeout=30).run()
    assert not at.exception
    assert len(at.tabs) == 6

    # Localized Moon crater display names hide raw ROI suffixes
    moon_caption_text = " ".join(c.value for c in at.caption)
    assert "ROI" not in moon_caption_text

    # No emojis remain in tabs, titles, alerts, or captions
    for col in (at.title, at.subheader, at.caption, at.markdown, at.info, at.warning):
        for el in col:
            assert not any(ord(ch) > 0x2600 for ch in el.value), el.value

    at.sidebar.radio[0].set_value("English").run()
    assert not at.exception
    assert len(at.tabs) == 6

    for mission in ("rover_mobility", "isru_ice", "radar_calibration"):
        at.sidebar.selectbox[1].set_value(mission).run()
        assert not at.exception

    # Verify Rank Diagnostic dataframe has 10 validation rows sorted monotonically by Mobility rank
    diag_df = next(
        el.value
        for el in at.dataframe
        if len(el.value) == 10 and any("DOI" in str(c) for c in el.value.columns)
    )
    # p4 v1 diagnostic renders ranks as one cell: "Mobility #3/40 · Surface #5/40 · ..."
    # The first "#N/40" occurrence is the Mobility rank; monotonicity check is unchanged.
    rank_col = next(
        c
        for c in diag_df.columns
        if diag_df[c].astype(str).str.contains(r"#\d+/\d+", regex=True).all()
    )
    ranks = (
        diag_df[rank_col].astype(str).str.extract(r"#(\d+)")[0].astype(int).tolist()
    )
    assert ranks == sorted(ranks)

    # (map toggle check removed: p4 v1 renders validation sites unconditionally,
    # the keyed checkbox no longer exists in the app)

    # Verify 8-dimension challenge scorecard, 40-site bibliography & plotly figures render
    assert any(len(el.value) == 8 for el in at.dataframe)
    assert any(len(el.value) == 40 for el in at.dataframe)
    md_text = " ".join(m.value for m in at.markdown)
    assert "Barker et al. (2021)" in md_text
    assert len(at.get("plotly_chart")) >= 3



