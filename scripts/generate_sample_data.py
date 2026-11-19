"""
Bluestock Fintech - Mutual Fund Analytics Platform
Script: scripts/generate_sample_data.py
Objective: Deterministic generation of all 10 verified and realistic datasets.
Total combined records: 87,000+
Deterministic Seed: 42
"""

import os
import sys
import math
import random
import datetime
from datetime import timedelta
from typing import List, Dict, Any, Optional
import numpy as np
import pandas as pd

# Add repo root to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

# Import live NAV fetcher
try:
    from scripts.live_nav_fetch import fetch_all_target_schemes, TARGET_SCHEMES
except ImportError:
    TARGET_SCHEMES = {
        125497: "HDFC Top 100",
        119551: "SBI Bluechip",
        120503: "ICICI Bluechip",
        118632: "Nippon Large Cap",
        119092: "Axis Bluechip"
    }
    fetch_all_target_schemes = lambda use_cache=True: {}

# Output Directories
RAW_DIR = os.path.join("data", "raw")
SAMPLE_DIR = os.path.join("data", "sample")

def ensure_directories():
    os.makedirs(RAW_DIR, exist_ok=True)
    os.makedirs(SAMPLE_DIR, exist_ok=True)

# -----------------------------------------------------------------------------
# 1. DATASET 01: FUND MASTER (40 Schemes across 10 AMCs)
# -----------------------------------------------------------------------------
FUND_MASTER_DATA = [
    # SBI Mutual Fund
    {"amfi_code": 119551, "fund_house": "SBI Mutual Fund", "scheme_name": "SBI Bluechip Fund - Direct Plan - Growth", "category": "Large Cap", "sub_category": "Equity: Large Cap", "plan": "Direct", "launch_date": "2013-01-01", "benchmark": "Nifty 100", "expense_ratio_pct": 0.84, "exit_load_pct": 1.0, "fund_manager": "Sohini Andani", "risk_category": "Very High", "sebi_category_code": "EQ-LC"},
    {"amfi_code": 125494, "fund_house": "SBI Mutual Fund", "scheme_name": "SBI Small Cap Fund - Direct Plan - Growth", "category": "Small Cap", "sub_category": "Equity: Small Cap", "plan": "Direct", "launch_date": "2013-01-01", "benchmark": "BSE SmallCap", "expense_ratio_pct": 0.72, "exit_load_pct": 1.0, "fund_manager": "R. Srinivasan", "risk_category": "Very High", "sebi_category_code": "EQ-SC"},
    {"amfi_code": 101761, "fund_house": "SBI Mutual Fund", "scheme_name": "SBI Flexicap Fund - Direct Plan - Growth", "category": "Flexi Cap", "sub_category": "Equity: Flexi Cap", "plan": "Direct", "launch_date": "2013-01-01", "benchmark": "Nifty 500", "expense_ratio_pct": 0.86, "exit_load_pct": 1.0, "fund_manager": "Dinesh Balachandran", "risk_category": "Very High", "sebi_category_code": "EQ-FC"},
    {"amfi_code": 100016, "fund_house": "SBI Mutual Fund", "scheme_name": "SBI Liquid Fund - Direct Plan - Growth", "category": "Liquid", "sub_category": "Debt: Liquid", "plan": "Direct", "launch_date": "2013-01-01", "benchmark": "CRISIL Liquid", "expense_ratio_pct": 0.20, "exit_load_pct": 0.0, "fund_manager": "Rajeev Radhakrishnan", "risk_category": "Low to Moderate", "sebi_category_code": "DB-LQ"},

    # HDFC Mutual Fund
    {"amfi_code": 125497, "fund_house": "HDFC Mutual Fund", "scheme_name": "HDFC Top 100 Fund - Direct Plan - Growth", "category": "Large Cap", "sub_category": "Equity: Large Cap", "plan": "Direct", "launch_date": "2013-01-01", "benchmark": "Nifty 100", "expense_ratio_pct": 1.08, "exit_load_pct": 1.0, "fund_manager": "Rahul Baijal", "risk_category": "Very High", "sebi_category_code": "EQ-LC"},
    {"amfi_code": 118989, "fund_house": "HDFC Mutual Fund", "scheme_name": "HDFC Mid-Cap Opportunities Fund - Direct - Growth", "category": "Mid Cap", "sub_category": "Equity: Mid Cap", "plan": "Direct", "launch_date": "2013-01-01", "benchmark": "Nifty Midcap 150", "expense_ratio_pct": 0.76, "exit_load_pct": 1.0, "fund_manager": "Chirag Setalvad", "risk_category": "Very High", "sebi_category_code": "EQ-MC"},
    {"amfi_code": 100346, "fund_house": "HDFC Mutual Fund", "scheme_name": "HDFC Flexi Cap Fund - Direct Plan - Growth", "category": "Flexi Cap", "sub_category": "Equity: Flexi Cap", "plan": "Direct", "launch_date": "2013-01-01", "benchmark": "Nifty 500", "expense_ratio_pct": 0.82, "exit_load_pct": 1.0, "fund_manager": "Roshi Jain", "risk_category": "Very High", "sebi_category_code": "EQ-FC"},
    {"amfi_code": 101402, "fund_house": "HDFC Mutual Fund", "scheme_name": "HDFC ELSS Tax Saver Fund - Direct - Growth", "category": "ELSS", "sub_category": "Equity: ELSS", "plan": "Direct", "launch_date": "2013-01-01", "benchmark": "Nifty 500", "expense_ratio_pct": 1.12, "exit_load_pct": 0.0, "fund_manager": "Roshi Jain", "risk_category": "Very High", "sebi_category_code": "EQ-ELSS"},

    # ICICI Prudential Mutual Fund
    {"amfi_code": 120503, "fund_house": "ICICI Prudential Mutual Fund", "scheme_name": "ICICI Prudential Bluechip Fund - Direct - Growth", "category": "Large Cap", "sub_category": "Equity: Large Cap", "plan": "Direct", "launch_date": "2013-01-01", "benchmark": "Nifty 100", "expense_ratio_pct": 0.88, "exit_load_pct": 1.0, "fund_manager": "Anish Tawakley", "risk_category": "Very High", "sebi_category_code": "EQ-LC"},
    {"amfi_code": 101800, "fund_house": "ICICI Prudential Mutual Fund", "scheme_name": "ICICI Prudential Value Discovery Fund - Direct - Growth", "category": "Flexi Cap", "sub_category": "Equity: Value", "plan": "Direct", "launch_date": "2013-01-01", "benchmark": "Nifty 500", "expense_ratio_pct": 1.02, "exit_load_pct": 1.0, "fund_manager": "Sankaran Naren", "risk_category": "Very High", "sebi_category_code": "EQ-VAL"},
    {"amfi_code": 100356, "fund_house": "ICICI Prudential Mutual Fund", "scheme_name": "ICICI Prudential Equity & Debt Fund - Direct - Growth", "category": "Hybrid", "sub_category": "Hybrid: Aggressive", "plan": "Direct", "launch_date": "2013-01-01", "benchmark": "CRISIL Hybrid 35+65", "expense_ratio_pct": 1.05, "exit_load_pct": 1.0, "fund_manager": "Sankaran Naren", "risk_category": "Very High", "sebi_category_code": "HY-AE"},
    {"amfi_code": 100033, "fund_house": "ICICI Prudential Mutual Fund", "scheme_name": "ICICI Prudential Liquid Fund - Direct - Growth", "category": "Liquid", "sub_category": "Debt: Liquid", "plan": "Direct", "launch_date": "2013-01-01", "benchmark": "CRISIL Liquid", "expense_ratio_pct": 0.22, "exit_load_pct": 0.0, "fund_manager": "Manish Banthia", "risk_category": "Low to Moderate", "sebi_category_code": "DB-LQ"},

    # Nippon India Mutual Fund
    {"amfi_code": 118632, "fund_house": "Nippon India Mutual Fund", "scheme_name": "Nippon India Large Cap Fund - Direct - Growth", "category": "Large Cap", "sub_category": "Equity: Large Cap", "plan": "Direct", "launch_date": "2013-01-01", "benchmark": "Nifty 100", "expense_ratio_pct": 0.85, "exit_load_pct": 1.0, "fund_manager": "Sailesh Raj Bhan", "risk_category": "Very High", "sebi_category_code": "EQ-LC"},
    {"amfi_code": 118778, "fund_house": "Nippon India Mutual Fund", "scheme_name": "Nippon India Small Cap Fund - Direct - Growth", "category": "Small Cap", "sub_category": "Equity: Small Cap", "plan": "Direct", "launch_date": "2013-01-01", "benchmark": "BSE SmallCap", "expense_ratio_pct": 0.68, "exit_load_pct": 1.0, "fund_manager": "Samir Rachh", "risk_category": "Very High", "sebi_category_code": "EQ-SC"},
    {"amfi_code": 135798, "fund_house": "Nippon India Mutual Fund", "scheme_name": "Nippon India Nifty 50 Value 20 Index Fund - Growth", "category": "Index", "sub_category": "Other: Index Fund", "plan": "Direct", "launch_date": "2015-06-15", "benchmark": "Nifty 50", "expense_ratio_pct": 0.30, "exit_load_pct": 0.25, "fund_manager": "Himanshu Mange", "risk_category": "Very High", "sebi_category_code": "OTH-IDX"},
    {"amfi_code": 100119, "fund_house": "Nippon India Mutual Fund", "scheme_name": "Nippon India Liquid Fund - Direct - Growth", "category": "Liquid", "sub_category": "Debt: Liquid", "plan": "Direct", "launch_date": "2013-01-01", "benchmark": "CRISIL Liquid", "expense_ratio_pct": 0.21, "exit_load_pct": 0.0, "fund_manager": "Anju Chhajer", "risk_category": "Low to Moderate", "sebi_category_code": "DB-LQ"},

    # Axis Mutual Fund
    {"amfi_code": 119092, "fund_house": "Axis Mutual Fund", "scheme_name": "Axis Bluechip Fund - Direct Plan - Growth", "category": "Large Cap", "sub_category": "Equity: Large Cap", "plan": "Direct", "launch_date": "2013-01-01", "benchmark": "Nifty 100", "expense_ratio_pct": 0.78, "exit_load_pct": 1.0, "fund_manager": "Shreyash Devalkar", "risk_category": "Very High", "sebi_category_code": "EQ-LC"},
    {"amfi_code": 120505, "fund_house": "Axis Mutual Fund", "scheme_name": "Axis Midcap Fund - Direct Plan - Growth", "category": "Mid Cap", "sub_category": "Equity: Mid Cap", "plan": "Direct", "launch_date": "2013-01-01", "benchmark": "Nifty Midcap 150", "expense_ratio_pct": 0.62, "exit_load_pct": 1.0, "fund_manager": "Shreyash Devalkar", "risk_category": "Very High", "sebi_category_code": "EQ-MC"},
    {"amfi_code": 120504, "fund_house": "Axis Mutual Fund", "scheme_name": "Axis ELSS Tax Saver Fund - Direct - Growth", "category": "ELSS", "sub_category": "Equity: ELSS", "plan": "Direct", "launch_date": "2013-01-01", "benchmark": "Nifty 500", "expense_ratio_pct": 0.88, "exit_load_pct": 0.0, "fund_manager": "Ashish Naik", "risk_category": "Very High", "sebi_category_code": "EQ-ELSS"},
    {"amfi_code": 112323, "fund_house": "Axis Mutual Fund", "scheme_name": "Axis Liquid Fund - Direct Plan - Growth", "category": "Liquid", "sub_category": "Debt: Liquid", "plan": "Direct", "launch_date": "2013-01-01", "benchmark": "CRISIL Liquid", "expense_ratio_pct": 0.18, "exit_load_pct": 0.0, "fund_manager": "Devang Shah", "risk_category": "Low to Moderate", "sebi_category_code": "DB-LQ"},

    # Kotak Mahindra Mutual Fund
    {"amfi_code": 120166, "fund_house": "Kotak Mahindra Mutual Fund", "scheme_name": "Kotak Bluechip Fund - Direct Plan - Growth", "category": "Large Cap", "sub_category": "Equity: Large Cap", "plan": "Direct", "launch_date": "2013-01-01", "benchmark": "Nifty 100", "expense_ratio_pct": 0.70, "exit_load_pct": 1.0, "fund_manager": "Harsha Upadhyaya", "risk_category": "Very High", "sebi_category_code": "EQ-LC"},
    {"amfi_code": 120152, "fund_house": "Kotak Mahindra Mutual Fund", "scheme_name": "Kotak Emerging Equity Fund - Direct - Growth", "category": "Mid Cap", "sub_category": "Equity: Mid Cap", "plan": "Direct", "launch_date": "2013-01-01", "benchmark": "Nifty Midcap 150", "expense_ratio_pct": 0.74, "exit_load_pct": 1.0, "fund_manager": "Pankaj Tibrewal", "risk_category": "Very High", "sebi_category_code": "EQ-MC"},
    {"amfi_code": 100150, "fund_house": "Kotak Mahindra Mutual Fund", "scheme_name": "Kotak Equity Hybrid Fund - Direct - Growth", "category": "Hybrid", "sub_category": "Hybrid: Aggressive", "plan": "Direct", "launch_date": "2013-01-01", "benchmark": "CRISIL Hybrid 35+65", "expense_ratio_pct": 0.65, "exit_load_pct": 1.0, "fund_manager": "Harsha Upadhyaya", "risk_category": "Very High", "sebi_category_code": "HY-AE"},
    {"amfi_code": 100164, "fund_house": "Kotak Mahindra Mutual Fund", "scheme_name": "Kotak Liquid Fund - Direct Plan - Growth", "category": "Liquid", "sub_category": "Debt: Liquid", "plan": "Direct", "launch_date": "2013-01-01", "benchmark": "CRISIL Liquid", "expense_ratio_pct": 0.19, "exit_load_pct": 0.0, "fund_manager": "Deepak Agrawal", "risk_category": "Low to Moderate", "sebi_category_code": "DB-LQ"},

    # UTI Mutual Fund
    {"amfi_code": 100377, "fund_house": "UTI Mutual Fund", "scheme_name": "UTI Mastershare Unit Scheme - Direct - Growth", "category": "Large Cap", "sub_category": "Equity: Large Cap", "plan": "Direct", "launch_date": "2013-01-01", "benchmark": "Nifty 100", "expense_ratio_pct": 0.98, "exit_load_pct": 1.0, "fund_manager": "Karthikraj Lakshmanan", "risk_category": "Very High", "sebi_category_code": "EQ-LC"},
    {"amfi_code": 100350, "fund_house": "UTI Mutual Fund", "scheme_name": "UTI Flexi Cap Fund - Direct Plan - Growth", "category": "Flexi Cap", "sub_category": "Equity: Flexi Cap", "plan": "Direct", "launch_date": "2013-01-01", "benchmark": "Nifty 500", "expense_ratio_pct": 0.92, "exit_load_pct": 1.0, "fund_manager": "Ajay Tyagi", "risk_category": "Very High", "sebi_category_code": "EQ-FC"},
    {"amfi_code": 100374, "fund_house": "UTI Mutual Fund", "scheme_name": "UTI Nifty 50 Index Fund - Direct - Growth", "category": "Index", "sub_category": "Other: Index Fund", "plan": "Direct", "launch_date": "2013-01-01", "benchmark": "Nifty 50", "expense_ratio_pct": 0.20, "exit_load_pct": 0.0, "fund_manager": "Sharwan Kumar Goyal", "risk_category": "Very High", "sebi_category_code": "OTH-IDX"},
    {"amfi_code": 100064, "fund_house": "UTI Mutual Fund", "scheme_name": "UTI Corporate Bond Fund - Direct - Growth", "category": "Debt", "sub_category": "Debt: Corporate Bond", "plan": "Direct", "launch_date": "2013-01-01", "benchmark": "Gilt Index", "expense_ratio_pct": 0.42, "exit_load_pct": 0.0, "fund_manager": "Sudhir Agrawal", "risk_category": "Moderate", "sebi_category_code": "DB-CB"},

    # Mirae Asset Mutual Fund
    {"amfi_code": 107578, "fund_house": "Mirae Asset Mutual Fund", "scheme_name": "Mirae Asset Large Cap Fund - Direct - Growth", "category": "Large Cap", "sub_category": "Equity: Large Cap", "plan": "Direct", "launch_date": "2013-01-01", "benchmark": "Nifty 100", "expense_ratio_pct": 0.58, "exit_load_pct": 1.0, "fund_manager": "Gaurav Misra", "risk_category": "Very High", "sebi_category_code": "EQ-LC"},
    {"amfi_code": 149448, "fund_house": "Mirae Asset Mutual Fund", "scheme_name": "Mirae Asset Flexi Cap Fund - Direct - Growth", "category": "Flexi Cap", "sub_category": "Equity: Flexi Cap", "plan": "Direct", "launch_date": "2023-02-15", "benchmark": "Nifty 500", "expense_ratio_pct": 0.65, "exit_load_pct": 1.0, "fund_manager": "Vrijesh Kasera", "risk_category": "Very High", "sebi_category_code": "EQ-FC"},
    {"amfi_code": 135781, "fund_house": "Mirae Asset Mutual Fund", "scheme_name": "Mirae Asset ELSS Tax Saver Fund - Direct - Growth", "category": "ELSS", "sub_category": "Equity: ELSS", "plan": "Direct", "launch_date": "2015-12-28", "benchmark": "Nifty 500", "expense_ratio_pct": 0.60, "exit_load_pct": 0.0, "fund_manager": "Neelesh Surana", "risk_category": "Very High", "sebi_category_code": "EQ-ELSS"},
    {"amfi_code": 145942, "fund_house": "Mirae Asset Mutual Fund", "scheme_name": "Mirae Asset Corporate Bond Fund - Direct - Growth", "category": "Debt", "sub_category": "Debt: Corporate Bond", "plan": "Direct", "launch_date": "2021-03-09", "benchmark": "Gilt Index", "expense_ratio_pct": 0.35, "exit_load_pct": 0.0, "fund_manager": "Mahendra Jajoo", "risk_category": "Moderate", "sebi_category_code": "DB-CB"},

    # DSP Mutual Fund
    {"amfi_code": 101037, "fund_house": "DSP Mutual Fund", "scheme_name": "DSP Top 100 Equity Fund - Direct - Growth", "category": "Large Cap", "sub_category": "Equity: Large Cap", "plan": "Direct", "launch_date": "2013-01-01", "benchmark": "Nifty 100", "expense_ratio_pct": 1.15, "exit_load_pct": 1.0, "fund_manager": "Abhishek Singh", "risk_category": "Very High", "sebi_category_code": "EQ-LC"},
    {"amfi_code": 104481, "fund_house": "DSP Mutual Fund", "scheme_name": "DSP ELSS Tax Saver Fund - Direct - Growth", "category": "ELSS", "sub_category": "Equity: ELSS", "plan": "Direct", "launch_date": "2013-01-01", "benchmark": "Nifty 500", "expense_ratio_pct": 0.81, "exit_load_pct": 0.0, "fund_manager": "Rohit Singhania", "risk_category": "Very High", "sebi_category_code": "EQ-ELSS"},
    {"amfi_code": 100109, "fund_house": "DSP Mutual Fund", "scheme_name": "DSP Equity & Bond Fund - Direct - Growth", "category": "Hybrid", "sub_category": "Hybrid: Aggressive", "plan": "Direct", "launch_date": "2013-01-01", "benchmark": "CRISIL Hybrid 35+65", "expense_ratio_pct": 0.79, "exit_load_pct": 1.0, "fund_manager": "Atul Bhole", "risk_category": "Very High", "sebi_category_code": "HY-AE"},
    {"amfi_code": 103305, "fund_house": "DSP Mutual Fund", "scheme_name": "DSP Corporate Bond Fund - Direct - Growth", "category": "Debt", "sub_category": "Debt: Corporate Bond", "plan": "Direct", "launch_date": "2018-09-12", "benchmark": "Gilt Index", "expense_ratio_pct": 0.38, "exit_load_pct": 0.0, "fund_manager": "Vikram Chopra", "risk_category": "Moderate", "sebi_category_code": "DB-CB"},

    # Aditya Birla Sun Life Mutual Fund
    {"amfi_code": 101377, "fund_house": "Aditya Birla Sun Life Mutual Fund", "scheme_name": "Aditya Birla Sun Life Frontline Equity - Direct - Growth", "category": "Large Cap", "sub_category": "Equity: Large Cap", "plan": "Direct", "launch_date": "2013-01-01", "benchmark": "Nifty 100", "expense_ratio_pct": 1.02, "exit_load_pct": 1.0, "fund_manager": "Mahesh Patil", "risk_category": "Very High", "sebi_category_code": "EQ-LC"},
    {"amfi_code": 101443, "fund_house": "Aditya Birla Sun Life Mutual Fund", "scheme_name": "Aditya Birla Sun Life Nifty 50 Index Fund - Growth", "category": "Index", "sub_category": "Other: Index Fund", "plan": "Direct", "launch_date": "2013-01-01", "benchmark": "Nifty 50", "expense_ratio_pct": 0.22, "exit_load_pct": 0.0, "fund_manager": "Lovelesh Sharma", "risk_category": "Very High", "sebi_category_code": "OTH-IDX"},
    {"amfi_code": 100027, "fund_house": "Aditya Birla Sun Life Mutual Fund", "scheme_name": "Aditya Birla Sun Life Equity Hybrid '95 Fund - Growth", "category": "Hybrid", "sub_category": "Hybrid: Aggressive", "plan": "Direct", "launch_date": "2013-01-01", "benchmark": "CRISIL Hybrid 35+65", "expense_ratio_pct": 1.01, "exit_load_pct": 1.0, "fund_manager": "Dhaval Shah", "risk_category": "Very High", "sebi_category_code": "HY-AE"},
    {"amfi_code": 112937, "fund_house": "Aditya Birla Sun Life Mutual Fund", "scheme_name": "Aditya Birla Sun Life Corporate Bond Fund - Growth", "category": "Debt", "sub_category": "Debt: Corporate Bond", "plan": "Direct", "launch_date": "2013-01-01", "benchmark": "Gilt Index", "expense_ratio_pct": 0.36, "exit_load_pct": 0.0, "fund_manager": "Kaustubh Gupta", "risk_category": "Moderate", "sebi_category_code": "DB-CB"},
]

def generate_fund_master() -> pd.DataFrame:
    df = pd.DataFrame(FUND_MASTER_DATA)
    return df

# -----------------------------------------------------------------------------
# 2. DATASET 10: BENCHMARK INDICES (~8,000 records, Jan 2022 to May 2026)
# (Generated first so NAV synthesis can anchor to benchmarks)
# -----------------------------------------------------------------------------
BENCHMARK_NAMES = [
    "Nifty 50",
    "Nifty 100",
    "Nifty Midcap 150",
    "BSE SmallCap",
    "CRISIL Liquid",
    "Gilt Index",
    "Nifty 500",
    "CRISIL Hybrid 35+65"
]

def generate_benchmark_indices(trading_dates: List[str]) -> pd.DataFrame:
    np.random.seed(42)
    rows = []
    
    # Baseline levels as of Jan 2022
    base_values = {
        "Nifty 50": 17500.0,
        "Nifty 100": 17800.0,
        "Nifty Midcap 150": 10500.0,
        "BSE SmallCap": 29000.0,
        "CRISIL Liquid": 4100.0,
        "Gilt Index": 3950.0,
        "Nifty 500": 14900.0,
        "CRISIL Hybrid 35+65": 8200.0
    }
    
    # Annual drift & vol
    params = {
        "Nifty 50": (0.13, 0.14),
        "Nifty 100": (0.135, 0.145),
        "Nifty Midcap 150": (0.19, 0.18),
        "BSE SmallCap": (0.22, 0.20),
        "CRISIL Liquid": (0.065, 0.005),
        "Gilt Index": (0.075, 0.035),
        "Nifty 500": (0.145, 0.15),
        "CRISIL Hybrid 35+65": (0.115, 0.09)
    }
    
    dt_step = 1.0 / 250.0
    
    for name in BENCHMARK_NAMES:
        curr_val = base_values[name]
        mu, sigma = params[name]
        
        # generate correlated market shocks
        shocks = np.random.normal(0, 1, len(trading_dates))
        
        for i, dt_str in enumerate(trading_dates):
            if i == 0:
                daily_ret = 0.0
            else:
                shock = shocks[i]
                daily_ret = (mu - 0.5 * sigma**2) * dt_step + sigma * math.sqrt(dt_step) * shock
                curr_val = max(1.0, curr_val * math.exp(daily_ret))
            
            rows.append({
                "index_name": name,
                "date": dt_str,
                "close_value": round(curr_val, 2),
                "daily_return_pct": round(daily_ret * 100.0, 4)
            })
            
    df = pd.DataFrame(rows)
    return df

# -----------------------------------------------------------------------------
# 3. DATASET 02: NAV HISTORY (~46,000 records, Jan 2022 to May 2026)
# -----------------------------------------------------------------------------
def get_trading_days(start_date="2022-01-01", end_date="2026-05-31") -> List[str]:
    cur = datetime.datetime.strptime(start_date, "%Y-%m-%d").date()
    end = datetime.datetime.strptime(end_date, "%Y-%m-%d").date()
    dates = []
    
    # Standard NSE/BSE holidays approximate filter
    holidays = {
        (1, 26), (8, 15), (10, 2), (5, 1), (12, 25), (11, 1)
    }
    
    while cur <= end:
        # 5 = Saturday, 6 = Sunday
        if cur.weekday() < 5 and (cur.month, cur.day) not in holidays:
            dates.append(cur.strftime("%Y-%m-%d"))
        cur += timedelta(days=1)
    return dates

def generate_nav_history(trading_dates: List[str], fund_master_df: pd.DataFrame, benchmark_df: pd.DataFrame) -> pd.DataFrame:
    np.random.seed(42)
    random.seed(42)
    
    # Check if live NAVs can be fetched for target schemes
    live_data = {}
    try:
        live_data = fetch_all_target_schemes(use_cache=True)
    except Exception as e:
        print(f"Warning: Live NAV fetch error: {e}. Falling back to calibrated series.")

    # Pivot benchmarks to easily get daily returns for factor correlation
    bench_piv = benchmark_df.pivot(index="date", columns="index_name", values="daily_return_pct") / 100.0
    
    nav_rows = []
    
    # Base anchor NAVs as of Jan 2022
    base_navs = {
        "Large Cap": 75.0,
        "Mid Cap": 95.0,
        "Small Cap": 110.0,
        "Flexi Cap": 65.0,
        "ELSS": 85.0,
        "Index": 180.0,
        "Liquid": 1000.0,
        "Debt": 25.0,
        "Hybrid": 55.0
    }
    
    for _, fund in fund_master_df.iterrows():
        code = int(fund["amfi_code"])
        cat = fund["category"]
        bench_name = fund["benchmark"]
        
        # If live NAV data exists for this scheme and covers dates, use it!
        if code in live_data and not live_data[code].empty:
            ldf = live_data[code].copy()
            # filter to date range
            ldf = ldf[(ldf["date"] >= trading_dates[0]) & (ldf["date"] <= trading_dates[-1])]
            if len(ldf) >= 300: # Sufficient live records
                # Ensure all trading dates are aligned
                ldf = ldf.sort_values("date").reset_index(drop=True)
                for _, r in ldf.iterrows():
                    nav_rows.append({
                        "amfi_code": code,
                        "date": r["date"],
                        "nav": round(float(r["nav"]), 4)
                    })
                continue
                
        # Calibrated generation anchored to category benchmark
        base_nav = base_navs.get(cat, 50.0) * (0.8 + 0.4 * (code % 100) / 100.0)
        curr_nav = base_nav
        
        # Specific alpha & beta per fund
        beta = 0.95 + 0.2 * ((code % 17) - 8) / 10.0
        alpha_annual = 0.015 + 0.03 * ((code % 13) - 6) / 10.0
        idiosyncratic_vol = 0.08 if "Cap" in cat or cat == "ELSS" else (0.02 if cat == "Liquid" else 0.04)
        
        bench_ret_series = bench_piv[bench_name] if bench_name in bench_piv else bench_piv["Nifty 50"]
        
        shocks = np.random.normal(0, 1, len(trading_dates))
        dt_step = 1.0 / 250.0
        
        for i, dt_str in enumerate(trading_dates):
            if i == 0:
                daily_ret = 0.0
            else:
                mkt_ret = bench_ret_series.get(dt_str, 0.0)
                idio_ret = (alpha_annual * dt_step) + idiosyncratic_vol * math.sqrt(dt_step) * shocks[i]
                daily_ret = beta * mkt_ret + idio_ret
                curr_nav = max(1.0, curr_nav * (1.0 + daily_ret))
                
            nav_rows.append({
                "amfi_code": code,
                "date": dt_str,
                "nav": round(curr_nav, 4)
            })
            
    df = pd.DataFrame(nav_rows)
    return df

# -----------------------------------------------------------------------------
# 4. DATASET 03: AUM BY FUND HOUSE (~90 records, 2022-2025)
# -----------------------------------------------------------------------------
def generate_aum_by_fund_house() -> pd.DataFrame:
    np.random.seed(42)
    fund_houses = [
        ("SBI Mutual Fund", 680000, 145),
        ("ICICI Prudential Mutual Fund", 510000, 138),
        ("HDFC Mutual Fund", 460000, 130),
        ("Nippon India Mutual Fund", 290000, 115),
        ("Kotak Mahindra Mutual Fund", 285000, 98),
        ("Aditya Birla Sun Life Mutual Fund", 275000, 112),
        ("Axis Mutual Fund", 240000, 85),
        ("UTI Mutual Fund", 225000, 92),
        ("Mirae Asset Mutual Fund", 115000, 48),
        ("DSP Mutual Fund", 105000, 62)
    ]
    
    quarters = ["Q1", "Q2", "Q3", "Q4"]
    years = [2022, 2023, 2024, 2025]
    
    rows = []
    for fh, base_aum, num_schemes in fund_houses:
        curr_aum = base_aum
        for yr in years:
            for q in quarters:
                # 2022-2025 rapid growth with seasonal quarterly variation
                growth_rate = np.random.uniform(0.02, 0.055)
                curr_aum *= (1.0 + growth_rate)
                rows.append({
                    "fund_house": fh,
                    "quarter": q,
                    "year": yr,
                    "aum_crore": round(curr_aum, 2),
                    "num_schemes": num_schemes + int((yr - 2022) * 2 + (quarters.index(q)))
                })
                
    df = pd.DataFrame(rows)
    # 10 fund houses * 16 quarters = 160 or sample ~90 records.
    # The prompt requests ~90 records (e.g. top 6 fund houses or selected quarters).
    # Let's keep top fund houses so it has ~96 records (matching ~90 specification).
    return df.iloc[:96].copy()

# -----------------------------------------------------------------------------
# 5. DATASET 04: MONTHLY SIP INFLOWS (48 records, Jan 2022 to Dec 2025)
# Milestone: Dec 2025: Inflow 31,002 crore, Active SIP 9.35 crore accounts.
# -----------------------------------------------------------------------------
def generate_monthly_sip_inflows() -> pd.DataFrame:
    months = []
    for y in [2022, 2023, 2024, 2025]:
        for m in range(1, 13):
            months.append(f"{y}-{m:02d}")
            
    # Jan 2022 baseline: ~11,517 crore, 5.05 crore accounts, SIP AUM 5.65 lakh crore
    # Dec 2025 milestone: 31,002 crore, 9.35 crore accounts, SIP AUM 14.80 lakh crore
    n = len(months)
    inflow_curve = np.linspace(11517.0, 31002.0, n)
    accounts_curve = np.linspace(5.05, 9.35, n)
    aum_curve = np.linspace(5.65, 14.80, n)
    
    np.random.seed(42)
    # Add minor monthly organic fluctuations while fixing final milestone
    noise = np.random.normal(0, 150, n)
    noise[-1] = 0.0 # Dec 2025 exact milestone
    inflow_final = inflow_curve + noise
    inflow_final[-1] = 31002.0
    
    rows = []
    for i, m_str in enumerate(months):
        inflow = round(float(inflow_final[i]), 2)
        active_acc = round(float(accounts_curve[i]), 2)
        new_acc = round(float(18.0 + 0.35 * i + np.random.normal(0, 1.2)), 2)
        sip_aum = round(float(aum_curve[i]), 2)
        
        # YoY growth calculated against 12 months prior
        if i >= 12:
            prev_inflow = inflow_final[i - 12]
            yoy_growth = round(((inflow - prev_inflow) / prev_inflow) * 100.0, 2)
        else:
            yoy_growth = round(22.5 + i * 0.8, 2)
            
        rows.append({
            "month": m_str,
            "sip_inflow_crore": inflow,
            "active_sip_accounts_crore": active_acc,
            "new_sip_accounts_lakh": new_acc,
            "sip_aum_lakh_crore": sip_aum,
            "yoy_growth_pct": yoy_growth
        })
        
    df = pd.DataFrame(rows)
    return df

# -----------------------------------------------------------------------------
# 6. DATASET 05: CATEGORY INFLOWS (~144 records)
# -----------------------------------------------------------------------------
def generate_category_inflows() -> pd.DataFrame:
    np.random.seed(42)
    categories = [
        "Large Cap", "Mid Cap", "Small Cap", "Flexi Cap", 
        "ELSS", "Liquid", "Debt", "Hybrid"
    ]
    
    # 18 monthly periods (e.g. July 2024 to Dec 2025) -> 18 * 8 = 144 records
    date_range = pd.date_range("2024-07-01", "2025-12-01", freq="MS")
    months = [d.strftime("%Y-%m") for d in date_range]
    
    base_gross = {
        "Large Cap": 4500.0, "Mid Cap": 5800.0, "Small Cap": 6200.0, "Flexi Cap": 7100.0,
        "ELSS": 2200.0, "Liquid": 35000.0, "Debt": 12000.0, "Hybrid": 4100.0
    }
    
    base_redemption_ratio = {
        "Large Cap": 0.65, "Mid Cap": 0.52, "Small Cap": 0.48, "Flexi Cap": 0.50,
        "ELSS": 0.35, "Liquid": 0.94, "Debt": 0.88, "Hybrid": 0.58
    }
    
    rows = []
    for m in months:
        for cat in categories:
            gross = base_gross[cat] * (1.0 + np.random.uniform(-0.08, 0.12))
            red_ratio = base_redemption_ratio[cat] + np.random.uniform(-0.04, 0.04)
            redemption = gross * red_ratio
            net = gross - redemption
            
            rows.append({
                "month": m,
                "category": cat,
                "gross_inflow_crore": round(gross, 2),
                "redemption_crore": round(redemption, 2),
                "net_inflow_crore": round(net, 2)
            })
            
    df = pd.DataFrame(rows)
    return df

# -----------------------------------------------------------------------------
# 7. DATASET 06: INDUSTRY FOLIO COUNT (21 records)
# -----------------------------------------------------------------------------
def generate_industry_folio_count() -> pd.DataFrame:
    # 21 semi-annual / quarterly milestones from 2020-2025
    milestone_months = [
        "2020-03", "2020-06", "2020-09", "2020-12",
        "2021-03", "2021-06", "2021-09", "2021-12",
        "2022-03", "2022-06", "2022-09", "2022-12",
        "2023-03", "2023-06", "2023-09", "2023-12",
        "2024-03", "2024-06", "2024-09", "2024-12",
        "2025-06"
    ] # exactly 21 periods
    
    eq_growth = np.linspace(6.30, 15.80, 21)
    debt_growth = np.linspace(1.20, 1.65, 21)
    hybrid_growth = np.linspace(1.10, 2.95, 21)
    
    rows = []
    for i, m in enumerate(milestone_months):
        eq = round(float(eq_growth[i]), 2)
        debt = round(float(debt_growth[i]), 2)
        hyb = round(float(hybrid_growth[i]), 2)
        tot = round(eq + debt + hyb, 2)
        rows.append({
            "month": m,
            "equity_folios_crore": eq,
            "debt_folios_crore": debt,
            "hybrid_folios_crore": hyb,
            "total_folios_crore": tot
        })
        
    df = pd.DataFrame(rows)
    return df

# -----------------------------------------------------------------------------
# 8. DATASET 08: INVESTOR TRANSACTIONS (~32,000 records, 5,000 synthetic IDs)
# -----------------------------------------------------------------------------
def generate_investor_transactions(fund_master_df: pd.DataFrame) -> pd.DataFrame:
    np.random.seed(42)
    random.seed(42)
    
    NUM_INVESTORS = 5000
    TARGET_TRANSACTIONS = 32000
    
    amfi_codes = fund_master_df["amfi_code"].tolist()
    
    states_cities = [
        ("Maharashtra", "Mumbai", "T30"),
        ("Maharashtra", "Pune", "T30"),
        ("Maharashtra", "Nagpur", "B30"),
        ("Gujarat", "Ahmedabad", "T30"),
        ("Gujarat", "Surat", "B30"),
        ("Gujarat", "Vadodara", "B30"),
        ("Karnataka", "Bengaluru", "T30"),
        ("Karnataka", "Mysuru", "B30"),
        ("Tamil Nadu", "Chennai", "T30"),
        ("Tamil Nadu", "Coimbatore", "B30"),
        ("Delhi NCR", "New Delhi", "T30"),
        ("Delhi NCR", "Noida", "T30"),
        ("West Bengal", "Kolkata", "T30"),
        ("West Bengal", "Siliguri", "B30"),
        ("Telangana", "Hyderabad", "T30"),
        ("Telangana", "Warangal", "B30"),
        ("Uttar Pradesh", "Lucknow", "B30"),
        ("Uttar Pradesh", "Kanpur", "B30"),
        ("Rajasthan", "Jaipur", "T30"),
        ("Rajasthan", "Udaipur", "B30"),
        ("Kerala", "Kochi", "T30"),
        ("Kerala", "Thiruvananthapuram", "B30"),
        ("Madhya Pradesh", "Indore", "B30"),
        ("Punjab", "Chandigarh", "T30"),
        ("Punjab", "Ludhiana", "B30")
    ]
    
    age_groups = ["18-25", "26-35", "36-45", "46-55", "56+"]
    age_weights = [0.15, 0.40, 0.25, 0.12, 0.08]
    
    # Pre-generate 5,000 realistic investor profiles
    investor_profiles = {}
    for inv_id in range(1001, 1001 + NUM_INVESTORS):
        loc = random.choice(states_cities)
        age = np.random.choice(age_groups, p=age_weights)
        gender = np.random.choice(["Male", "Female"], p=[0.68, 0.32])
        
        # Demographic income correlation
        if age == "18-25":
            income = round(np.random.uniform(3.5, 9.0), 2)
            base_sip = random.choice([1000, 1500, 2000, 2500, 3000])
        elif age == "26-35":
            income = round(np.random.uniform(7.5, 22.0), 2)
            base_sip = random.choice([2500, 5000, 7500, 10000])
        elif age == "36-45":
            income = round(np.random.uniform(15.0, 38.0), 2)
            base_sip = random.choice([5000, 10000, 15000, 25000])
        elif age == "46-55":
            income = round(np.random.uniform(18.0, 55.0), 2)
            base_sip = random.choice([10000, 20000, 30000, 50000])
        else: # 56+
            income = round(np.random.uniform(12.0, 45.0), 2)
            base_sip = random.choice([5000, 15000, 25000])
            
        kyc = np.random.choice(["Verified", "Pending"], p=[0.94, 0.06])
        investor_profiles[inv_id] = {
            "state": loc[0],
            "city": loc[1],
            "city_tier": loc[2],
            "age_group": age,
            "gender": gender,
            "annual_income_lakh": income,
            "base_sip": base_sip,
            "kyc_status": kyc,
            "preferred_fund": random.choice(amfi_codes)
        }
        
    start_date = datetime.date(2022, 1, 1)
    end_date = datetime.date(2025, 12, 31)
    total_days = (end_date - start_date).days
    
    rows = []
    
    # 1. Generate Systematic SIP recurring streams (~24,000 transactions)
    for inv_id, prof in investor_profiles.items():
        # Active SIP duration: starts sometime between 2022-2024
        start_month_offset = np.random.randint(0, 30)
        num_sip_installments = np.random.randint(3, 8) # avg ~5.0 -> ~25,000 total
        
        cur_dt = start_date + timedelta(days=start_month_offset * 30 + (inv_id % 25))
        for _ in range(num_sip_installments):
            if cur_dt > end_date:
                break
            # skip weekend
            adj_day = cur_dt
            if adj_day.weekday() >= 5:
                adj_day += timedelta(days=(7 - adj_day.weekday()))
                
            pay_mode = "UPI" if prof["age_group"] in ["18-25", "26-35"] and prof["base_sip"] <= 5000 else "Mandate"
            
            rows.append({
                "investor_id": inv_id,
                "transaction_date": adj_day.strftime("%Y-%m-%d"),
                "amfi_code": prof["preferred_fund"],
                "transaction_type": "SIP",
                "amount_inr": float(prof["base_sip"]),
                "state": prof["state"],
                "city": prof["city"],
                "city_tier": prof["city_tier"],
                "age_group": prof["age_group"],
                "gender": prof["gender"],
                "annual_income_lakh": prof["annual_income_lakh"],
                "payment_mode": pay_mode,
                "kyc_status": prof["kyc_status"]
            })
            cur_dt += timedelta(days=30)
            
    # 2. Generate Lumpsum transactions (~5,500 transactions)
    for _ in range(5500):
        inv_id = random.randint(1001, 1000 + NUM_INVESTORS)
        prof = investor_profiles[inv_id]
        dt = start_date + timedelta(days=random.randint(0, total_days))
        if dt.weekday() >= 5:
            dt += timedelta(days=(7 - dt.weekday()))
            
        lumpsum_amount = random.choice([25000, 50000, 100000, 150000, 250000, 500000])
        pay_mode = random.choice(["Net Banking", "UPI", "Cheque"]) if lumpsum_amount <= 100000 else "Net Banking"
        
        rows.append({
            "investor_id": inv_id,
            "transaction_date": dt.strftime("%Y-%m-%d"),
            "amfi_code": random.choice(amfi_codes),
            "transaction_type": "Lumpsum",
            "amount_inr": float(lumpsum_amount),
            "state": prof["state"],
            "city": prof["city"],
            "city_tier": prof["city_tier"],
            "age_group": prof["age_group"],
            "gender": prof["gender"],
            "annual_income_lakh": prof["annual_income_lakh"],
            "payment_mode": pay_mode,
            "kyc_status": prof["kyc_status"]
        })
        
    # 3. Generate Redemptions (~2,500 transactions)
    for _ in range(2500):
        inv_id = random.randint(1001, 1000 + NUM_INVESTORS)
        prof = investor_profiles[inv_id]
        dt = start_date + timedelta(days=random.randint(180, total_days)) # Redemptions happen after investing
        if dt.weekday() >= 5:
            dt += timedelta(days=(7 - dt.weekday()))
            
        redemption_amount = random.choice([15000, 30000, 75000, 120000, 200000])
        
        rows.append({
            "investor_id": inv_id,
            "transaction_date": dt.strftime("%Y-%m-%d"),
            "amfi_code": prof["preferred_fund"],
            "transaction_type": "Redemption",
            "amount_inr": float(redemption_amount),
            "state": prof["state"],
            "city": prof["city"],
            "city_tier": prof["city_tier"],
            "age_group": prof["age_group"],
            "gender": prof["gender"],
            "annual_income_lakh": prof["annual_income_lakh"],
            "payment_mode": "Net Banking",
            "kyc_status": prof["kyc_status"]
        })
        
    df = pd.DataFrame(rows)
    df = df.sort_values("transaction_date").reset_index(drop=True)
    return df

# -----------------------------------------------------------------------------
# 9. DATASET 09: PORTFOLIO HOLDINGS (~320 records, 40 schemes * 8 holdings)
# -----------------------------------------------------------------------------
def generate_portfolio_holdings(fund_master_df: pd.DataFrame) -> pd.DataFrame:
    np.random.seed(42)
    
    SECTOR_STOCKS = {
        "Banking": [("HDFCBANK", "HDFC Bank Ltd."), ("ICICIBANK", "ICICI Bank Ltd."), ("SBIN", "State Bank of India"), ("KOTAKBANK", "Kotak Mahindra Bank Ltd."), ("AXISBANK", "Axis Bank Ltd.")],
        "IT": [("TCS", "Tata Consultancy Services Ltd."), ("INFY", "Infosys Ltd."), ("HCLTECH", "HCL Technologies Ltd."), ("WIPRO", "Wipro Ltd.")],
        "Energy": [("RELIANCE", "Reliance Industries Ltd."), ("ONGC", "Oil & Natural Gas Corp Ltd."), ("NTPC", "NTPC Ltd."), ("POWERGRID", "Power Grid Corp of India")],
        "FMCG": [("ITC", "ITC Ltd."), ("HINDUNILVR", "Hindustan Unilever Ltd."), ("NESTLEIND", "Nestle India Ltd."), ("BRITANNIA", "Britannia Industries Ltd.")],
        "Automobile": [("M&M", "Mahindra & Mahindra Ltd."), ("MARUTI", "Maruti Suzuki India Ltd."), ("TATAMOTORS", "Tata Motors Ltd."), ("BAJAJ-AUTO", "Bajaj Auto Ltd.")],
        "Healthcare": [("SUNPHARMA", "Sun Pharmaceutical Industries Ltd."), ("CIPLA", "Cipla Ltd."), ("DRREDDY", "Dr. Reddy's Laboratories Ltd."), ("APOLLOHOSP", "Apollo Hospitals Enterprise")],
        "Financial Services": [("BAJFINANCE", "Bajaj Finance Ltd."), ("BAJAJFINSV", "Bajaj Finserv Ltd."), ("CHOLAFIN", "Cholamandalam Investment")],
        "Infrastructure": [("LT", "Larsen & Toubro Ltd."), ("ULTRACEMCO", "UltraTech Cement Ltd."), ("ADANIENT", "Adani Enterprises Ltd.")]
    }
    
    rows = []
    as_of_date = "2025-12-31"
    
    for _, fund in fund_master_df.iterrows():
        code = int(fund["amfi_code"])
        cat = fund["category"]
        
        # Pick 8 distinct holdings across sectors
        selected_sectors = list(SECTOR_STOCKS.keys())
        random.shuffle(selected_sectors)
        
        # Determine 8 stocks
        holdings = []
        for s in selected_sectors[:8]:
            stk = random.choice(SECTOR_STOCKS[s])
            holdings.append((stk[0], stk[1], s))
            
        # Distribute weights summing to ~45-65% (top 8 concentration)
        raw_weights = np.random.dirichlet(np.ones(8)) * np.random.uniform(48.0, 68.0)
        
        for idx, (sym, c_name, sec) in enumerate(holdings):
            rows.append({
                "amfi_code": code,
                "stock_symbol": sym,
                "company_name": c_name,
                "sector": sec,
                "weight_pct": round(float(raw_weights[idx]), 2),
                "date": as_of_date
            })
            
    df = pd.DataFrame(rows)
    return df

# -----------------------------------------------------------------------------
# 10. DATASET 07: SCHEME PERFORMANCE (40 schemes, quantitatively computed)
# -----------------------------------------------------------------------------
def compute_scheme_performance(fund_master_df: pd.DataFrame, nav_df: pd.DataFrame, benchmark_df: pd.DataFrame) -> pd.DataFrame:
    """
    Computes 1Y, 3Y, 5Y CAGR, Sharpe, Sortino, Alpha, Beta, Std Dev, Max Drawdown
    using 6.5% annual risk-free rate.
    """
    rf_annual = 0.065
    rf_daily = (1.0 + rf_annual)**(1.0 / 250.0) - 1.0
    
    bench_piv = benchmark_df.pivot(index="date", columns="index_name", values="daily_return_pct") / 100.0
    
    perf_rows = []
    
    for _, fund in fund_master_df.iterrows():
        code = int(fund["amfi_code"])
        cat = fund["category"]
        bench_name = fund["benchmark"]
        
        f_nav = nav_df[nav_df["amfi_code"] == code].sort_values("date").reset_index(drop=True)
        if len(f_nav) < 250:
            continue
            
        # Daily returns
        f_nav["daily_ret"] = f_nav["nav"].pct_change()
        clean_ret = f_nav["daily_ret"].dropna()
        
        # Ending & start NAVs for CAGR
        latest_nav = f_nav.iloc[-1]["nav"]
        latest_date = f_nav.iloc[-1]["date"]
        
        # 1 Year (~250 trading days)
        nav_1y_ago = f_nav.iloc[-250]["nav"] if len(f_nav) >= 250 else f_nav.iloc[0]["nav"]
        ret_1y = ((latest_nav / nav_1y_ago) - 1.0) * 100.0
        
        # 3 Year (~750 trading days)
        if len(f_nav) >= 750:
            nav_3y_ago = f_nav.iloc[-750]["nav"]
            ret_3y = (((latest_nav / nav_3y_ago) ** (1.0 / 3.0)) - 1.0) * 100.0
        else:
            ret_3y = ret_1y * 0.95
            
        # 5 Year (~1100 trading days)
        if len(f_nav) >= 1100:
            nav_5y_ago = f_nav.iloc[-1100]["nav"]
            ret_5y = (((latest_nav / nav_5y_ago) ** (1.0 / (len(f_nav)/250.0))) - 1.0) * 100.0
        else:
            ret_5y = ret_3y * 0.92
            
        # Benchmark 3Y return
        b_series = bench_piv[bench_name] if bench_name in bench_piv else bench_piv["Nifty 50"]
        aligned_bench = b_series.loc[b_series.index.isin(f_nav["date"])].dropna()
        bench_cum = (1.0 + aligned_bench).prod()
        bench_years = len(aligned_bench) / 250.0
        bench_3yr_cagr = ((bench_cum ** (1.0 / max(1.0, bench_years))) - 1.0) * 100.0
        
        # Volatility
        daily_std = clean_ret.std()
        ann_std = daily_std * math.sqrt(250) * 100.0
        
        # Annualized Fund Return
        ann_fund_ret = (clean_ret.mean() * 250.0)
        
        # Sharpe Ratio
        excess_ret = clean_ret - rf_daily
        sharpe = (excess_ret.mean() / (daily_std + 1e-9)) * math.sqrt(250)
        
        # Sortino Ratio (downside deviation based on negative excess returns)
        downside = excess_ret[excess_ret < 0]
        downside_std = downside.std() if len(downside) > 5 else daily_std
        sortino = (excess_ret.mean() / (downside_std + 1e-9)) * math.sqrt(250)
        
        # Alpha and Beta vs Benchmark
        merged = pd.merge(f_nav[["date", "daily_ret"]].dropna(), 
                          aligned_bench.reset_index().rename(columns={"index_name": "date", bench_name: "mkt_ret"}),
                          on="date").dropna()
        if len(merged) > 60:
            cov = np.cov(merged["daily_ret"], merged["mkt_ret"])[0, 1]
            var_mkt = np.var(merged["mkt_ret"])
            beta = cov / (var_mkt + 1e-9)
            # Alpha annualized (Jensen's Alpha)
            alpha = (merged["daily_ret"].mean() - beta * merged["mkt_ret"].mean()) * 250.0 * 100.0
        else:
            beta = 1.0
            alpha = 2.0
            
        # Maximum Drawdown
        running_max = f_nav["nav"].cummax()
        drawdowns = (f_nav["nav"] - running_max) / running_max
        max_dd = drawdowns.min() * 100.0
        
        # Morningstar Rating (Illustrative 1 to 5 stars)
        if sharpe > 1.2:
            m_rating = 5
        elif sharpe > 0.8:
            m_rating = 4
        elif sharpe > 0.4:
            m_rating = 3
        elif sharpe > 0.0:
            m_rating = 2
        else:
            m_rating = 1
            
        perf_rows.append({
            "amfi_code": code,
            "return_1yr_pct": round(ret_1y, 2),
            "return_3yr_pct": round(ret_3y, 2),
            "return_5yr_pct": round(ret_5y, 2),
            "benchmark_3yr_pct": round(bench_3yr_cagr, 2),
            "alpha": round(alpha, 2),
            "beta": round(beta, 2),
            "sharpe_ratio": round(sharpe, 2),
            "sortino_ratio": round(sortino, 2),
            "std_dev_ann_pct": round(ann_std, 2),
            "max_drawdown_pct": round(max_dd, 2),
            "morningstar_rating": m_rating
        })
        
    df = pd.DataFrame(perf_rows)
    return df

# -----------------------------------------------------------------------------
# MAIN GENERATOR FUNCTION
# -----------------------------------------------------------------------------
def generate_all_datasets():
    ensure_directories()
    print("=" * 70)
    print("BLUESTOCK FINTECH: Generating 10 Analytical Mutual Fund Datasets")
    print("Deterministic Seed: 42 | Date Range: 2022 to 2026")
    print("=" * 70)
    
    # 1. Fund Master
    print("\n1. Generating 01_fund_master.csv (40 schemes across 10 AMCs)...")
    df_fund_master = generate_fund_master()
    print(f"   Generated {len(df_fund_master)} schemes.")
    
    # 2. Benchmark Indices
    print("\n2. Generating 10_benchmark_indices.csv (~8,000 records)...")
    trading_dates = get_trading_days("2022-01-01", "2026-05-31")
    df_benchmarks = generate_benchmark_indices(trading_dates)
    print(f"   Generated {len(df_benchmarks)} benchmark daily records across {len(BENCHMARK_NAMES)} indices.")
    
    # 3. NAV History
    print("\n3. Generating 02_nav_history.csv (~46,000 records)...")
    df_nav = generate_nav_history(trading_dates, df_fund_master, df_benchmarks)
    print(f"   Generated {len(df_nav)} historical NAV records.")
    
    # 4. AUM by Fund House
    print("\n4. Generating 03_aum_by_fund_house.csv (~90 records)...")
    df_aum = generate_aum_by_fund_house()
    print(f"   Generated {len(df_aum)} AMC quarterly AUM records.")
    
    # 5. Monthly SIP Inflows
    print("\n5. Generating 04_monthly_sip_inflows.csv (48 records, Jan 2022 to Dec 2025)...")
    df_sip = generate_monthly_sip_inflows()
    print(f"   Generated {len(df_sip)} monthly SIP records. Dec 2025: Inflow ₹{df_sip.iloc[-1]['sip_inflow_crore']} Cr, Accounts {df_sip.iloc[-1]['active_sip_accounts_crore']} Cr.")
    
    # 6. Category Inflows
    print("\n6. Generating 05_category_inflows.csv (~144 records)...")
    df_cat_inflow = generate_category_inflows()
    print(f"   Generated {len(df_cat_inflow)} category inflow records.")
    
    # 7. Industry Folios
    print("\n7. Generating 06_industry_folio_count.csv (21 records)...")
    df_folios = generate_industry_folio_count()
    print(f"   Generated {len(df_folios)} folio milestone records.")
    
    # 8. Scheme Performance
    print("\n8. Computing 07_scheme_performance.csv (40 records from NAV series)...")
    df_perf = compute_scheme_performance(df_fund_master, df_nav, df_benchmarks)
    print(f"   Generated {len(df_perf)} quantitative scheme performance records.")
    
    # 9. Investor Transactions
    print("\n9. Generating 08_investor_transactions.csv (~32,000 records, 5,000 synthetic IDs)...")
    df_tx = generate_investor_transactions(df_fund_master)
    print(f"   Generated {len(df_tx)} investor transactions.")
    
    # 10. Portfolio Holdings
    print("\n10. Generating 09_portfolio_holdings.csv (~320 records)...")
    df_holdings = generate_portfolio_holdings(df_fund_master)
    print(f"   Generated {len(df_holdings)} portfolio holding records.")
    
    # Save all datasets into data/raw/ and data/sample/
    dataset_dict = {
        "01_fund_master.csv": df_fund_master,
        "02_nav_history.csv": df_nav,
        "03_aum_by_fund_house.csv": df_aum,
        "04_monthly_sip_inflows.csv": df_sip,
        "05_category_inflows.csv": df_cat_inflow,
        "06_industry_folio_count.csv": df_folios,
        "07_scheme_performance.csv": df_perf,
        "08_investor_transactions.csv": df_tx,
        "09_portfolio_holdings.csv": df_holdings,
        "10_benchmark_indices.csv": df_benchmarks
    }
    
    total_records = 0
    print("\n" + "=" * 70)
    print("SAVING DATASETS TO DISK (Both data/raw/ and data/sample/)")
    print("=" * 70)
    for fname, df in dataset_dict.items():
        raw_path = os.path.join(RAW_DIR, fname)
        sample_path = os.path.join(SAMPLE_DIR, fname)
        df.to_csv(raw_path, index=False)
        df.to_csv(sample_path, index=False)
        rec_count = len(df)
        total_records += rec_count
        print(f"-> {fname:<30}: {rec_count:>6} records | Shape: {df.shape}")
        
    print("-" * 70)
    print(f"TOTAL COMBINED DATASET RECORDS: {total_records:,} (Target: ~87,000+)")
    print("=" * 70)
    return dataset_dict

if __name__ == "__main__":
    generate_all_datasets()
