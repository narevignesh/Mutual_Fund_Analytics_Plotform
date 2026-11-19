-- ====================================================================
-- BLUESTOCK FINTECH: MUTUAL FUND ANALYTICS PLATFORM
-- Analytical SQL Queries (SQLite Compatible)
-- File: sql/queries.sql
-- ====================================================================

-- 1. Top 5 Funds by AUM (Latest available quarter from fact_aum / fund master)
-- Demonstrates AMC market leadership and asset concentration
SELECT 
    fund_house,
    year,
    quarter,
    aum_crore,
    num_schemes,
    ROUND(aum_crore / 1000.0, 2) AS aum_thousand_crore
FROM fact_aum
WHERE (year, quarter) = (SELECT MAX(year), MAX(quarter) FROM fact_aum)
ORDER BY aum_crore DESC
LIMIT 5;

-- 2. Average NAV per Month for Selected Benchmark Funds
-- Calculates monthly average NAV progression for trend analysis
SELECT 
    f.amfi_code,
    f.scheme_name,
    strftime('%Y-%m', n.date) AS year_month,
    ROUND(AVG(n.nav), 4) AS avg_nav,
    ROUND(MIN(n.nav), 4) AS min_nav,
    ROUND(MAX(n.nav), 4) AS max_nav,
    COUNT(n.nav) AS trading_days
FROM fact_nav n
JOIN dim_fund f ON n.amfi_code = f.amfi_code
GROUP BY f.amfi_code, strftime('%Y-%m', n.date)
ORDER BY f.amfi_code, year_month DESC;

-- 3. SIP Inflow Year-over-Year Growth
-- Evaluates systematic investment inflow acceleration over time
SELECT 
    month,
    sip_inflow_crore,
    active_sip_accounts_crore,
    sip_aum_lakh_crore,
    yoy_growth_pct,
    ROUND(sip_inflow_crore - LAG(sip_inflow_crore, 12) OVER (ORDER BY month), 2) AS absolute_yoy_growth_crore
FROM fact_sip_industry
ORDER BY month DESC;

-- 4. Transactions by State
-- Geographic distribution of investor transactions and capital flow
SELECT 
    state,
    COUNT(transaction_id) AS total_transactions,
    ROUND(SUM(amount_inr) / 10000000.0, 2) AS total_amount_crore,
    ROUND(AVG(amount_inr), 2) AS avg_ticket_size_inr,
    ROUND(100.0 * SUM(CASE WHEN city_tier = 'T30' THEN 1 ELSE 0 END) / COUNT(*), 1) AS t30_percentage,
    ROUND(100.0 * SUM(CASE WHEN city_tier = 'B30' THEN 1 ELSE 0 END) / COUNT(*), 1) AS b30_percentage
FROM fact_transactions
GROUP BY state
ORDER BY total_amount_crore DESC;

-- 5. Funds with Expense Ratio Below 1.0% (Cost Efficiency Screening)
-- Filters cost-effective schemes across equity and passive categories
SELECT 
    amfi_code,
    fund_house,
    scheme_name,
    category,
    plan,
    expense_ratio_pct,
    fund_manager
FROM dim_fund
WHERE expense_ratio_pct < 1.00
ORDER BY expense_ratio_pct ASC;

-- 6. Top-Performing Funds by Category (Based on 3-Year CAGR and Sharpe Ratio)
-- Identifies category leaders with risk-adjusted performance
WITH CategoryRanked AS (
    SELECT 
        f.category,
        f.scheme_name,
        f.fund_house,
        p.return_3yr_pct,
        p.sharpe_ratio,
        p.alpha,
        p.composite_score,
        DENSE_RANK() OVER (PARTITION BY f.category ORDER BY p.composite_score DESC) as rank_in_cat
    FROM fact_performance p
    JOIN dim_fund f ON p.amfi_code = f.amfi_code
)
SELECT 
    category,
    rank_in_cat,
    scheme_name,
    fund_house,
    return_3yr_pct,
    sharpe_ratio,
    alpha,
    composite_score
FROM CategoryRanked
WHERE rank_in_cat <= 3
ORDER BY category, rank_in_cat;

-- 7. Monthly Transaction Volumes and Inflow/Outflow Breakdown
-- Monitors liquidity velocity and transaction type distribution
SELECT 
    strftime('%Y-%m', transaction_date) AS tx_month,
    COUNT(CASE WHEN transaction_type = 'SIP' THEN 1 END) AS sip_count,
    ROUND(SUM(CASE WHEN transaction_type = 'SIP' THEN amount_inr ELSE 0 END) / 10000000.0, 2) AS sip_volume_crore,
    COUNT(CASE WHEN transaction_type = 'Lumpsum' THEN 1 END) AS lumpsum_count,
    ROUND(SUM(CASE WHEN transaction_type = 'Lumpsum' THEN amount_inr ELSE 0 END) / 10000000.0, 2) AS lumpsum_volume_crore,
    COUNT(CASE WHEN transaction_type = 'Redemption' THEN 1 END) AS redemption_count,
    ROUND(SUM(CASE WHEN transaction_type = 'Redemption' THEN amount_inr ELSE 0 END) / 10000000.0, 2) AS redemption_volume_crore,
    ROUND((SUM(CASE WHEN transaction_type IN ('SIP', 'Lumpsum') THEN amount_inr ELSE -amount_inr END)) / 10000000.0, 2) AS net_flow_crore
FROM fact_transactions
GROUP BY strftime('%Y-%m', transaction_date)
ORDER BY tx_month DESC;

-- 8. Average SIP Amount by Age Group and Income Bracket
-- Investor demographic segmentation analysis
SELECT 
    age_group,
    COUNT(DISTINCT investor_id) AS distinct_investors,
    COUNT(transaction_id) AS total_sip_count,
    ROUND(AVG(amount_inr), 2) AS avg_sip_amount,
    ROUND(MIN(amount_inr), 2) AS min_sip,
    ROUND(MAX(amount_inr), 2) AS max_sip,
    ROUND(AVG(annual_income_lakh), 2) AS avg_income_lakh
FROM fact_transactions
WHERE transaction_type = 'SIP'
GROUP BY age_group
ORDER BY age_group ASC;

-- 9. Top Fund Houses by Cumulative Industry AUM Share
-- Evaluates AMC concentration and market share
SELECT 
    fund_house,
    ROUND(AVG(aum_crore), 2) AS avg_quarterly_aum_crore,
    MAX(aum_crore) AS peak_aum_crore,
    ROUND(100.0 * AVG(aum_crore) / (SELECT SUM(aum_crore) FROM fact_aum WHERE year = 2025 AND quarter = 'Q4'), 2) AS approximate_market_share_pct
FROM fact_aum
GROUP BY fund_house
ORDER BY peak_aum_crore DESC;

-- 10. Investor Redemption Analysis: Behavior across City Tiers and Categories
-- Analyzes capital churn and exit patterns
SELECT 
    t.city_tier,
    f.category,
    COUNT(t.transaction_id) AS redemption_count,
    ROUND(SUM(t.amount_inr) / 10000000.0, 2) AS total_redemption_crore,
    ROUND(AVG(t.amount_inr), 2) AS avg_redemption_ticket,
    ROUND(100.0 * COUNT(t.transaction_id) / (
        SELECT COUNT(*) FROM fact_transactions sub 
        WHERE sub.city_tier = t.city_tier AND sub.transaction_type = 'Redemption'
    ), 2) AS pct_of_tier_redemptions
FROM fact_transactions t
JOIN dim_fund f ON t.amfi_code = f.amfi_code
WHERE t.transaction_type = 'Redemption'
GROUP BY t.city_tier, f.category
ORDER BY t.city_tier, total_redemption_crore DESC;

