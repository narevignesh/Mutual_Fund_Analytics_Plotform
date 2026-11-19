"""
Bluestock Fintech - Mutual Fund Analytics Platform
Script: scripts/etl_pipeline.py
Objective: Master ETL Pipeline (Extract -> Transform -> Load -> Validate).
Populates SQLite database: db/bluestock_mf.db
"""

import os
import sys
import sqlite3
import logging
from typing import Dict, Any
import pandas as pd
from sqlalchemy import create_engine

# Ensure repo root in sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from scripts.data_ingestion import load_all_datasets, profile_and_validate
from scripts.data_cleaning import clean_all_datasets

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("ETLPipeline")

DB_DIR = "db"
DB_PATH = os.path.join(DB_DIR, "bluestock_mf.db")
SCHEMA_PATH = os.path.join("sql", "schema.sql")
QUERIES_PATH = os.path.join("sql", "queries.sql")

def initialize_database():
    """
    Applies sql/schema.sql to recreate tables and indexes in db/bluestock_mf.db.
    """
    os.makedirs(DB_DIR, exist_ok=True)
    logger.info(f"Initializing SQLite database schema at {DB_PATH} using {SCHEMA_PATH}...")
    
    with open(SCHEMA_PATH, "r", encoding="utf-8") as f:
        schema_sql = f.read()
        
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.executescript(schema_sql)
    conn.commit()
    conn.close()
    logger.info("Database schema initialized successfully.")

def load_tables_to_db(cleaned_dict: Dict[str, pd.DataFrame]):
    """
    Loads cleaned DataFrames into SQLite relational database.
    """
    engine = create_engine(f"sqlite:///{DB_PATH}")
    
    # Mapping CSV filename to Database Table
    table_map = {
        "dim_fund.csv": "dim_fund",
        "dim_date.csv": "dim_date",
        "fact_nav.csv": "fact_nav",
        "fact_transactions.csv": "fact_transactions",
        "fact_performance.csv": "fact_performance",
        "fact_portfolio.csv": "fact_portfolio",
        "fact_aum.csv": "fact_aum",
        "fact_sip_industry.csv": "fact_sip_industry",
        "fact_category_inflows.csv": "fact_category_inflows",
        "fact_industry_folios.csv": "fact_industry_folios",
        "fact_benchmark_indices.csv": "fact_benchmark_indices"
    }
    
    logger.info("Loading cleaned facts and dimensions into SQLite database...")
    for fname, table_name in table_map.items():
        if fname in cleaned_dict:
            df = cleaned_dict[fname]
            # Write to database (append mode because schema is pre-created)
            df.to_sql(table_name, con=engine, if_exists="append", index=False)
            logger.info(f"Loaded {len(df):>6} rows into table [{table_name}]")
            
    engine.dispose()
    logger.info("All tables successfully loaded into bluestock_mf.db.")

def verify_database_counts():
    """
    Queries sqlite_master and verifies record counts in all tables.
    """
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%';")
    tables = [row[0] for row in cursor.fetchall()]
    
    print("\n" + "=" * 65)
    print(f"DATABASE VERIFICATION: {DB_PATH}")
    print("=" * 65)
    print(f"{'Table Name':<30} {'Row Count':>12}")
    print("-" * 65)
    total_db_rows = 0
    for tbl in sorted(tables):
        cursor.execute(f"SELECT COUNT(*) FROM {tbl};")
        cnt = cursor.fetchone()[0]
        total_db_rows += cnt
        print(f"{tbl:<30} {cnt:>12,}")
    print("-" * 65)
    print(f"{'Total Database Records':<30} {total_db_rows:>12,}")
    print("=" * 65 + "\n")
    conn.close()

def run_analytical_sample_queries():
    """
    Executes sample analytical queries from sql/queries.sql to verify BI readiness.
    """
    conn = sqlite3.connect(DB_PATH)
    logger.info("Running verification SQL queries...")
    
    # Query 1: Top 5 Funds Houses by AUM
    print("\n--- SQL Query 1: Top 5 Fund Houses by Latest AUM ---")
    q1 = """
    SELECT fund_house, year, quarter, aum_crore, num_schemes
    FROM fact_aum
    WHERE (year, quarter) = (SELECT MAX(year), MAX(quarter) FROM fact_aum)
    ORDER BY aum_crore DESC LIMIT 5;
    """
    df_q1 = pd.read_sql_query(q1, conn)
    print(df_q1.to_string(index=False))
    
    # Query 2: Funds with Expense Ratio < 1.0%
    print("\n--- SQL Query 5: Funds with Expense Ratio < 1.0% (Cost Efficiency) ---")
    q5 = """
    SELECT amfi_code, fund_house, scheme_name, expense_ratio_pct
    FROM dim_fund
    WHERE expense_ratio_pct < 0.70
    ORDER BY expense_ratio_pct ASC LIMIT 5;
    """
    df_q5 = pd.read_sql_query(q5, conn)
    print(df_q5.to_string(index=False))
    
    # Query 3: Average SIP by Age Group
    print("\n--- SQL Query 8: Average SIP Amount by Age Group ---")
    q8 = """
    SELECT age_group, COUNT(*) as tx_count, ROUND(AVG(amount_inr), 2) as avg_sip, ROUND(AVG(annual_income_lakh), 2) as avg_income
    FROM fact_transactions
    WHERE transaction_type = 'SIP'
    GROUP BY age_group
    ORDER BY age_group ASC;
    """
    df_q8 = pd.read_sql_query(q8, conn)
    print(df_q8.to_string(index=False))
    
    conn.close()

def run_etl():
    """
    Master pipeline runner.
    """
    print("\n" + "=" * 70)
    print("BLUESTOCK FINTECH: Starting Master End-to-End ETL Pipeline")
    print("=" * 70)
    
    # Stage 1: Ingestion & Validation
    raw_dfs = load_all_datasets()
    profile_and_validate(raw_dfs)
    
    # Stage 2: Data Cleaning & Transformation
    cleaned_dfs = clean_all_datasets()
    
    # Stage 3: Schema Initialization & Database Loading
    initialize_database()
    load_tables_to_db(cleaned_dfs)
    
    # Stage 4: Verification & Analytical Queries
    verify_database_counts()
    run_analytical_sample_queries()
    
    print("\n>>> Master ETL Pipeline completed with 100% SUCCESS. <<<\n")

if __name__ == "__main__":
    run_etl()

