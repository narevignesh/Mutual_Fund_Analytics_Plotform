"""
Bluestock Fintech - Mutual Fund Analytics Platform
Script: scripts/build_notebooks.py
Objective: Generate the 5 required end-to-end Jupyter Notebooks in notebooks/
with structured markdown documentation and executable Python cells.
"""

import os
import json

NOTEBOOKS_DIR = "notebooks"
os.makedirs(NOTEBOOKS_DIR, exist_ok=True)

def make_notebook(cells):
    return {
        "cells": cells,
        "metadata": {
            "kernelspec": {
                "display_name": "Python 3",
                "language": "python",
                "name": "python3"
            },
            "language_info": {
                "name": "python",
                "version": "3.11"
            }
        },
        "nbformat": 4,
        "nbformat_minor": 5
    }

def md_cell(source):
    return {
        "cell_type": "markdown",
        "metadata": {},
        "source": [line + "\n" for line in source.split("\n")]
    }

def code_cell(source):
    return {
        "cell_type": "code",
        "execution_count": None,
        "metadata": {},
        "outputs": [],
        "source": [line + "\n" for line in source.split("\n")]
    }

# -----------------------------------------------------------------------------
# Notebook 1: 01_data_ingestion.ipynb
# -----------------------------------------------------------------------------
nb1_cells = [
    md_cell("# BLUESTOCK FINTECH: MUTUAL FUND ANALYTICS PLATFORM\n## Notebook 01: Data Ingestion & API Integration\n**Author:** Data Analyst Intern\n**Dataset Provenance:** AMFI India, mfapi.in & Synthetic Modeling"),
    md_cell("### 1. Project Overview & Ingestion Objectives\nThis notebook demonstrates the extraction of 10 mutual fund datasets, including live AMFI API responses for benchmark schemes, missing value profiling, and data quality validation."),
    code_cell("import os\nimport sys\nimport pandas as pd\nimport numpy as np\n\n# Ensure root directory is accessible\nsys.path.insert(0, os.path.abspath('..'))\nfrom scripts.data_ingestion import load_all_datasets, profile_and_validate, print_quality_summary\nfrom scripts.live_nav_fetch import fetch_all_target_schemes, TARGET_SCHEMES"),
    md_cell("### 2. Live NAV Fetch via AMFI API (`api.mfapi.in`)"),
    code_cell("print('Fetching live NAV data for benchmark schemes:')\nfor code, name in TARGET_SCHEMES.items():\n    print(f'- Scheme Code: {code} ({name})')\n\nlive_dfs = fetch_all_target_schemes(use_cache=True)\nfor code, df in live_dfs.items():\n    print(f'Retrieved {len(df)} daily NAV rows for AMFI Code {code}')"),
    md_cell("### 3. Loading All 10 Raw Datasets"),
    code_cell("datasets = load_all_datasets()\nfor name, df in datasets.items():\n    print(f'{name:<32}: Shape {str(df.shape):<14} Columns: {list(df.columns[:4])}...')"),
    md_cell("### 4. Data Quality & Schema Integrity Profiling"),
    code_cell("quality_report = profile_and_validate(datasets)\nprint_quality_summary(quality_report)"),
    md_cell("### 5. Sample Inspect: Fund Master & Investor Transactions"),
    code_cell("print('--- Fund Master (01_fund_master.csv) ---')\ndisplay(datasets['01_fund_master.csv'].head(3))\n\nprint('\\n--- Investor Transactions Sample ---')\ndisplay(datasets['08_investor_transactions.csv'].head(3))")
]

# -----------------------------------------------------------------------------
# Notebook 2: 02_data_cleaning.ipynb
# -----------------------------------------------------------------------------
nb2_cells = [
    md_cell("# BLUESTOCK FINTECH: MUTUAL FUND ANALYTICS PLATFORM\n## Notebook 02: Data Cleaning, Standardization & SQL Database Loading\n**Database:** SQLite (`db/bluestock_mf.db`)\n**Schema:** Star-Schema Relational Data Warehouse"),
    md_cell("### 1. Cleaning Requirements & Transformation Principles\n- Clean string fields and standardise categories.\n- Deduplicate transaction records.\n- Enforce strictly positive NAV and transaction values.\n- Generate a time dimension `dim_date` covering market trading calendar.\n- Calculate within-scheme daily returns without cross-scheme data leakage."),
    code_cell("import os\nimport sys\nimport sqlite3\nimport pandas as pd\nsys.path.insert(0, os.path.abspath('..'))\nfrom scripts.data_cleaning import clean_all_datasets\nfrom scripts.etl_pipeline import initialize_database, load_tables_to_db, verify_database_counts"),
    md_cell("### 2. Execute Data Cleaning Pipeline"),
    code_cell("cleaned_dict = clean_all_datasets()\nfor name, df in cleaned_dict.items():\n    print(f'Processed {name:<28}: {len(df):>6} clean records')"),
    md_cell("### 3. Initialize SQLite Star Schema (`sql/schema.sql`)"),
    code_cell("initialize_database()\nload_tables_to_db(cleaned_dict)\nverify_database_counts()"),
    md_cell("### 4. Verification SQL Queries"),
    code_cell("conn = sqlite3.connect('../db/bluestock_mf.db')\nq = '''\nSELECT f.category, COUNT(*) as scheme_count, ROUND(AVG(f.expense_ratio_pct), 2) as avg_ter\nFROM dim_fund f\nGROUP BY f.category\nORDER BY avg_ter ASC;\n'''\ndisplay(pd.read_sql_query(q, conn))\nconn.close()")
]

# -----------------------------------------------------------------------------
# Notebook 3: 03_eda_analysis.ipynb
# -----------------------------------------------------------------------------
nb3_cells = [
    md_cell("# BLUESTOCK FINTECH: MUTUAL FUND ANALYTICS PLATFORM\n## Notebook 03: Exploratory Data Analysis (EDA) & Key Findings\n**Visualizations:** 15 High-Resolution Charts\n**Domain Focus:** Performance, AMC Concentration, Demographics, SIP Inflows"),
    md_cell("### 1. Overview of EDA Visualizations\nThis notebook analyzes market dynamics, retail investor transaction patterns, SIP growth, and sector allocations across the 10 datasets."),
    code_cell("import os\nimport sys\nimport sqlite3\nimport pandas as pd\nimport matplotlib.pyplot as plt\nimport seaborn as sns\n\nsys.path.insert(0, os.path.abspath('..'))\nfrom scripts.generate_eda_charts import generate_all_eda\n\n# Run chart generation\ngenerate_all_eda()"),
    md_cell("### 2. Display Generated Charts"),
    code_cell("from IPython.display import Image, display\ncharts = [\n    'eda_01_nav_trends.png',\n    'eda_02_aum_growth.png',\n    'eda_03_sip_inflows.png',\n    'eda_06_sip_by_age.png',\n    'eda_08_t30_b30_analysis.png',\n    'eda_10_correlation_matrix.png'\n]\nfor ch in charts:\n    p = os.path.join('../reports/charts', ch)\n    if os.path.exists(p):\n        print(f'Chart: {ch}')\n        display(Image(p, width=700))"),
    md_cell("### 3. Empirical Analytical Findings (Backed by Actual Data)"),
    code_cell("findings_path = '../reports/charts/eda_findings.txt'\nwith open(findings_path, 'r', encoding='utf-8') as f:\n    print(f.read())")
]

# -----------------------------------------------------------------------------
# Notebook 4: 04_performance_analytics.ipynb
# -----------------------------------------------------------------------------
nb4_cells = [
    md_cell("# BLUESTOCK FINTECH: MUTUAL FUND ANALYTICS PLATFORM\n## Notebook 04: Fund Performance Analytics & Composite Scorecard\n**Formulas:** CAGR, Sharpe ($R_f=6.5\%$), Sortino, Alpha, Beta, Tracking Error, Drawdown"),
    md_cell("### 1. Financial Performance Metric Definitions\n$$\\text{CAGR} = (\\text{Ending NAV} / \\text{Start NAV})^{1/\\text{Years}} - 1$$\n$$\\text{Sharpe} = \\frac{R_p - R_f}{\\sigma_p}, \\quad \\text{Sortino} = \\frac{R_p - R_f}{\\sigma_{\\text{downside}}}$$\n$$\\text{Composite Score} = 0.30 R_{3Y} + 0.25 \\text{Sharpe} + 0.20 \\alpha + 0.15 \\text{TER}_{\\text{inv}} + 0.10 \\text{MDD}_{\\text{inv}}$$"),
    code_cell("import os\nimport sys\nimport sqlite3\nimport pandas as pd\nsys.path.insert(0, os.path.abspath('..'))\nfrom scripts.compute_metrics import run_metrics_computation, load_data_from_db\n\nrun_metrics_computation()"),
    md_cell("### 2. Inspect Fund Scorecard (0-100 Multi-Factor Rankings)"),
    code_cell("conn = sqlite3.connect('../db/bluestock_mf.db')\nq = '''\nSELECT p.fund_rank, f.scheme_name, f.category, p.return_3yr_pct, p.sharpe_ratio, p.alpha, f.expense_ratio_pct, p.max_drawdown_pct, p.composite_score\nFROM fact_performance p\nJOIN dim_fund f ON p.amfi_code = f.amfi_code\nORDER BY p.fund_rank ASC\nLIMIT 10;\n'''\ndf_scorecard = pd.read_sql_query(q, conn)\nconn.close()\ndisplay(df_scorecard)")
]

# -----------------------------------------------------------------------------
# Notebook 5: 05_advanced_analytics.ipynb
# -----------------------------------------------------------------------------
nb5_cells = [
    md_cell("# BLUESTOCK FINTECH: MUTUAL FUND ANALYTICS PLATFORM\n## Notebook 05: Advanced Quantitative Analytics & Recommendation Engine\n**Topics:** VaR/CVaR, Rolling Sharpe, Cohort Analysis, SIP Continuity, Sector HHI, Recommender"),
    md_cell("### 1. Value at Risk (VaR 95%) and Conditional VaR (Expected Shortfall)"),
    code_cell("import os\nimport sys\nimport pandas as pd\nimport sqlite3\nsys.path.insert(0, os.path.abspath('..'))\nfrom scripts.recommender import get_recommendations, display_recommendations_cli\n\nvar_df = pd.read_csv('../data/processed/var_cvar_report.csv')\nprint('Value-at-Risk & Expected Shortfall (Sample):')\ndisplay(var_df.head(5))"),
    md_cell("### 2. Investor Cohort Analysis"),
    code_cell("cohort_df = pd.read_csv('../data/processed/cohort_analysis.csv')\nprint('Investor Vintage Cohort Analysis:')\ndisplay(cohort_df)"),
    md_cell("### 3. SIP Continuity & Churn Risk Analysis"),
    code_cell("sip_cont = pd.read_csv('../data/processed/sip_continuity.csv')\nat_risk_count = sip_cont['at_risk_flag'].sum()\nprint(f'Total Investors with >=6 SIPs: {len(sip_cont):,}')\nprint(f'Investors flagged At-Risk (Gap > 35 Days): {at_risk_count:,} ({at_risk_count/len(sip_cont)*100:.1f}%)')\ndisplay(sip_cont.head(5))"),
    md_cell("### 4. Portfolio Sector Concentration (Herfindahl-Hirschman Index - HHI)"),
    code_cell("hhi_df = pd.read_csv('../data/processed/sector_hhi.csv')\nprint('Sector Allocation Concentration (HHI):')\ndisplay(hhi_df.head(5))"),
    md_cell("### 5. Risk-Adjusted Fund Recommendation Engine Testing"),
    code_cell("print('Testing Recommendation Engine across 3 Risk Profiles:')\nfor profile in ['Low', 'Moderate', 'High']:\n    display_recommendations_cli(profile)")
]

notebooks = {
    "01_data_ingestion.ipynb": make_notebook(nb1_cells),
    "02_data_cleaning.ipynb": make_notebook(nb2_cells),
    "03_eda_analysis.ipynb": make_notebook(nb3_cells),
    "04_performance_analytics.ipynb": make_notebook(nb4_cells),
    "05_advanced_analytics.ipynb": make_notebook(nb5_cells)
}

def write_notebooks():
    for fname, nb in notebooks.items():
        fpath = os.path.join(NOTEBOOKS_DIR, fname)
        with open(fpath, "w", encoding="utf-8") as f:
            json.dump(nb, f, indent=2)
        print(f"Created notebook: {fpath}")

if __name__ == "__main__":
    write_notebooks()

