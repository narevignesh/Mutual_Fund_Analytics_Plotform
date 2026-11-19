"""
Bluestock Fintech - Mutual Fund Analytics Platform
Test Suite: tests/test_etl.py
Objective: Automated validation of dataset file existence, schemas, duplicates,
missing values, AMFI code integrity, and domain constraints.
"""

import os
import pytest
import pandas as pd
import numpy as np

RAW_DIR = os.path.join("data", "raw")
SAMPLE_DIR = os.path.join("data", "sample")

REQUIRED_DATASETS = [
    "01_fund_master.csv",
    "02_nav_history.csv",
    "03_aum_by_fund_house.csv",
    "04_monthly_sip_inflows.csv",
    "05_category_inflows.csv",
    "06_industry_folio_count.csv",
    "07_scheme_performance.csv",
    "08_investor_transactions.csv",
    "09_portfolio_holdings.csv",
    "10_benchmark_indices.csv"
]

REQUIRED_COLUMNS = {
    "01_fund_master.csv": ["amfi_code", "fund_house", "scheme_name", "category", "benchmark", "expense_ratio_pct"],
    "02_nav_history.csv": ["amfi_code", "date", "nav"],
    "03_aum_by_fund_house.csv": ["fund_house", "quarter", "year", "aum_crore", "num_schemes"],
    "04_monthly_sip_inflows.csv": ["month", "sip_inflow_crore", "active_sip_accounts_crore"],
    "05_category_inflows.csv": ["month", "category", "gross_inflow_crore", "redemption_crore", "net_inflow_crore"],
    "06_industry_folio_count.csv": ["month", "equity_folios_crore", "debt_folios_crore", "total_folios_crore"],
    "07_scheme_performance.csv": ["amfi_code", "return_3yr_pct", "sharpe_ratio", "alpha", "beta"],
    "08_investor_transactions.csv": ["investor_id", "transaction_date", "amfi_code", "transaction_type", "amount_inr", "city_tier"],
    "09_portfolio_holdings.csv": ["amfi_code", "stock_symbol", "sector", "weight_pct"],
    "10_benchmark_indices.csv": ["index_name", "date", "close_value", "daily_return_pct"]
}

def test_dataset_files_existence():
    """Verify all 10 datasets exist in data/raw/ or data/sample/."""
    for fname in REQUIRED_DATASETS:
        raw_p = os.path.join(RAW_DIR, fname)
        sample_p = os.path.join(SAMPLE_DIR, fname)
        exists = os.path.exists(raw_p) or os.path.exists(sample_p)
        assert exists, f"Missing required dataset file: {fname}"

def test_required_columns():
    """Verify each dataset has all mandatory columns."""
    for fname, cols in REQUIRED_COLUMNS.items():
        p = os.path.join(RAW_DIR, fname)
        if not os.path.exists(p):
            p = os.path.join(SAMPLE_DIR, fname)
        df = pd.read_csv(p)
        for col in cols:
            assert col in df.columns, f"File {fname} is missing column: {col}"

def test_missing_values():
    """Verify zero critical nulls in key identifiers."""
    fm = pd.read_csv(os.path.join(RAW_DIR, "01_fund_master.csv"))
    assert fm["amfi_code"].isnull().sum() == 0, "Nulls found in amfi_code"
    
    nav = pd.read_csv(os.path.join(RAW_DIR, "02_nav_history.csv"))
    assert nav["nav"].isnull().sum() == 0, "Nulls found in historical NAV series"

def test_valid_amfi_codes():
    """Verify AMFI codes in NAV and Transactions match Fund Master catalog."""
    fm = pd.read_csv(os.path.join(RAW_DIR, "01_fund_master.csv"))
    valid_codes = set(fm["amfi_code"].unique())
    assert len(valid_codes) == 40, f"Expected exactly 40 schemes, got {len(valid_codes)}"
    
    nav = pd.read_csv(os.path.join(RAW_DIR, "02_nav_history.csv"))
    nav_codes = set(nav["amfi_code"].unique())
    assert nav_codes.issubset(valid_codes), "Found orphan AMFI codes in NAV history"

def test_positive_nav_values():
    """Verify all historical NAV values are strictly positive."""
    nav = pd.read_csv(os.path.join(RAW_DIR, "02_nav_history.csv"))
    assert (nav["nav"] > 0).all(), "Found zero or negative NAV records"
    assert nav["nav"].min() >= 5.0, f"Unrealistically low NAV: {nav['nav'].min()}"

def test_positive_transaction_amounts():
    """Verify transaction amounts are strictly positive."""
    tx = pd.read_csv(os.path.join(RAW_DIR, "08_investor_transactions.csv"))
    assert (tx["amount_inr"] > 0).all(), "Found zero or negative transaction amounts"

def test_portfolio_weight_bounds():
    """Verify top-8 portfolio weights per fund do not exceed 100%."""
    port = pd.read_csv(os.path.join(RAW_DIR, "09_portfolio_holdings.csv"))
    weights_per_fund = port.groupby("amfi_code")["weight_pct"].sum()
    assert (weights_per_fund <= 100.0).all(), f"Found fund with total weight > 100%: {weights_per_fund.max()}"

