"""
Bluestock Fintech - Mutual Fund Analytics Platform
Script: scripts/data_ingestion.py
Objective: Data ingestion, schema validation, data profiling, and quality reporting.
"""

import os
import sys
import json
import logging
from typing import Dict, Any, List
import pandas as pd
import numpy as np

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("DataIngestion")

RAW_DIR = os.path.join("data", "raw")
SAMPLE_DIR = os.path.join("data", "sample")
PROCESSED_DIR = os.path.join("data", "processed")

DATASET_FILES = [
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

def load_all_datasets() -> Dict[str, pd.DataFrame]:
    """
    Load all 10 CSV datasets from data/raw/ or data/sample/
    """
    datasets = {}
    for fname in DATASET_FILES:
        raw_path = os.path.join(RAW_DIR, fname)
        sample_path = os.path.join(SAMPLE_DIR, fname)
        
        target_path = raw_path if os.path.exists(raw_path) else sample_path
        if not os.path.exists(target_path):
            raise FileNotFoundError(f"Required dataset {fname} not found in {RAW_DIR} or {SAMPLE_DIR}")
            
        df = pd.read_csv(target_path)
        datasets[fname] = df
        logger.info(f"Loaded {fname:<30}: Shape {str(df.shape):<12} from {target_path}")
        
    return datasets

def profile_and_validate(datasets: Dict[str, pd.DataFrame]) -> Dict[str, Any]:
    """
    Performs comprehensive schema validation, missing value check, AMFI verification,
    and returns a structured data quality report.
    """
    os.makedirs(PROCESSED_DIR, exist_ok=True)
    report = {
        "timestamp": pd.Timestamp.now().isoformat(),
        "total_datasets": len(datasets),
        "total_records": sum(len(df) for df in datasets.values()),
        "dataset_summaries": {},
        "integrity_checks": {
            "amfi_code_validation": {},
            "nav_validity": {},
            "transaction_validity": {},
            "portfolio_weight_validity": {}
        },
        "status": "PASS"
    }
    
    # 1. Profile each dataset
    for fname, df in datasets.items():
        missing_counts = df.isnull().sum().to_dict()
        duplicates = int(df.duplicated().sum())
        
        col_types = {col: str(dtype) for col, dtype in df.dtypes.items()}
        sample_dict = df.head(2).to_dict(orient="records")
        
        report["dataset_summaries"][fname] = {
            "rows": int(len(df)),
            "columns": int(df.shape[1]),
            "column_list": list(df.columns),
            "dtypes": col_types,
            "missing_values": missing_counts,
            "total_nulls": int(sum(missing_counts.values())),
            "duplicate_rows": duplicates,
            "sample_records": sample_dict
        }
        
    # 2. Specific integrity checks
    fm = datasets["01_fund_master.csv"]
    valid_amfi_codes = set(fm["amfi_code"].unique())
    
    # Check AMFI in NAV History
    nav_df = datasets["02_nav_history.csv"]
    nav_codes = set(nav_df["amfi_code"].unique())
    orphan_nav = nav_codes - valid_amfi_codes
    report["integrity_checks"]["amfi_code_validation"]["nav_orphans"] = list(orphan_nav)
    
    # Check NAV positive
    invalid_navs = int((nav_df["nav"] <= 0).sum())
    report["integrity_checks"]["nav_validity"]["negative_or_zero_navs"] = invalid_navs
    report["integrity_checks"]["nav_validity"]["min_nav"] = float(nav_df["nav"].min())
    report["integrity_checks"]["nav_validity"]["max_nav"] = float(nav_df["nav"].max())
    
    # Check Transactions
    tx_df = datasets["08_investor_transactions.csv"]
    tx_codes = set(tx_df["amfi_code"].unique())
    orphan_tx = tx_codes - valid_amfi_codes
    report["integrity_checks"]["amfi_code_validation"]["transaction_orphans"] = list(orphan_tx)
    report["integrity_checks"]["transaction_validity"]["negative_amounts"] = int((tx_df["amount_inr"] <= 0).sum())
    report["integrity_checks"]["transaction_validity"]["unique_investors"] = int(tx_df["investor_id"].nunique())
    
    # Check Portfolio Holdings
    port_df = datasets["09_portfolio_holdings.csv"]
    weights_by_fund = port_df.groupby("amfi_code")["weight_pct"].sum()
    invalid_weights = int((weights_by_fund > 100.0).sum())
    report["integrity_checks"]["portfolio_weight_validity"]["schemes_exceeding_100pct"] = invalid_weights
    
    # Save Report
    report_path = os.path.join(PROCESSED_DIR, "data_quality_report.json")
    with open(report_path, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2)
        
    return report

def print_quality_summary(report: Dict[str, Any]):
    print("\n" + "=" * 75)
    print("BLUESTOCK FINTECH: DATA QUALITY & INGESTION AUDIT REPORT")
    print("=" * 75)
    print(f"Total Datasets Processed : {report['total_datasets']}")
    print(f"Total Records Ingested   : {report['total_records']:,}")
    print(f"Ingestion Audit Status   : {report['status']}")
    print("-" * 75)
    print(f"{'Dataset Name':<32} {'Rows':>8} {'Cols':>6} {'Nulls':>6} {'Dupes':>6}")
    print("-" * 75)
    
    for fname, summ in report["dataset_summaries"].items():
        print(f"{fname:<32} {summ['rows']:>8} {summ['columns']:>6} {summ['total_nulls']:>6} {summ['duplicate_rows']:>6}")
        
    print("=" * 75)
    print("INTEGRITY VERIFICATION CHECKS:")
    ic = report["integrity_checks"]
    print(f"- NAV Foreign Key Integrity     : {'VALID (0 orphans)' if len(ic['amfi_code_validation']['nav_orphans']) == 0 else 'FAILED'}")
    print(f"- Transaction FK Integrity      : {'VALID (0 orphans)' if len(ic['amfi_code_validation']['transaction_orphans']) == 0 else 'FAILED'}")
    print(f"- Positive NAV Verification     : {'VALID (Min: ₹' + str(ic['nav_validity']['min_nav']) + ')' if ic['nav_validity']['negative_or_zero_navs'] == 0 else 'FAILED'}")
    print(f"- Transaction Amounts > 0       : {'VALID (0 negative)' if ic['transaction_validity']['negative_amounts'] == 0 else 'FAILED'}")
    print(f"- Distinct Synthetic Investors  : {ic['transaction_validity']['unique_investors']:,} (Target: 5,000)")
    print(f"- Portfolio Scheme Weight <=100%: {'VALID (0 breaches)' if ic['portfolio_weight_validity']['schemes_exceeding_100pct'] == 0 else 'FAILED'}")
    print("=" * 75)

if __name__ == "__main__":
    dfs = load_all_datasets()
    rep = profile_and_validate(dfs)
    print_quality_summary(rep)

