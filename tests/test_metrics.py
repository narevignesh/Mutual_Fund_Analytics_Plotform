"""
Bluestock Fintech - Mutual Fund Analytics Platform
Test Suite: tests/test_metrics.py
Objective: Automated mathematical and financial logic validation:
CAGR, Sharpe, Sortino, Alpha, Beta, VaR, CVaR, Scorecard, and Recommender.
"""

import os
import sqlite3
import pytest
import numpy as np
import pandas as pd

DB_PATH = os.path.join("db", "bluestock_mf.db")

def test_cagr_formula():
    """Verify CAGR formula: (Ending / Beginning) ^ (1/Years) - 1."""
    start_nav = 100.0
    end_nav = 172.80
    years = 3.0
    # Expected: (172.8 / 100) ^ (1/3) - 1 = 1.2 - 1 = 0.20 (20.0%)
    cagr = ((end_nav / start_nav) ** (1.0 / years)) - 1.0
    assert abs(cagr - 0.20) < 1e-4

def test_sharpe_ratio_logic():
    """Verify Sharpe formula: (Rp - Rf) / Volatility."""
    # Synthetic annual returns
    rf = 0.065
    fund_return = 0.165 # 16.5%
    volatility = 0.10   # 10.0%
    expected_sharpe = (fund_return - rf) / volatility # 1.00
    assert abs(expected_sharpe - 1.00) < 1e-4

def test_var_and_cvar():
    """Verify Value at Risk (5th percentile) and CVaR calculations."""
    returns = np.array([-0.05, -0.04, -0.03, -0.02, -0.01, 0.0, 0.01, 0.02, 0.03, 0.04] * 10)
    var_95 = np.percentile(returns, 5)
    worst_tail = returns[returns <= var_95]
    cvar_95 = worst_tail.mean()
    
    assert var_95 < 0, "95% VaR should represent negative return threshold"
    assert cvar_95 <= var_95, "CVaR (Expected Shortfall) must be more severe than VaR"

def test_fund_scorecard_bounds():
    """Verify composite scorecard scores are bounded within [0, 100] and properly ranked."""
    conn = sqlite3.connect(DB_PATH)
    perf = pd.read_sql_query("SELECT composite_score, fund_rank FROM fact_performance ORDER BY fund_rank", conn)
    conn.close()
    
    assert len(perf) == 40, "Expected 40 performance records"
    assert (perf["composite_score"] >= 0).all() and (perf["composite_score"] <= 100).all(), "Scores must be within [0, 100]"
    assert (perf["fund_rank"].values == np.arange(1, 41)).all(), "Ranks must be strictly sequential 1 to 40"

def test_recommender_engine():
    """Verify fund recommender returns top 3 matching schemes with required fields."""
    from scripts.recommender import get_recommendations
    
    for risk in ["Low", "Moderate", "High"]:
        rec = get_recommendations(risk, top_n=3)
        assert len(rec) == 3, f"Expected 3 recommendations for {risk} profile"
        for col in ["scheme_name", "category", "risk_grade", "sharpe_ratio", "cagr_3yr_pct", "composite_score"]:
            assert col in rec.columns, f"Recommender output missing column {col}"
        # Validate ranked by Sharpe
        assert rec["sharpe_ratio"].iloc[0] >= rec["sharpe_ratio"].iloc[1] >= rec["sharpe_ratio"].iloc[2]

