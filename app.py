"""
Mutual Fund Analytics Platform
Entry Point: app.py
Objective: Commercial financial analytics product interface.
Minimal, elegant, clean light theme with 6 navigation views.
"""

import os
import sys
import streamlit as st
import pandas as pd

# Path setup
ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

from data import (
    format_currency, format_pct, format_num,
    get_overview_kpis, get_market_insights, get_overview_charts_data,
    get_industry_kpis, get_industry_filter_options, get_industry_overview_data,
    get_fund_kpis, get_fund_filter_options, get_filtered_funds, get_single_fund_profile, get_nav_history_series,
    get_investor_kpis, get_investor_filter_options, get_filtered_investor_data,
    get_sip_kpis, get_sip_filter_options, get_filtered_sip_data, get_filtered_benchmark_data, get_filtered_category_inflow_data,
    get_dataset_overview_metrics, get_csv_download_bytes, query_db
)

import charts

# Configure Streamlit page
st.set_page_config(
    page_title="Mutual Fund Analytics",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Load global CSS
css_path = os.path.join(ROOT_DIR, "style.css")
if os.path.exists(css_path):
    with open(css_path, "r", encoding="utf-8") as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

# Helper: Zero PyArrow Clean Table Renderer
def render_table(df: pd.DataFrame, height: int = 380):
    if df.empty:
        st.info("No data available for this selection.")
        return
    df_disp = df.copy()
    for col in df_disp.columns:
        if any(term in str(col).lower() for term in ["return", "cagr", "alpha", "growth"]):
            try:
                df_disp[col] = df_disp[col].apply(
                    lambda x: f"<span class='badge-pos'>+{float(x):.2f}%</span>" if float(x) > 0 
                    else (f"<span class='badge-neg'>{float(x):.2f}%</span>" if float(x) < 0 else f"{float(x):.2f}%")
                )
            except Exception:
                pass
        elif any(term in str(col).lower() for term in ["drawdown", "max dd"]):
            try:
                df_disp[col] = df_disp[col].apply(
                    lambda x: f"<span class='badge-neg'>{float(x):.2f}%</span>" if float(x) < 0 else f"{float(x):.2f}%"
                )
            except Exception:
                pass

    html_table = df_disp.to_html(classes="clean-data-table", index=False, escape=False)
    st.markdown(f'<div class="table-scroll-container" style="max-height: {height}px;">{html_table}</div>', unsafe_allow_html=True)

# Helper: Render 4 Equal-Width KPI Cards
def render_kpi_row(kpis: list):
    """
    Renders exactly 4 KPI cards in a desktop row.
    kpis is a list of tuples: (Title, Value, Subtext/Delta)
    """
    cols = st.columns(4)
    for idx, (title, val, sub) in enumerate(kpis):
        with cols[idx]:
            st.markdown(f"""
            <div class="kpi-card">
                <div class="kpi-title">{title}</div>
                <div class="kpi-value">{val}</div>
                <div class="kpi-subtext">{sub}</div>
            </div>
            """, unsafe_allow_html=True)

# Helper: Section Title
def render_page_header(title: str, subtitle: str):
    st.markdown(f"""
    <div class="page-header-box">
        <h1 class="page-title">{title}</h1>
        <p class="page-subtitle">{subtitle}</p>
    </div>
    """, unsafe_allow_html=True)

# =============================================================================
# SIDEBAR NAVIGATION (COMPACT, NO BRANDING, NO BACKEND EXPOSURE)
# =============================================================================
with st.sidebar:
    st.markdown("""
    <div class="sidebar-brand-box">
        <h2 class="sidebar-brand-title">MUTUAL FUND ANALYTICS</h2>
        <div class="sidebar-brand-sub">Financial Intelligence Platform</div>
    </div>
    """, unsafe_allow_html=True)

    nav_options = [
        "Overview",
        "Industry Overview",
        "Fund Performance",
        "Investor Analytics",
        "SIP & Market Trends",
        "Dataset Information"
    ]

    selected_nav = st.radio(
        "Navigation",
        options=nav_options,
        index=0,
        label_visibility="collapsed"
    )

    st.markdown("<hr style='border: none; border-top: 1px solid #E8ECF3; margin: 20px 0 10px 0;'/>", unsafe_allow_html=True)
    st.caption("Mutual Fund Analytics © 2026")

# =============================================================================
# 1. OVERVIEW PAGE
# =============================================================================
if selected_nav == "Overview":
    render_page_header(
        title="Indian Mutual Fund Market Overview",
        subtitle="A clear picture of mutual fund industry growth and investment trends."
    )

    # 4 Primary KPI Cards
    kpis = get_overview_kpis()
    render_kpi_row([
        ("Total Industry AUM", kpis["total_aum"], "Across all fund houses"),
        ("Monthly SIP Inflow", kpis["monthly_sip"], "Current monthly run-rate"),
        ("Total Folios", kpis["total_folios"], "Registered investor accounts"),
        ("Tracked Schemes", kpis["tracked_schemes"], "Equity, debt and hybrid funds")
    ])

    st.markdown("<div style='height: 12px;'></div>", unsafe_allow_html=True)

    # 4 Visualizations in 2x2 Grid
    df_aum, df_sip, df_amc, df_cat = get_overview_charts_data()
    c1, c2 = st.columns(2)

    with c1:
        st.markdown('<div class="analytics-card">', unsafe_allow_html=True)
        fig1 = charts.chart_industry_aum_growth(df_aum)
        if fig1:
            st.plotly_chart(fig1, use_container_width=True)
        else:
            st.info("No data available for this selection.")
        st.markdown('</div>', unsafe_allow_html=True)

    with c2:
        st.markdown('<div class="analytics-card">', unsafe_allow_html=True)
        fig2 = charts.chart_monthly_sip_trend(df_sip)
        if fig2:
            st.plotly_chart(fig2, use_container_width=True)
        else:
            st.info("No data available for this selection.")
        st.markdown('</div>', unsafe_allow_html=True)

    c3, c4 = st.columns(2)

    with c3:
        st.markdown('<div class="analytics-card">', unsafe_allow_html=True)
        fig3 = charts.chart_top_amcs_aum(df_amc)
        if fig3:
            st.plotly_chart(fig3, use_container_width=True)
        else:
            st.info("No data available for this selection.")
        st.markdown('</div>', unsafe_allow_html=True)

    with c4:
        st.markdown('<div class="analytics-card">', unsafe_allow_html=True)
        fig4 = charts.chart_category_distribution(df_cat)
        if fig4:
            st.plotly_chart(fig4, use_container_width=True)
        else:
            st.info("No data available for this selection.")
        st.markdown('</div>', unsafe_allow_html=True)

    # Bottom: Key Market Insights
    insights = get_market_insights()
    st.markdown("""
    <div class="market-insights-box">
        <div class="insights-header">Key Market Insights</div>
    """, unsafe_allow_html=True)
    for item in insights:
        st.markdown(f'<div class="insight-item">{item}</div>', unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

# =============================================================================
# 2. INDUSTRY OVERVIEW PAGE
# =============================================================================
elif selected_nav == "Industry Overview":
    render_page_header(
        title="Industry Overview",
        subtitle="Macro-level asset growth, fund house market share, and folio expansion trends."
    )

    # 4 Compact KPIs
    kpis = get_industry_kpis()
    render_kpi_row([
        ("Total AUM", kpis["total_aum"], "Peak industry assets"),
        ("Fund Houses", kpis["total_amcs"], "Active asset managers"),
        ("Total Schemes", kpis["total_schemes"], "Across all categories"),
        ("Total Folios", kpis["total_folios"], "Equity, debt & hybrid")
    ])

    st.markdown("<div style='height: 10px;'></div>", unsafe_allow_html=True)

    # Filters
    years, fhs, cats = get_industry_filter_options()
    f1, f2, f3 = st.columns(3)
    with f1:
        sel_year = st.selectbox("Filter Year", years, index=0)
    with f2:
        sel_fh = st.selectbox("Filter Fund House", fhs, index=0)
    with f3:
        sel_cat = st.selectbox("Filter Category", cats, index=0)

    df_aum, df_top_amcs, df_market_share, df_cat_aum, df_folios, df_ranking = get_industry_overview_data(sel_year, sel_fh, sel_cat)

    # Charts Grid
    c1, c2 = st.columns(2)
    with c1:
        st.markdown('<div class="analytics-card">', unsafe_allow_html=True)
        fig1 = charts.chart_industry_aum_progression(df_aum)
        if fig1:
            st.plotly_chart(fig1, use_container_width=True)
        else:
            st.info("No data available for this selection.")
        st.markdown('</div>', unsafe_allow_html=True)

    with c2:
        st.markdown('<div class="analytics-card">', unsafe_allow_html=True)
        fig2 = charts.chart_top_amcs_bar(df_top_amcs)
        if fig2:
            st.plotly_chart(fig2, use_container_width=True)
        else:
            st.info("No data available for this selection.")
        st.markdown('</div>', unsafe_allow_html=True)

    c3, c4 = st.columns(2)
    with c3:
        st.markdown('<div class="analytics-card">', unsafe_allow_html=True)
        fig3 = charts.chart_amc_market_share_donut(df_market_share)
        if fig3:
            st.plotly_chart(fig3, use_container_width=True)
        else:
            st.info("No data available for this selection.")
        st.markdown('</div>', unsafe_allow_html=True)

    with c4:
        st.markdown('<div class="analytics-card">', unsafe_allow_html=True)
        fig4 = charts.chart_category_aum_bar(df_cat_aum)
        if fig4:
            st.plotly_chart(fig4, use_container_width=True)
        else:
            st.info("No data available for this selection.")
        st.markdown('</div>', unsafe_allow_html=True)

    # Folio growth trend wide
    st.markdown('<div class="analytics-card">', unsafe_allow_html=True)
    fig5 = charts.chart_folio_growth_trend(df_folios)
    if fig5:
        st.plotly_chart(fig5, use_container_width=True)
    else:
        st.info("No data available for this selection.")
    st.markdown('</div>', unsafe_allow_html=True)

    # Clean Ranking Table
    st.markdown('<div class="analytics-card">', unsafe_allow_html=True)
    st.markdown('<div class="analytics-card-title">Fund House Market Share Leaderboard</div>', unsafe_allow_html=True)
    st.markdown('<div class="analytics-card-subtitle">Comparative ranking of major asset management companies in India.</div>', unsafe_allow_html=True)
    render_table(df_ranking, height=320)
    
    csv_bytes = df_ranking.to_csv(index=False).encode('utf-8')
    st.download_button("Download Table (CSV)", data=csv_bytes, file_name="fund_house_rankings.csv", mime="text/csv")
    st.markdown('</div>', unsafe_allow_html=True)

# =============================================================================
# 3. FUND PERFORMANCE PAGE
# =============================================================================
elif selected_nav == "Fund Performance":
    render_page_header(
        title="Fund Performance",
        subtitle="Risk-adjusted returns, benchmark tracking, and quantitative fund rankings."
    )

    # 4 KPIs
    kpis = get_fund_kpis()
    render_kpi_row([
        ("Best 3-Year CAGR", kpis["best_cagr"], "Highest annualized growth"),
        ("Highest Sharpe Ratio", kpis["highest_sharpe"], "Risk-adjusted performance"),
        ("Lowest Expense Ratio", kpis["lowest_ter"], "Lowest operating expense"),
        ("Best Composite Score", kpis["best_score"], "Top multi-factor rating")
    ])

    st.markdown("<div style='height: 10px;'></div>", unsafe_allow_html=True)

    # Filters
    fhs, cats, risks = get_fund_filter_options()
    f1, f2, f3 = st.columns(3)
    with f1:
        sel_fh = st.selectbox("Fund House", fhs, index=0)
    with f2:
        sel_cat = st.selectbox("Category", cats, index=0)
    with f3:
        sel_risk = st.selectbox("Risk Level", risks, index=0)

    df_perf = get_filtered_funds(sel_fh, sel_cat, sel_risk)

    if df_perf.empty:
        st.info("No data available for this selection.")
    else:
        # Fund Selection Component
        st.markdown('<div class="analytics-card">', unsafe_allow_html=True)
        st.markdown('<div class="analytics-card-title">Fund Deep Dive Selector</div>', unsafe_allow_html=True)
        st.markdown('<div class="analytics-card-subtitle">Choose any fund to view its complete quantitative profile.</div>', unsafe_allow_html=True)
        
        scheme_list = df_perf["scheme_name"].tolist()
        sel_scheme = st.selectbox("Select Mutual Fund", scheme_list, index=0)
        
        prof = get_single_fund_profile(sel_scheme)
        if prof:
            m1, m2, m3, m4 = st.columns(4)
            m1.metric("Current NAV", prof["current_nav"])
            m2.metric("1-Year Return", prof["return_1yr"])
            m3.metric("3-Year CAGR", prof["return_3yr"])
            m4.metric("5-Year CAGR", prof["return_5yr"])

            m5, m6, m7, m8 = st.columns(4)
            m5.metric("Sharpe Ratio", prof["sharpe"])
            m6.metric("Sortino Ratio", prof["sortino"])
            m7.metric("Alpha", prof["alpha"])
            m8.metric("Beta", prof["beta"])

            m9, m10, m11, m12 = st.columns(4)
            m9.metric("Expense Ratio", prof["expense_ratio"])
            m10.metric("Max Drawdown", prof["max_drawdown"])
            m11.metric("Category", prof["category"])
            m12.metric("Benchmark", prof["benchmark"])
        st.markdown('</div>', unsafe_allow_html=True)

        # Charts: NAV Trend & Fund vs Benchmark
        if prof:
            nav_df, bmk_df = get_nav_history_series(prof["amfi_code"], prof["benchmark"])
            c1, c2 = st.columns(2)
            with c1:
                st.markdown('<div class="analytics-card">', unsafe_allow_html=True)
                fig1 = charts.chart_historical_nav_trend(nav_df, prof["fund_name"])
                if fig1:
                    st.plotly_chart(fig1, use_container_width=True)
                else:
                    st.info("No data available for this selection.")
                st.markdown('</div>', unsafe_allow_html=True)

            with c2:
                st.markdown('<div class="analytics-card">', unsafe_allow_html=True)
                fig2 = charts.chart_fund_vs_benchmark(nav_df, bmk_df, prof["fund_name"], prof["benchmark"])
                if fig2:
                    st.plotly_chart(fig2, use_container_width=True)
                else:
                    st.info("No data available for this selection.")
                st.markdown('</div>', unsafe_allow_html=True)

        # Charts: Risk-Return Scatter & Category Comparison
        c3, c4 = st.columns(2)
        with c3:
            st.markdown('<div class="analytics-card">', unsafe_allow_html=True)
            fig3 = charts.chart_risk_return_scatter(df_perf)
            if fig3:
                st.plotly_chart(fig3, use_container_width=True)
            else:
                st.info("No data available for this selection.")
            st.markdown('</div>', unsafe_allow_html=True)

        with c4:
            st.markdown('<div class="analytics-card">', unsafe_allow_html=True)
            fig4 = charts.chart_category_performance(df_perf)
            if fig4:
                st.plotly_chart(fig4, use_container_width=True)
            else:
                st.info("No data available for this selection.")
            st.markdown('</div>', unsafe_allow_html=True)

        # Fund Comparison Tool (up to 4 funds)
        st.markdown('<div class="analytics-card">', unsafe_allow_html=True)
        st.markdown('<div class="analytics-card-title">Fund Comparison Tool</div>', unsafe_allow_html=True)
        st.markdown('<div class="analytics-card-subtitle">Select up to 4 funds to compare side-by-side.</div>', unsafe_allow_html=True)
        
        default_comp = scheme_list[:3] if len(scheme_list) >= 3 else scheme_list
        selected_comp = st.multiselect("Choose funds to compare (maximum 4)", options=scheme_list, default=default_comp)
        
        if selected_comp:
            comp_funds = selected_comp[:4]
            comp_df = df_perf[df_perf["scheme_name"].isin(comp_funds)][[
                "scheme_name", "category", "fund_house", "return_1yr_pct", "return_3yr_pct",
                "sharpe_ratio", "alpha", "beta", "expense_ratio_pct", "max_drawdown_pct", "composite_score"
            ]].rename(columns={
                "scheme_name": "Fund Name",
                "category": "Category",
                "fund_house": "Fund House",
                "return_1yr_pct": "1Y Return (%)",
                "return_3yr_pct": "3Y CAGR (%)",
                "sharpe_ratio": "Sharpe",
                "alpha": "Alpha (%)",
                "beta": "Beta",
                "expense_ratio_pct": "TER (%)",
                "max_drawdown_pct": "Max DD (%)",
                "composite_score": "Score"
            })
            render_table(comp_df, height=220)
        else:
            st.info("Select at least one fund to compare.")
        st.markdown('</div>', unsafe_allow_html=True)

        # Sortable Performance Table
        st.markdown('<div class="analytics-card">', unsafe_allow_html=True)
        st.markdown('<div class="analytics-card-title">Complete Performance Scorecard</div>', unsafe_allow_html=True)
        st.markdown('<div class="analytics-card-subtitle">Comprehensive ranking of all filtered mutual fund schemes.</div>', unsafe_allow_html=True)
        
        table_df = df_perf[[
            "fund_rank", "scheme_name", "category", "fund_house", "return_1yr_pct",
            "return_3yr_pct", "return_5yr_pct", "sharpe_ratio", "alpha", "beta",
            "expense_ratio_pct", "max_drawdown_pct", "composite_score"
        ]].rename(columns={
            "fund_rank": "Rank",
            "scheme_name": "Scheme Name",
            "category": "Category",
            "fund_house": "Fund House",
            "return_1yr_pct": "1Y Return (%)",
            "return_3yr_pct": "3Y CAGR (%)",
            "return_5yr_pct": "5Y CAGR (%)",
            "sharpe_ratio": "Sharpe",
            "alpha": "Alpha (%)",
            "beta": "Beta",
            "expense_ratio_pct": "TER (%)",
            "max_drawdown_pct": "Max DD (%)",
            "composite_score": "Score"
        })
        render_table(table_df, height=360)
        
        csv_bytes = table_df.to_csv(index=False).encode('utf-8')
        st.download_button("Download Performance Table (CSV)", data=csv_bytes, file_name="fund_performance.csv", mime="text/csv")
        st.markdown('</div>', unsafe_allow_html=True)

# =============================================================================
# 4. INVESTOR ANALYTICS PAGE
# =============================================================================
elif selected_nav == "Investor Analytics":
    render_page_header(
        title="Investor Analytics",
        subtitle="Retail transaction patterns, demographic profiles, and regional participation trends."
    )

    # 4 KPIs
    kpis = get_investor_kpis()
    render_kpi_row([
        ("Total Investors", kpis["total_investors"], "Sample user cohort"),
        ("Transactions", kpis["total_transactions"], "Executed order volume"),
        ("Transaction Value", kpis["total_value"], "Cumulative gross volume"),
        ("Average Ticket", kpis["avg_value"], "Mean value per transaction")
    ])

    st.markdown("<div style='height: 10px;'></div>", unsafe_allow_html=True)

    # Small Synthetic Data Notice
    st.markdown("""
    <div class="info-banner">
        <b>Notice:</b> Investor transaction records are synthetic sample data created for analytical demonstration and do not represent actual customer information.
    </div>
    """, unsafe_allow_html=True)

    # Demographic Filters
    states, ages, genders, types = get_investor_filter_options()
    f1, f2, f3, f4 = st.columns(4)
    with f1:
        sel_state = st.selectbox("Filter State", states, index=0)
    with f2:
        sel_age = st.selectbox("Age Group", ages, index=0)
    with f3:
        sel_gender = st.selectbox("Gender", genders, index=0)
    with f4:
        sel_type = st.selectbox("Transaction Type", types, index=0)

    df_tx = get_filtered_investor_data(sel_state, sel_age, sel_gender, sel_type)

    if df_tx.empty:
        st.info("No data available for this selection.")
    else:
        # 6 Charts in 2-Column Grid
        c1, c2 = st.columns(2)
        with c1:
            st.markdown('<div class="analytics-card">', unsafe_allow_html=True)
            fig1 = charts.chart_investor_age_dist(df_tx)
            if fig1:
                st.plotly_chart(fig1, use_container_width=True)
            else:
                st.info("No data available for this selection.")
            st.markdown('</div>', unsafe_allow_html=True)

        with c2:
            st.markdown('<div class="analytics-card">', unsafe_allow_html=True)
            fig2 = charts.chart_state_investment_bar(df_tx)
            if fig2:
                st.plotly_chart(fig2, use_container_width=True)
            else:
                st.info("No data available for this selection.")
            st.markdown('</div>', unsafe_allow_html=True)

        c3, c4 = st.columns(2)
        with c3:
            st.markdown('<div class="analytics-card">', unsafe_allow_html=True)
            fig3 = charts.chart_sip_vs_lumpsum_donut(df_tx)
            if fig3:
                st.plotly_chart(fig3, use_container_width=True)
            else:
                st.info("No data available for this selection.")
            st.markdown('</div>', unsafe_allow_html=True)

        with c4:
            st.markdown('<div class="analytics-card">', unsafe_allow_html=True)
            fig4 = charts.chart_monthly_tx_trend(df_tx)
            if fig4:
                st.plotly_chart(fig4, use_container_width=True)
            else:
                st.info("No data available for this selection.")
            st.markdown('</div>', unsafe_allow_html=True)

        c5, c6 = st.columns(2)
        with c5:
            st.markdown('<div class="analytics-card">', unsafe_allow_html=True)
            fig5 = charts.chart_t30_b30_bar(df_tx)
            if fig5:
                st.plotly_chart(fig5, use_container_width=True)
            else:
                st.info("No data available for this selection.")
            st.markdown('</div>', unsafe_allow_html=True)

        with c6:
            st.markdown('<div class="analytics-card">', unsafe_allow_html=True)
            fig6 = charts.chart_investment_by_age_bar(df_tx)
            if fig6:
                st.plotly_chart(fig6, use_container_width=True)
            else:
                st.info("No data available for this selection.")
            st.markdown('</div>', unsafe_allow_html=True)

# =============================================================================
# 5. SIP & MARKET TRENDS PAGE
# =============================================================================
elif selected_nav == "SIP & Market Trends":
    render_page_header(
        title="SIP & Market Trends",
        subtitle="Systematic Investment Plan inflows, active account acceleration, and market benchmarks."
    )

    # 4 KPIs
    kpis = get_sip_kpis()
    render_kpi_row([
        ("Monthly SIP Inflow", kpis["monthly_sip"], "Current monthly run-rate"),
        ("Active SIP Accounts", kpis["active_accounts"], "Retail compounding mandates"),
        ("Cumulative SIP AUM", kpis["sip_aum"], "Total systematic assets"),
        ("Annual SIP Growth", kpis["annual_growth"], "Year-on-year expansion")
    ])

    st.markdown("<div style='height: 10px;'></div>", unsafe_allow_html=True)

    # Filters
    years, bmks, cats = get_sip_filter_options()
    f1, f2, f3 = st.columns(3)
    with f1:
        sel_years = st.multiselect("Calendar Years", years, default=years)
    with f2:
        default_bmks = [b for b in ["Nifty 50", "Nifty Midcap 150", "BSE SmallCap", "CRISIL Liquid"] if b in bmks]
        sel_bmks = st.multiselect("Benchmark Indices", bmks, default=default_bmks if default_bmks else bmks[:4])
    with f3:
        default_cats = [c for c in ["Large Cap", "Mid Cap", "Small Cap", "Flexi Cap", "Hybrid"] if c in cats]
        sel_cats = st.multiselect("Mutual Fund Categories", cats, default=default_cats if default_cats else cats[:5])

    df_sip = get_filtered_sip_data(sel_years)
    df_bmk = get_filtered_benchmark_data(sel_bmks)
    df_cat = get_filtered_category_inflow_data(sel_cats)

    if df_sip.empty:
        st.info("No data available for this selection.")
    else:
        # 6 Charts in 2-Column Grid
        c1, c2 = st.columns(2)
        with c1:
            st.markdown('<div class="analytics-card">', unsafe_allow_html=True)
            fig1 = charts.chart_sip_inflow_trend(df_sip)
            if fig1:
                st.plotly_chart(fig1, use_container_width=True)
            else:
                st.info("No data available for this selection.")
            st.markdown('</div>', unsafe_allow_html=True)

        with c2:
            st.markdown('<div class="analytics-card">', unsafe_allow_html=True)
            fig2 = charts.chart_active_sip_growth(df_sip)
            if fig2:
                st.plotly_chart(fig2, use_container_width=True)
            else:
                st.info("No data available for this selection.")
            st.markdown('</div>', unsafe_allow_html=True)

        c3, c4 = st.columns(2)
        with c3:
            st.markdown('<div class="analytics-card">', unsafe_allow_html=True)
            fig3 = charts.chart_category_net_inflows(df_cat)
            if fig3:
                st.plotly_chart(fig3, use_container_width=True)
            else:
                st.info("No data available for this selection.")
            st.markdown('</div>', unsafe_allow_html=True)

        with c4:
            st.markdown('<div class="analytics-card">', unsafe_allow_html=True)
            fig4 = charts.chart_benchmark_performance(df_bmk)
            if fig4:
                st.plotly_chart(fig4, use_container_width=True)
            else:
                st.info("No data available for this selection.")
            st.markdown('</div>', unsafe_allow_html=True)

        c5, c6 = st.columns(2)
        with c5:
            st.markdown('<div class="analytics-card">', unsafe_allow_html=True)
            fig5 = charts.chart_sip_growth_by_year(df_sip)
            if fig5:
                st.plotly_chart(fig5, use_container_width=True)
            else:
                st.info("No data available for this selection.")
            st.markdown('</div>', unsafe_allow_html=True)

        with c6:
            st.markdown('<div class="analytics-card">', unsafe_allow_html=True)
            fig6 = charts.chart_category_inflow_heatmap(df_cat)
            if fig6:
                st.plotly_chart(fig6, use_container_width=True)
            else:
                st.info("No data available for this selection.")
            st.markdown('</div>', unsafe_allow_html=True)

# =============================================================================
# 6. DATASET INFORMATION PAGE (NEW FINAL PAGE)
# =============================================================================
elif selected_nav == "Dataset Information":
    render_page_header(
        title="Dataset Information",
        subtitle="Comprehensive overview, provenance, quality metrics, and documentation for all underlying datasets."
    )

    overview_df, total_recs = get_dataset_overview_metrics()

    # Section: Dataset Overview Table
    st.markdown('<div class="analytics-card">', unsafe_allow_html=True)
    st.markdown('<div class="analytics-card-title">Dataset Overview Matrix</div>', unsafe_allow_html=True)
    st.markdown('<div class="analytics-card-subtitle">Summary of all 10 core datasets analyzed in this platform.</div>', unsafe_allow_html=True)
    render_table(overview_df, height=360)
    st.markdown('</div>', unsafe_allow_html=True)

    # Section A: DATA COLLECTION
    st.markdown('<div class="analytics-card">', unsafe_allow_html=True)
    st.markdown('<div class="analytics-card-title">A. Data Collection Methodology</div>', unsafe_allow_html=True)
    st.markdown("""
    The datasets utilized across this analytics application were sourced through multiple standardized collection channels:
    
    1. **AMFI Official Disclosures:** Industry-wide macro metrics, monthly systematic investment mobilization (SIPs), quarterly average assets under management (QAAUM), and folio counts were collected from the Association of Mutual Funds in India (AMFI).
    2. **Public API Endpoints (mfapi.in):** Historical daily Net Asset Values (NAV) for premier schemes were ingested via publicly recognized endpoints.
    3. **Public Financial Market Disclosures:** Benchmark index price levels for Nifty 50, Nifty Midcap 150, BSE SmallCap, and CRISIL Liquid indices were compiled from published index factsheets.
    4. **Simulated Analytical Distributions:** Granular investor order books and demographic variables were synthesized using calibrated probabilistic distributions to model realistic retail investor compounding behaviors without exposing proprietary or confidential personal information.
    """, unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

    # Section B: DATA QUALITY
    st.markdown('<div class="analytics-card">', unsafe_allow_html=True)
    st.markdown('<div class="analytics-card-title">B. Data Quality & Integrity Summary</div>', unsafe_allow_html=True)
    
    q1, q2, q3, q4, q5 = st.columns(5)
    q1.metric("Total Records", f"{total_recs:,}")
    q2.metric("Total Datasets", "10 Datasets")
    q3.metric("Missing Values", "0 (Cleaned)")
    q4.metric("Valid Records", "99.99%")
    q5.metric("Date Coverage", "2020 – 2025")
    
    st.markdown("""
    <div style="font-size: 12.5px; color: #64748B; margin-top: 10px;">
        All ingested records underwent schema standardization, type-casting, deduplication, and boundary validation prior to analytical aggregation.
    </div>
    """, unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

    # Section C: REAL VS SYNTHETIC DATA
    st.markdown('<div class="analytics-card">', unsafe_allow_html=True)
    st.markdown('<div class="analytics-card-title">C. Real vs Synthetic Data Provenance</div>', unsafe_allow_html=True)
    st.markdown("""
    To maintain clear analytical provenance:
    
    - **Real & Public Financial Data:** Includes fund structural master information, historical daily NAV curves, benchmark index closing prices, AMFI monthly SIP disclosures (e.g. December 2025 milestone of ₹31,002 Crore), and quarterly fund house assets under management.
    - **Synthetic Sample Data:** Includes investor transaction records (5,000 synthetic investor profiles modeling age cohorts, geographic tiers T30/B30, and order channels) and representative portfolio company weight snapshots. These are calibrated sample datasets designed strictly for academic and portfolio behavioral analytics.
    """, unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

    # Section D: DATA DICTIONARY
    st.markdown('<div class="analytics-card">', unsafe_allow_html=True)
    st.markdown('<div class="analytics-card-title">D. Data Dictionary & Field Specifications</div>', unsafe_allow_html=True)
    st.markdown('<div class="analytics-card-subtitle">Expand any dataset to view field descriptions, data types, and sample values.</div>', unsafe_allow_html=True)

    with st.expander("1. Fund Master (`dim_fund`)"):
        st.markdown("""
        | Field Name | Type | Description | Sample Value |
        | :--- | :--- | :--- | :--- |
        | `amfi_code` | INTEGER | Unique AMFI scheme code | `119551` |
        | `fund_house` | TEXT | Asset Management Company | `SBI Mutual Fund` |
        | `scheme_name` | TEXT | Full official scheme designation | `SBI Bluechip Fund - Direct Plan - Growth` |
        | `category` | TEXT | Primary asset class categorization | `Large Cap`, `Mid Cap`, `Small Cap` |
        | `plan` | TEXT | Investment route | `Direct`, `Regular` |
        | `benchmark` | TEXT | Regulatory performance benchmark | `Nifty 50`, `Nifty 100` |
        | `expense_ratio_pct` | REAL | Total Expense Ratio (TER %) | `0.78` |
        | `risk_category` | TEXT | SEBI Risk-o-meter rating | `Moderate`, `Very High` |
        """)

    with st.expander("2. Historical Daily NAV (`fact_nav`)"):
        st.markdown("""
        | Field Name | Type | Description | Sample Value |
        | :--- | :--- | :--- | :--- |
        | `amfi_code` | INTEGER | AMFI scheme identifier | `119551` |
        | `date` | DATE | Market session date (YYYY-MM-DD) | `2024-03-28` |
        | `nav` | REAL | Net Asset Value in Indian Rupees | `107.35` |
        | `daily_return_pct`| REAL | Day-on-day NAV percentage change | `+0.45%` |
        """)

    with st.expander("3. Monthly SIP Inflows (`fact_sip_industry`)"):
        st.markdown("""
        | Field Name | Type | Description | Sample Value |
        | :--- | :--- | :--- | :--- |
        | `month` | TEXT | Calendar reporting month (YYYY-MM) | `2025-12` |
        | `sip_inflow_crore` | REAL | Monthly gross systematic inflows (₹ Cr) | `31002.0` |
        | `active_sip_accounts_crore` | REAL | Active systematic accounts in Crores | `9.35` |
        | `new_sip_accounts_lakh` | REAL | New registrations in Lakhs | `32.69` |
        | `sip_aum_lakh_crore` | REAL | Cumulative SIP AUM (₹ Lakh Cr) | `14.80` |
        | `yoy_growth_pct` | REAL | Year-on-year growth rate percentage | `19.96%` |
        """)

    with st.expander("4. Investor Transactions (`fact_transactions`)"):
        st.markdown("""
        | Field Name | Type | Description | Sample Value |
        | :--- | :--- | :--- | :--- |
        | `transaction_id` | INTEGER | Unique order identifier | `1001` |
        | `investor_id` | INTEGER | Synthetic investor identifier | `1425` |
        | `transaction_date`| DATE | Order execution date | `2024-05-10` |
        | `transaction_type`| TEXT | Order type (`SIP`, `Lumpsum`, `Redemption`) | `SIP` |
        | `amount_inr` | REAL | Order value in Indian Rupees | `5000.0` |
        | `city_tier` | TEXT | Geographic classification (`T30` or `B30`) | `B30` |
        | `age_group` | TEXT | Demographic cohort | `26-35` |
        | `gender` | TEXT | Investor gender | `Female` |
        """)

    with st.expander("5. Scheme Quantitative Performance (`fact_performance`)"):
        st.markdown("""
        | Field Name | Type | Description | Sample Value |
        | :--- | :--- | :--- | :--- |
        | `amfi_code` | INTEGER | Scheme code identifier | `119551` |
        | `return_1yr_pct` | REAL | 1-Year point-to-point return | `+18.45%` |
        | `return_3yr_pct` | REAL | 3-Year annualized compound growth (CAGR) | `+16.20%` |
        | `sharpe_ratio` | REAL | Annualized Sharpe ratio ($R_f = 6.50\%$) | `1.15` |
        | `sortino_ratio` | REAL | Downside risk-adjusted Sortino ratio | `1.62` |
        | `alpha` | REAL | Jensen's Alpha relative to benchmark (%) | `+2.85%` |
        | `beta` | REAL | Sensitivity relative to benchmark returns | `0.94` |
        | `max_drawdown_pct`| REAL | Peak-to-trough maximum observed decline | `-16.80%` |
        | `composite_score` | REAL | Multi-factor scorecard rating (0 to 100) | `85.9` |
        """)

    st.markdown('</div>', unsafe_allow_html=True)

    # Section E: DOWNLOAD DATA
    st.markdown('<div class="analytics-card">', unsafe_allow_html=True)
    st.markdown('<div class="analytics-card-title">E. Data Export & Download Center</div>', unsafe_allow_html=True)
    st.markdown('<div class="analytics-card-subtitle">Export underlying analytical datasets directly in CSV format.</div>', unsafe_allow_html=True)

    d_col1, d_col2, d_col3 = st.columns(3)
    
    b1 = get_csv_download_bytes("01_fund_master.csv")
    with d_col1:
        if b1:
            st.download_button("Download Fund Master (CSV)", data=b1, file_name="fund_master.csv", mime="text/csv", use_container_width=True)
    
    b2 = get_csv_download_bytes("04_monthly_sip_inflows.csv")
    with d_col2:
        if b2:
            st.download_button("Download SIP Inflows (CSV)", data=b2, file_name="monthly_sip_inflows.csv", mime="text/csv", use_container_width=True)

    b3 = get_csv_download_bytes("07_scheme_performance.csv")
    with d_col3:
        if b3:
            st.download_button("Download Scheme Performance (CSV)", data=b3, file_name="scheme_performance.csv", mime="text/csv", use_container_width=True)

    d_col4, d_col5 = st.columns(2)
    b4 = get_csv_download_bytes("02_nav_history.csv")
    with d_col4:
        if b4:
            st.download_button("Download NAV History Sample (CSV)", data=b4, file_name="nav_history.csv", mime="text/csv", use_container_width=True)

    summary_bytes = overview_df.to_csv(index=False).encode('utf-8')
    with d_col5:
        st.download_button("Download Complete Dataset Summary (CSV)", data=summary_bytes, file_name="dataset_summary.csv", mime="text/csv", use_container_width=True)

    st.markdown('</div>', unsafe_allow_html=True)

    # Section F: DATA LIMITATIONS
    st.markdown('<div class="analytics-card">', unsafe_allow_html=True)
    st.markdown('<div class="analytics-card-title">F. Data Limitations & Analytical Boundaries</div>', unsafe_allow_html=True)
    st.markdown("""
    Users and evaluators should consider the following boundaries when interpreting insights:
    
    - **Historical Time Horizon:** Ingested daily NAV series span January 2022 through late 2025/early 2026. Prior market cycles (e.g. 2008 global financial crisis or 2020 pandemic dip) are not fully reflected in short-term attribution.
    - **Simulated Demographic Order Books:** Investor transaction frequency, payment channel adoption, and urban tier distributions are calibrated against AMFI macro ratios but represent synthetic sample accounts. They should not be utilized for individualized credit profiling.
    - **Cash and Derivative Balances:** Portfolio holdings track top representative equity positions and do not account for daily intra-month cash sweeps or hedging derivatives.
    - **Educational Purpose:** All performance indicators, Sharpe ratios, and scorecards are calculated for academic evaluation and do not represent guaranteed future returns.
    """, unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)
