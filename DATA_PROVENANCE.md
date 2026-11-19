# DATA PROVENANCE AND METHODOLOGY SPECIFICATION
## Bluestock Fintech - Mutual Fund Analytics Platform
**Document Version:** 1.0  
**Author:** Data Analyst Intern, Bluestock Fintech Pvt. Ltd.  
**Domain:** Indian Mutual Fund Ecosystem & WealthTech  
**Date of Compilation:** November 2026  

---

### 1. Executive Summary & Provenance Matrix

This document details the exact origin, collection methodology, verification status, and mathematical synthesis rules for the 10 core datasets powering the Bluestock Fintech Mutual Fund Analytics Platform. 

To maintain academic and regulatory integrity (SEBI / AMFI guidelines):
1. **Real Data**: Verified public scheme metadata and real historical NAVs fetched directly via AMFI-recognized endpoints (`mfapi.in`).
2. **AMFI Benchmark & Industry Statistics**: Real benchmark reference levels and verified AMFI monthly SIP records (e.g., December 2025 milestones: ₹31,002 crore SIP inflow, 9.35 crore active accounts).
3. **Simulated / Synthetic Datasets**: Investor transactions, demographic attributes, and portfolio holding snapshots are generated using deterministic probabilistic distributions (seed: `42`) to model realistic Indian investor behavior without exposing any Personal Identifiable Information (PII) or proprietary trading logs.
4. **Derived / Analytical Datasets**: Calculated directly using standard quantitative finance formulas (CAGR, Sharpe, Sortino, Jensen's Alpha, Beta, VaR, CVaR, HHI).

| Dataset ID | Filename | Record Count | Provenance Type | Primary Source / Basis | Verification Status |
|:---|:---|:---|:---|:---|:---|
| **01** | `01_fund_master.csv` | 40 | Real / Curated | AMFI India, AMC Offer Documents | Verified AMFI codes & SEBI categories |
| **02** | `02_nav_history.csv` | ~46,000 | Real API + Calibrated Fallback | `https://api.mfapi.in/mf/{code}` | Validated for Top 5 schemes; Calibrated geometric Brownian motion with mean-reversion for missing historical trading windows |
| **03** | `03_aum_by_fund_house.csv` | ~90 | Public Reference + Modeled | AMFI Quarterly Average AUM (QAAUM) 2022–2025 | Calibrated against Top 10 Indian AMCs |
| **04** | `04_monthly_sip_inflows.csv` | 48 | Public AMFI Historical Data | AMFI Monthly Industry Data (Jan 2022 – Dec 2025) | Includes official Dec 2025 milestone figures |
| **05** | `05_category_inflows.csv` | ~144 | Modeled AMFI Trend | AMFI Monthly Net Inflow Reports | Calibrated category-wise redemption & inflow ratios |
| **06** | `06_industry_folio_count.csv` | 21 | AMFI Industry Milestones | AMFI Factsheets (2022–2025) | Verified total & category folios milestones |
| **07** | `07_scheme_performance.csv` | 40 | Quantitative Derived | Calculated from Dataset 02 & 10 NAV series | Deterministic Python / NumPy / SciPy computation |
| **08** | `08_investor_transactions.csv` | ~32,000 | Synthetic (AMFI Calibrated) | Probabilistic synthesis (5,000 synthetic IDs) | Pure synthetic modeling of T30/B30, age, ticket sizes |
| **09** | `09_portfolio_holdings.csv` | ~320 | Curated Representative | NSE/BSE Top Holdings & Monthly Factsheets | Realistic top-8 equity holdings per fund (weights <= 100%) |
| **10** | `10_benchmark_indices.csv` | ~8,000 | Public Market Data + Synthesized | NSE Indices / CRISIL Debt Indices | Calibrated daily index levels Jan 2022 – May 2026 |

---

### 2. Dataset Specific Provenance Details

#### Dataset 01: Fund Master (`01_fund_master.csv`)
- **Coverage**: 10 premier Indian Asset Management Companies (SBI, HDFC, ICICI Prudential, Nippon India, Axis, Kotak Mahindra, UTI, Mirae Asset, DSP, Aditya Birla Sun Life).
- **Schema**: Validated SEBI categorisation codes (e.g., `EQ-LC`, `EQ-MC`, `EQ-SC`, `EQ-FC`, `EQ-ELSS`, `DB-LQ`, `DB-CB`, `HY-AE`).
- **AMFI Codes**: Cross-referenced against AMFI's active open-ended scheme directory.

#### Dataset 02: NAV History (`02_nav_history.csv`)
- **API Endpoint**: `https://api.mfapi.in/mf/{amfi_code}`
- **Specific Live Schemes Tracked**:
  - HDFC Top 100 Fund: Code `125497`
  - SBI Bluechip Fund: Code `119551`
  - ICICI Prudential Bluechip Fund: Code `120503`
  - Nippon India Large Cap Fund: Code `118632`
  - Axis Bluechip Fund: Code `119092`
- **Fallback Rule**: In instances of network timeout, strict rate limits, or offline execution, historical NAVs are synthesized using an anchored Geometric Brownian Motion (GBM) with volatility matched to each fund's historical asset class standard deviation (12% to 22% annual for Equity; 4% to 6% for Debt/Liquid). All NAV values are strictly positive (> ₹10.00).

#### Dataset 04: Monthly SIP Inflows (`04_monthly_sip_inflows.csv`)
- **Benchmark Observation**: Exactly includes the milestone data point for December 2025:
  - Monthly SIP Inflow: ₹31,002 crore
  - Active SIP Accounts: 9.35 crore
- **Historical Curve**: Captures the documented surge from ~₹11,500 crore/month in early 2022 to >₹31,000 crore in late 2025, reflecting nationwide retail financialization.

#### Dataset 08: Investor Transactions (`08_investor_transactions.csv`)
- **Synthetic Disclaimer**: This dataset does NOT represent actual investor records, real names, PAN numbers, or live banking account activities.
- **Generation Logic**:
  - 5,000 unique synthetic `investor_id`s mapped to 12 Indian states (Maharashtra, Gujarat, Karnataka, Tamil Nadu, Delhi NCR, West Bengal, Telangana, Uttar Pradesh, Rajasthan, Kerala, Madhya Pradesh, Punjab).
  - T30 (Top 30 cities) vs B30 (Beyond 30 cities) segregation matching AMFI's ~75:25 AUM / 55:45 folio patterns.
  - Realistic correlation: Younger age groups (18-25, 26-35) show higher propensity for UPI and SIPs with ticket sizes between ₹1,000 - ₹5,000; older age brackets (46-55, 56+) show larger Lumpsum investments via Net Banking and Mandates.

---

### 3. Quantitative Derivation & Mathematical Rules

- **CAGR**:
  $$\text{CAGR} = \left(\frac{\text{NAV}_{\text{end}}}{\text{NAV}_{\text{start}}}\right)^{\frac{1}{\text{Years}}} - 1$$
- **Risk-Free Rate**: $R_f = 6.50\%$ annual ($r_{f,\text{daily}} = (1 + 0.065)^{1/252} - 1 \approx 0.0249\%$).
- **Sharpe Ratio**:
  $$\text{Sharpe} = \frac{R_p - R_f}{\sigma_p}$$
- **Sortino Ratio**:
  $$\text{Sortino} = \frac{R_p - R_f}{\sigma_{\text{downside}}}$$
- **Capital Asset Pricing Model (Alpha & Beta)**:
  $$R_{p,t} - R_{f,t} = \alpha + \beta (R_{m,t} - R_{f,t}) + \epsilon_t$$
- **Composite Fund Score (0 to 100)**:
  $$\text{Score} = 0.30 \cdot \text{Rank}_{3\text{Y Ret}} + 0.25 \cdot \text{Rank}_{\text{Sharpe}} + 0.20 \cdot \text{Rank}_{\alpha} + 0.15 \cdot \text{Rank}_{\text{ExpenseInv}} + 0.10 \cdot \text{Rank}_{\text{DrawdownInv}}$$

