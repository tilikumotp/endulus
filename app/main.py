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

AXIS_LABELS = {"mobility": "Mobility", "thermal": "Thermal", "surface": "Surface"}

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

BREAKDOWN_NOTES = (
    "**Where the analogy breaks down** — no Earth site can reproduce:\n"
    "- **Gravity:** Moon ~1/6 g, Mars ~3/8 g (regolith mechanics, dust settling)\n"
    "- **Vacuum / thin atmosphere:** no Earth surface has <= 1 Pa pressure\n"
    "- **Radiation:** no magnetosphere-free, ozone-free chronic particle flux\n"
    "- **Diurnal cycle:** lunar day ≈ 29.5 Earth days\n"
    "- **Regolith composition:** lunar/Martian mineralogy differs from any Earth rock\n\n"
    "**Qualitative v1 factors (tracked, NOT in the numeric score — AGENTS.md §2):**\n"
    "- **Water ice / permanently shadowed regions (PSR):** Earth has no "
    "permanently shadowed, cryogenically cold terrain\n"
    "- **Lava tubes / subsurface caves:** presence is site-specific; assessed "
    "qualitatively from geology maps only\n"
    "- **Electrostatic dust / wind:** lunar electrostatic dust levitation has "
    "no Earth counterpart; Earth wind is a different (stronger) process\n\n"
    "Use Earth analogs only for the matched axes; validate the rest in lab/simulation."
)

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
        name="CI high", hoverinfo="skip",
    ))
    fig.add_trace(go.Scatterpolar(
        r=_closed(lo), theta=labels_c,
        line=dict(color="#8A847A", width=1, dash="dot"),
        name="CI low", hoverinfo="skip",
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

    tooltip = {
        "html": "<b>{name}</b><br/>Role: {role}<br/>Score: {score_txt}"
                "<br/>Lithology: {lithology_class}",
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
        st.caption(
            "Blue outline = known validation analogue. Candidate marker size "
            "and colour encode the mission-weighted score (0–1)."
        )
    except ImportError:
        st.info("pydeck not installed — falling back to st.map.")
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
    st.header("Settings")

    body = "Moon"
    st.caption("Reference body · Moon")
    ref_df = moon_df

    refs = ref_df[ref_df["role"] == "reference"].reset_index(drop=True)

    ref_name = st.selectbox("Reference site", refs["name"].tolist())
    ref_row = refs[refs["name"] == ref_name].iloc[0]
    st.caption(f"`site_id`: {ref_row['site_id']} · lat {ref_row['lat']:.2f}°, "
               f"lon {ref_row['lon']:.2f}° · lithology: "
               f"{ref_row.get('lithology_class', '—')}")

    mission = st.selectbox(
        "Mission / use case",
        list(MISSION_PRESETS.keys()),
        format_func=lambda k: MISSION_LABELS.get(k, k),
    )

    top_n = st.slider(
        "Top Earth sites shown", 1, max(2, len(earth_df)), min(6, len(earth_df))
    )
    min_score = st.slider(
        "Portfolio coverage threshold", 0.30, 0.95, 0.70, 0.05,
        help="A site covers an axis when its score >= this value.",
    )

# ── TITLE ────────────────────────────────────────────────────────────────────
st.title("Moon / Mars ↔ Earth Analog Finder")
st.caption(
    "Compare mobility, thermal and surface conditions across Earth sites, "
    "with uncertainty shown for each axis."
)

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
with st.expander(f"Reference measurements · {ref_name}", expanded=False):
    st.dataframe(ref_tbl, width="stretch", hide_index=True)
    st.caption(
        "`temp_amplitude` is the diurnal-cycle surface temperature range. "
        "Feature sources and native resolutions are shown above."
    )

# ── TABS ─────────────────────────────────────────────────────────────────────
tab_map, tab_radar, tab_table, tab_validation, tab_portfolio, tab_breakdown = st.tabs([
    "Map", "Radar", "Scores", "Validation", "Portfolio", "Analogy limits",
])

# ── TAB 1: MAP ───────────────────────────────────────────────────────────────
with tab_map:
    st.markdown(
        f"**Top {top_n} Earth sites for {ref_name}** · "
        "Marker size and colour encode the mission-weighted score."
    )
    _map_chart(result, top_n)

# ── TAB 2: RADAR CHARTS ──────────────────────────────────────────────────────
with tab_radar:
    st.markdown(
        "Per-axis scores (0–1). Lines show the 5th–95th Monte Carlo "
        "percentiles, expanded to include the point estimate."
    )
    per_row = 3
    for i in range(0, len(top), per_row):
        chunk = top.iloc[i:i + per_row]
        cols = st.columns(len(chunk))
        for col, (_, row) in zip(cols, chunk.iterrows()):
            with col:
                st.plotly_chart(_radar_chart(row, axes), width="stretch")
                st.caption(f"Overall: **{row['score']:.2f}** "
                           f"({row['n_axes_used']} axes used) · "
                           f"lithology: {row.get('lithology_class', '—')}")

# ── TAB 3: SCORE TABLE ───────────────────────────────────────────────────────
with tab_table:
    st.markdown(
        "Mission-weighted overall score and per-axis scores. Brackets show "
        "the 5th–95th Monte Carlo percentiles, expanded to include the point "
        "estimate, for each axis."
    )
    role_filter = st.multiselect(
        "Filter by role", ["validation", "candidate"],
        default=["validation", "candidate"],
        help="validation = known analogues (blind check) · candidate = test "
             "candidates, never confirmed analogues.",
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
            "Site": r["name"],
            "Role": r["role"],
            "Lithology": (
                f"{lith} (matches reference)"
                if ref_lith and lith == ref_lith else lith
            ),
            "Overall": "—" if np.isnan(r["score"]) else f"{r['score']:.3f}",
        }
        for a in axes:
            rec[AXIS_LABELS[a]] = _fmt(
                r.get(f"score_{a}", np.nan),
                r.get(f"ci_low_{a}", np.nan),
                r.get(f"ci_high_{a}", np.nan),
            )
        rows.append(rec)
    st.dataframe(pd.DataFrame(rows), width="stretch", hide_index=True)
    st.caption(
        "— = axis not scoreable because required features are missing. "
        "Lithology is qualitative and is not included in the numeric score."
    )

# ── TAB 4: VALIDATION (blind recovery of known analogues) ────────────────────
with tab_validation:
    st.markdown(
        "Blind check (leader's `run_blind_validation`): sites with role "
        "`validation` — the known analogues — should rank near the top per "
        f"axis. Recovery = rank ≤ {VALIDATION_TOP_K} of {len(earth_df)} "
        "scored sites. The scorer itself never sees roles."
    )
    val = run_blind_validation(long_scores, earth_df, top_k=VALIDATION_TOP_K)
    val = val.merge(earth_df[["site_id", "name"]], on="site_id", how="left")

    recovered = int(val["in_top_k"].sum())
    st.metric("Recovered (site × axis) pairs",
              f"{recovered} / {len(val)}")

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
            title="Rank (1 = best)",
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
        .rename(columns={"in_top_k": f"in_top_{VALIDATION_TOP_K}"})
        .sort_values(["name", "axis"]),
        width="stretch", hide_index=True,
    )

# ── TAB 5: PORTFOLIO (greedy set-cover heuristic) ────────────────────────────
with tab_portfolio:
    st.markdown(
        "Greedy set-cover heuristic (leader's `select_portfolio`): selects a "
        f"compact portfolio of Earth sites covering the maximum number of axes "
        f"with score ≥ **{min_score:.2f}**. "
        "Greedy is fast and transparent but does not guarantee the global "
        "minimum set; axes no site covers must be validated in lab/simulation."
    )
    selected_ids, uncovered = select_portfolio(long_scores, min_score, axes=axes)
    if not selected_ids:
        st.info(f"No Earth site reaches {min_score:.2f} on any axis — lower "
                "the threshold in the sidebar.")
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
                "Pick": len(rows) + 1,
                "Site": name,
                "Covers (score ≥ threshold)": ", ".join(covered),
            })
        st.dataframe(pd.DataFrame(rows), width="stretch", hide_index=True)

        st.markdown(
            "**Uncovered axes:** "
            + (", ".join(AXIS_LABELS[a] for a in uncovered)
               if uncovered else "none — all axes covered")
        )

# ── TAB 6: ANALOGY LIMITS ────────────────────────────────────────────────────
with tab_breakdown:
    st.markdown(BREAKDOWN_NOTES)
    st.divider()
    sel_name = st.selectbox(
        "Inspect candidate site", result["name"].tolist(), index=0,
        help="Feature-gap breakdown for any candidate, not only the top one.",
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

    st.markdown(f"### Visual and topographic context · {ref_name} vs {sel_name}")
    c_moon_wac, c_moon_lola, c_earth_opt = st.columns(3)

    with c_moon_wac:
        st.markdown("**Moon Optical Context**")
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
                    caption=f"{ref_name} — LRO WAC Orthomosaic (~30×30 km "
                            f"window, display ~71 m/px; centered on "
                            f"{lat_r:.2f}°, {lon_r:.2f}°)",
                )
            else:
                st.info(f"Lunar WAC preview unavailable ({err}).")
        else:
            st.info("Live lunar South Pole WMS applies to Moon reference "
                    "sites only.")
        st.caption("Imagery source: NASA LRO Wide Angle Camera (WAC) via "
                   "USGS Astrogeology WMS.")

    with c_moon_lola:
        st.markdown("**Moon Topographic / Relief Context**")
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
                    caption=f"{ref_name} — LOLA Shaded Relief (~30×30 km "
                            f"window; DEM feature extraction radius = "
                            f"{rad_r_m:.0f} m)",
                )
            else:
                st.info(f"Lunar LOLA preview unavailable ({err}).")
        else:
            st.info("Live lunar South Pole WMS applies to Moon reference "
                    "sites only.")
        st.caption("Relief preview: NASA LRO LOLA via USGS Astrogeology WMS. "
                   "Numeric features come from row `*_src`.")

    with c_earth_opt:
        st.markdown("**Earth Candidate Optical Context**")
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
                caption=f"{sel_name} ({lat_c:.4f}°, {lon_c:.4f}°) — "
                        f"~{used_km:.1f}×{used_km:.1f} km window "
                        f"(analysis radius = {rad_c_m:.0f} m)",
            )
        else:
            st.info(f"Esri imagery preview unavailable ({err}).")
        st.caption(
            "**Optical preview source:** Esri World Imagery (Esri, Maxar, "
            "Earthstar Geographics). Note: Numeric scores use the satellite "
            "datasets listed in the table below (`*_src`), not this optical "
            "preview."
        )
        wv_url = (
            f"https://worldview.earthdata.nasa.gov/"
            f"?v={lon_c - 0.15:.4f},{lat_c - 0.15:.4f},"
            f"{lon_c + 0.15:.4f},{lat_c + 0.15:.4f}"
            "&l=Reference_Labels_15m,MODIS_Terra_Land_Surface_Temp_Day,"
            "Coastlines_15m"
        )
        st.markdown(
            f"[Open region in NASA EOSDIS Worldview]({wv_url}) · "
            f"[Google Maps Satellite](https://www.google.com/maps/@"
            f"{lat_c:.5f},{lon_c:.5f},14z/data=!3m1!1e3)"
        )

    # Scientific context: imagery must be judged against the numbers.
    ci_lines = [
        f"**{AXIS_LABELS[a]}:** "
        f"{float(inspected.get(f'score_{a}', np.nan)):.2f} "
        f"(Monte Carlo range: [{float(inspected.get(f'ci_low_{a}', np.nan)):.2f}, "
        f"{float(inspected.get(f'ci_high_{a}', np.nan)):.2f}])"
        for a in AXIS_LABELS
    ]
    st.info(
        "Quantitative context for the imagery above — "
        + " · ".join(ci_lines)
        + "\n\nVisual similarity alone is not enough: compare the orbital "
        "imagery above against the quantitative per-axis scores, uncertainty "
        "intervals, and instrument resolutions below."
    )

    st.markdown(f"### Feature gaps: {sel_name} vs {ref_name} "
                "(leader's `axis_gaps`)")
    gaps = axis_gaps(ref_row, earth_df)
    gaps = gaps[gaps["site_id"] == inspected["site_id"]]
    if gaps.empty:
        st.info("No comparable features for this site.")
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
        st.caption(
            "|z_diff| large → biggest physical mismatch (sort order: largest "
            "first). `*_src` = dataset per AGENTS.md §5; `*_res_m` = native "
            "resolution — a coarse product (e.g. ~1 km MODIS) cannot resolve "
            "a 500 m site even when the DEM is 30 m."
        )

# ── FOOTER ───────────────────────────────────────────────────────────────────
st.divider()
st.caption("NASA Space Apps 2026 · Moon South Pole ↔ Earth Multi-Axis Analog Scorer")
