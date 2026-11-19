"""
Bluestock Fintech - Mutual Fund Analytics Platform
Script: scripts/recommender.py
Objective: Rule-based, risk-adjusted Mutual Fund Recommendation Engine.
Filters by risk profile and ranks top 3 funds by Sharpe ratio and Composite Score.
DISCLAIMER: For educational analytics only. Not financial advice. Mutual fund investments
are subject to market risks. Past performance does not guarantee future returns.
"""

import os
import sys
import sqlite3
from typing import List, Dict, Any
import pandas as pd

DB_PATH = os.path.join("db", "bluestock_mf.db")

RISK_MAPPINGS = {
    "Low": ["Liquid", "Debt"],
    "Moderate": ["Hybrid", "Debt", "Large Cap"],
    "High": ["Large Cap", "Mid Cap", "Small Cap", "Flexi Cap", "ELSS", "Index"]
}

def get_recommendations(risk_profile: str = "Moderate", top_n: int = 3) -> pd.DataFrame:
    """
    Returns top N mutual funds matching the user's risk appetite, ranked by Sharpe ratio.
    """
    clean_profile = risk_profile.capitalize()
    if clean_profile not in RISK_MAPPINGS:
        clean_profile = "Moderate"
        
    allowed_categories = RISK_MAPPINGS[clean_profile]
    
    conn = sqlite3.connect(DB_PATH)
    query = """
    SELECT 
        f.amfi_code,
        f.scheme_name,
        f.fund_house,
        f.category,
        f.risk_category AS risk_grade,
        p.sharpe_ratio,
        p.return_3yr_pct AS cagr_3yr_pct,
        f.expense_ratio_pct,
        p.composite_score,
        p.alpha,
        p.morningstar_rating
    FROM dim_fund f
    JOIN fact_performance p ON f.amfi_code = p.amfi_code
    WHERE f.category IN ({seq})
    ORDER BY p.sharpe_ratio DESC, p.composite_score DESC
    LIMIT {limit};
    """.format(
        seq=",".join([f"'{c}'" for c in allowed_categories]),
        limit=top_n
    )
    
    df_rec = pd.read_sql_query(query, conn)
    conn.close()
    return df_rec

def display_recommendations_cli(risk_profile: str = "Moderate"):
    print("=" * 80)
    print(f"BLUESTOCK FINTECH: FUND RECOMMENDATION ENGINE (Profile: {risk_profile.upper()})")
    print("=" * 80)
    print("CRITERIA: Filtered by risk suitability, ranked by Sharpe Ratio & Composite Score.")
    print("DISCLAIMER: Mutual fund investments are subject to market risks.")
    print("            Past returns are not indicative of future performance.")
    print("-" * 80)
    
    df = get_recommendations(risk_profile, top_n=3)
    if df.empty:
        print("No recommendations found. Please ensure database and metrics are populated.")
        return
        
    display_cols = ["scheme_name", "category", "risk_grade", "sharpe_ratio", "cagr_3yr_pct", "expense_ratio_pct", "composite_score"]
    for idx, row in df.iterrows():
        print(f"\nRANK #{idx + 1}: {row['scheme_name']}")
        print(f"   AMC            : {row['fund_house']}")
        print(f"   Category       : {row['category']} | Risk Grade: {row['risk_grade']}")
        print(f"   Sharpe Ratio   : {row['sharpe_ratio']} | 3-Year CAGR: {row['cagr_3yr_pct']}%")
        print(f"   Expense Ratio  : {row['expense_ratio_pct']}% | Composite Score: {row['composite_score']}/100")
        print(f"   Alpha (vs Mkt) : {row['alpha']}% | Rating: {'★' * int(row['morningstar_rating'])}")
    print("=" * 80 + "\n")

if __name__ == "__main__":
    profile = sys.argv[1] if len(sys.argv) > 1 else "Moderate"
    display_recommendations_cli(profile)

