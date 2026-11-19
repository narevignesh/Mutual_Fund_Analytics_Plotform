-- ====================================================================
-- BLUESTOCK FINTECH: MUTUAL FUND ANALYTICS PLATFORM
-- Relational Star-Schema Database Definition (SQLite)
-- Database: db/bluestock_mf.db
-- ====================================================================

-- 1. DIMENSION: FUND MASTER
DROP TABLE IF EXISTS dim_fund;
CREATE TABLE dim_fund (
    amfi_code INTEGER PRIMARY KEY,
    fund_house TEXT NOT NULL,
    scheme_name TEXT NOT NULL,
    category TEXT NOT NULL,
    sub_category TEXT,
    plan TEXT DEFAULT 'Growth',
    launch_date DATE,
    benchmark TEXT NOT NULL,
    expense_ratio_pct REAL NOT NULL,
    exit_load_pct REAL DEFAULT 1.0,
    fund_manager TEXT NOT NULL,
    risk_category TEXT NOT NULL,
    sebi_category_code TEXT
);

CREATE INDEX IF NOT EXISTS idx_fund_house ON dim_fund(fund_house);
CREATE INDEX IF NOT EXISTS idx_fund_category ON dim_fund(category);
CREATE INDEX IF NOT EXISTS idx_fund_risk ON dim_fund(risk_category);

-- 2. DIMENSION: DATE
DROP TABLE IF EXISTS dim_date;
CREATE TABLE dim_date (
    date DATE PRIMARY KEY,
    year INTEGER NOT NULL,
    quarter TEXT NOT NULL,
    month INTEGER NOT NULL,
    month_name TEXT NOT NULL,
    day INTEGER NOT NULL,
    day_of_week TEXT NOT NULL,
    is_weekend INTEGER NOT NULL DEFAULT 0,
    is_month_end INTEGER NOT NULL DEFAULT 0
);

CREATE INDEX IF NOT EXISTS idx_dim_date_ym ON dim_date(year, month);

-- 3. FACT: NAV HISTORY
DROP TABLE IF EXISTS fact_nav;
CREATE TABLE fact_nav (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    amfi_code INTEGER NOT NULL,
    date DATE NOT NULL,
    nav REAL NOT NULL CHECK(nav > 0),
    daily_return_pct REAL,
    FOREIGN KEY (amfi_code) REFERENCES dim_fund(amfi_code),
    FOREIGN KEY (date) REFERENCES dim_date(date),
    UNIQUE(amfi_code, date)
);

CREATE INDEX IF NOT EXISTS idx_fact_nav_code_date ON fact_nav(amfi_code, date);
CREATE INDEX IF NOT EXISTS idx_fact_nav_date ON fact_nav(date);

-- 4. FACT: INVESTOR TRANSACTIONS (Synthetic AMFI-modeled)
DROP TABLE IF EXISTS fact_transactions;
CREATE TABLE fact_transactions (
    transaction_id INTEGER PRIMARY KEY AUTOINCREMENT,
    investor_id INTEGER NOT NULL,
    transaction_date DATE NOT NULL,
    amfi_code INTEGER NOT NULL,
    transaction_type TEXT NOT NULL CHECK(transaction_type IN ('SIP', 'Lumpsum', 'Redemption')),
    amount_inr REAL NOT NULL CHECK(amount_inr > 0),
    state TEXT NOT NULL,
    city TEXT NOT NULL,
    city_tier TEXT NOT NULL CHECK(city_tier IN ('T30', 'B30')),
    age_group TEXT NOT NULL,
    gender TEXT NOT NULL,
    annual_income_lakh REAL NOT NULL,
    payment_mode TEXT NOT NULL,
    kyc_status TEXT NOT NULL,
    FOREIGN KEY (amfi_code) REFERENCES dim_fund(amfi_code)
);

CREATE INDEX IF NOT EXISTS idx_tx_investor ON fact_transactions(investor_id);
CREATE INDEX IF NOT EXISTS idx_tx_date ON fact_transactions(transaction_date);
CREATE INDEX IF NOT EXISTS idx_tx_type ON fact_transactions(transaction_type);
CREATE INDEX IF NOT EXISTS idx_tx_tier ON fact_transactions(city_tier);
CREATE INDEX IF NOT EXISTS idx_tx_state ON fact_transactions(state);

-- 5. FACT: SCHEME PERFORMANCE AND RISK METRICS
DROP TABLE IF EXISTS fact_performance;
CREATE TABLE fact_performance (
    amfi_code INTEGER PRIMARY KEY,
    return_1yr_pct REAL,
    return_3yr_pct REAL,
    return_5yr_pct REAL,
    benchmark_3yr_pct REAL,
    alpha REAL,
    beta REAL,
    sharpe_ratio REAL,
    sortino_ratio REAL,
    std_dev_ann_pct REAL,
    max_drawdown_pct REAL,
    tracking_error_pct REAL,
    information_ratio REAL,
    var_95_pct REAL,
    cvar_95_pct REAL,
    composite_score REAL,
    fund_rank INTEGER,
    morningstar_rating INTEGER,
    calculated_date DATE,
    FOREIGN KEY (amfi_code) REFERENCES dim_fund(amfi_code)
);

CREATE INDEX IF NOT EXISTS idx_perf_score ON fact_performance(composite_score);
CREATE INDEX IF NOT EXISTS idx_perf_sharpe ON fact_performance(sharpe_ratio);

-- 6. FACT: PORTFOLIO HOLDINGS & SECTORS
DROP TABLE IF EXISTS fact_portfolio;
CREATE TABLE fact_portfolio (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    amfi_code INTEGER NOT NULL,
    stock_symbol TEXT NOT NULL,
    company_name TEXT NOT NULL,
    sector TEXT NOT NULL,
    weight_pct REAL NOT NULL CHECK(weight_pct >= 0 AND weight_pct <= 100),
    date DATE NOT NULL,
    FOREIGN KEY (amfi_code) REFERENCES dim_fund(amfi_code)
);

CREATE INDEX IF NOT EXISTS idx_portfolio_code ON fact_portfolio(amfi_code);
CREATE INDEX IF NOT EXISTS idx_portfolio_sector ON fact_portfolio(sector);

-- 7. FACT: AUM BY FUND HOUSE
DROP TABLE IF EXISTS fact_aum;
CREATE TABLE fact_aum (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    fund_house TEXT NOT NULL,
    quarter TEXT NOT NULL,
    year INTEGER NOT NULL,
    aum_crore REAL NOT NULL,
    num_schemes INTEGER NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_aum_fh_year ON fact_aum(fund_house, year, quarter);

-- 8. FACT: SIP INDUSTRY INFLOWS
DROP TABLE IF EXISTS fact_sip_industry;
CREATE TABLE fact_sip_industry (
    month TEXT PRIMARY KEY,
    sip_inflow_crore REAL NOT NULL,
    active_sip_accounts_crore REAL NOT NULL,
    new_sip_accounts_lakh REAL NOT NULL,
    sip_aum_lakh_crore REAL NOT NULL,
    yoy_growth_pct REAL
);

-- 9. FACT: CATEGORY INFLOWS
DROP TABLE IF EXISTS fact_category_inflows;
CREATE TABLE fact_category_inflows (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    month TEXT NOT NULL,
    category TEXT NOT NULL,
    gross_inflow_crore REAL NOT NULL,
    redemption_crore REAL NOT NULL,
    net_inflow_crore REAL NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_cat_inflows_cat ON fact_category_inflows(category);
CREATE INDEX IF NOT EXISTS idx_cat_inflows_month ON fact_category_inflows(month);

-- 10. FACT: BENCHMARK INDICES
DROP TABLE IF EXISTS fact_benchmark_indices;
CREATE TABLE fact_benchmark_indices (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    index_name TEXT NOT NULL,
    date DATE NOT NULL,
    close_value REAL NOT NULL,
    daily_return_pct REAL
);

CREATE INDEX IF NOT EXISTS idx_benchmark_name_date ON fact_benchmark_indices(index_name, date);

-- 11. FACT: INDUSTRY FOLIO COUNT
DROP TABLE IF EXISTS fact_industry_folios;
CREATE TABLE fact_industry_folios (
    month TEXT PRIMARY KEY,
    equity_folios_crore REAL NOT NULL,
    debt_folios_crore REAL NOT NULL,
    hybrid_folios_crore REAL NOT NULL,
    total_folios_crore REAL NOT NULL
);

