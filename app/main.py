"""app/main.py – Moon/Mars <-> Earth Analog Finder (Person 4, v1)

Run:  streamlit run app/main.py

Scores come from the leader's src/scoring/similarity.py (axis_scores,
axis_pivot, combine_axes, axis_gaps) — this app does NOT compute its own
scores. Data: data/processed first, falls back to data/mock (MOCK banner
is shown whenever any *_src column equals "MOCK", AGENTS.md rule 10).
"""

from __future__ import annotations

import pathlib
import sys

import numpy as np
import pandas as pd
import plotly.graph_objects as go
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

# ── page config ──────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Moon/Mars <-> Earth Analog Finder",
    page_icon="🌕",
    layout="wide",
)

# ── constants ────────────────────────────────────────────────────────────────
MOCK_DIR = ROOT / "data" / "mock"
PROC_DIR = ROOT / "data" / "processed"

AXIS_LABELS = {"mobility": "Mobility", "thermal": "Thermal", "surface": "Surface"}

MISSION_LABELS = {
    "default": "Balanced (all axes equal)",
    "rover_mobility": "Rover mobility test",
    "isru_ice": "ISRU / ice prospecting",
    "radar_calibration": "Subsurface radar calibration",
}

BREAKDOWN_NOTES = (
    "⚠️ **Where the analogy breaks down** — no Earth site can reproduce:\n"
    "- **Gravity:** Moon ~1/6 g, Mars ~3/8 g (regolith mechanics, dust settling)\n"
    "- **Vacuum / thin atmosphere:** no Earth surface has <= 1 Pa pressure\n"
    "- **Radiation:** no magnetosphere-free, ozone-free chronic particle flux\n"
    "- **Diurnal cycle:** lunar day ≈ 29.5 Earth days\n"
    "- **Regolith composition:** lunar/Martian mineralogy differs from any Earth rock\n\n"
    "Use Earth analogs only for the matched axes; validate the rest in lab/simulation."
)


# ── data loading ─────────────────────────────────────────────────────────────
def _is_mock(df: pd.DataFrame) -> bool:
    """True if any *_src column contains 'MOCK' (AGENTS.md rule 10)."""
    src_cols = [c for c in df.columns if c.endswith("_src")]
    return bool(src_cols) and bool((df[src_cols] == "MOCK").any().any())


def _load_body(stem: str) -> pd.DataFrame:
    proc = PROC_DIR / f"{stem}.parquet"
    mock = MOCK_DIR / f"{stem}.parquet"
    if proc.exists():
        return pd.read_parquet(proc)
    if mock.exists():
        return pd.read_parquet(mock)
    st.error(f"Cannot find {stem}.parquet in data/processed/ or data/mock/.")
    st.stop()


@st.cache_data
def load_data() -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, bool]:
    """Load moon/mars/earth parquets; flag whether any MOCK row is present."""
    moon_df = _load_body("features_moon")
    mars_df = _load_body("features_mars")
    earth_df = _load_body("features_earth")
    any_mock = _is_mock(moon_df) or _is_mock(mars_df) or _is_mock(earth_df)
    return moon_df, mars_df, earth_df, any_mock


# ── scoring (leader's module, called as-is) ──────────────────────────────────
def score_earth(
    ref_row: pd.Series, earth_df: pd.DataFrame, mission: str
) -> pd.DataFrame:
    """Run axis_scores + pivot + weighted combine; return one row per site."""
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
    return result


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
        fillcolor="rgba(99,110,250,0.35)",
        line=dict(color="rgb(99,110,250)", width=2),
        name=row["name"],
        hovertemplate="%{theta}: %{r:.2f}<extra></extra>",
    ))
    fig.add_trace(go.Scatterpolar(
        r=_closed(hi), theta=labels_c, line=dict(color="green", width=1, dash="dash"),
        name="CI high", hoverinfo="skip",
    ))
    fig.add_trace(go.Scatterpolar(
        r=_closed(lo), theta=labels_c, line=dict(color="red", width=1, dash="dot"),
        name="CI low", hoverinfo="skip",
    ))
    fig.update_layout(
        polar=dict(radialaxis=dict(visible=True, range=[0, 1])),
        showlegend=False,
        margin=dict(l=20, r=20, t=40, b=20),
        title=dict(text=str(row["name"]), font=dict(size=13)),
        height=320,
    )
    return fig


def _map_chart(result: pd.DataFrame, top_n: int) -> None:
    """pydeck scatter map of the top-N scored Earth sites."""
    map_df = result.head(top_n)[
        ["site_id", "name", "role", "lat", "lon", "score"]
    ].copy()

    def _color(score: float) -> list[int]:
        if np.isnan(score):
            return [128, 128, 128, 160]
        r, g = int(255 * (1 - score)), int(255 * score)
        return [r, g, 60, 200]

    map_df["color"] = map_df["score"].apply(_color)
    map_df["radius"] = (map_df["score"].fillna(0.3) * 150_000 + 40_000).astype(int)
    map_df["score_txt"] = (map_df["score"] * 100).round(1).astype(str) + "%"

    tooltip = {
        "html": "<b>{name}</b><br/>Role: {role}<br/>Score: {score_txt}",
        "style": {"background": "#1e1e2e", "color": "white",
                  "font-size": "13px", "padding": "6px"},
    }
    try:
        import pydeck as pdk

        layer = pdk.Layer(
            "ScatterplotLayer",
            data=map_df,
            get_position="[lon, lat]",
            get_fill_color="color",
            get_radius="radius",
            pickable=True,
            auto_highlight=True,
        )
        view = pdk.ViewState(latitude=20, longitude=10, zoom=1, pitch=0)
        st.pydeck_chart(
            pdk.Deck(layers=[layer], initial_view_state=view, tooltip=tooltip),
            width="stretch",
        )
    except ImportError:
        st.info("pydeck not installed — falling back to st.map.")
        st.map(map_df.rename(columns={"name": "name"}), size=200_000)


# ═══════════════════════════════════════════════════════════════════════════════
# MAIN UI
# ═══════════════════════════════════════════════════════════════════════════════

moon_df, mars_df, earth_df, any_mock = load_data()

# ── MOCK BANNER (AGENTS.md rule 10) ──────────────────────────────────────────
if any_mock:
    st.warning(
        "🚧 **MOCK DATA — all scores on this page are fully synthetic.**\n\n"
        "Computed from `data/mock/` placeholder values, not real instrument data. "
        "For interface testing only; do not present as scientific findings. "
        "This banner disappears when real parquets land in `data/processed/`.",
        icon="🚧",
    )

# ── TITLE ────────────────────────────────────────────────────────────────────
st.title("🌕 Moon / Mars ↔ Earth Analog Finder")
st.caption(
    "NASA Space Apps 2026 · per-axis Gaussian similarity [0–1], higher = closer "
    "· scores via `scoring.similarity.axis_scores` · **current output: MOCK**"
    if any_mock else
    "NASA Space Apps 2026 · per-axis Gaussian similarity [0–1], higher = closer "
    "· scores via `scoring.similarity.axis_scores`"
)

# ── SIDEBAR ──────────────────────────────────────────────────────────────────
with st.sidebar:
    st.header("⚙️ Settings")

    body_choice = st.radio("Reference body", ["Moon", "Mars"], horizontal=True)
    ref_df = moon_df if body_choice == "Moon" else mars_df
    refs = ref_df[ref_df["role"] == "reference"].reset_index(drop=True)

    ref_name = st.selectbox(
        f"Reference site ({body_choice})", refs["name"].tolist()
    )
    ref_row = refs[refs["name"] == ref_name].iloc[0]
    st.caption(f"`site_id`: {ref_row['site_id']} · lat {ref_row['lat']:.2f}°, "
               f"lon {ref_row['lon']:.2f}°")

    st.divider()
    mission = st.selectbox(
        "Mission / use case",
        list(MISSION_PRESETS.keys()),
        format_func=lambda k: MISSION_LABELS.get(k, k),
    )

    st.divider()
    top_n = st.slider(
        "Show top N Earth sites", 3, len(earth_df), min(6, len(earth_df))
    )

# ── COMPUTE SCORES (leader's module) ─────────────────────────────────────────
result = score_earth(ref_row, earth_df, mission)
top = result.head(top_n)
axes = list(AXES.keys())  # mobility, thermal, surface

# ── REFERENCE SITE VALUES ────────────────────────────────────────────────────
st.subheader(f"📍 Reference: {ref_name} ({body_choice})")
ref_features = [f for feats in AXES.values() for f in feats]
ref_tbl = pd.DataFrame({
    "feature": ref_features,
    "value": [round(float(ref_row.get(f, np.nan)), 3) for f in ref_features],
    "sd": [round(float(ref_row.get(f"{f}_sd", np.nan)), 3) for f in ref_features],
})
st.dataframe(ref_tbl, width="stretch", hide_index=True)

st.divider()

# ── TABS ─────────────────────────────────────────────────────────────────────
tab_map, tab_radar, tab_table, tab_breakdown = st.tabs([
    "🗺️ Map", "📡 Radar Charts", "📊 Score Table", "⚠️ Analogy Limits"
])

# ── TAB 1: MAP ───────────────────────────────────────────────────────────────
with tab_map:
    st.markdown(f"**Top {top_n} Earth analogs for {ref_name}** — circle size "
                f"& colour = mission-weighted overall score")
    _map_chart(result, top_n)

# ── TAB 2: RADAR CHARTS ──────────────────────────────────────────────────────
with tab_radar:
    st.markdown("Per-axis score [0–1] (solid) with 95% CI high (green dashed) "
                "and CI low (red dotted). Outer ring = perfect match.")
    per_row = 3
    for i in range(0, len(top), per_row):
        chunk = top.iloc[i:i + per_row]
        cols = st.columns(len(chunk))
        for col, (_, row) in zip(cols, chunk.iterrows()):
            with col:
                st.plotly_chart(_radar_chart(row, axes), width="stretch")
                st.caption(f"Overall: **{row['score']:.2f}** "
                           f"({row['n_axes_used']} axes used)")

# ── TAB 3: SCORE TABLE ───────────────────────────────────────────────────────
with tab_table:
    st.markdown("Mission-weighted overall score + per-axis scores with "
                "[ci_low – ci_high] for every Earth site.")

    def _fmt(score: float, lo: float, hi: float) -> str:
        if np.isnan(score):
            return "—"
        if np.isnan(lo) or np.isnan(hi):
            return f"{score:.2f}"
        return f"{score:.2f} [{lo:.2f}–{hi:.2f}]"

    rows = []
    for _, r in result.iterrows():
        rec = {
            "Site": r["name"],
            "Role": r["role"],
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
    st.caption("— = axis not scoreable (missing features, e.g. NaN thermal_inertia).")

# ── TAB 4: ANALOGY LIMITS ────────────────────────────────────────────────────
with tab_breakdown:
    st.markdown(BREAKDOWN_NOTES)
    st.divider()
    if len(top) > 0:
        best = top.iloc[0]
        st.markdown(f"### Feature gaps: {best['name']} vs {ref_name} "
                    "(leader's `axis_gaps`)")
        gaps = axis_gaps(ref_row, earth_df)
        gaps = gaps[gaps["site_id"] == best["site_id"]]
        if gaps.empty:
            st.info("No comparable features for this site.")
        else:
            gaps = gaps.sort_values("z_diff", key=lambda s: s.abs(), ascending=False)
            show = gaps[["feature", "ref_value", "cand_value", "diff", "z_diff"]]
            st.dataframe(
                show.round(3), width="stretch", hide_index=True
            )
            st.caption("|z_diff| large → biggest physical mismatch; "
                       "sort order: largest first.")
    else:
        st.info("No scored sites.")

# ── FOOTER ───────────────────────────────────────────────────────────────────
st.divider()
if any_mock:
    st.error("🚧 **MOCK DATA** — every score above is synthetic. Replace "
             "`data/mock/` with `data/processed/` outputs for real results.",
             icon="🚧")
st.caption("NASA Space Apps 2026 · Person 4 (app/) · branch: p4-app")
