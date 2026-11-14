"""Diagnostic 1 km mixed-pixel representativeness classifier for MODIS thermal and albedo sites."""

from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any


@dataclass(frozen=True)
class MixedPixelAuditRecord:
    """Verified ESA WorldCover 10m and Sentinel-2 L2A SCL fractions within radius_m=1000 m."""

    site_id: str
    label: str
    lat: float
    lon: float
    wc_bare_pct: float
    wc_water_pct: float
    wc_snow_pct: float
    wc_crop_pct: float
    wc_veg_pct: float
    wc_built_pct: float
    wc_scene_id: str
    s2_bare_or_dark_pct: float
    s2_veg_pct: float
    s2_water_pct: float
    s2_snow_pct: float
    s2_scene_id: str
    mixed_pixel_flag: str
    is_mixed: bool
    note: str


def classify_mixed_pixel(
    water_pct: float,
    snow_pct: float,
    crop_pct: float,
    veg_pct: float,
    *,
    water_thresh: float = 10.0,
    snow_thresh: float = 10.0,
    crop_thresh: float = 10.0,
    veg_thresh: float = 25.0,
) -> tuple[bool, str]:
    """Classify non-target surface mixing inside a 1 km MODIS footprint from 10 m cover fractions."""
    flags: list[str] = []
    if water_pct >= water_thresh:
        flags.append("WATER")
    if snow_pct >= snow_thresh:
        flags.append("SNOW")
    if crop_pct >= crop_thresh:
        flags.append("CROP")
    if veg_pct >= veg_thresh:
        flags.append("VEG")
    if not flags:
        return False, "PURE_TARGET"
    return True, "MIXED_" + "+".join(flags)


MADDE3_AUDITED_RECORDS: tuple[MixedPixelAuditRecord, ...] = (
    MixedPixelAuditRecord(
        site_id="earth_salda_terrace",
        label="Salda Lake Terrace (current)",
        lat=37.5150,
        lon=29.6350,
        wc_bare_pct=2.0,
        wc_water_pct=0.1,
        wc_snow_pct=0.0,
        wc_crop_pct=40.2,
        wc_veg_pct=55.9,
        wc_built_pct=1.7,
        wc_scene_id="ESA_WorldCover_10m_2021_v200_N36E027",
        s2_bare_or_dark_pct=93.1,
        s2_veg_pct=6.9,
        s2_water_pct=0.0,
        s2_snow_pct=0.0,
        s2_scene_id="S2B_MSIL2A_20240816T084559_R107_T36STG_20240816T111352",
        mixed_pixel_flag="MIXED_CROP+VEG",
        is_mixed=True,
        note="Adjacent shoreline fields/dry steppe in 1 km MOD11A2/500 m MCD43A3; summer S2 mostly bare dry soil (93.1%).",
    ),
    MixedPixelAuditRecord(
        site_id="earth_tuz_golu_south",
        label="Tuz Golu South Salt Flat (current)",
        lat=38.5500,
        lon=33.6200,
        wc_bare_pct=73.2,
        wc_water_pct=26.8,
        wc_snow_pct=0.0,
        wc_crop_pct=0.0,
        wc_veg_pct=0.0,
        wc_built_pct=0.0,
        wc_scene_id="ESA_WorldCover_10m_2021_v200_N36E033",
        s2_bare_or_dark_pct=73.3,
        s2_veg_pct=0.0,
        s2_water_pct=9.1,
        s2_snow_pct=17.6,
        s2_scene_id="S2B_MSIL2A_20240820T082559_R021_T36SWH_20240820T130351",
        mixed_pixel_flag="MIXED_WATER",
        is_mixed=True,
        note="Shallow brine covers 26.8% of 1 km buffer (WC); S2 SCL=11 (17.6%) is bright halite crust false-positive, not snow.",
    ),
    MixedPixelAuditRecord(
        site_id="earth_svalbard_bockfjorden",
        label="Svalbard Bockfjorden (current)",
        lat=79.4280,
        lon=13.3850,
        wc_bare_pct=41.1,
        wc_water_pct=15.5,
        wc_snow_pct=0.3,
        wc_crop_pct=0.0,
        wc_veg_pct=43.1,
        wc_built_pct=0.0,
        wc_scene_id="ESA_WorldCover_10m_2021_v200_N78E012",
        s2_bare_or_dark_pct=51.9,
        s2_veg_pct=17.2,
        s2_water_pct=29.8,
        s2_snow_pct=0.0,
        s2_scene_id="S2A_MSIL2A_20240718T122651_R052_T33XVJ_20240718T185224",
        mixed_pixel_flag="MIXED_WATER+VEG",
        is_mixed=True,
        note="Fjord water (15.5% WC / 29.8% S2) and Arctic tundra (43.1% WC) contaminate 1 km LST & 500 m albedo.",
    ),
    MixedPixelAuditRecord(
        site_id="earth_suphan_south_apron",
        label="Mount Suphan Apron (new approved: 38.8650, 42.8300)",
        lat=38.8650,
        lon=42.8300,
        wc_bare_pct=2.3,
        wc_water_pct=0.0,
        wc_snow_pct=0.0,
        wc_crop_pct=18.4,
        wc_veg_pct=79.3,
        wc_built_pct=0.1,
        wc_scene_id="ESA_WorldCover_10m_2021_v200_N36E042",
        s2_bare_or_dark_pct=99.8,
        s2_veg_pct=0.2,
        s2_water_pct=0.0,
        s2_snow_pct=0.0,
        s2_scene_id="S2A_MSIL2A_20240905T075611_R035_T38SLJ_20240905T123250",
        mixed_pixel_flag="MIXED_CROP+VEG",
        is_mixed=True,
        note="Dry highland steppe/fallow fields in WC (79.3% grass/scrub, 18.4% fallow crop), 99.8% bare in Sep S2.",
    ),
    MixedPixelAuditRecord(
        site_id="earth_meteor_crater_arizona",
        label="Meteor Crater Arizona (current)",
        lat=35.0272,
        lon=-111.0225,
        wc_bare_pct=57.3,
        wc_water_pct=0.0,
        wc_snow_pct=0.0,
        wc_crop_pct=0.0,
        wc_veg_pct=41.9,
        wc_built_pct=0.8,
        wc_scene_id="ESA_WorldCover_10m_2021_v200_N33W114",
        s2_bare_or_dark_pct=99.9,
        s2_veg_pct=0.0,
        s2_water_pct=0.0,
        s2_snow_pct=0.0,
        s2_scene_id="S2A_MSIL2A_20240816T175911_R041_T12SVD_20240816T230946",
        mixed_pixel_flag="MIXED_VEG",
        is_mixed=True,
        note="WC maps sparse Colorado Plateau desert scrub (41.9%); Aug S2 confirms 99.9% bare soil/ejecta reflectance.",
    ),
    MixedPixelAuditRecord(
        site_id="earth_etna_cisternazza",
        label="Mount Etna (applied Candidate 1 Cisternazza: 37.7257, 15.0084)",
        lat=37.7257,
        lon=15.0084,
        wc_bare_pct=99.4,
        wc_water_pct=0.0,
        wc_snow_pct=0.0,
        wc_crop_pct=0.0,
        wc_veg_pct=0.6,
        wc_built_pct=0.0,
        wc_scene_id="ESA_WorldCover_10m_2021_v200_N36E012+N36E015",
        s2_bare_or_dark_pct=76.8,
        s2_veg_pct=0.0,
        s2_water_pct=1.3,
        s2_snow_pct=22.0,
        s2_scene_id="S2A_MSIL2A_20240208T094141_R036_T33SVB_20240208T151801",
        mixed_pixel_flag="PURE_TARGET",
        is_mixed=False,
        note="Selected Candidate 1 (WC=99.4% bare tephra, 0.6% veg; summer S2 0% snow, Apr S2 0.3% snow, Feb S2 22.0% snow).",
    ),
    MixedPixelAuditRecord(
        site_id="earth_etna_cand1_cisternazza",
        label="Etna Candidate 1: Cisternazza (37.7257, 15.0084)",
        lat=37.7257,
        lon=15.0084,
        wc_bare_pct=99.4,
        wc_water_pct=0.0,
        wc_snow_pct=0.0,
        wc_crop_pct=0.0,
        wc_veg_pct=0.6,
        wc_built_pct=0.0,
        wc_scene_id="ESA_WorldCover_10m_2021_v200_N36E012+N36E015",
        s2_bare_or_dark_pct=76.8,
        s2_veg_pct=0.0,
        s2_water_pct=1.3,
        s2_snow_pct=22.0,
        s2_scene_id="S2A_MSIL2A_20240208T094141_R036_T33SVB_20240208T151801",
        mixed_pixel_flag="PURE_TARGET",
        is_mixed=False,
        note="Purest volcanic surface: WC=99.4% bare tephra, 0.6% veg; summer S2 0% snow; lowest Feb snow (22.0%).",
    ),
    MixedPixelAuditRecord(
        site_id="earth_etna_cand2_pianolago_w",
        label="Etna Candidate 2: Piano del Lago W (37.7190, 14.9970)",
        lat=37.7190,
        lon=14.9970,
        wc_bare_pct=96.7,
        wc_water_pct=0.0,
        wc_snow_pct=0.0,
        wc_crop_pct=0.0,
        wc_veg_pct=3.3,
        wc_built_pct=0.0,
        wc_scene_id="ESA_WorldCover_10m_2021_v200_N36E012+N36E015",
        s2_bare_or_dark_pct=42.6,
        s2_veg_pct=0.0,
        s2_water_pct=4.3,
        s2_snow_pct=53.1,
        s2_scene_id="S2A_MSIL2A_20240208T094141_R036_T33SVB_20240208T151801",
        mixed_pixel_flag="PURE_TARGET",
        is_mixed=False,
        note="WC=96.7% bare tephra, 3.3% veg, summer S2 1.0-1.5% veg/0% snow; Feb 2024 winter S2 shows 53.1% snow.",
    ),
)


def build_diagnostic_rows() -> list[dict[str, Any]]:
    """Return all audited mixed-pixel diagnostic records with rule-recomputed flags."""
    rows: list[dict[str, Any]] = []
    for rec in MADDE3_AUDITED_RECORDS:
        is_mix, flag = classify_mixed_pixel(
            water_pct=rec.wc_water_pct,
            snow_pct=rec.wc_snow_pct,
            crop_pct=rec.wc_crop_pct,
            veg_pct=rec.wc_veg_pct,
        )
        d = asdict(rec)
        d["rule_is_mixed"] = is_mix
        d["rule_flag"] = flag
        rows.append(d)
    return rows


def main() -> None:
    """Print the 1 km mixed-pixel diagnostic summary without altering parquet outputs."""
    print("=== MADDE 3: 1 km Mixed-Pixel Diagnostic Report (ESA WorldCover 10m + Sentinel-2 SCL) ===")
    for row in build_diagnostic_rows():
        print(
            f"{row['site_id']:30s} | {row['rule_flag']:16s} | "
            f"WC bare={row['wc_bare_pct']:5.1f}% water={row['wc_water_pct']:4.1f}% "
            f"crop={row['wc_crop_pct']:4.1f}% veg={row['wc_veg_pct']:4.1f}% snow={row['wc_snow_pct']:4.1f}% | "
            f"S2_snow={row['s2_snow_pct']:4.1f}%"
        )


if __name__ == "__main__":
    main()
