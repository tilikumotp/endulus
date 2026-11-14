"""app/main.py — Moon/Mars ↔ Earth Analog Finder (UI only).

Scores come from src/scoring (axis_scores_with_draws, axis_pivot,
combine_axes_with_uncertainty, axis_gaps) — this app does NOT compute
its own scores. Data is loaded directly from verified orbital parquets
in data/processed/. All user-visible strings come from app/i18n.py
(Turkish default + English) — no hardcoded copy in this file.
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

# ── make src/scoring and app/ importable ─────────────────────────────────────
ROOT = pathlib.Path(__file__).resolve().parent.parent
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))
if str(ROOT / "app") not in sys.path:
    sys.path.insert(0, str(ROOT / "app"))

from scoring.config import AXES, MISSION_PRESETS  # noqa: E402
from scoring.similarity import (  # noqa: E402
    axis_gaps,
    axis_pivot,
    axis_scores_with_draws,
    combine_axes_with_uncertainty,
)
from scoring.validation import run_blind_validation  # noqa: E402

import i18n  # noqa: E402
import terrain  # noqa: E402

LOGGER = logging.getLogger(__name__)

# ── page config ──────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Moon <-> Earth Similar Conditions Analysis",
    page_icon="🌕",
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

FEATURE_UNITS = {
    "slope_mean": "deg", "slope_p90": "deg", "roughness": "m",
    "relief": "m", "temp_amplitude": "K",
    "thermal_inertia": "J m^-2 K^-1 s^-1/2", "albedo": "0-1",
}

VALIDATION_TOP_K = 5  # descriptive rank threshold, not a pass/fail criterion

# Continent buckets for the table filter, resolved from site coordinates.
REGION_OPTIONS = [
    "all", "europe", "asia", "africa", "north_america",
    "south_america", "oceania", "antarctica",
]

# Active language + shorthand resolver (updated in the sidebar).
LANG = i18n.DEFAULT_LANG


def T(key: str, **kwargs: object) -> str:
    """Shorthand: translated string in the active language."""
    return i18n.t(key, LANG, **kwargs)


AXIS_LABELS = {a: i18n.t(f"axis_{a}", LANG)
               for a in ("mobility", "thermal", "surface")}


# ── data loading ─────────────────────────────────────────────────────────────
def _load_body(stem: str) -> pd.DataFrame:
    proc = PROC_DIR / f"{stem}.parquet"
    if proc.exists():
        return pd.read_parquet(proc)
    st.error(T("data_missing", stem=stem))
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


# ── scoring (scoring module, called as-is) ───────────────────────────────────
def score_earth(
    ref_row: pd.Series, earth_df: pd.DataFrame, mission: str
) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Run per-axis scoring and weighted combination with uncertainty draws.

    Returns the ranked result and per-axis scores used by validation/portfolio.
    """
    long_scores, score_draws = axis_scores_with_draws(ref_row, earth_df)
    wide = axis_pivot(long_scores)
    overall = combine_axes_with_uncertainty(
        long_scores, score_draws, MISSION_PRESETS[mission]
    ).rename(columns={"q05": "q05_overall", "q95": "q95_overall"})

    result = (
        earth_df[["site_id", "name", "role", "lat", "lon", "lithology_class"]]
        .merge(overall, on="site_id", how="left")
        .merge(wide, on="site_id", how="left")
        .sort_values("score", ascending=False, na_position="last")
        .reset_index(drop=True)
    )
    return result, long_scores


def _region_of(lat: float, lon: float) -> str:
    """Continent bucket resolved from site coordinates (rules checked in order)."""
    if lat < -60:
        return "antarctica"
    if lat < 0 and lon > 110:
        return "oceania"
    if lon < -30:
        return "south_america" if lat < 15 else "north_america"
    if -20 <= lon < 35 and lat < 37:
        return "africa"
    if lon > 26:
        return "asia"
    return "europe"


def _role_text(role: str) -> str:
    """Readable role name for the active language."""
    return T("role_validation" if role == "validation" else "role_candidate")


def _terrain_figure(row: pd.Series, exag: int, orbit: float) -> go.Figure:
    """Plotly 3D surface with hillshade colouring for one site."""
    z, _ = terrain.get_tile(row)
    radius = float(row.get("radius_m", 1000.0) or 1000.0)
    shade = terrain.hillshade(z, radius)
    z_disp = z * exag
    xs = np.linspace(-1.0, 1.0, z.shape[1])  # km across the 2r window
    ys = np.linspace(-1.0, 1.0, z.shape[0])

    fig = go.Figure()
    fig.add_trace(go.Surface(
        x=xs, y=ys, z=z_disp, surfacecolor=shade,
        colorscale="gray", showscale=False,
        hovertemplate=T("terrain_hover"),
    ))
    # r = 1 km measurement-ring outline, drawn above the surface so the
    # measured area stays visible at every camera angle (2D-card parity).
    t = np.linspace(0.0, 2.0 * np.pi, 121)
    ring_z = float(np.nanmax(z_disp)) * 1.04
    fig.add_trace(go.Scatter3d(
        x=np.cos(t), y=np.sin(t), z=[ring_z] * len(t),
        mode="lines", line=dict(color="#2C2923", width=3),
        hoverinfo="skip",
    ))

    z_span = float(np.nanmax(z_disp) - np.nanmin(z_disp))
    aspect_z = float(np.clip((z_span / 1000.0) / 2.0, 0.05, 1.2))
    ang = np.radians(orbit)
    fig.update_layout(
        scene=dict(
            xaxis_visible=False, yaxis_visible=False, zaxis_visible=False,
            aspectmode="manual",
            aspectratio=dict(x=1, y=1, z=aspect_z),
            camera=dict(eye=dict(
                x=float(np.cos(ang) * 1.7),
                y=float(np.sin(ang) * 1.7),
                z=1.0,
            )),
        ),
        margin=dict(l=0, r=0, t=10, b=0),
        height=380,
        paper_bgcolor="rgba(0,0,0,0)",
        font=dict(color="#2C2923"),
    )
    return fig


def _terrain_caption(row: pd.Series, is_stub: bool) -> str:
    """One-line source + resolution + window label under a 3D card."""
    src = str(row.get("relief_src", "—")).replace("_", " ")
    res = f"{float(row.get('relief_res_m', np.nan)):g}"
    km = f"{2.0 * float(row.get('radius_m', 1000.0) or 1000.0) / 1000.0:g}"
    key = "terrain_card_stub" if is_stub else "terrain_card_source"
    return T(key, src=src, res=res, km=km)


# ── charts ───────────────────────────────────────────────────────────────────
def _radar_chart(row: pd.Series, axes: list[str]) -> go.Figure:
    """Plotly radar of per-axis scores with 5th/95th percentile lines."""
    labels = [AXIS_LABELS[a] for a in axes]
    vals = [float(row.get(f"score_{a}", np.nan)) for a in axes]
    lo = [float(row.get(f"q05_{a}", np.nan)) for a in axes]
    hi = [float(row.get(f"q95_{a}", np.nan)) for a in axes]

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
        name=T("q95_label"), hoverinfo="skip",
    ))
    fig.add_trace(go.Scatterpolar(
        r=_closed(lo), theta=labels_c,
        line=dict(color="#8A847A", width=1, dash="dot"),
        name=T("q05_label"), hoverinfo="skip",
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
        [
            "site_id", "name", "role", "lat", "lon", "score",
            "q05_overall", "q95_overall", "lithology_class",
        ]
    ].copy()

    def _color(score: float) -> list[int]:
        if np.isnan(score):
            return [128, 128, 128, 160]
        r, g = int(255 * (1 - score)), int(255 * score)
        return [r, g, 60, 200]

    map_df["color"] = map_df["score"].apply(_color)
    map_df["radius"] = (map_df["score"].fillna(0.3) * 150_000 + 40_000).astype(int)
    map_df["score_txt"] = map_df["score"].map(
        lambda value: f"{value:.3f}" if np.isfinite(value) else "—"
    )
    map_df["interval_txt"] = map_df.apply(
        lambda row: (
            f"[{row['q05_overall']:.3f}, {row['q95_overall']:.3f}]"
            if np.isfinite(row["q05_overall"])
            and np.isfinite(row["q95_overall"])
            else T("uncertainty_unavailable")
        ),
        axis=1,
    )
    map_df["role_disp"] = map_df["role"].map(_role_text)
    map_df["lith_disp"] = map_df["lithology_class"].map(
        lambda c: i18n.lith_label(str(c), LANG))

    tooltip = {
        "html": T(
            "map_tooltip",
            name="{name}", role="{role_disp}", score="{score_txt}",
            interval="{interval_txt}", lith="{lith_disp}",
        ),
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
        st.caption(T("map_caption"))
    except ImportError:
        st.info(T("map_fallback"))
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
    lang_display = st.radio(
        i18n.LANGUAGE_LABEL, ["Türkçe", "English"], horizontal=True, key="lang"
    )
    LANG = "tr" if lang_display == "Türkçe" else "en"
    AXIS_LABELS = {a: i18n.t(f"axis_{a}", LANG)
                   for a in ("mobility", "thermal", "surface")}

    st.header(T("settings_header"))

    body = "Moon"

    refs = moon_df[moon_df["role"] == "reference"].reset_index(drop=True)

    ref_name = st.selectbox(T("ref_site_label_moon"), refs["name"].tolist())
    ref_row = refs[refs["name"] == ref_name].iloc[0]
    st.caption(
        f"{ref_name} · "
        + T("ref_site_caption",
            lat=f"{float(ref_row['lat']):.2f}", lon=f"{float(ref_row['lon']):.2f}",
            lith=i18n.lith_label(str(ref_row.get("lithology_class", "")), LANG)),
        help=T("ref_site_tooltip", site_id=str(ref_row["site_id"])),
    )

    mission = st.selectbox(
        T("mission_label"),
        list(MISSION_PRESETS.keys()),
        format_func=lambda k: T(f"mission_{k}"),
    )

    top_n = st.slider(
        T("top_n_label"), 1, max(2, len(earth_df)), min(6, len(earth_df))
    )

# ── TITLE ────────────────────────────────────────────────────────────────────
st.title(T("app_title"))
st.caption(T("subtitle", n=len(earth_df)))
st.caption(T("thermal_note"))

# ── COMPUTE SCORES (scoring module) ──────────────────────────────────────────
result, long_scores = score_earth(ref_row, earth_df, mission)
result["region"] = [
    _region_of(float(la), float(lo)) for la, lo in zip(result["lat"], result["lon"])
]
top = result.head(top_n)
axes = list(AXES.keys())  # mobility, thermal, surface

# ── REFERENCE SITE VALUES ────────────────────────────────────────────────────
st.subheader(T("ref_subheader", name=ref_name, body=T("body_moon")))
ref_features = [f for feats in AXES.values() for f in feats]
ref_tbl = pd.DataFrame({
    T("ref_col_feature"): [i18n.feature_label(f, LANG) for f in ref_features],
    T("ref_col_value"): [round(float(ref_row.get(f, np.nan)), 3) for f in ref_features],
    T("ref_col_unit"): [FEATURE_UNITS.get(f, "—") for f in ref_features],
    T("ref_col_sd"): [round(float(ref_row.get(f"{f}_sd", np.nan)), 3) for f in ref_features],
    T("ref_col_res"): [ref_row.get(f"{f}_res_m", np.nan) for f in ref_features],
    T("ref_col_src"): [str(ref_row.get(f"{f}_src", "—")) for f in ref_features],
})
with st.expander(f"{T('ref_expander')} · {ref_name.split('(')[0].strip()}"):
    st.dataframe(ref_tbl, width="stretch", hide_index=True)
    st.caption(T("ref_table_caption"))
    st.caption(T("temp_note"))

# ── TABS ─────────────────────────────────────────────────────────────────────
tab_map, tab_radar, tab_terrain, tab_table, tab_validation, tab_breakdown = st.tabs([
    T("tab_map"), T("tab_radar"), T("tab_terrain"), T("tab_table"),
    T("tab_validation"), T("tab_breakdown"),
])

# ── TAB 1: MAP ───────────────────────────────────────────────────────────────
with tab_map:
    st.markdown(T("map_heading", n=top_n))
    _map_chart(result, top_n)

# ── TAB 2: RADAR CHARTS ──────────────────────────────────────────────────────
with tab_radar:
    st.markdown(T("radar_caption"))
    per_row = 3
    for i in range(0, len(top), per_row):
        chunk = top.iloc[i:i + per_row]
        cols = st.columns(len(chunk))
        for col, (_, row) in zip(cols, chunk.iterrows()):
            with col:
                st.plotly_chart(_radar_chart(row, axes), width="stretch")
                q05 = row.get("q05_overall", np.nan)
                q95 = row.get("q95_overall", np.nan)
                interval = (
                    f"{q05:.2f}–{q95:.2f}"
                    if np.isfinite(q05) and np.isfinite(q95)
                    else T("uncertainty_unavailable")
                )
                st.caption(T(
                    "radar_line",
                    score=f"{float(row['score']):.2f}",
                    interval=interval,
                    n=int(row.get("n_axes_used", 0)), total=len(axes),
                    lith=i18n.lith_label(str(row.get("lithology_class", "")), LANG),
                ))

# ── TAB 3: 3D TERRAIN (stub until M6/E7 DEM tiles land) ──────────────────────
with tab_terrain:
    st.markdown(T("terrain_intro"))
    terrain_sel_name = st.selectbox(
        T("terrain_pick"), result["name"].tolist(), index=0
    )
    terrain_row = result[result["name"] == terrain_sel_name].iloc[0]
    terrain_cand = earth_df[earth_df["site_id"] == terrain_row["site_id"]].iloc[0]

    exag = st.slider(T("terrain_exag_label"), 1, 4, 2)
    st.caption(T("terrain_exag_note"))
    orbit = st.slider(T("terrain_orbit_label"), 0, 360, 0, 5)

    col_moon, col_earth = st.columns(2)
    _, moon_stub = terrain.get_tile(ref_row)
    _, earth_stub = terrain.get_tile(terrain_cand)
    any_stub = moon_stub or earth_stub
    with col_moon:
        st.markdown(f"**{ref_name} ({T('body_moon')})**")
        st.plotly_chart(_terrain_figure(ref_row, exag, orbit), width="stretch")
        st.caption(_terrain_caption(ref_row, moon_stub))
    with col_earth:
        st.markdown(f"**{terrain_sel_name} ({T('body_earth')})**")
        st.plotly_chart(_terrain_figure(terrain_cand, exag, orbit), width="stretch")
        st.caption(_terrain_caption(terrain_cand, earth_stub))

    if any_stub:
        st.info(T("terrain_stub_note"))

# ── TAB 4: SCORE TABLE ───────────────────────────────────────────────────────
with tab_table:
    st.markdown(T("table_caption"))
    lith_opts = sorted(set(result["lithology_class"].dropna().astype(str)))
    lith_filter = st.multiselect(
        T("filter_lith"), lith_opts,
        format_func=lambda c: i18n.lith_label(c, LANG),
    )
    region_filter = st.selectbox(
        T("filter_region"), REGION_OPTIONS,
        format_func=lambda k: T(f"region_{k}"),
    )
    shown = result
    if lith_filter:
        shown = shown[shown["lithology_class"].astype(str).isin(lith_filter)]
    if region_filter != "all":
        shown = shown[shown["region"] == region_filter]

    def _fmt(score: float, lo: float, hi: float) -> str:
        if np.isnan(score):
            return ""
        if np.isnan(lo) or np.isnan(hi):
            return f"{score:.2f}"
        return f"{score:.2f} [{lo:.2f}–{hi:.2f}]"

    ref_lith = str(ref_row.get("lithology_class", ""))
    rows = []
    for _, r in shown.iterrows():
        lith_code = str(r.get("lithology_class", ""))
        lith_txt = i18n.lith_label(lith_code, LANG)
        if ref_lith and lith_code == ref_lith:
            lith_txt += " ✓"
        rec = {
            T("col_site"): r["name"],
            T("col_role"): _role_text(r["role"]),
            T("col_lith"): lith_txt,
            T("col_overall"): _fmt(
                r["score"], r.get("q05_overall", np.nan),
                r.get("q95_overall", np.nan),
            ),
        }
        for a in axes:
            rec[AXIS_LABELS[a]] = _fmt(
                r.get(f"score_{a}", np.nan),
                r.get(f"q05_{a}", np.nan),
                r.get(f"q95_{a}", np.nan),
            )
        rows.append(rec)
    st.dataframe(pd.DataFrame(rows), width="stretch", hide_index=True)
    st.caption(T("table_footer_caption"))

# ── TAB 5: VALIDATION (blind ranking diagnostic) ────────────────────────────
with tab_validation:
    st.markdown(T("val_intro"))
    val = run_blind_validation(long_scores, earth_df, top_k=VALIDATION_TOP_K)
    val = val.merge(earth_df[["site_id", "name"]], on="site_id", how="left")

    top_k_count = int(val["in_top_k"].sum())
    st.metric(
        T("val_metric_label"), f"{top_k_count} / {len(val)}",
        help=T("val_metric_help"),
    )

    # Simple summary chart: one bar per criterion, counting how many of the
    # 10 comparisons had a known analogue inside the top 5.
    per_axis = [
        int(val[val["axis"] == a]["in_top_k"].sum()) for a in axes
    ]
    n_val_sites = int((val["axis"] == axes[0]).sum())
    fig = go.Figure(go.Bar(
        x=[AXIS_LABELS[a] for a in axes],
        y=per_axis,
        marker_color=["#8A5A18", "#66838A", "#7B8088"][: len(axes)],
        text=[f"{c} / {n_val_sites}" for c in per_axis],
        textposition="outside",
        cliponaxis=False,
    ))
    fig.update_layout(
        template="plotly_white",
        yaxis=dict(
            range=[0, max(n_val_sites, max(per_axis) + 1)],
            dtick=max(n_val_sites // 5, 1),
            gridcolor="rgba(55,48,38,0.14)",
            zeroline=False,
        ),
        margin=dict(l=10, r=10, t=30, b=10),
        height=340,
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(color="#2C2923"),
    )
    st.plotly_chart(fig, width="stretch")
    st.caption(T("val_chart_caption"))

    val_tbl = val[["name", "axis", "rank", "in_top_k"]].copy()
    val_tbl["axis"] = val_tbl["axis"].map(lambda a: AXIS_LABELS.get(a, a))
    val_tbl["verdict"] = val_tbl["in_top_k"].map(
        lambda b: T("val_verdict_yes") if b else T("val_verdict_no"))
    val_tbl = val_tbl.drop(columns=["in_top_k"])
    val_tbl.columns = [
        T("val_col_site"), T("val_col_axis"), T("val_col_rank"),
        T("val_col_verdict"),
    ]
    st.dataframe(val_tbl.sort_values(
        [T("val_col_axis"), T("val_col_rank")]), width="stretch", hide_index=True)

# ── TAB 6: ANALOGY LIMITS ────────────────────────────────────────────────────
with tab_breakdown:
    st.markdown(T("breakdown_notes"))
    st.divider()
    sel_name = st.selectbox(
        T("inspect_label"), result["name"].tolist(), index=0,
        help=T("inspect_help"),
    )
    inspected = result[result["name"] == sel_name].iloc[0]
    cand_row = earth_df[earth_df["site_id"] == inspected["site_id"]].iloc[0]

    # ── Visual & topographic context inspector (evidence panel) ─────────────
    # Purpose: evidence & exploration only. Imagery never creates or changes
    # a score — the quantitative per-axis scores + percentiles below are the
    # basis of every claim.
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

    st.markdown(T("vis_heading", ref=ref_name, sel=sel_name))
    c_moon_wac, c_moon_lola, c_earth_opt = st.columns(3)

    with c_moon_wac:
        st.markdown(f"**{T('vis_col_moon_opt')}**")
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
                    caption=T("vis_wac_caption", ref=ref_name,
                              lat=f"{lat_r:.2f}", lon=f"{lon_r:.2f}"),
                )
            else:
                st.info(T("vis_wac_error", err=err))
        else:
            st.info(T("vis_moon_only_note"))
        st.caption(T("vis_wac_source"))

    with c_moon_lola:
        st.markdown(f"**{T('vis_col_moon_relief')}**")
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
                    caption=T("vis_lola_caption", ref=ref_name,
                              rad=f"{rad_r_m:.0f}"),
                )
            else:
                st.info(T("vis_lola_error", err=err))
        else:
            st.info(T("vis_moon_only_note"))
        st.caption(T("vis_lola_source"))

    with c_earth_opt:
        st.markdown(f"**{T('vis_col_earth')}**")
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
                caption=T("vis_earth_caption", sel=sel_name,
                          lat=f"{lat_c:.4f}", lon=f"{lon_c:.4f}",
                          km=f"{used_km:.1f}", rad=f"{rad_c_m:.0f}"),
            )
        else:
            st.info(T("vis_earth_error", err=err))
        st.caption(T("vis_earth_source"))
        wv_url = (
            f"https://worldview.earthdata.nasa.gov/"
            f"?v={lon_c - 0.15:.4f},{lat_c - 0.15:.4f},"
            f"{lon_c + 0.15:.4f},{lat_c + 0.15:.4f}"
            "&l=Reference_Labels_15m,MODIS_Terra_Land_Surface_Temp_Day,"
            "Coastlines_15m"
        )
        gmaps_url = (
            f"https://www.google.com/maps/@"
            f"{lat_c:.5f},{lon_c:.5f},14z/data=!3m1!1e3"
        )
        st.markdown(
            T("vis_link_worldview", url=wv_url) + " · "
            + T("vis_link_gmaps", url=gmaps_url)
        )

    # Scientific context: imagery must be judged against the numbers.
    ci_lines = []
    for axis in axes:
        score = float(inspected.get(f"score_{axis}", np.nan))
        q05 = float(inspected.get(f"q05_{axis}", np.nan))
        q95 = float(inspected.get(f"q95_{axis}", np.nan))
        score_text = f"{score:.2f}" if np.isfinite(score) else "—"
        interval = (
            f"{q05:.2f}–{q95:.2f}"
            if np.isfinite(q05) and np.isfinite(q95)
            else T("uncertainty_unavailable")
        )
        ci_lines.append(T("vis_quant_line", axis=AXIS_LABELS[axis],
                          score=score_text, lo=interval.split("–")[0],
                          hi=interval.split("–")[-1]))
    st.info(T("vis_quant_head") + " · ".join(ci_lines) + "\n\n" + T("vis_quant_msg"))

    st.markdown(T("gaps_heading", sel=sel_name, ref=ref_name))
    gaps = axis_gaps(ref_row, earth_df)
    gaps = gaps[gaps["site_id"] == inspected["site_id"]]
    if gaps.empty:
        st.info(T("gaps_empty"))
    else:
        gaps = gaps.sort_values("z_diff", key=lambda s: s.abs(), ascending=False)
        # Source + native-resolution transparency: e.g. a ~1 km thermal
        # product cannot resolve a 500 m site, while the DEM features
        # are 30 m.
        gaps["ref_src"] = gaps["feature"].map(
            lambda f: str(ref_row.get(f"{f}_src", "—")))
        gaps["ref_res_m"] = gaps["feature"].map(
            lambda f: float(ref_row.get(f"{f}_res_m", np.nan)))
        gaps["cand_src"] = gaps["feature"].map(
            lambda f: str(cand_row.get(f"{f}_src", "—")))
        gaps["cand_res_m"] = gaps["feature"].map(
            lambda f: float(cand_row.get(f"{f}_res_m", np.nan)))
        gaps["feature"] = gaps["feature"].map(lambda f: i18n.feature_label(f, LANG))
        keep = ["feature", "ref_value", "cand_value", "diff", "z_diff",
                "ref_src", "ref_res_m", "cand_src", "cand_res_m"]
        show = gaps[keep].copy()
        show.columns = i18n.GAP_COLUMNS[LANG]
        st.dataframe(show.round(3), width="stretch", hide_index=True)
        st.caption(T("gaps_caption"))
