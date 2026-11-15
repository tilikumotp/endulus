"""app/main.py — Moon South Pole ↔ Earth Multi-Axis Analog Finder (UI only).

Scores come from src/scoring (axis_scores_with_draws, axis_pivot,
combine_axes_with_uncertainty, axis_gaps, select_portfolio,
run_blind_validation, expanded_interval) — this app does NOT compute its
own scores. Data is loaded directly from verified orbital parquets and
local visual/3D assets in data/processed/. All user-visible strings come
from app/i18n.py (Turkish default + English) — no hardcoded copy here.
"""

from __future__ import annotations

import json
import pathlib
import sys

import numpy as np
import pandas as pd
import plotly.graph_objects as go
import streamlit as st

# ── make src/scoring and app/ importable ─────────────────────────────────────
ROOT = pathlib.Path(__file__).resolve().parent.parent
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))
if str(ROOT / "app") not in sys.path:
    sys.path.insert(0, str(ROOT / "app"))

from scoring.config import AXES, MISSION_PRESETS  # noqa: E402
from scoring.display import expanded_interval  # noqa: E402
from scoring.portfolio import select_portfolio  # noqa: E402
from scoring.similarity import (  # noqa: E402
    axis_gaps,
    axis_pivot,
    axis_scores_with_draws,
    combine_axes_with_uncertainty,
)
from scoring.validation import run_blind_validation  # noqa: E402

import i18n  # noqa: E402
import terrain  # noqa: E402

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
MOON_ATLAS_DIR = PROC_DIR / "moon_atlas"
EARTH_ATLAS_DIR = PROC_DIR / "earth_atlas"

PORTFOLIO_THRESHOLD = 0.70

FEATURE_UNITS = {
    "slope_mean": "deg",
    "slope_p90": "deg",
    "roughness": "m",
    "relief": "m",
    "temp_amplitude": "K",
    "thermal_inertia": "J m^-2 K^-1 s^-1/2",
    "albedo": "0-1",
}

# Continent buckets for the table filter, resolved from site coordinates.
REGION_OPTIONS = [
    "all",
    "europe",
    "asia",
    "africa",
    "north_america",
    "south_america",
    "oceania",
    "antarctica",
]

# Active language + shorthand resolver (updated in the sidebar).
LANG = i18n.DEFAULT_LANG


def T(key: str, **kwargs: object) -> str:
    """Shorthand: translated string in the active language."""
    return i18n.t(key, LANG, **kwargs)


AXIS_LABELS = {
    a: i18n.t(f"axis_{a}", LANG) for a in ("mobility", "thermal", "surface")
}


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


@st.cache_data(show_spinner=False)
def load_atlas_metadata() -> tuple[dict[str, dict], dict[str, dict]]:
    """Load committed Moon and Earth visual atlas metadata JSONs."""
    moon_meta: dict[str, dict] = {}
    moon_json = MOON_ATLAS_DIR / "atlas_metadata.json"
    if moon_json.exists():
        with open(moon_json, encoding="utf-8") as fh:
            for item in json.load(fh):
                moon_meta[str(item.get("site_id", ""))] = item

    earth_meta: dict[str, dict] = {}
    earth_json = EARTH_ATLAS_DIR / "metadata.json"
    if earth_json.exists():
        with open(earth_json, encoding="utf-8") as fh:
            payload = json.load(fh)
            for item in payload.get("sites", []):
                earth_meta[str(item.get("site_id", ""))] = item

    return moon_meta, earth_meta


# ── scoring (scoring module, called as-is) ───────────────────────────────────
def score_earth(
    ref_row: pd.Series, earth_df: pd.DataFrame, mission: str
) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Run per-axis scoring and weighted combination with uncertainty draws.

    Returns the ranked result table and long-format per-axis scores used by
    the compact portfolio card and the descriptive rank diagnostic.
    """
    long_scores, score_draws = axis_scores_with_draws(ref_row, earth_df)
    wide = axis_pivot(long_scores)
    overall = combine_axes_with_uncertainty(
        long_scores, score_draws, MISSION_PRESETS[mission]
    ).rename(columns={"q05": "q05_overall", "q95": "q95_overall"})

    keep_cols = [
        "site_id",
        "name",
        "role",
        "lat",
        "lon",
        "lithology_class",
        "slope_mean",
        "roughness",
        "relief",
        "albedo",
    ]
    result = (
        earth_df[keep_cols]
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


def _format_score_interval(
    score: float, q05: float, q95: float, precision: int = 2
) -> tuple[str, bool]:
    """Format point score and expanded display interval (lo, hi, widened)."""
    if not np.isfinite(score):
        return "", False
    lo, hi, widened = expanded_interval(score, q05, q95)
    if not (np.isfinite(lo) and np.isfinite(hi)):
        return f"{score:.{precision}f}", False
    mark = "*" if widened else ""
    return f"{score:.{precision}f} [{lo:.{precision}f}–{hi:.{precision}f}]{mark}", widened


# ── charts ───────────────────────────────────────────────────────────────────
def _terrain_figure(row: pd.Series, exag: int, orbit: float) -> go.Figure:
    """Plotly 3D surface with hillshade colouring for one site."""
    z, is_stub = terrain.get_tile(row)
    radius = float(row.get("radius_m", 1000.0) or 1000.0)
    shade = terrain.hillshade(z, radius)
    z_min = float(np.nanmin(z))
    z_disp = z_min + (z - z_min) * exag
    half_km = 1.0 if is_stub else 1.1
    xs = np.linspace(-half_km, half_km, z.shape[1])
    ys = np.linspace(-half_km, half_km, z.shape[0])

    fig = go.Figure()
    fig.add_trace(
        go.Surface(
            x=xs,
            y=ys,
            z=z_disp,
            surfacecolor=shade,
            customdata=z,
            colorscale="gray",
            showscale=False,
            hovertemplate=T("terrain_hover"),
        )
    )
    # r = 1 km measurement-ring outline, drawn slightly above peak elevation
    t = np.linspace(0.0, 2.0 * np.pi, 121)
    z_span = float(np.nanmax(z_disp) - np.nanmin(z_disp))
    ring_z = float(np.nanmax(z_disp)) + max(z_span * 0.04, 2.0)
    fig.add_trace(
        go.Scatter3d(
            x=np.cos(t),
            y=np.sin(t),
            z=[ring_z] * len(t),
            mode="lines",
            line=dict(color="#2C2923", width=3),
            hoverinfo="skip",
        )
    )

    aspect_z = float(np.clip((z_span / 1000.0) / 2.0, 0.08, 1.2))
    ang = np.radians(orbit)
    fig.update_layout(
        scene=dict(
            xaxis_visible=False,
            yaxis_visible=False,
            zaxis_visible=False,
            aspectmode="manual",
            aspectratio=dict(x=1, y=1, z=aspect_z),
            camera=dict(
                eye=dict(
                    x=float(np.cos(ang) * 1.7),
                    y=float(np.sin(ang) * 1.7),
                    z=1.0,
                )
            ),
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
    km = "2.0" if is_stub else "2.2"
    key = "terrain_card_stub" if is_stub else "terrain_card_source"
    return T(key, src=src, res=res, km=km)


def _physical_scatter_chart(
    result: pd.DataFrame, ref_row: pd.Series, ref_disp_name: str
) -> go.Figure:
    """2D physical feature-space scatter (slope_mean vs albedo) for 40 Earth sites + Moon ref."""
    fig = go.Figure()

    rough_vals = result["roughness"].fillna(5.0).to_numpy(dtype=float)
    sizes = np.clip(9.0 + np.sqrt(np.maximum(rough_vals, 0.5)) * 2.2, 9.0, 24.0)

    hover_texts = []
    for _, r in result.iterrows():
        s_ov, _ = _format_score_interval(
            float(r.get("score", np.nan)),
            float(r.get("q05_overall", np.nan)),
            float(r.get("q95_overall", np.nan)),
        )
        s_mob, _ = _format_score_interval(
            float(r.get("score_mobility", np.nan)),
            float(r.get("q05_mobility", np.nan)),
            float(r.get("q95_mobility", np.nan)),
        )
        s_surf, _ = _format_score_interval(
            float(r.get("score_surface", np.nan)),
            float(r.get("q05_surface", np.nan)),
            float(r.get("q95_surface", np.nan)),
        )
        hover_texts.append(
            f"<b>{r['name']}</b> ({_role_text(str(r['role']))})<br/>"
            f"{T('col_lith')}: {i18n.lith_label(str(r.get('lithology_class', '')), LANG)}<br/>"
            f"{T('col_overall')}: {s_ov}<br/>"
            f"{AXIS_LABELS['mobility']}: {s_mob} · {AXIS_LABELS['surface']}: {s_surf}"
        )

    fig.add_trace(
        go.Scatter(
            x=result["slope_mean"],
            y=result["albedo"],
            mode="markers",
            marker=dict(
                size=sizes,
                color=result["score"],
                colorscale="YlGnBu",
                cmin=0.0,
                cmax=1.0,
                colorbar=dict(title=T("scatter_colorbar"), thickness=14),
                line=dict(
                    color=[
                        "#2B6CB0" if role == "validation" else "#3A352F"
                        for role in result["role"]
                    ],
                    width=[2.0 if role == "validation" else 1.0 for role in result["role"]],
                ),
                opacity=0.88,
            ),
            text=hover_texts,
            hovertemplate="%{text}<br/>slope_mean: %{x:.2f}° · albedo: %{y:.3f}<extra></extra>",
            name=T("body_earth"),
        )
    )

    fig.add_trace(
        go.Scatter(
            x=[float(ref_row.get("slope_mean", np.nan))],
            y=[float(ref_row.get("albedo", np.nan))],
            mode="markers+text",
            marker=dict(
                symbol="star",
                size=20,
                color="#D4AF37",
                line=dict(color="#2C2923", width=2),
            ),
            text=[f"⭐ {ref_disp_name}"],
            textposition="top center",
            hovertemplate=(
                f"<b>⭐ {ref_disp_name} ({T('body_moon')})</b><br/>"
                "slope_mean: %{x:.2f}° · albedo: %{y:.3f}<extra></extra>"
            ),
            name=ref_disp_name,
        )
    )

    max_slope = float(
        np.nanmax(
            np.append(
                result["slope_mean"].to_numpy(dtype=float),
                float(ref_row.get("slope_mean", 25.0)),
            )
        )
    )
    fig.update_layout(
        template="plotly_white",
        xaxis=dict(
            title=T("scatter_x"),
            range=[0, max(30.0, max_slope * 1.12)],
            gridcolor="rgba(55,48,38,0.14)",
        ),
        yaxis=dict(
            title=T("scatter_y"),
            range=[0, 0.75],
            gridcolor="rgba(55,48,38,0.14)",
        ),
        showlegend=False,
        margin=dict(l=20, r=20, t=20, b=20),
        height=390,
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(color="#2C2923"),
    )
    return fig


def _axis_bar_card(row: pd.Series) -> tuple[go.Figure, bool]:
    """Horizontal bar chart of Overall + 2 active axes (Mobility, Surface) with expanded_interval."""
    items = [
        (
            AXIS_LABELS["surface"],
            float(row.get("score_surface", np.nan)),
            float(row.get("q05_surface", np.nan)),
            float(row.get("q95_surface", np.nan)),
            "#66838A",
        ),
        (
            AXIS_LABELS["mobility"],
            float(row.get("score_mobility", np.nan)),
            float(row.get("q05_mobility", np.nan)),
            float(row.get("q95_mobility", np.nan)),
            "#8A5A18",
        ),
        (
            T("col_overall"),
            float(row.get("score", np.nan)),
            float(row.get("q05_overall", np.nan)),
            float(row.get("q95_overall", np.nan)),
            "#2E6B4E",
        ),
    ]

    labels = [it[0] for it in items]
    vals = [float(np.nan_to_num(it[1], nan=0.0)) for it in items]
    colors = [it[4] for it in items]
    err_plus = []
    err_minus = []
    texts = []
    any_widened = False

    for _, sc, q05, q95, _ in items:
        lo, hi, wid = expanded_interval(sc, q05, q95)
        any_widened = any_widened or wid
        if np.isfinite(sc) and np.isfinite(lo) and np.isfinite(hi):
            err_minus.append(max(0.0, sc - lo))
            err_plus.append(max(0.0, hi - sc))
            mark = "*" if wid else ""
            texts.append(f"{sc:.2f} [{lo:.2f}–{hi:.2f}]{mark}")
        elif np.isfinite(sc):
            err_minus.append(0.0)
            err_plus.append(0.0)
            texts.append(f"{sc:.2f}")
        else:
            err_minus.append(0.0)
            err_plus.append(0.0)
            texts.append("—")

    fig = go.Figure(
        go.Bar(
            y=labels,
            x=vals,
            orientation="h",
            marker_color=colors,
            error_x=dict(
                type="data",
                symmetric=False,
                array=err_plus,
                arrayminus=err_minus,
                color="#2C2923",
                thickness=1.6,
                width=5,
            ),
            text=texts,
            textposition="outside",
            cliponaxis=False,
            hovertemplate="%{y}: %{text}<extra></extra>",
        )
    )
    fig.update_layout(
        template="plotly_white",
        xaxis=dict(
            range=[0, 1.18],
            gridcolor="rgba(55,48,38,0.14)",
            zeroline=False,
        ),
        yaxis=dict(gridcolor="rgba(0,0,0,0)"),
        showlegend=False,
        margin=dict(l=16, r=48, t=36, b=16),
        title=dict(text=str(row["name"]), font=dict(size=13, color="#2C2923")),
        height=240,
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(color="#2C2923"),
    )
    return fig, any_widened


def _map_chart(result: pd.DataFrame, top_n: int) -> None:
    """pydeck scatter map of the top-N scored Earth sites.

    Known validation analogues are outlined in blue; both validation and
    candidate dot fill colours (`color_val` / `color`) and radii encode the
    selected reference/mission similarity score.
    """
    map_df = result.head(top_n)[
        [
            "site_id",
            "name",
            "role",
            "lat",
            "lon",
            "score",
            "q05_overall",
            "q95_overall",
            "lithology_class",
        ]
    ].copy()

    def _color(score: float) -> list[int]:
        if np.isnan(score):
            return [128, 128, 128, 160]
        r, g = int(255 * (1 - score)), int(255 * score)
        return [r, g, 60, 200]

    map_df["color"] = map_df["score"].apply(_color)
    map_df["color_val"] = map_df["score"].apply(_color)
    map_df["radius"] = (map_df["score"].fillna(0.3) * 150_000 + 40_000).astype(int)
    map_df["score_txt"] = map_df["score"].map(
        lambda value: f"{value:.3f}" if np.isfinite(value) else "—"
    )

    def _fmt_map_interval(row: pd.Series) -> str:
        lo, hi, wid = expanded_interval(
            float(row.get("score", np.nan)),
            float(row.get("q05_overall", np.nan)),
            float(row.get("q95_overall", np.nan)),
        )
        if np.isfinite(lo) and np.isfinite(hi):
            mark = "*" if wid else ""
            return f"[{lo:.3f}, {hi:.3f}]{mark}"
        return T("uncertainty_unavailable")

    map_df["interval_txt"] = map_df.apply(_fmt_map_interval, axis=1)
    map_df["role_disp"] = map_df["role"].map(_role_text)
    map_df["lith_disp"] = map_df["lithology_class"].map(
        lambda c: i18n.lith_label(str(c), LANG)
    )

    tooltip = {
        "html": T(
            "map_tooltip",
            name="{name}",
            role="{role_disp}",
            score="{score_txt}",
            interval="{interval_txt}",
            lith="{lith_disp}",
        ),
        "style": {
            "background": "#2C2923",
            "color": "white",
            "font-size": "13px",
            "padding": "6px",
        },
    }
    try:
        import pydeck as pdk

        view = pdk.ViewState(latitude=20, longitude=10, zoom=1, pitch=0)
        layers = []
        val_df = map_df[map_df["role"] == "validation"]
        cand_df = map_df[map_df["role"] != "validation"]
        if len(val_df):
            layers.append(
                pdk.Layer(
                    "ScatterplotLayer",
                    data=val_df,
                    get_position="[lon, lat]",
                    get_fill_color="color_val",
                    get_radius="radius",
                    stroked=True,
                    get_line_color=[56, 132, 255, 240],
                    line_width_min_pixels=2,
                    radius_min_pixels=6,
                    radius_max_pixels=18,
                    pickable=True,
                    auto_highlight=True,
                )
            )
        if len(cand_df):
            layers.append(
                pdk.Layer(
                    "ScatterplotLayer",
                    data=cand_df,
                    get_position="[lon, lat]",
                    get_fill_color="color",
                    get_radius="radius",
                    radius_min_pixels=6,
                    radius_max_pixels=18,
                    pickable=True,
                    auto_highlight=True,
                )
            )
        st.pydeck_chart(
            pdk.Deck(layers=layers, initial_view_state=view, tooltip=tooltip),
            width="stretch",
        )
        st.caption(T("map_caption"))
    except ImportError:
        st.info(T("map_fallback"))
        st.map(map_df, size=200_000)


# ═══════════════════════════════════════════════════════════════════════════════
# MAIN UI
# ═══════════════════════════════════════════════════════════════════════════════

moon_df, earth_df = load_data(
    _source_mtime("features_moon"),
    _source_mtime("features_earth"),
)
moon_atlas_meta, earth_atlas_meta = load_atlas_metadata()

# ── SIDEBAR ──────────────────────────────────────────────────────────────────
with st.sidebar:
    lang_display = st.radio(
        i18n.LANGUAGE_LABEL, ["Türkçe", "English"], horizontal=True, key="lang"
    )
    LANG = "tr" if lang_display == "Türkçe" else "en"
    AXIS_LABELS = {
        a: i18n.t(f"axis_{a}", LANG) for a in ("mobility", "thermal", "surface")
    }

    st.header(T("settings_header"))

    body = "Moon"

    refs = moon_df[moon_df["role"] == "reference"].reset_index(drop=True)

    ref_site_id = st.selectbox(
        T("ref_site_label_moon"),
        refs["site_id"].tolist(),
        format_func=lambda sid: i18n.moon_site_label(str(sid), LANG),
    )
    ref_row = refs[refs["site_id"] == ref_site_id].iloc[0]
    ref_name = i18n.moon_site_label(str(ref_site_id), LANG)
    st.caption(
        f"{ref_name} · "
        + T(
            "ref_site_caption",
            lat=f"{float(ref_row['lat']):.2f}",
            lon=f"{float(ref_row['lon']):.2f}",
            lith=i18n.lith_label(str(ref_row.get("lithology_class", "")), LANG),
        ),
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
st.caption(T("app_badge"))
st.markdown(T("subtitle", n=len(earth_df)))
st.info(T("thermal_note"))

# ── COMPUTE SCORES (scoring module) ──────────────────────────────────────────
result, long_scores = score_earth(ref_row, earth_df, mission)
result["region"] = [
    _region_of(float(la), float(lo)) for la, lo in zip(result["lat"], result["lon"])
]
top = result.head(top_n)
axes = list(AXES.keys())  # mobility, thermal, surface
active_axes = ["mobility", "surface"]

# ── REFERENCE SITE VALUES ────────────────────────────────────────────────────
st.subheader(T("ref_subheader", name=ref_name, body=T("body_moon")))
ref_features = [f for feats in AXES.values() for f in feats]
ref_tbl = pd.DataFrame(
    {
        T("ref_col_feature"): [i18n.feature_label(f, LANG) for f in ref_features],
        T("ref_col_value"): [
            round(float(ref_row.get(f, np.nan)), 3) for f in ref_features
        ],
        T("ref_col_unit"): [FEATURE_UNITS.get(f, "—") for f in ref_features],
        T("ref_col_sd"): [
            round(float(ref_row.get(f"{f}_sd", np.nan)), 3) for f in ref_features
        ],
        T("ref_col_res"): [ref_row.get(f"{f}_res_m", np.nan) for f in ref_features],
        T("ref_col_src"): [
            str(ref_row.get(f"{f}_src", "")) or "—" for f in ref_features
        ],
    }
)
with st.expander(f"{T('ref_expander')} · {ref_name}"):
    st.dataframe(ref_tbl, width="stretch", hide_index=True)
    st.caption(T("ref_table_caption"))
    st.caption(T("temp_note"))

# ── TABS ─────────────────────────────────────────────────────────────────────
tab_map, tab_radar, tab_terrain, tab_table, tab_validation, tab_breakdown = st.tabs(
    [
        T("tab_map"),
        T("tab_radar"),
        T("tab_terrain"),
        T("tab_table"),
        T("tab_validation"),
        T("tab_breakdown"),
    ]
)

# ── TAB 1: MAP ───────────────────────────────────────────────────────────────
with tab_map:
    st.markdown(T("map_heading", n=top_n))
    _map_chart(result, top_n)

# ── TAB 2: VISUAL COMPARISON & AXES (2D Scatter + Horizontal Axis Bars) ──────
with tab_radar:
    st.markdown(T("scatter_heading"))
    st.plotly_chart(
        _physical_scatter_chart(result, ref_row, ref_name), width="stretch"
    )
    st.caption(T("scatter_caption"))
    st.divider()

    st.markdown(T("bars_heading", n=top_n))
    st.markdown(T("radar_caption"))
    per_row = 2
    any_card_widened = False
    for i in range(0, len(top), per_row):
        chunk = top.iloc[i : i + per_row]
        cols = st.columns(len(chunk))
        for col, (_, row) in zip(cols, chunk.iterrows()):
            with col:
                fig_bar, card_wid = _axis_bar_card(row)
                any_card_widened = any_card_widened or card_wid
                st.plotly_chart(fig_bar, width="stretch")

                sc_ov = float(row.get("score", np.nan))
                lo_ov, hi_ov, wid_ov = expanded_interval(
                    sc_ov,
                    float(row.get("q05_overall", np.nan)),
                    float(row.get("q95_overall", np.nan)),
                )
                any_card_widened = any_card_widened or wid_ov
                interval_txt = (
                    f"{lo_ov:.2f}–{hi_ov:.2f}{'*' if wid_ov else ''}"
                    if np.isfinite(lo_ov) and np.isfinite(hi_ov)
                    else T("uncertainty_unavailable")
                )
                st.caption(
                    T(
                        "radar_line",
                        score=f"{sc_ov:.2f}",
                        interval=interval_txt,
                        n=int(row.get("n_axes_used", 2)),
                        lith=i18n.lith_label(
                            str(row.get("lithology_class", "")), LANG
                        ),
                    )
                )
                s_mob = float(row.get("score_mobility", 0.0))
                s_surf = float(row.get("score_surface", 0.0))
                if s_mob >= s_surf:
                    strong_ax, weak_ax = (
                        AXIS_LABELS["mobility"],
                        AXIS_LABELS["surface"],
                    )
                else:
                    strong_ax, weak_ax = (
                        AXIS_LABELS["surface"],
                        AXIS_LABELS["mobility"],
                    )
                st.caption(T("card_strength_line", strong=strong_ax, weak=weak_ax))
    if any_card_widened:
        st.caption(T("table_widened_note"))

# ── TAB 3: 3D TERRAIN (real M6 Moon 5m LOLA + E7 Earth 30m GLO-30 tiles) ─────
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

# ── TAB 4: SCORE TABLE + COMPACT PORTFOLIO CARD ──────────────────────────────
with tab_table:
    st.markdown(T("table_caption"))
    lith_opts = sorted(set(result["lithology_class"].dropna().astype(str)))
    lith_filter = st.multiselect(
        T("filter_lith"),
        lith_opts,
        format_func=lambda c: i18n.lith_label(c, LANG),
    )
    region_filter = st.selectbox(
        T("filter_region"),
        REGION_OPTIONS,
        format_func=lambda k: T(f"region_{k}"),
    )
    shown = result
    if lith_filter:
        shown = shown[shown["lithology_class"].astype(str).isin(lith_filter)]
    if region_filter != "all":
        shown = shown[shown["region"] == region_filter]

    any_table_widened = False
    rows = []
    for _, r in shown.iterrows():
        lith_code = str(r.get("lithology_class", ""))
        lith_txt = i18n.lith_label(lith_code, LANG)
        ov_txt, wid_ov = _format_score_interval(
            float(r.get("score", np.nan)),
            float(r.get("q05_overall", np.nan)),
            float(r.get("q95_overall", np.nan)),
        )
        any_table_widened = any_table_widened or wid_ov
        rec = {
            T("col_site"): r["name"],
            T("col_role"): _role_text(str(r["role"])),
            T("col_lith"): lith_txt,
            T("col_overall"): ov_txt,
        }
        for a in axes:
            if a == "thermal":
                continue  # suspended in v1 under Decision #30 (Moon thermal = NaN)
            ax_txt, wid_ax = _format_score_interval(
                float(r.get(f"score_{a}", np.nan)),
                float(r.get(f"q05_{a}", np.nan)),
                float(r.get(f"q95_{a}", np.nan)),
            )
            any_table_widened = any_table_widened or wid_ax
            rec[AXIS_LABELS[a]] = ax_txt
        rows.append(rec)

    st.dataframe(pd.DataFrame(rows), width="stretch", hide_index=True)
    st.caption(T("table_thermal_note"))
    if any_table_widened:
        st.caption(T("table_widened_note"))
    st.caption(T("table_footer_caption"))

    # ── Compact Portfolio Card right below Score Table ───────────────────────
    st.divider()
    st.markdown(T("portfolio_heading"))
    st.markdown(T("portfolio_intro"))

    selected_ids, uncovered_axes = select_portfolio(
        long_scores, min_score=PORTFOLIO_THRESHOLD, axes=axes
    )
    covered_axes = [a for a in axes if a not in uncovered_axes]

    if selected_ids:
        port_rows = []
        for idx, sid in enumerate(selected_ids, start=1):
            s_row = result[result["site_id"] == sid].iloc[0]
            cov_here = [
                AXIS_LABELS[a]
                for a in active_axes
                if float(s_row.get(f"score_{a}", np.nan)) >= PORTFOLIO_THRESHOLD
            ]
            port_rows.append(
                {
                    T("portfolio_col_order"): idx,
                    T("portfolio_col_site"): s_row["name"],
                    T("portfolio_col_role"): _role_text(str(s_row["role"])),
                    T("portfolio_col_covered"): ", ".join(cov_here) or "—",
                    T("portfolio_col_scores"): (
                        f"{AXIS_LABELS['mobility']}: {float(s_row.get('score_mobility', np.nan)):.2f} · "
                        f"{AXIS_LABELS['surface']}: {float(s_row.get('score_surface', np.nan)):.2f}"
                    ),
                }
            )
        st.dataframe(pd.DataFrame(port_rows), width="stretch", hide_index=True)
    else:
        st.info(T("portfolio_none_selected"))

    covered_txt = (
        ", ".join(AXIS_LABELS[a] for a in covered_axes)
        if covered_axes
        else ("Yok" if LANG == "tr" else "None")
    )
    uncovered_labels = []
    for a in uncovered_axes:
        if a == "thermal":
            uncovered_labels.append(
                f"{AXIS_LABELS[a]} ({'v1 askıda / NaN' if LANG == 'tr' else 'suspended in v1 / NaN'})"
            )
        else:
            uncovered_labels.append(
                f"{AXIS_LABELS[a]} (< {PORTFOLIO_THRESHOLD:.2f})"
            )
    uncovered_txt = ", ".join(uncovered_labels) if uncovered_labels else "—"

    st.markdown(T("portfolio_covered_label", axes=covered_txt))
    st.markdown(T("portfolio_uncovered_label", axes=uncovered_txt))

    if "mobility" in uncovered_axes:
        best_mob_row = result.sort_values(
            "score_mobility", ascending=False, na_position="last"
        ).iloc[0]
        st.caption(
            T(
                "portfolio_best_mobility_note",
                site=str(best_mob_row["name"]),
                score=f"{float(best_mob_row['score_mobility']):.2f}",
            )
        )

    st.caption(T("portfolio_threshold_note"))

# ── TAB 5: DESCRIPTIVE RANK DIAGNOSTIC (10 validation sites × E1/E8) ─────────
with tab_validation:
    st.markdown(T("val_intro"))
    val = run_blind_validation(long_scores, earth_df)
    rank_piv = val.pivot(index="site_id", columns="axis", values="rank")

    val_sites = earth_df[earth_df["role"] == "validation"].reset_index(drop=True)
    diag_rows = []
    for _, vrow in val_sites.iterrows():
        sid = str(vrow["site_id"])
        mob_r = (
            rank_piv.loc[sid, "mobility"]
            if sid in rank_piv.index and "mobility" in rank_piv.columns
            else np.nan
        )
        surf_r = (
            rank_piv.loc[sid, "surface"]
            if sid in rank_piv.index and "surface" in rank_piv.columns
            else np.nan
        )
        mob_str = str(int(mob_r)) if pd.notna(mob_r) else "—"
        surf_str = str(int(surf_r)) if pd.notna(surf_r) else "—"

        exp_info = i18n.VALIDATION_EXPECTATIONS.get(sid, {}).get(LANG, {})
        diag_rows.append(
            {
                T("val_col_site"): vrow["name"],
                T("val_col_expected"): exp_info.get("expected", "—"),
                T("val_col_raw_rank"): T(
                    "val_rank_cell", mob=mob_str, surf=surf_str
                ),
                T("val_col_ice"): exp_info.get("ice", "—"),
                T("val_col_rationale"): exp_info.get("rationale", "—"),
                T("val_col_source"): exp_info.get("source", "—"),
            }
        )

    st.dataframe(pd.DataFrame(diag_rows), width="stretch", hide_index=True)
    st.caption(T("val_footer_note"))

# ── TAB 6: ANALOGY LIMITS & 8-DIMENSION SCORECARD & ORBITAL EVIDENCE ─────────
with tab_breakdown:
    st.markdown(T("breakdown_notes"))
    st.divider()

    st.markdown(T("scorecard_heading"))
    st.dataframe(
        pd.DataFrame(i18n.DIMENSION_SCORECARD[LANG]),
        width="stretch",
        hide_index=True,
    )
    st.divider()

    sel_name = st.selectbox(
        T("inspect_label"),
        result["name"].tolist(),
        index=0,
        help=T("inspect_help"),
    )
    inspected = result[result["name"] == sel_name].iloc[0]
    cand_row = earth_df[earth_df["site_id"] == inspected["site_id"]].iloc[0]
    cand_sid = str(cand_row["site_id"])
    ref_sid = str(ref_row["site_id"])

    # ── Verified Local Orbital Visual & Topographic Context Card ────────────
    st.markdown(T("vis_heading", ref=ref_name, sel=sel_name))
    c_moon_wac, c_moon_lola, c_earth_opt = st.columns(3)

    m_meta = moon_atlas_meta.get(ref_sid, {})
    hillshade_file = MOON_ATLAS_DIR / f"{ref_sid}_hillshade.png"
    hazard_file = MOON_ATLAS_DIR / f"{ref_sid}_hazard.png"

    with c_moon_wac:
        st.markdown(f"**{T('vis_col_moon_opt')}**")
        if hillshade_file.exists():
            st.image(
                str(hillshade_file),
                caption=T(
                    "vis_moon_hillshade_caption",
                    ref=ref_name,
                    relief=f"{float(m_meta.get('relief_m', ref_row.get('relief', np.nan))):.1f}",
                    slope=f"{float(m_meta.get('slope_mean_deg', ref_row.get('slope_mean', np.nan))):.1f}",
                ),
            )
        else:
            st.info(T("vis_moon_missing"))
        st.caption(T("vis_moon_local_source"))

    with c_moon_lola:
        st.markdown(f"**{T('vis_col_moon_relief')}**")
        if hazard_file.exists():
            st.image(
                str(hazard_file),
                caption=T(
                    "vis_moon_hazard_caption",
                    ref=ref_name,
                    lt10=f"{float(m_meta.get('pct_lt10deg', 0.0)):.1f}",
                    mid=f"{float(m_meta.get('pct_10_20deg', 0.0)):.1f}",
                    gt20=f"{float(m_meta.get('pct_gt20deg', 0.0)):.1f}",
                ),
            )
        else:
            st.info(T("vis_moon_missing"))
        st.caption(T("vis_moon_local_source"))

    with c_earth_opt:
        st.markdown(f"**{T('vis_col_earth')}**")
        lat_c = float(cand_row["lat"])
        lon_c = float(cand_row["lon"])
        e_meta = earth_atlas_meta.get(cand_sid, {})
        webp_file = EARTH_ATLAS_DIR / f"{cand_sid}.webp"
        if webp_file.exists():
            st.image(
                str(webp_file),
                caption=T(
                    "vis_earth_s2_caption",
                    sel=sel_name,
                    lat=f"{lat_c:.4f}",
                    lon=f"{lon_c:.4f}",
                ),
            )
            acq_date = str(e_meta.get("acquisition_date", "—"))[:10]
            st.caption(
                T(
                    "vis_earth_s2_meta",
                    collection=str(e_meta.get("collection", "sentinel-2-l2a")),
                    scene_id=str(e_meta.get("scene_id", "—")),
                    date=acq_date,
                    cloud=f"{float(e_meta.get('local_cloud_pct', 0.0)):.2f}",
                )
            )
        else:
            st.info(T("vis_earth_missing"))

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
            T("vis_link_worldview", url=wv_url)
            + " · "
            + T("vis_link_gmaps", url=gmaps_url)
        )

    # Quantitative context banner
    ci_lines = []
    for axis in axes:
        score = float(inspected.get(f"score_{axis}", np.nan))
        q05 = float(inspected.get(f"q05_{axis}", np.nan))
        q95 = float(inspected.get(f"q95_{axis}", np.nan))
        if not np.isfinite(score):
            ci_lines.append(T("vis_quant_suspended", axis=AXIS_LABELS[axis]))
        else:
            lo, hi, wid = expanded_interval(score, q05, q95)
            mark = "*" if wid else ""
            lo_txt = f"{lo:.2f}" if np.isfinite(lo) else "—"
            hi_txt = f"{hi:.2f}{mark}" if np.isfinite(hi) else "—"
            ci_lines.append(
                T(
                    "vis_quant_line",
                    axis=AXIS_LABELS[axis],
                    score=f"{score:.2f}",
                    lo=lo_txt,
                    hi=hi_txt,
                )
            )
    st.info(
        T("vis_quant_head")
        + " · ".join(ci_lines)
        + "\n\n"
        + T("vis_quant_msg")
    )

    st.markdown(T("gaps_heading", sel=sel_name, ref=ref_name))
    gaps = axis_gaps(ref_row, earth_df)
    gaps = gaps[gaps["site_id"] == inspected["site_id"]]
    if gaps.empty:
        st.info(T("gaps_empty"))
    else:
        gaps = gaps.sort_values("z_diff", key=lambda s: s.abs(), ascending=False)
        gaps["ref_src"] = gaps["feature"].map(
            lambda f: str(ref_row.get(f"{f}_src", "")) or "—"
        )
        gaps["ref_res_m"] = gaps["feature"].map(
            lambda f: float(ref_row.get(f"{f}_res_m", np.nan))
        )
        gaps["cand_src"] = gaps["feature"].map(
            lambda f: str(cand_row.get(f"{f}_src", "")) or "—"
        )
        gaps["cand_res_m"] = gaps["feature"].map(
            lambda f: float(cand_row.get(f"{f}_res_m", np.nan))
        )
        gaps["feature"] = gaps["feature"].map(
            lambda f: i18n.feature_label(f, LANG)
        )
        keep = [
            "feature",
            "ref_value",
            "cand_value",
            "diff",
            "z_diff",
            "ref_src",
            "ref_res_m",
            "cand_src",
            "cand_res_m",
        ]
        show = gaps[keep].copy()
        show.columns = i18n.GAP_COLUMNS[LANG]
        st.dataframe(show.round(3), width="stretch", hide_index=True)
        st.caption(T("gaps_caption"))
