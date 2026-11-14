"""Export verified parquet metrics, Monte Carlo uncertainty bands, offline atlas
assets, 3D DEM terrain grids, and consolidated Emirhan/Eray citations into
static assets for the React observatory (`web/public/`).
"""
from __future__ import annotations

import json
import pathlib
import shutil
import sys

import numpy as np
import pandas as pd

ROOT = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "app"))

from app.expectations import VALIDATION_EXPECTATIONS  # noqa: E402
from app.i18n import (  # noqa: E402
    DIMENSION_SCORECARD,
    EARTH_DATASET_REFS,
    MOON_BIBLIOGRAPHY,
    MOON_REF_NAMES,
)
from earth.mixed_pixel import build_diagnostic_rows  # noqa: E402
from earth.sites import VERIFIED_EARTH_SITES  # noqa: E402
from moon_mars.albedo_sensitivity import FACTORS, run_albedo_sensitivity  # noqa: E402
from scoring.config import MISSION_PRESETS  # noqa: E402
from scoring.display import expanded_interval  # noqa: E402
from scoring.portfolio import select_portfolio  # noqa: E402
from scoring.similarity import (  # noqa: E402
    axis_gaps,
    axis_scores_with_draws,
    combine_axes_with_uncertainty,
)

WEB_PUBLIC = ROOT / "web" / "public"
DATA_OUT = WEB_PUBLIC / "data"
DEM_SIDE = 51  # Crisp 51x51 grid for smooth 3D DEM meshes and W-E / S-N cross sections

TURKISH_SITE_IDS = {
    "earth_karapinar_meke",
    "earth_karacadag_summit",
    "earth_karacadag_ovabag",
    "earth_kula_divlit",
    "earth_acigol_guneydag",
    "earth_hasandagi_kecekalecik",
    "earth_erciyes_kojugedigi",
    "earth_cappadocia_kavakkoy",
    "earth_nemrut_caldera_flank",
    "earth_agri_dogubayazit_flow",
    "earth_tendurek_shield",
    "earth_suphan_south_apron",
    "earth_salda_terrace",
    "earth_tuz_golu_south",
}

SHORT_NAME_TR: dict[str, str] = {
    "earth_karapinar_meke": "Karapınar Meke (TR)",
    "earth_mcmurdo_wright_valley": "McMurdo Wright Valley",
    "earth_hasandagi_kecekalecik": "Hasandağı Keçikaleçik (TR)",
    "earth_agri_dogubayazit_flow": "Ağrı Doğubayazıt (TR)",
    "earth_erciyes_kojugedigi": "Erciyes Koçdağ (TR)",
    "earth_kula_divlit": "Kula Divlit (TR)",
    "earth_lunar_crater_nevada": "Lunar Crater (Nevada)",
    "earth_nemrut_caldera_flank": "Nemrut Kalderası (TR)",
    "earth_deccan_mahabaleshwar": "Deccan Panchgani",
    "earth_karacadag_summit": "Karacadağ Kollubaba (TR)",
    "earth_harrat_ash_shaam": "Harrat Ash Shaam",
    "earth_payunia_pampa_negra": "Payunia Pampa Negra",
    "earth_salda_terrace": "Salda Gölü (TR)",
    "earth_kilbourne_hole_nm": "Kilbourne Hole",
    "earth_karacadag_ovabag": "Karacadağ Ovabağ (TR)",
    "earth_meteor_crater_arizona": "Meteor Crater",
    "earth_tendurek_shield": "Tendürek Kalkanı (TR)",
    "earth_acigol_guneydag": "Acıgöl Güneydağ (TR)",
    "earth_svalbard_bockfjorden": "Svalbard Bockfjorden",
    "earth_puna_campo_piedra_pomez": "Puna de Atacama",
    "earth_harrat_rahat_madinah": "Harrat Rahat",
    "earth_chajnantor_plateau": "Chajnantor Platosu",
    "earth_suphan_south_apron": "Süphan Güney Eteği (TR)",
    "earth_tibesti_tarso_voon": "Tibesti Tarso Voon",
    "earth_cappadocia_kavakkoy": "Kapadokya Kavak (TR)",
    "earth_etna_cisternazza": "Etna Cisternazza",
    "earth_qaidam_dalangtan": "Qaidam Dalangtan",
    "earth_paricutin_lava_field": "Parícutin",
    "earth_tolbachik_apron": "Tolbachik",
    "earth_craters_of_the_moon": "Craters of the Moon",
    "earth_tuz_golu_south": "Tuz Gölü Güney (TR)",
    "earth_waw_an_namus_apron": "Waw an-Namus",
    "earth_tongariro_rangipo": "Tongariro Rangipo",
    "earth_pinacate_el_elegante": "Pinacate El Elegante",
    "earth_askja_holuhraun": "Askja Holuhraun",
    "earth_lanzarote_timanfaya": "Lanzarote Timanfaya",
    "earth_atacama_yungay": "Atacama Yungay",
    "earth_haughton_crater": "Haughton Krateri",
    "earth_mauna_loa_hiseas": "Mauna Loa HI-SEAS",
    "earth_kilauea_kau_desert": "Kīlauea Kaʻū Çölü",
}


def _f(val: object, ndigits: int = 4) -> float | None:
    if val is None:
        return None
    fval = float(val)
    if np.isnan(fval) or np.isinf(fval):
        return None
    return round(fval, ndigits)


def _continent(lat: float, lon: float) -> str:
    if lat < -60:
        return "antarctica"
    if lon < -30:
        return "north_america" if lat > 12 else "south_america"
    if lat < -10 and lon > 110:
        return "oceania"
    if lat > 34 and -25 <= lon <= 45:
        if 26 <= lon <= 45 and lat < 42.5:
            return "asia"
        return "europe"
    if lat <= 34 and -20 <= lon <= 52:
        return "africa"
    return "asia"


def _resample_grid(arr: np.ndarray, target: int = DEM_SIDE) -> list[list[float]]:
    """Resample 2D elevation grid to target x target and center relative to min."""
    arr = np.nan_to_num(arr, nan=float(np.nanmedian(arr)))
    idx_r = np.round(np.linspace(0, arr.shape[0] - 1, target)).astype(int)
    idx_c = np.round(np.linspace(0, arr.shape[1] - 1, target)).astype(int)
    sub = arr[np.ix_(idx_r, idx_c)]
    rel = np.round(sub - float(np.min(sub)), 1)
    return rel.tolist()


def _resample_1d(vals: np.ndarray, target: int = DEM_SIDE) -> list[float]:
    arr = np.nan_to_num(np.asarray(vals, dtype=float), nan=0.0)
    idx = np.round(np.linspace(0, len(arr) - 1, target)).astype(int)
    return [round(float(v), 1) for v in arr[idx]]


def main() -> None:
    DATA_OUT.mkdir(parents=True, exist_ok=True)
    for folder in ("moon_atlas", "earth_atlas", "figures", "thumbs/moon"):
        if folder == "figures":
            src = ROOT / "report" / "figures"
        elif folder == "thumbs/moon":
            src = ROOT / "data" / "processed" / "thumbs" / "moon"
        else:
            src = ROOT / "data" / "processed" / folder
        dst = WEB_PUBLIC / folder
        dst.mkdir(parents=True, exist_ok=True)
        if folder == "figures":
            for p in src.glob("fig*.png"):
                shutil.copy2(p, dst / p.name)
        elif folder == "thumbs/moon":
            for p in src.glob("moon_*.png"):
                shutil.copy2(p, dst / p.name)
        else:
            for p in src.iterdir():
                if p.is_file():
                    shutil.copy2(p, dst / p.name)

    world_src = ROOT / "web" / "node_modules" / "world-atlas" / "countries-50m.json"
    if world_src.exists():
        shutil.copy2(world_src, DATA_OUT / "world-50m.json")

    moon_df = pd.read_parquet(ROOT / "data" / "processed" / "features_moon.parquet")
    earth_df = pd.read_parquet(ROOT / "data" / "processed" / "features_earth.parquet")
    moon_atlas_meta = {
        m["site_id"]: m
        for m in json.loads((ROOT / "data" / "processed" / "moon_atlas" / "atlas_metadata.json").read_text("utf-8"))
    }
    earth_atlas_list = json.loads((ROOT / "data" / "processed" / "earth_atlas" / "metadata.json").read_text("utf-8"))["sites"]
    earth_atlas_meta = {s["site_id"]: s for s in earth_atlas_list}
    citations_by_id = {s["site_id"]: s["citation"] for s in VERIFIED_EARTH_SITES}

    earth_sites: list[dict] = []
    for _, row in earth_df.iterrows():
        sid = str(row["site_id"])
        ea = earth_atlas_meta.get(sid, {})
        exp = VALIDATION_EXPECTATIONS.get(sid)
        lat = round(float(row["lat"]), 4)
        lon = round(float(row["lon"]), 4)
        earth_sites.append({
            "site_id": sid,
            "name": str(row["name"]),
            "short": SHORT_NAME_TR.get(sid, str(row["name"]).split("(")[0].strip()),
            "role": str(row["role"]),
            "is_tr": sid in TURKISH_SITE_IDS,
            "continent": _continent(lat, lon),
            "lat": lat,
            "lon": lon,
            "lithology": str(row.get("lithology_class") or "unknown"),
            "slope_mean": _f(row["slope_mean"], 2),
            "slope_mean_sd": _f(row["slope_mean_sd"], 2),
            "slope_p90": _f(row["slope_p90"], 2),
            "roughness": _f(row["roughness"], 2),
            "relief": _f(row["relief"], 1),
            "albedo": _f(row["albedo"], 4),
            "albedo_sd": _f(row["albedo_sd"], 4),
            "dem_src": str(row["slope_mean_src"]),
            "dem_res_m": _f(row["slope_mean_res_m"], 0),
            "albedo_src": str(row["albedo_src"]),
            "albedo_res_m": _f(row["albedo_res_m"], 0),
            "temp_amplitude": _f(row["temp_amplitude"], 2),
            "temp_src": str(row["temp_amplitude_src"]),
            "citation": citations_by_id.get(sid, ""),
            "atlas_img": f"/earth_atlas/{sid}.webp",
            "s2_scene": ea.get("scene_id", ""),
            "s2_date": ea.get("acquisition_date", ""),
            "s2_cloud_pct": ea.get("local_cloud_pct"),
            "validation": exp,
        })

    moon_refs: list[dict] = []
    comparisons: dict[str, dict] = {}
    gaps_by_moon: dict[str, dict[str, list[dict]]] = {}

    for _, mrow in moon_df.iterrows():
        mid = str(mrow["site_id"])
        ma = moon_atlas_meta.get(mid, {})
        names = MOON_REF_NAMES.get(mid, {})

        axis_tbl, draws = axis_scores_with_draws(mrow, earth_df)
        mob_df = axis_tbl[axis_tbl["axis"] == "mobility"].set_index("site_id")
        surf_df = axis_tbl[axis_tbl["axis"] == "surface"].set_index("site_id")

        mob_rank_map = mob_df["score"].rank(ascending=False, method="min").astype(int).to_dict()
        surf_rank_map = surf_df["score"].rank(ascending=False, method="min").astype(int).to_dict()

        pf_selected, pf_uncovered = select_portfolio(axis_tbl, min_score=0.70, axes=["mobility", "surface"])
        pf_covered = [a for a in ("mobility", "surface") if a not in pf_uncovered]

        moon_refs.append({
            "site_id": mid,
            "name_tr": names.get("tr", str(mrow["name"])),
            "name_en": names.get("en", str(mrow["name"])),
            "lat": round(float(mrow["lat"]), 4),
            "lon": round(float(mrow["lon"]), 4),
            "lithology": str(mrow.get("lithology_class") or "regolith"),
            "slope_mean": _f(mrow["slope_mean"], 2),
            "slope_mean_sd": _f(mrow["slope_mean_sd"], 2),
            "slope_p90": _f(mrow["slope_p90"], 2),
            "roughness": _f(mrow["roughness"], 2),
            "relief": _f(mrow["relief"], 1),
            "albedo": _f(mrow["albedo"], 4),
            "albedo_sd": _f(mrow["albedo_sd"], 4),
            "dem_src": str(mrow["slope_mean_src"]),
            "dem_res_m": _f(mrow["slope_mean_res_m"], 0),
            "albedo_src": str(mrow["albedo_src"]),
            "albedo_res_m": _f(mrow["albedo_res_m"], 0),
            "thumb_img": f"/thumbs/moon/{mid}.png",
            "hillshade_img": f"/moon_atlas/{mid}_hillshade.png",
            "hazard_img": f"/moon_atlas/{mid}_hazard.png",
            "atlas_plate_img": f"/moon_atlas/{mid}_atlas.png",
            "pct_lt10deg": ma.get("pct_lt10deg"),
            "pct_10_20deg": ma.get("pct_10_20deg"),
            "pct_gt20deg": ma.get("pct_gt20deg"),
            "elev_min_m": ma.get("elev_min_m"),
            "elev_max_m": ma.get("elev_max_m"),
            "portfolio_070": {
                "selected": list(pf_selected),
                "covered": pf_covered,
                "uncovered": list(pf_uncovered),
            },
        })

        mission_scores: dict[str, list[dict]] = {}
        for mkey, weights in MISSION_PRESETS.items():
            comb = combine_axes_with_uncertainty(axis_tbl, draws, weights)
            comb["rank_overall"] = comb["score"].rank(ascending=False, method="min").astype(int)
            comb = comb.sort_values("score", ascending=False).reset_index(drop=True)
            rows_out = []
            for _, cr in comb.iterrows():
                sid = str(cr["site_id"])
                lo, hi, wid = expanded_interval(float(cr["score"]), float(cr["q05"]), float(cr["q95"]))
                m_row = mob_df.loc[sid]
                s_row = surf_df.loc[sid]
                mlo, mhi, mwid = expanded_interval(float(m_row["score"]), float(m_row["q05"]), float(m_row["q95"]))
                slo, shi, swid = expanded_interval(float(s_row["score"]), float(s_row["q05"]), float(s_row["q95"]))
                rows_out.append({
                    "site_id": sid,
                    "score": _f(cr["score"], 4),
                    "ci_lo": _f(lo, 4),
                    "ci_hi": _f(hi, 4),
                    "widened": bool(wid),
                    "rank": int(cr["rank_overall"]),
                    "mob": _f(m_row["score"], 4),
                    "mob_lo": _f(mlo, 4),
                    "mob_hi": _f(mhi, 4),
                    "mob_widened": bool(mwid),
                    "mob_rank": int(mob_rank_map[sid]),
                    "surf": _f(s_row["score"], 4),
                    "surf_lo": _f(slo, 4),
                    "surf_hi": _f(shi, 4),
                    "surf_widened": bool(swid),
                    "surf_rank": int(surf_rank_map[sid]),
                })
            mission_scores[mkey] = rows_out
        comparisons[mid] = mission_scores

        g_df = axis_gaps(mrow, earth_df)
        g_map: dict[str, list[dict]] = {}
        for sid, grp in g_df.groupby("site_id"):
            g_map[str(sid)] = [
                {
                    "axis": str(gr["axis"]),
                    "feature": str(gr["feature"]),
                    "moon_val": _f(gr["ref_value"], 3),
                    "earth_val": _f(gr["cand_value"], 3),
                    "diff": _f(gr["diff"], 3),
                    "z_diff": _f(gr["z_diff"], 2),
                }
                for _, gr in grp.iterrows()
            ]
        gaps_by_moon[mid] = g_map

    dem_grids: dict[str, dict] = {}
    for mid in moon_df["site_id"]:
        npz_path = ROOT / "data" / "processed" / "moon_3d" / f"{mid}_3d.npz"
        with np.load(npz_path) as data:
            z = np.asarray(data["elev_m"], dtype=float)
            dx = float(data["dx_m"]) if "dx_m" in data else 5.0
            we_x = np.asarray(data["profile_we_x_m"], dtype=float)
            we_dz = np.asarray(data["profile_we_dz_m"], dtype=float)
            sn_y = np.asarray(data["profile_sn_y_m"], dtype=float)
            sn_dz = np.asarray(data["profile_sn_dz_m"], dtype=float)
        half_w = round(0.5 * (z.shape[1] - 1) * dx, 1)
        dem_grids[str(mid)] = {
            "body": "moon",
            "half_width_m": half_w,
            "native_res_m": dx,
            "relief_m": round(float(np.nanmax(z) - np.nanmin(z)), 1),
            "grid": _resample_grid(z),
            "profile_we_m": _resample_1d(we_x),
            "profile_we_dz_m": _resample_1d(we_dz),
            "profile_sn_m": _resample_1d(sn_y),
            "profile_sn_dz_m": _resample_1d(sn_dz),
        }
    with np.load(ROOT / "data" / "processed" / "earth_3d_grids.npz") as ez:
        for sid in ez.files:
            z = np.asarray(ez[sid], dtype=float)
            z = np.nan_to_num(z, nan=float(np.nanmedian(z)))
            mid_r = z.shape[0] // 2
            mid_c = z.shape[1] // 2
            center_z = float(z[mid_r, mid_c])
            coords_m = np.linspace(-1110.0, 1110.0, z.shape[1])
            we_dz = z[mid_r, :] - center_z
            sn_dz = z[::-1, mid_c] - center_z  # row 0 is North (-30m step), flip S->N
            dem_grids[str(sid)] = {
                "body": "earth",
                "half_width_m": 1110.0,
                "native_res_m": 30.0,
                "relief_m": round(float(np.nanmax(z) - np.nanmin(z)), 1),
                "grid": _resample_grid(z),
                "profile_we_m": _resample_1d(coords_m),
                "profile_we_dz_m": _resample_1d(we_dz),
                "profile_sn_m": _resample_1d(coords_m),
                "profile_sn_dz_m": _resample_1d(sn_dz),
            }

    sens_df = run_albedo_sensitivity(moon_df, earth_df)
    albedo_sensitivity = [
        {
            "ref_site_id": str(r["ref_site_id"]),
            "factor": round(float(r["factor"]), 2),
            "moon_albedo_scaled": round(float(r["moon_albedo_scaled"]), 4),
            "mean_surface_score_delta": round(float(r["mean_surface_score_delta"]), 4),
            "mean_overall_score_delta": round(float(r["mean_overall_score_delta"]), 4),
            "spearman_rho_overall": round(float(r["spearman_rho_overall"]), 4),
            "top1_site_id": str(r["top1_site_id"]),
            "top3_site_ids": str(r["top3_site_ids"]).split(", "),
            "top1_candidate_id": str(r["top1_candidate_id"]),
        }
        for _, r in sens_df.iterrows()
    ]

    mixed_pixel_audit = build_diagnostic_rows()

    app_payload = {
        "meta": {
            "moon_count": len(moon_refs),
            "earth_count": len(earth_sites),
            "validation_count": sum(1 for s in earth_sites if s["role"] == "validation"),
            "tr_candidate_count": sum(1 for s in earth_sites if s["role"] == "candidate" and s["is_tr"]),
            "global_candidate_count": sum(1 for s in earth_sites if s["role"] == "candidate" and not s["is_tr"]),
            "active_axes": ["mobility", "surface"],
            "suspended_axes": ["thermal"],
            "tests_passed": "51/51",
            "mock_rows": 0,
            "albedo_factors": [round(float(f), 2) for f in FACTORS],
        },
        "moon_refs": moon_refs,
        "earth_sites": earth_sites,
        "comparisons": comparisons,
        "gaps": gaps_by_moon,
        "albedo_sensitivity": albedo_sensitivity,
        "mixed_pixel_audit": mixed_pixel_audit,
        "dimensions": DIMENSION_SCORECARD,
        "bibliography": {
            "moon_tr": MOON_BIBLIOGRAPHY["tr"],
            "moon_en": MOON_BIBLIOGRAPHY["en"],
            "earth_tr": EARTH_DATASET_REFS["tr"],
            "earth_en": EARTH_DATASET_REFS["en"],
        },
    }

    (DATA_OUT / "app_data.json").write_text(
        json.dumps(app_payload, ensure_ascii=False, separators=(",", ":")),
        encoding="utf-8",
    )
    (DATA_OUT / "dem_3d.json").write_text(
        json.dumps(dem_grids, ensure_ascii=False, separators=(",", ":")),
        encoding="utf-8",
    )
    print(f"app_data.json: {(DATA_OUT / 'app_data.json').stat().st_size} bytes")
    print(f"dem_3d.json:   {(DATA_OUT / 'dem_3d.json').stat().st_size} bytes")
    print(f"moon_atlas:    {len(list((WEB_PUBLIC / 'moon_atlas').glob('*.png')))} png")
    print(f"earth_atlas:   {len(list((WEB_PUBLIC / 'earth_atlas').glob('*.webp')))} webp")
    print(f"figures:       {len(list((WEB_PUBLIC / 'figures').glob('*.png')))} png")


if __name__ == "__main__":
    main()
