# INDIAN MUTUAL FUND ANALYTICS PLATFORM
### Data Analyst Capstone Project — Financial Technology Analytics
**Application Name:** Mutual Fund Analytics  
**Subtitle:** Explore mutual fund performance, market movements, investor behaviour and SIP trends through interactive analytics.  
**Domain:** Indian Mutual Fund Ecosystem & Wealth Analytics  
**Runtime Environment:** Windows 10/11, Python 3.10+  
**Database:** Relational Data Warehouse (`db/bluestock_mf.db`) — 90,497 Audited Records  

---

## 1. Project Introduction

The **Indian Mutual Fund Analytics Platform** is a minimal, modern, and professional financial analytics application designed to explore mutual fund performance, fund house market share, retail Systematic Investment Plan (SIP) mobilization, and investor behavior.

Built with a clean commercial Light Fintech aesthetic (inspired by Groww and Zerodha), the application combines relational data engineering, quantitative financial metrics (CAGR, Sharpe, Sortino, Alpha, Beta, Drawdowns), and interactive visualizations.

> **Notice:**  
> This application is built strictly for educational analytics and evaluation. It does not constitute investment or financial advisory services. Mutual fund investments are subject to market risks.

---

## 2. Project Folder Structure

```
mutual_fund_analytics/
│
├── app.py                # Main Streamlit application, navigation (6 views) and UI
├── data.py               # Data loading, cleaning, database queries, filters and dynamic KPIs
├── charts.py             # Reusable Plotly chart functions
├── style.css             # Global application styling (Minimal Light Theme: #F7F8FC, #2563EB)
├── requirements.txt      # Required dependencies
├── README.md             # Project documentation
│
├── data/
│   ├── raw/              # 10 Raw CSV datasets & cached API payloads
│   └── processed/        # Standardized facts & dimensions
│
├── db/
│   └── bluestock_mf.db   # SQLite relational database (90,497 records)
│
├── reports/
│   ├── Final_Report.pdf  # Comprehensive Research Report
│   └── Presentation.pptx # Executive Slide Deck
│
└── tests/                # Automated pytest validation suite (17 tests)
```

---

## 3. Technology Stack

- **Application & Dashboard:** Python 3.11+, Streamlit
- **Data Engineering:** Pandas, NumPy, SciPy, SQLite 3
- **Data Visualization:** Plotly Express & Graph Objects (Custom Light Theme)
- **Styling:** Custom CSS (`style.css`), Google Fonts Inter
- **Quality Assurance:** pytest (17 unit and integration tests)

---

## 4. Key Navigation Sections (6 Pages)

1. **Overview:**
   - 4 Primary KPIs: Total Industry AUM, Monthly SIP Inflow, Total Folios, Tracked Schemes
   - 4 Visualizations: Industry AUM Growth, Monthly SIP Investment Trend, Top 10 Fund Houses by AUM, Category Distribution
   - Key Market Insights generated from actual data in simple English.
2. **Industry Overview:**
   - 4 Compact KPIs: Total AUM, Fund Houses, Total Schemes, Total Folios
   - Visualizations: AUM Progression, Top AMCs by Peak Assets, AMC Market Share Donut, Category AUM, Folio Growth Trend
   - Filters: Year, Fund House, Category
   - AMC Market Share Leaderboard Table with CSV download.
3. **Fund Performance:**
   - 4 KPIs: Best 3Y CAGR, Highest Sharpe Ratio, Lowest Expense Ratio, Best Composite Score
   - Filters: Fund House, Category, Risk Level
   - Fund Selector displaying 12 quantitative metrics (NAV, 1Y, 3Y, 5Y, Sharpe, Sortino, Alpha, Beta, TER, Max DD)
   - Visualizations: Historical NAV Trend, Fund vs Benchmark (Base = 100), Risk vs Return Scatter, Category Performance
   - Fund Comparison Tool (up to 4 funds side-by-side)
   - Sortable Performance Table with CSV export.
4. **Investor Analytics:**
   - 4 KPIs: Total Investors, Total Transactions, Total Value, Average Ticket Size
   - Synthetic data provenance notice
   - Filters: State, Age Group, Gender, Transaction Type
   - 6 Visualizations: Age Distribution, State-wise Volume, SIP vs Lumpsum vs Redemption, Monthly Trends, T30 vs B30, Investment by Age Group.
5. **SIP & Market Trends:**
   - 4 KPIs: Monthly SIP Inflow, Active SIP Accounts, Cumulative SIP AUM, Annual SIP Growth
   - Filters: Calendar Year, Benchmark Indices, Categories
   - 6 Visualizations: Monthly SIP Trend, Active Account Growth, Category Net Inflows, Benchmark Index Performance, Annual SIP Inflows, Inflow Intensity Heatmap.
6. **Dataset Information:**
   - Comprehensive matrix covering all 10 datasets with dynamic record counts
   - Section A: Data Collection Methodology
   - Section B: Data Quality & Integrity Summary
   - Section C: Real vs Synthetic Data Provenance
   - Section D: Data Dictionary with expandable field specifications
   - Section E: Data Export Center (working CSV download buttons)
   - Section F: Data Limitations & Analytical Boundaries.

---

## 5. How to Launch the Application

Run the application locally via PowerShell / Terminal:

```powershell
python -m streamlit run app.py
```

Expected local URL: `http://localhost:8501`

Or double-click:
`run_dashboard.bat`
