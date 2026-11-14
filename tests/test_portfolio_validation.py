"""Tests for select_portfolio and run_blind_validation."""
import numpy as np
import pandas as pd

from scoring.portfolio import select_portfolio
from scoring.validation import run_blind_validation


def _scores_a() -> pd.DataFrame:
    return pd.DataFrame({
        "site_id": ["A", "A", "A", "B", "B", "B", "C", "C", "C"],
        "axis": ["mobility", "thermal", "surface"] * 3,
        "score": [0.9, 0.8, 0.1, 0.2, 0.2, 0.7, 0.5, np.nan, 0.3],
    })


def test_portfolio_greedy_picks_best_coverage_first() -> None:
    selected, uncovered = select_portfolio(_scores_a(), min_score=0.5)
    # A covers mobility+thermal (2 axes); then B covers surface; C covers nothing.
    assert selected == ["A", "B"]
    assert uncovered == []


def test_portfolio_reports_uncovered_axes() -> None:
    scores = _scores_a()
    scores.loc[(scores["site_id"] == "B") & (scores["axis"] == "surface"), "score"] = 0.4
    selected, uncovered = select_portfolio(scores, min_score=0.5)
    assert selected == ["A"]
    assert uncovered == ["surface"]


def test_validation_ranks_known_analogues() -> None:
    # mobility: good 0.9, mid 0.5, bad 0.2 | thermal: good 0.3, mid 0.6, bad 0.9
    scores = pd.DataFrame({
        "site_id": ["good", "good", "mid", "mid", "bad", "bad"],
        "axis": ["mobility", "thermal"] * 3,
        "score": [0.9, 0.3, 0.5, 0.6, 0.2, 0.9],
    })
    earth = pd.DataFrame({
        "site_id": ["good", "mid", "bad"],
        "role": ["validation", "validation", "validation"],
    })
    out = run_blind_validation(scores, earth, top_k=1)
    gm = out[(out["site_id"] == "good") & (out["axis"] == "mobility")]
    gt = out[(out["site_id"] == "good") & (out["axis"] == "thermal")]
    bt = out[(out["site_id"] == "bad") & (out["axis"] == "thermal")]
    assert gm["rank"].iat[0] == 1 and bool(gm["in_top_k"].iat[0])
    assert bt["rank"].iat[0] == 1 and bool(bt["in_top_k"].iat[0])
    assert gt["rank"].iat[0] == 3 and not bool(gt["in_top_k"].iat[0])
    assert (out["n_sites"] == 3).all()


def test_validation_explicit_ids_and_missing_site() -> None:
    scores = pd.DataFrame({
        "site_id": ["a", "b", "a", "b"],
        "axis": ["mobility", "mobility", "thermal", "thermal"],
        "score": [0.8, 0.2, 0.1, 0.9],
    })
    earth = pd.DataFrame({"site_id": ["a", "b"]})
    out = run_blind_validation(scores, earth, known_analog_ids=["b", "ghost"], top_k=1)
    b_m = out[(out["site_id"] == "b") & (out["axis"] == "mobility")]
    ghost = out[out["site_id"] == "ghost"]
    assert b_m["rank"].iat[0] == 2 and not bool(b_m["in_top_k"].iat[0])
    assert ghost["rank"].isna().all() and not ghost["in_top_k"].any()
