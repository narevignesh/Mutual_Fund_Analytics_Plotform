"""
Bluestock Fintech - Mutual Fund Analytics Platform
Test Suite: tests/test_database.py
Objective: Automated validation of SQLite database schema, table populations,
relational foreign keys, and SQL query execution.
"""

import os
import sqlite3
import pytest
import pandas as pd

DB_PATH = os.path.join("db", "bluestock_mf.db")

EXPECTED_TABLES = [
    "dim_fund",
    "dim_date",
    "fact_nav",
    "fact_transactions",
    "fact_performance",
    "fact_portfolio",
    "fact_aum",
    "fact_sip_industry",
    "fact_category_inflows",
    "fact_industry_folios",
    "fact_benchmark_indices"
]

def test_database_file_exists():
    """Verify bluestock_mf.db exists."""
    assert os.path.exists(DB_PATH), f"Database not found at {DB_PATH}"

def test_tables_created():
    """Verify all 11 dimensional and fact tables exist in database."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%';")
    tables = [r[0] for r in cursor.fetchall()]
    conn.close()
    
    for tbl in EXPECTED_TABLES:
        assert tbl in tables, f"Expected table {tbl} not found in database!"

def test_table_row_counts():
    """Verify non-empty record counts across tables."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute("SELECT COUNT(*) FROM dim_fund;")
    assert cursor.fetchone()[0] == 40, "dim_fund should contain 40 schemes"
    
    cursor.execute("SELECT COUNT(*) FROM fact_nav;")
    nav_count = cursor.fetchone()[0]
    assert nav_count > 40000, f"fact_nav count {nav_count} below expected ~44,000+"
    
    cursor.execute("SELECT COUNT(*) FROM fact_transactions;")
    tx_count = cursor.fetchone()[0]
    assert tx_count > 30000, f"fact_transactions count {tx_count} below expected ~30,000+"
    
    cursor.execute("SELECT COUNT(*) FROM fact_performance;")
    assert cursor.fetchone()[0] == 40, "fact_performance should contain 40 rows"
    
    conn.close()

def test_foreign_key_referential_integrity():
    """Verify fact_transactions and fact_nav contain zero orphan AMFI codes."""
    conn = sqlite3.connect(DB_PATH)
    
    q_tx_orphan = """
    SELECT COUNT(*) FROM fact_transactions t
    LEFT JOIN dim_fund f ON t.amfi_code = f.amfi_code
    WHERE f.amfi_code IS NULL;
    """
    cursor = conn.cursor()
    cursor.execute(q_tx_orphan)
    assert cursor.fetchone()[0] == 0, "Found orphan foreign keys in fact_transactions"
    
    q_nav_orphan = """
    SELECT COUNT(*) FROM fact_nav n
    LEFT JOIN dim_fund f ON n.amfi_code = f.amfi_code
    WHERE f.amfi_code IS NULL;
    """
    cursor.execute(q_nav_orphan)
    assert cursor.fetchone()[0] == 0, "Found orphan foreign keys in fact_nav"
    conn.close()

def test_sql_analytical_queries():
    """Test execution of analytical queries from sql/queries.sql."""
    conn = sqlite3.connect(DB_PATH)
    
    # Test Query 1: Top 5 Fund Houses
    q1 = """
    SELECT fund_house, aum_crore
    FROM fact_aum
    WHERE (year, quarter) = (SELECT MAX(year), MAX(quarter) FROM fact_aum)
    ORDER BY aum_crore DESC LIMIT 5;
    """
    df1 = pd.read_sql_query(q1, conn)
    assert len(df1) == 5, "Query 1 failed to return top 5 fund houses"
    
    # Test Query 8: Average SIP by Age Group
    q8 = """
    SELECT age_group, AVG(amount_inr) as avg_sip
    FROM fact_transactions
    WHERE transaction_type = 'SIP'
    GROUP BY age_group;
    """
    df8 = pd.read_sql_query(q8, conn)
    assert len(df8) == 5, "Query 8 failed to segment 5 age groups"
    conn.close()

