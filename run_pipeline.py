"""
Bluestock Fintech - Mutual Fund Analytics Platform
Master Execution Script: run_pipeline.py
Runs the complete ingestion, data cleaning, ETL pipeline, database population,
and financial risk/return calculations.
"""

import os
import sys
import logging

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("PipelineRunner")

REQUIRED_RAW_FILES = [
    os.path.join("data", "raw", "01_fund_master.csv"),
    os.path.join("data", "raw", "02_nav_history.csv"),
    os.path.join("data", "raw", "08_investor_transactions.csv")
]

def check_and_generate_datasets():
    """
    Ensure all 10 datasets exist. If missing, automatically generate them.
    """
    missing = [f for f in REQUIRED_RAW_FILES if not os.path.exists(f)]
    if missing:
        logger.info("Raw datasets not found. Triggering automated dataset generator...")
        from scripts.generate_sample_data import generate_all_datasets
        generate_all_datasets()
    else:
        logger.info("Raw datasets verified. Proceeding to ETL.")

def main():
    print("=" * 75)
    print("BLUESTOCK FINTECH: MUTUAL FUND ANALYTICS PLATFORM")
    print("Master Orchestrator Pipeline (ETL + Database + Financial Metrics)")
    print("=" * 75)
    
    # Step 1: Ensure datasets exist
    check_and_generate_datasets()
    
    # Step 2: Run Master ETL Pipeline (Loads db/bluestock_mf.db)
    from scripts.etl_pipeline import run_etl
    run_etl()
    
    # Step 3: Run Financial Analytics & Scorecard Calculation
    try:
        from scripts.compute_metrics import run_metrics_computation
        run_metrics_computation()
    except ImportError:
        logger.warning("compute_metrics.py not yet invoked or present. Skipping metric computation.")
        
    print("=" * 75)
    print("PIPELINE EXECUTION COMPLETE: SQLite DB & Analytics are ready.")
    print("To launch the interactive dashboard:")
    print("    python -m streamlit run dashboard/app.py")
    print("=" * 75)

if __name__ == "__main__":
    main()

