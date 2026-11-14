"""app/main.py – Moon/Mars <-> Earth Analog Finder (Person 4, v1)

Run:  streamlit run app/main.py

Scores come from the leader's src/scoring/similarity.py (axis_scores,
axis_pivot, combine_axes, axis_gaps) — this app does NOT compute its own
scores. Data is loaded directly from verified orbital parquets in data/processed/.
"""

from __future__ import annotations

import logging
import pathlib
import sys

import numpy as np
import pandas as pd
import plotly.graph_objects as go
import requests
import streamlit as st

# ── make src/scoring importable (scoring.config is imported inside) ──────────
ROOT = pathlib.Path(__file__).resolve().parent.parent
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))
if str(ROOT / "app") not in sys.path:
    sys.path.insert(0, str(ROOT / "app"))

from i18n import (  # noqa: E402
    AXIS_LABELS_ALL,
    BREAKDOWN,
    I18N,
    MISSION_LABELS_ALL,
    ROLE_LABELS,
)

from scoring.config import AXES, MISSION_PRESETS  # noqa: E402
from scoring.similarity import (  # noqa: E402
    axis_gaps,
    axis_pivot,
    axis_scores,
    combine_axes,
)
from scoring.portfolio import select_portfolio  # noqa: E402
from scoring.validation import run_blind_validation  # noqa: E402

LOGGER = logging.getLogger(__name__)

# ── page config ──────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Moon/Mars <-> Earth Analog Finder",
    layout="wide",
)

st.markdown(
    """
    <style>
    [data-testid="stAppViewContainer"] .main .block-container {
        padding-top: 1.75rem;
        padding-bottom: 2rem;
    }
    h1 {
        font-size: 2rem;
        font-weight: 500;
        line-height: 1.15;
    }
    h2, h3 {
        font-weight: 500;
    }
    [data-testid="stTabs"] button p {
        font-size: 0.875rem;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# ── constants ────────────────────────────────────────────────────────────────
PROC_DIR = ROOT / "data" / "processed"

AXIS_LABELS = AXIS_LABELS_ALL["en"]     # resolved per language in the sidebar
MISSION_LABELS = MISSION_LABELS_ALL["en"]
BREAKDOWN_NOTES = BREAKDOWN["en"]
S = I18N["en"]                          # per-language UI strings (resolved below)
LANG = "en"                             # language code, resolved in the sidebar

FEATURE_UNITS = {
    "slope_mean": "deg", "slope_p90": "deg", "roughness": "m",
    "relief": "m", "temp_amplitude": "K",
    "thermal_inertia": "J m^-2 K^-1 s^-1/2", "albedo": "0-1",
}

MISSION_LABELS = {
    "default": "Balanced (all axes equal)",
    "rover_mobility": "Rover mobility test",
    "isru_ice": "ISRU / ice prospecting",
    "radar_calibration": "Subsurface radar calibration",
}

VALIDATION_TOP_K = 5  # analogue counts as recovered when its rank <= k


# ── data loading ─────────────────────────────────────────────────────────────
def _load_body(stem: str) -> pd.DataFrame:
    proc = PROC_DIR / f"{stem}.parquet"
    if proc.exists():
        return pd.read_parquet(proc)
    st.error(f"Cannot find {stem}.parquet in data/processed/.")
    st.stop()


def _source_mtime(stem: str) -> float:
    """Mtime of the processed parquet file."""
    proc = PROC_DIR / f"{stem}.parquet"
    return proc.stat().st_mtime if proc.exists() else 0.0


@st.cache_data
def load_data(m_moon: float, m_earth: float) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Load verified moon and earth parquets from data/processed/.

    File mtimes are part of the cache key, so replacing a parquet in
    data/processed/ invalidates the cache automatically.
    """
    moon_df = _load_body("features_moon")
    earth_df = _load_body("features_earth")
    return moon_df, earth_df


# ── scoring (leader's module, called as-is) ──────────────────────────────────
def score_earth(
    ref_row: pd.Series, earth_df: pd.DataFrame, mission: str
) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Run axis_scores + pivot + weighted combine.

    Returns (result, long_scores) — long_scores is the raw axis_scores
    output needed by the validation and portfolio tabs.
    """
    long_scores = axis_scores(ref_row, earth_df)
    wide = axis_pivot(long_scores)
    overall = combine_axes(long_scores, MISSION_PRESETS[mission])

    result = (
        earth_df[["site_id", "name", "role", "lat", "lon", "lithology_class"]]
        .merge(overall, on="site_id", how="left")
        .merge(wide, on="site_id", how="left")
        .sort_values("score", ascending=False, na_position="last")
        .reset_index(drop=True)
    )
    return result, long_scores


# ── charts ───────────────────────────────────────────────────────────────────
def _radar_chart(row: pd.Series, axes: list[str]) -> go.Figure:
    """Plotly radar of per-axis scores with CI low/high lines for one site."""
    labels = [AXIS_LABELS[a] for a in axes]
    vals = [float(row.get(f"score_{a}", np.nan)) for a in axes]
    lo = [float(row.get(f"ci_low_{a}", np.nan)) for a in axes]
    hi = [float(row.get(f"ci_high_{a}", np.nan)) for a in axes]

    def _closed(xs: list[float]) -> list[float]:
        return xs + [xs[0]]

    labels_c = labels + [labels[0]]
    fig = go.Figure()
    fig.add_trace(go.Scatterpolar(
        r=_closed(vals), theta=labels_c, fill="toself",
        fillcolor="rgba(138,90,24,0.12)",
        line=dict(color="#8A5A18", width=2),
        name=row["name"],
        hovertemplate="%{theta}: %{r:.2f}<extra></extra>",
    ))
    fig.add_trace(go.Scatterpolar(
        r=_closed(hi), theta=labels_c,
        line=dict(color="#8A847A", width=1, dash="dash"),
        name=S["ci_high"], hoverinfo="skip",
    ))
    fig.add_trace(go.Scatterpolar(
        r=_closed(lo), theta=labels_c,
        line=dict(color="#8A847A", width=1, dash="dot"),
        name=S["ci_low"], hoverinfo="skip",
    ))
    fig.update_layout(
        polar=dict(
            bgcolor="rgba(0,0,0,0)",
            radialaxis=dict(
                visible=True,
                range=[0, 1],
                gridcolor="rgba(55,48,38,0.14)",
                color="#6E685D",
                tickfont=dict(size=10),
            ),
            angularaxis=dict(gridcolor="rgba(55,48,38,0.14)"),
        ),
        showlegend=False,
        margin=dict(l=32, r=32, t=40, b=24),
        title=dict(text=str(row["name"]), font=dict(size=13, color="#2C2923")),
        height=320,
        paper_bgcolor="rgba(0,0,0,0)",
        font=dict(color="#2C2923"),
    )
    return fig


def _map_chart(result: pd.DataFrame, top_n: int) -> None:
    """pydeck scatter map of the top-N scored Earth sites.

    Known validation analogues are outlined in blue; candidate size and
    colour encode the mission-weighted score.
    """
    map_df = result.head(top_n)[
        ["site_id", "name", "role", "lat", "lon", "score", "lithology_class"]
    ].copy()

    def _color(score: float) -> list[int]:
        if np.isnan(score):
            return [128, 128, 128, 160]
        r, g = int(255 * (1 - score)), int(255 * score)
        return [r, g, 60, 200]

    map_df["color"] = map_df["score"].apply(_color)
    map_df["radius"] = (map_df["score"].fillna(0.3) * 150_000 + 40_000).astype(int)
    map_df["score_txt"] = (map_df["score"] * 100).round(1).astype(str) + "%"
    map_df["color_val"] = [[60, 130, 255, 220]] * len(map_df)
    map_df["role_disp"] = map_df["role"].map(
        lambda r: ROLE_LABELS[LANG].get(r, r))

    tooltip = {
        "html": f"<b>{{name}}</b><br/>{S['tt_role']}: {{role_disp}}"
                f"<br/>{S['tt_score']}: {{score_txt}}"
                f"<br/>{S['tt_lith']}: {{lithology_class}}",
        "style": {"background": "#2C2923", "color": "white",
                  "font-size": "13px", "padding": "6px"},
    }
    try:
        import pydeck as pdk

        view = pdk.ViewState(latitude=20, longitude=10, zoom=1, pitch=0)
        layers = []
        val_df = map_df[map_df["role"] == "validation"]
        cand_df = map_df[map_df["role"] != "validation"]
        if len(val_df):
            layers.append(pdk.Layer(
                "ScatterplotLayer",
                data=val_df,
                get_position="[lon, lat]",
                get_fill_color="color_val",
                get_radius=110_000,
                stroked=True,
                get_line_color=[230, 230, 230],
                line_width_min_pixels=1,
                radius_min_pixels=6,
                radius_max_pixels=18,
                pickable=True,
                auto_highlight=True,
            ))
        if len(cand_df):
            layers.append(pdk.Layer(
                "ScatterplotLayer",
                data=cand_df,
                get_position="[lon, lat]",
                get_fill_color="color",
                get_radius="radius",
                radius_min_pixels=6,
                radius_max_pixels=18,
                pickable=True,
                auto_highlight=True,
            ))
        st.pydeck_chart(
            pdk.Deck(layers=layers, initial_view_state=view, tooltip=tooltip),
            width="stretch",
        )
        st.caption(S["map_caption"])
    except ImportError:
        st.info(S["map_fallback"])
        st.map(map_df, size=200_000)


# ── Remote imagery helpers (visual evidence panel) ──────────────────────────

@st.cache_data(ttl=3600, show_spinner=False)
def _fetch_preview_png(url: str) -> bytes:
    """Fetch remote satellite/WMS preview PNG; raises on error so failures are not cached."""
    resp = requests.get(
        url,
        timeout=8,
        headers={"User-Agent": "SpaceApps2026-Endulus-AnalogFinder/1.0"},
    )
    resp.raise_for_status()
    ctype = resp.headers.get("Content-Type", "").lower()
    if not ctype.startswith("image/"):
        raise ValueError(f"Unexpected content type ({ctype or 'unknown'})")
    return resp.content


def _safe_fetch_preview_png(url: str) -> tuple[bytes | None, str]:
    """Non-cached wrapper around _fetch_preview_png so transient errors can retry immediately."""
    try:
        return _fetch_preview_png(url), ""
    except (requests.RequestException, ValueError) as exc:
        LOGGER.warning("Preview fetch failed for %s: %s", url, exc)
        return None, str(exc)


# ═══════════════════════════════════════════════════════════════════════════════
# MAIN UI
# ═══════════════════════════════════════════════════════════════════════════════

moon_df, earth_df = load_data(
    _source_mtime("features_moon"),
    _source_mtime("features_earth"),
)

# ── SIDEBAR ──────────────────────────────────────────────────────────────────
with st.sidebar:
    lang_display = st.radio("Dil / Language", ["Türkçe", "English"],
                            horizontal=True, key="lang")
    LANG = "tr" if lang_display == "Türkçe" else "en"
    S = I18N[LANG]
    AXIS_LABELS = AXIS_LABELS_ALL[LANG]
    MISSION_LABELS = MISSION_LABELS_ALL[LANG]
    BREAKDOWN_NOTES = BREAKDOWN[LANG]

    st.header(S["settings"])

    body = "Moon"
    st.caption(S["ref_body"])
    ref_df = moon_df

    refs = ref_df[ref_df["role"] == "reference"].reset_index(drop=True)

    ref_name = st.selectbox(S["ref_site"], refs["name"].tolist())
    ref_row = refs[refs["name"] == ref_name].iloc[0]
    st.caption(S["site_meta"].format(
        sid=ref_row["site_id"], lat=ref_row["lat"], lon=ref_row["lon"],
        lith=ref_row.get("lithology_class", "—")))

    mission = st.selectbox(
        S["mission_uc"],
        list(MISSION_PRESETS.keys()),
        format_func=lambda k: MISSION_LABELS.get(k, k),
    )

    top_n = st.slider(
        S["top_n"], 1, max(2, len(earth_df)), min(6, len(earth_df))
    )
    min_score = st.slider(
        S["thr"], 0.30, 0.95, 0.70, 0.05,
        help=S["thr_help"],
    )

# ── TITLE ────────────────────────────────────────────────────────────────────
st.title(S["app_title"])
st.caption(S["app_caption"])

# ── COMPUTE SCORES (leader's module) ─────────────────────────────────────────
result, long_scores = score_earth(ref_row, earth_df, mission)
top = result.head(top_n)
axes = list(AXES.keys())  # mobility, thermal, surface

# ── REFERENCE SITE VALUES ────────────────────────────────────────────────────
ref_features = [f for feats in AXES.values() for f in feats]
ref_tbl = pd.DataFrame({
    "feature": ref_features,
    "value": [round(float(ref_row.get(f, np.nan)), 3) for f in ref_features],
    "unit": [FEATURE_UNITS.get(f, "—") for f in ref_features],
    "sd": [round(float(ref_row.get(f"{f}_sd", np.nan)), 3) for f in ref_features],
    "res_m": [ref_row.get(f"{f}_res_m", np.nan) for f in ref_features],
    "source": [str(ref_row.get(f"{f}_src", "—")) for f in ref_features],
})
with st.expander(S["ref_meas"].format(ref=ref_name), expanded=False):
    st.dataframe(ref_tbl, width="stretch", hide_index=True)
    st.caption(S["ref_meas_note"])

# ── TABS ─────────────────────────────────────────────────────────────────────
tab_map, tab_radar, tab_table, tab_validation, tab_portfolio, tab_breakdown = st.tabs(
    S["tabs"]
)

# ── TAB 1: MAP ───────────────────────────────────────────────────────────────
with tab_map:
    st.markdown(S["map_top"].format(n=top_n, ref=ref_name))
    _map_chart(result, top_n)

# ── TAB 2: RADAR CHARTS ──────────────────────────────────────────────────────
with tab_radar:
    st.markdown(S["radar_intro"])
    per_row = 3
    for i in range(0, len(top), per_row):
        chunk = top.iloc[i:i + per_row]
        cols = st.columns(len(chunk))
        for col, (_, row) in zip(cols, chunk.iterrows()):
            with col:
                st.plotly_chart(_radar_chart(row, axes), width="stretch")
                st.caption(S["radar_overall"].format(
                    score=row["score"], n=row["n_axes_used"],
                    lith=row.get("lithology_class", "—")))

# ── TAB 3: SCORE TABLE ───────────────────────────────────────────────────────
with tab_table:
    st.markdown(S["table_intro"])
    role_filter = st.multiselect(
        S["filter_role"], ["validation", "candidate"],
        default=["validation", "candidate"],
        format_func=lambda r: ROLE_LABELS[LANG].get(r, r),
        help=S["filter_help"],
    )
    shown = result if not role_filter else result[result["role"].isin(role_filter)]

    def _fmt(score: float, lo: float, hi: float) -> str:
        if np.isnan(score):
            return "—"
        if np.isnan(lo) or np.isnan(hi):
            return f"{score:.2f}"
        return f"{score:.2f} [{lo:.2f}–{hi:.2f}]"

    ref_lith = str(ref_row.get("lithology_class", ""))
    rows = []
    for _, r in shown.iterrows():
        lith = str(r.get("lithology_class", "—"))
        rec = {
            S["col_site"]: r["name"],
            S["col_role"]: ROLE_LABELS[LANG].get(r["role"], r["role"]),
            S["col_lith"]: (
                S["matches_ref"].format(lith=lith)
                if ref_lith and lith == ref_lith else lith
            ),
            S["col_overall"]: "—" if np.isnan(r["score"]) else f"{r['score']:.3f}",
        }
        for a in axes:
            rec[AXIS_LABELS[a]] = _fmt(
                r.get(f"score_{a}", np.nan),
                r.get(f"ci_low_{a}", np.nan),
                r.get(f"ci_high_{a}", np.nan),
            )
        rows.append(rec)
    st.dataframe(pd.DataFrame(rows), width="stretch", hide_index=True)
    st.caption(S["table_caption"])

# ── TAB 4: VALIDATION (blind recovery of known analogues) ────────────────────
with tab_validation:
    st.markdown(S["val_intro"].format(k=VALIDATION_TOP_K, n=len(earth_df)))
    val = run_blind_validation(long_scores, earth_df, top_k=VALIDATION_TOP_K)
    val = val.merge(earth_df[["site_id", "name"]], on="site_id", how="left")

    recovered = int(val["in_top_k"].sum())
    st.metric(S["val_metric"], f"{recovered} / {len(val)}")

    fig = go.Figure()
    for axis in axes:
        sub = val[val["axis"] == axis].dropna(subset=["rank"])
        fig.add_trace(go.Bar(
            y=sub["name"], x=sub["rank"], orientation="h",
            name=AXIS_LABELS[axis],
        ))
    fig.update_layout(
        template="plotly_white",
        barmode="group",
        xaxis=dict(
            autorange="reversed",
            title=S["rank_axis"],
            gridcolor="rgba(55,48,38,0.14)",
            zeroline=False,
        ),
        yaxis=dict(gridcolor="rgba(55,48,38,0.10)"),
        margin=dict(l=10, r=10, t=10, b=10),
        height=320,
        legend=dict(orientation="h", y=1.12),
        colorway=["#8A5A18", "#66838A", "#7B8088"],
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(color="#2C2923"),
    )
    st.plotly_chart(fig, width="stretch")

    st.dataframe(
        val[["name", "axis", "rank", "n_sites", "in_top_k"]]
        .rename(columns={
            "name": S["val_col_site"],
            "axis": S["val_col_axis"],
            "rank": S["val_col_rank"],
            "n_sites": S["val_col_nsites"],
            "in_top_k": f"in_top_{VALIDATION_TOP_K}",
        })
        .sort_values([S["val_col_site"], S["val_col_axis"]]),
        width="stretch", hide_index=True,
    )

# ── TAB 5: PORTFOLIO (greedy set-cover heuristic) ────────────────────────────
with tab_portfolio:
    st.markdown(S["port_intro"].format(thr=min_score))
    selected_ids, uncovered = select_portfolio(long_scores, min_score, axes=axes)
    if not selected_ids:
        st.info(S["port_none"].format(thr=min_score))
    else:
        rows = []
        for sid in selected_ids:
            grp = long_scores[
                (long_scores["site_id"] == sid) & long_scores["score"].notna()
            ]
            covered = [AXIS_LABELS[a] for a, s in zip(grp["axis"], grp["score"])
                       if s >= min_score]
            name = earth_df.loc[earth_df["site_id"] == sid, "name"].iloc[0]
            rows.append({
                S["col_pick"]: len(rows) + 1,
                S["col_site"]: name,
                S["col_covers"]: ", ".join(covered),
            })
        st.dataframe(pd.DataFrame(rows), width="stretch", hide_index=True)

        st.markdown(
            S["uncovered"]
            + (", ".join(AXIS_LABELS[a] for a in uncovered)
               if uncovered else S["covered_all"])
        )

# ── TAB 6: ANALOGY LIMITS ────────────────────────────────────────────────────
with tab_breakdown:
    st.markdown(BREAKDOWN_NOTES)
    st.divider()
    sel_name = st.selectbox(
        S["inspect"], result["name"].tolist(), index=0,
        help=S["inspect_help"],
    )
    inspected = result[result["name"] == sel_name].iloc[0]
    cand_row = earth_df[earth_df["site_id"] == inspected["site_id"]].iloc[0]

    # ── Visual & topographic context inspector (evidence panel) ─────────────
    # Purpose: evidence & exploration only. Imagery never creates or changes
    # a score — the quantitative per-axis scores + CIs below are the basis of
    # every claim (AGENTS.md rule 3: every number carries its *_src).
    is_moon_ref = (str(ref_row.get("body", body)).strip().lower() == "moon")

    # Earth candidate: geodesic bbox for a ~2x-radius view window (WGS84).
    lat_c = float(cand_row["lat"])
    lon_c = float(cand_row["lon"])
    rad_c_m = float(cand_row.get("radius_m", 1000.0))
    half_box_m = max(rad_c_m * 1.5, 1500.0)

    # Moon reference: south-pole stereographic metric coords (EPSG:32761,
    # R = 1,737,400 m, lat_0 = -90°, lon_0 = 0°), centred on the selected
    # ref site — never pinned to (0, 0).
    moon_bbox = None
    lat_r = lon_r = rad_r_m = np.nan
    if is_moon_ref:
        lat_r = float(ref_row["lat"])
        lon_r = float(ref_row["lon"])
        rad_r_m = float(ref_row.get("radius_m", 1000.0))
        r_m = 2.0 * 1_737_400.0 * np.tan(np.radians(90.0 + lat_r) / 2.0)
        x_m = r_m * np.sin(np.radians(lon_r))
        y_m = r_m * np.cos(np.radians(lon_r))
        pad_m = 15_000.0  # 30x30 km regional context window around the ref site
        moon_bbox = (f"{x_m - pad_m:.1f},{y_m - pad_m:.1f},"
                     f"{x_m + pad_m:.1f},{y_m + pad_m:.1f}")

    st.markdown(S["visual_head"].format(ref=ref_name, cand=sel_name))
    c_moon_wac, c_moon_lola, c_earth_opt = st.columns(3)

    with c_moon_wac:
        st.markdown(f"**{S['moon_opt']}**")
        if is_moon_ref and moon_bbox:
            wac_url = (
                "https://planetarymaps.usgs.gov/cgi-bin/mapserv"
                "?map=/maps/earth/moon_spole.map&SERVICE=WMS&VERSION=1.1.1"
                "&REQUEST=GetMap&LAYERS=LRO_WAC_south&STYLES=&SRS=EPSG:32761"
                f"&BBOX={moon_bbox}&WIDTH=420&HEIGHT=420&FORMAT=image/png"
            )
            img, err = _safe_fetch_preview_png(wac_url)
            if img is not None:
                st.image(
                    img,
                    caption=S["wac_cap"].format(
                        ref=ref_name, lat=lat_r, lon=lon_r),
                )
            else:
                st.info(S["wac_err"].format(err=err))
        else:
            st.info(S["wms_moon_only"])
        st.caption(S["src_wac"])

    with c_moon_lola:
        st.markdown(f"**{S['moon_topo']}**")
        if is_moon_ref and moon_bbox:
            lola_url = (
                "https://planetarymaps.usgs.gov/cgi-bin/mapserv"
                "?map=/maps/earth/moon_spole.map&SERVICE=WMS&VERSION=1.1.1"
                "&REQUEST=GetMap&LAYERS=LOLA_south&STYLES=&SRS=EPSG:32761"
                f"&BBOX={moon_bbox}&WIDTH=420&HEIGHT=420&FORMAT=image/png"
            )
            img, err = _safe_fetch_preview_png(lola_url)
            if img is not None:
                st.image(
                    img,
                    caption=S["lola_cap"].format(
                        ref=ref_name, rad=rad_r_m),
                )
            else:
                st.info(S["lola_err"].format(err=err))
        else:
            st.info(S["wms_moon_only"])
        st.caption(S["src_lola"])

    with c_earth_opt:
        st.markdown(f"**{S['earth_opt']}**")
        img = used_km = None
        err = ""
        # First try the ~2x-radius window; if the export service has no
        # imagery at that pixel resolution (e.g. open ocean), retry once
        # with a 3x-wider regional window before surfacing the error.
        for hb_m in (half_box_m, half_box_m * 3.0):
            dlat_h = hb_m / 111_320.0
            dlon_h = hb_m / (111_320.0 * max(np.cos(np.radians(lat_c)), 0.1))
            esri_url = (
                "https://server.arcgisonline.com/ArcGIS/rest/services/"
                "World_Imagery/MapServer/export"
                f"?bbox={lon_c - dlon_h:.6f},{lat_c - dlat_h:.6f},"
                f"{lon_c + dlon_h:.6f},{lat_c + dlat_h:.6f}"
                "&bboxSR=4326&imageSR=4326&size=420,420&format=png&f=image"
            )
            img, err = _safe_fetch_preview_png(esri_url)
            if img is not None:
                used_km = 2 * hb_m / 1000
                break
        if img is not None:
            st.image(
                img,
                caption=S["esri_cap"].format(
                    cand=sel_name, lat=lat_c, lon=lon_c, km=used_km,
                    rad=rad_c_m),
            )
        else:
            st.info(S["esri_err"].format(err=err))
        st.caption(S["src_esri"])
        wv_url = (
            f"https://worldview.earthdata.nasa.gov/"
            f"?v={lon_c - 0.15:.4f},{lat_c - 0.15:.4f},"
            f"{lon_c + 0.15:.4f},{lat_c + 0.15:.4f}"
            "&l=Reference_Labels_15m,MODIS_Terra_Land_Surface_Temp_Day,"
            "Coastlines_15m"
        )
        st.markdown(
            f"[{S['wv_link']}]({wv_url}) · "
            f"[{S['gmaps_link']}](https://www.google.com/maps/@"
            f"{lat_c:.5f},{lon_c:.5f},14z/data=!3m1!1e3)"
        )

    # Scientific context: imagery must be judged against the numbers.
    ci_lines = [
        f"**{AXIS_LABELS[a]}:** "
        f"{float(inspected.get(f'score_{a}', np.nan)):.2f} "
        f"({S['quant_range'].format(lo=float(inspected.get(f'ci_low_{a}', np.nan)), hi=float(inspected.get(f'ci_high_{a}', np.nan)))})"
        for a in AXIS_LABELS
    ]
    st.info(S["quant_head"] + " · ".join(ci_lines) + S["quant_tail"])

    st.markdown(S["gaps_head"].format(cand=sel_name, ref=ref_name))
    gaps = axis_gaps(ref_row, earth_df)
    gaps = gaps[gaps["site_id"] == inspected["site_id"]]
    if gaps.empty:
        st.info(S["gaps_none"])
    else:
        gaps = gaps.sort_values("z_diff", key=lambda s: s.abs(), ascending=False)
        # Source + native-resolution transparency (AGENTS.md §5): the jury
        # must see that e.g. a ~1 km thermal product cannot resolve a
        # 500 m site, while the DEM features are 30 m.
        gaps["ref_src"] = gaps["feature"].map(
            lambda f: str(ref_row.get(f"{f}_src", "—")))
        gaps["ref_res_m"] = gaps["feature"].map(
            lambda f: float(ref_row.get(f"{f}_res_m", np.nan)))
        gaps["cand_src"] = gaps["feature"].map(
            lambda f: str(cand_row.get(f"{f}_src", "—")))
        gaps["cand_res_m"] = gaps["feature"].map(
            lambda f: float(cand_row.get(f"{f}_res_m", np.nan)))
        show = gaps[["feature", "ref_value", "cand_value", "diff", "z_diff",
                     "ref_src", "ref_res_m", "cand_src", "cand_res_m"]]
        st.dataframe(show.round(3), width="stretch", hide_index=True)
        st.caption(S["gaps_caption"])

# ── FOOTER ───────────────────────────────────────────────────────────────────
st.divider()
st.caption(S["footer"])
