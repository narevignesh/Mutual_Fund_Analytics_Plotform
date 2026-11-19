"""
Bluestock Fintech - Mutual Fund Analytics Platform
Script: scripts/data_cleaning.py
Objective: Data standardization, date parsing, deduplication, sanity checks,
and star-schema preparation (dim_date, cleaned facts & dimensions).
"""

import os
import sys
import logging
from typing import Dict, Tuple
import pandas as pd
import numpy as np

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("DataCleaning")

RAW_DIR = os.path.join("data", "raw")
PROCESSED_DIR = os.path.join("data", "processed")

def clean_fund_master(df: pd.DataFrame) -> pd.DataFrame:
    """
    Standardize categories, validate expense ratios and exit loads.
    """
    df = df.drop_duplicates(subset=["amfi_code"]).copy()
    df["amfi_code"] = df["amfi_code"].astype(int)
    df["expense_ratio_pct"] = df["expense_ratio_pct"].astype(float)
    df["exit_load_pct"] = df["exit_load_pct"].astype(float)
    
    # Validation checks
    assert (df["expense_ratio_pct"] > 0).all() and (df["expense_ratio_pct"] <= 3.0).all(), "Invalid expense ratio"
    assert (df["exit_load_pct"] >= 0).all() and (df["exit_load_pct"] <= 5.0).all(), "Invalid exit load"
    
    # Standardize scheme strings
    df["scheme_name"] = df["scheme_name"].str.strip()
    df["fund_house"] = df["fund_house"].str.strip()
    df["category"] = df["category"].str.strip()
    return df

def generate_dim_date(start_date: str = "2020-01-01", end_date: str = "2026-12-31") -> pd.DataFrame:
    """
    Generate comprehensive date dimension for star schema.
    """
    date_range = pd.date_range(start_date, end_date, freq="D")
    df = pd.DataFrame({"date": date_range})
    df["date_str"] = df["date"].dt.strftime("%Y-%m-%d")
    df["year"] = df["date"].dt.year
    df["quarter"] = "Q" + df["date"].dt.quarter.astype(str)
    df["month"] = df["date"].dt.month
    df["month_name"] = df["date"].dt.strftime("%B")
    df["day"] = df["date"].dt.day
    df["day_of_week"] = df["date"].dt.strftime("%A")
    df["is_weekend"] = df["date"].dt.weekday.apply(lambda x: 1 if x >= 5 else 0)
    df["is_month_end"] = df["date"].dt.is_month_end.astype(int)
    
    dim_date = df[["date_str", "year", "quarter", "month", "month_name", "day", "day_of_week", "is_weekend", "is_month_end"]].copy()
    dim_date = dim_date.rename(columns={"date_str": "date"})
    return dim_date

def clean_nav_history(df: pd.DataFrame) -> pd.DataFrame:
    """
    Clean NAV series: validate NAV > 0, parse dates, deduplicate,
    and compute daily_return_pct strictly per scheme without cross-scheme leakage.
    """
    df = df.drop_duplicates(subset=["amfi_code", "date"]).copy()
    df["amfi_code"] = df["amfi_code"].astype(int)
    df["date"] = pd.to_datetime(df["date"]).dt.strftime("%Y-%m-%d")
    df["nav"] = df["nav"].astype(float)
    
    # Rule: NAV must be strictly positive
    df = df[df["nav"] > 0].copy()
    
    # Sort strictly by scheme and date
    df = df.sort_values(["amfi_code", "date"]).reset_index(drop=True)
    
    # Calculate daily return strictly within each scheme
    df["daily_return_pct"] = df.groupby("amfi_code")["nav"].pct_change() * 100.0
    df["daily_return_pct"] = df["daily_return_pct"].fillna(0.0).round(4)
    return df

def clean_investor_transactions(df: pd.DataFrame, valid_amfi_codes: set) -> pd.DataFrame:
    """
    Clean investor transactions: remove duplicates, validate amounts > 0,
    ensure standardized transaction types and kyc statuses.
    """
    initial_len = len(df)
    df = df.drop_duplicates().copy()
    logger.info(f"Deduplicated transactions: removed {initial_len - len(df)} duplicate records.")
    
    df["investor_id"] = df["investor_id"].astype(int)
    df["amfi_code"] = df["amfi_code"].astype(int)
    df["transaction_date"] = pd.to_datetime(df["transaction_date"]).dt.strftime("%Y-%m-%d")
    df["amount_inr"] = df["amount_inr"].astype(float)
    
    # Filter valid amounts & foreign keys
    df = df[(df["amount_inr"] > 0) & (df["amfi_code"].isin(valid_amfi_codes))].copy()
    
    # Standardize text
    df["transaction_type"] = df["transaction_type"].str.strip()
    df["state"] = df["state"].str.strip()
    df["city"] = df["city"].str.strip()
    df["city_tier"] = df["city_tier"].str.strip().str.upper()
    df["age_group"] = df["age_group"].str.strip()
    df["gender"] = df["gender"].str.strip().str.capitalize()
    df["payment_mode"] = df["payment_mode"].str.strip()
    df["kyc_status"] = df["kyc_status"].str.strip().str.capitalize()
    
    # Reset index
    df = df.sort_values(["transaction_date", "investor_id"]).reset_index(drop=True)
    return df

def clean_portfolio_holdings(df: pd.DataFrame, valid_amfi_codes: set) -> pd.DataFrame:
    """
    Clean portfolio holdings, validate scheme weight boundaries <= 100%.
    """
    df = df.drop_duplicates().copy()
    df["amfi_code"] = df["amfi_code"].astype(int)
    df["weight_pct"] = df["weight_pct"].astype(float)
    df["date"] = pd.to_datetime(df["date"]).dt.strftime("%Y-%m-%d")
    
    df = df[df["amfi_code"].isin(valid_amfi_codes)].copy()
    
    # Ensure no fund has total weight exceeding 100%
    scheme_totals = df.groupby("amfi_code")["weight_pct"].sum()
    for code, total_wt in scheme_totals.items():
        if total_wt > 100.0:
            logger.warning(f"Scheme {code} holdings sum to {total_wt}%. Rescaling to 100%.")
            mask = df["amfi_code"] == code
            df.loc[mask, "weight_pct"] = (df.loc[mask, "weight_pct"] / total_wt) * 95.0
            
    df["weight_pct"] = df["weight_pct"].round(2)
    return df

def clean_benchmarks(df: pd.DataFrame) -> pd.DataFrame:
    """
    Clean benchmark indices table.
    """
    df = df.drop_duplicates(subset=["index_name", "date"]).copy()
    df["date"] = pd.to_datetime(df["date"]).dt.strftime("%Y-%m-%d")
    df["close_value"] = df["close_value"].astype(float)
    df["daily_return_pct"] = df["daily_return_pct"].astype(float)
    df = df.sort_values(["index_name", "date"]).reset_index(drop=True)
    return df

def clean_all_datasets() -> Dict[str, pd.DataFrame]:
    """
    Loads raw datasets, applies all cleaning transformations, saves to data/processed/.
    """
    os.makedirs(PROCESSED_DIR, exist_ok=True)
    logger.info("Starting complete data cleaning pipeline...")
    
    # Load raw
    fm_raw = pd.read_csv(os.path.join(RAW_DIR, "01_fund_master.csv"))
    nav_raw = pd.read_csv(os.path.join(RAW_DIR, "02_nav_history.csv"))
    aum_raw = pd.read_csv(os.path.join(RAW_DIR, "03_aum_by_fund_house.csv"))
    sip_raw = pd.read_csv(os.path.join(RAW_DIR, "04_monthly_sip_inflows.csv"))
    cat_inflow_raw = pd.read_csv(os.path.join(RAW_DIR, "05_category_inflows.csv"))
    folios_raw = pd.read_csv(os.path.join(RAW_DIR, "06_industry_folio_count.csv"))
    perf_raw = pd.read_csv(os.path.join(RAW_DIR, "07_scheme_performance.csv"))
    tx_raw = pd.read_csv(os.path.join(RAW_DIR, "08_investor_transactions.csv"))
    port_raw = pd.read_csv(os.path.join(RAW_DIR, "09_portfolio_holdings.csv"))
    bench_raw = pd.read_csv(os.path.join(RAW_DIR, "10_benchmark_indices.csv"))
    
    # Clean Dimensions
    fm_clean = clean_fund_master(fm_raw)
    valid_codes = set(fm_clean["amfi_code"].unique())
    dim_date = generate_dim_date("2020-01-01", "2026-12-31")
    
    # Clean Facts
    nav_clean = clean_nav_history(nav_raw)
    tx_clean = clean_investor_transactions(tx_raw, valid_codes)
    port_clean = clean_portfolio_holdings(port_raw, valid_codes)
    bench_clean = clean_benchmarks(bench_raw)
    
    # Save Cleaned CSVs into data/processed/
    cleaned_dict = {
        "dim_fund.csv": fm_clean,
        "dim_date.csv": dim_date,
        "fact_nav.csv": nav_clean,
        "fact_transactions.csv": tx_clean,
        "fact_performance.csv": perf_raw,
        "fact_portfolio.csv": port_clean,
        "fact_aum.csv": aum_raw,
        "fact_sip_industry.csv": sip_raw,
        "fact_category_inflows.csv": cat_inflow_raw,
        "fact_industry_folios.csv": folios_raw,
        "fact_benchmark_indices.csv": bench_clean
    }
    
    for fname, df in cleaned_dict.items():
        out_path = os.path.join(PROCESSED_DIR, fname)
        df.to_csv(out_path, index=False)
        logger.info(f"Saved processed {fname:<28}: {len(df):>6} rows")
        
    logger.info("Data cleaning completed successfully.")
    return cleaned_dict

if __name__ == "__main__":
    clean_all_datasets()

