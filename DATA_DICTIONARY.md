# DATA DICTIONARY SPECIFICATION
## Bluestock Fintech - Mutual Fund Analytics Platform
**Database Engine:** SQLite 3  
**Database File:** `db/bluestock_mf.db`  
**Architecture:** Star Schema with Dimension Tables and Normalized Fact Tables  

---

### Table 1: `dim_fund` (Fund Master Dimension)
Stores the structural and regulatory metadata for each mutual fund scheme.

| Column Name | Data Type | Key / Constraint | Description | Example / Allowed Values |
|:---|:---|:---|:---|:---|
| `amfi_code` | INTEGER | PRIMARY KEY | Unique Association of Mutual Funds in India (AMFI) scheme code | `119551`, `125497` |
| `fund_house` | TEXT | NOT NULL | Asset Management Company (AMC) name | `SBI Mutual Fund`, `HDFC Mutual Fund` |
| `scheme_name` | TEXT | NOT NULL | Full official name of the scheme and plan | `SBI Bluechip Fund - Direct Plan - Growth` |
| `category` | TEXT | NOT NULL | Broader mutual fund asset category | `Large Cap`, `Mid Cap`, `Small Cap`, `Flexi Cap`, `ELSS`, `Index`, `Liquid`, `Debt`, `Hybrid` |
| `sub_category` | TEXT | NULLABLE | SEBI standard granular classification | `Equity: Large Cap`, `Debt: Liquid` |
| `plan` | TEXT | NOT NULL | Scheme investment route | `Direct`, `Regular` |
| `launch_date` | DATE | NULLABLE | Official fund inception date (YYYY-MM-DD) | `2013-01-01` |
| `benchmark` | TEXT | NOT NULL | Designated benchmark index | `Nifty 50`, `Nifty 100`, `CRISIL Liquid` |
| `expense_ratio_pct` | REAL | NOT NULL | Annual recurring scheme operating expense percentage (TER) | `0.78`, `1.08` |
| `exit_load_pct` | REAL | DEFAULT 1.0 | Redemption penalty percentage if withdrawn within lock-in period | `1.0`, `0.0` |
| `fund_manager` | TEXT | NOT NULL | Primary investment portfolio manager | `Rahul Baijal`, `Sohini Andani` |
| `risk_category` | TEXT | NOT NULL | SEBI Risk-o-meter level | `Low to Moderate`, `Moderate`, `Very High` |
| `sebi_category_code` | TEXT | NULLABLE | Standard SEBI categorization code | `EQ-LC`, `EQ-MC`, `DB-LQ` |

---

### Table 2: `dim_date` (Time Dimension)
Facilitates high-speed analytical time-series slicing across years, quarters, months, and weekdays.

| Column Name | Data Type | Key / Constraint | Description | Example Values |
|:---|:---|:---|:---|:---|
| `date` | DATE | PRIMARY KEY | Calendar Date in ISO 8601 format (YYYY-MM-DD) | `2024-03-31` |
| `year` | INTEGER | NOT NULL | Calendar year | `2022`, `2023`, `2024`, `2025` |
| `quarter` | TEXT | NOT NULL | Calendar quarter identifier | `Q1`, `Q2`, `Q3`, `Q4` |
| `month` | INTEGER | NOT NULL | Month number (1 - 12) | `1` to `12` |
| `month_name` | TEXT | NOT NULL | Full month name | `January`, `December` |
| `day` | INTEGER | NOT NULL | Day of month (1 - 31) | `1` to `31` |
| `day_of_week` | TEXT | NOT NULL | Day of week | `Monday`, `Friday` |
| `is_weekend` | INTEGER | DEFAULT 0 | Flag indicating Saturday or Sunday (1=True, 0=False) | `0`, `1` |
| `is_month_end` | INTEGER | DEFAULT 0 | Flag indicating last calendar day of month | `0`, `1` |

---

### Table 3: `fact_nav` (Historical Daily NAV Series)
Historical Net Asset Values recorded across verified trading days.

| Column Name | Data Type | Key / Constraint | Description | Example Values |
|:---|:---|:---|:---|:---|
| `id` | INTEGER | PRIMARY KEY AUTOINCREMENT | Unique record surrogate key | `1`, `2` |
| `amfi_code` | INTEGER | FK -> `dim_fund(amfi_code)` | Reference to mutual fund scheme | `119551` |
| `date` | DATE | FK -> `dim_date(date)` | Market trading date (YYYY-MM-DD) | `2024-01-15` |
| `nav` | REAL | NOT NULL, CHECK(nav > 0) | Net Asset Value in Indian Rupees (INR) | `107.3493` |
| `daily_return_pct` | REAL | NULLABLE | Daily percentage change: $(NAV_t / NAV_{t-1} - 1) \times 100$ | `0.4521`, `-0.3120` |

---

### Table 4: `fact_transactions` (Investor Transactions Fact)
Granular synthetic investor order book modeling Indian retail demographic patterns.

| Column Name | Data Type | Key / Constraint | Description | Example Values |
|:---|:---|:---|:---|:---|
| `transaction_id` | INTEGER | PRIMARY KEY AUTOINCREMENT | Unique transaction identifier | `1001` |
| `investor_id` | INTEGER | NOT NULL | Synthetic investor identifier (1001 to 6000) | `1425` |
| `transaction_date` | DATE | NOT NULL | Order execution date | `2024-05-10` |
| `amfi_code` | INTEGER | FK -> `dim_fund(amfi_code)` | Mutual fund scheme purchased | `125497` |
| `transaction_type` | TEXT | CHECK IN ('SIP', 'Lumpsum', 'Redemption') | Transaction classification | `SIP`, `Lumpsum`, `Redemption` |
| `amount_inr` | REAL | NOT NULL, CHECK(amount_inr > 0) | Transaction value in INR | `5000.0`, `100000.0` |
| `state` | TEXT | NOT NULL | Indian State / Union Territory | `Maharashtra`, `Karnataka` |
| `city` | TEXT | NOT NULL | City of investor residence | `Mumbai`, `Bengaluru` |
| `city_tier` | TEXT | CHECK IN ('T30', 'B30') | AMFI geographic tier classification | `T30` (Top 30), `B30` (Beyond 30) |
| `age_group` | TEXT | NOT NULL | Demographic age cohort | `18-25`, `26-35`, `36-45`, `46-55`, `56+` |
| `gender` | TEXT | NOT NULL | Investor gender | `Male`, `Female` |
| `annual_income_lakh` | REAL | NOT NULL | Self-reported annual income in Lakhs INR | `12.5`, `28.0` |
| `payment_mode` | TEXT | NOT NULL | Payment rails used | `UPI`, `Net Banking`, `Mandate`, `Cheque` |
| `kyc_status` | TEXT | NOT NULL | SEBI KYC compliance status | `Verified`, `Pending` |

---

### Table 5: `fact_performance` (Calculated Risk & Return Metrics)
Quantitatively computed financial indicators derived from the NAV history and benchmark returns.

| Column Name | Data Type | Key / Constraint | Description | Example Values |
|:---|:---|:---|:---|:---|
| `amfi_code` | INTEGER | PRIMARY KEY, FK -> `dim_fund` | Mutual fund scheme code | `119551` |
| `return_1yr_pct` | REAL | NULLABLE | 1-Year Point-to-Point return percentage | `18.45` |
| `return_3yr_pct` | REAL | NULLABLE | 3-Year Compound Annual Growth Rate (CAGR %) | `16.20` |
| `return_5yr_pct` | REAL | NULLABLE | 5-Year Compound Annual Growth Rate (CAGR %) | `15.80` |
| `benchmark_3yr_pct` | REAL | NULLABLE | 3-Year CAGR of designated benchmark index (%) | `13.50` |
| `alpha` | REAL | NULLABLE | Jensen's Alpha annualized over benchmark (%) | `2.85` |
| `beta` | REAL | NULLABLE | Market sensitivity relative to benchmark | `0.94` |
| `sharpe_ratio` | REAL | NULLABLE | Risk-adjusted return ratio ($R_f = 6.5\%$) | `1.15` |
| `sortino_ratio` | REAL | NULLABLE | Downside risk-adjusted return ratio | `1.62` |
| `std_dev_ann_pct` | REAL | NULLABLE | Annualized standard deviation of daily returns (%) | `14.25` |
| `max_drawdown_pct` | REAL | NULLABLE | Peak-to-trough maximum observed decline (%) | `-16.80` |
| `tracking_error_pct` | REAL | NULLABLE | Annualized volatility of excess returns over benchmark (%) | `2.15` |
| `information_ratio` | REAL | NULLABLE | Active return divided by tracking error | `1.25` |
| `var_95_pct` | REAL | NULLABLE | 95% Historical Value-at-Risk daily threshold (%) | `-1.85` |
| `cvar_95_pct` | REAL | NULLABLE | 95% Conditional Value-at-Risk (Expected Shortfall %) | `-2.75` |
| `composite_score` | REAL | NULLABLE | 0-100 Multi-factor ranking score | `84.50` |
| `fund_rank` | INTEGER | NULLABLE | Category or universe composite ranking | `1` to `40` |
| `morningstar_rating` | INTEGER | NULLABLE | Illustrative rating (1 to 5 stars) | `4`, `5` |
| `calculated_date` | DATE | NULLABLE | Computation timestamp date | `2026-05-31` |

---

### Table 6: `fact_portfolio` (Fund Holdings and Sector Allocations)
Constituent stock holdings and portfolio sector concentrations.

| Column Name | Data Type | Key / Constraint | Description | Example Values |
|:---|:---|:---|:---|:---|
| `id` | INTEGER | PRIMARY KEY AUTOINCREMENT | Unique holding row ID | `1` |
| `amfi_code` | INTEGER | FK -> `dim_fund` | Mutual fund scheme code | `125497` |
| `stock_symbol` | TEXT | NOT NULL | NSE ticker symbol | `HDFCBANK`, `RELIANCE` |
| `company_name` | TEXT | NOT NULL | Registered corporate name | `HDFC Bank Ltd.` |
| `sector` | TEXT | NOT NULL | Economic sector classification | `Banking`, `IT`, `Energy` |
| `weight_pct` | REAL | NOT NULL | Portfolio asset allocation percentage ($\le 100\%$) | `8.75`, `6.20` |
| `date` | DATE | NOT NULL | Portfolio disclosure date (YYYY-MM-DD) | `2025-12-31` |

---

### Table 7: `fact_aum` (Fund House Assets Under Management)
Quarterly Average AUM (QAAUM) progression across premier fund houses.

| Column Name | Data Type | Key / Constraint | Description | Example Values |
|:---|:---|:---|:---|:---|
| `id` | INTEGER | PRIMARY KEY AUTOINCREMENT | Row identifier | `1` |
| `fund_house` | TEXT | NOT NULL | Name of AMC | `SBI Mutual Fund` |
| `quarter` | TEXT | NOT NULL | Calendar quarter | `Q1`, `Q2`, `Q3`, `Q4` |
| `year` | INTEGER | NOT NULL | Calendar year | `2022`, `2025` |
| `aum_crore` | REAL | NOT NULL | Total quarterly average AUM in Crores INR | `785000.50` |
| `num_schemes` | INTEGER | NOT NULL | Total number of operational schemes | `148` |

---

### Table 8: `fact_sip_industry` (Industry Monthly SIP Inflows)
National macro-level SIP volumes, active folios, and systematic asset base.

| Column Name | Data Type | Key / Constraint | Description | Example Values |
|:---|:---|:---|:---|:---|
| `month` | TEXT | PRIMARY KEY | Month identifier (YYYY-MM) | `2025-12` |
| `sip_inflow_crore` | REAL | NOT NULL | Gross monthly SIP collection in Crores INR | `31002.0` |
| `active_sip_accounts_crore`| REAL | NOT NULL | Total registered operational SIP accounts in Crores | `9.35` |
| `new_sip_accounts_lakh` | REAL | NOT NULL | Fresh SIP registrations added in Lakhs | `32.50` |
| `sip_aum_lakh_crore` | REAL | NOT NULL | Cumulative asset value of SIP holdings in Lakh Crores | `14.80` |
| `yoy_growth_pct` | REAL | NULLABLE | Year-over-Year percentage expansion in monthly inflow | `24.8` |

---

### Table 9: `fact_category_inflows` (Category Inflow & Outflow Dynamics)
Gross subscriptions, redemptions, and net flows segmented by fund category.

| Column Name | Data Type | Key / Constraint | Description | Example Values |
|:---|:---|:---|:---|:---|
| `id` | INTEGER | PRIMARY KEY AUTOINCREMENT | Unique row ID | `1` |
| `month` | TEXT | NOT NULL | Observation month (YYYY-MM) | `2025-08` |
| `category` | TEXT | NOT NULL | Fund category | `Large Cap`, `Flexi Cap` |
| `gross_inflow_crore` | REAL | NOT NULL | New gross purchases in Crores | `7450.0` |
| `redemption_crore` | REAL | NOT NULL | Total redemptions in Crores | `3820.0` |
| `net_inflow_crore` | REAL | NOT NULL | Net asset inflow: Gross - Redemptions | `3630.0` |

---

### Table 10: `fact_benchmark_indices` (Daily Benchmark Index Levels)
Daily closing indices for relative performance attribution and beta calculation.

| Column Name | Data Type | Key / Constraint | Description | Example Values |
|:---|:---|:---|:---|:---|
| `id` | INTEGER | PRIMARY KEY AUTOINCREMENT | Unique row ID | `1` |
| `index_name` | TEXT | NOT NULL | Official index title | `Nifty 50`, `Nifty Midcap 150` |
| `date` | DATE | NOT NULL | Trading date (YYYY-MM-DD) | `2024-02-15` |
| `close_value` | REAL | NOT NULL | Index closing level | `21845.20` |
| `daily_return_pct` | REAL | NULLABLE | Daily percentage return | `0.62` |

---

### Table 11: `fact_industry_folios` (Folio Milestones)
Total investor folios segmented into equity, debt, and hybrid assets.

| Column Name | Data Type | Key / Constraint | Description | Example Values |
|:---|:---|:---|:---|:---|
| `month` | TEXT | PRIMARY KEY | Milestone month (YYYY-MM) | `2025-06` |
| `equity_folios_crore` | REAL | NOT NULL | Equity folios in Crores | `15.80` |
| `debt_folios_crore` | REAL | NOT NULL | Debt folios in Crores | `1.65` |
| `hybrid_folios_crore` | REAL | NOT NULL | Hybrid folios in Crores | `2.95` |
| `total_folios_crore` | REAL | NOT NULL | Total mutual fund investor folios | `20.40` |

