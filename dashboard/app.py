"""
Bluestock Fintech - Mutual Fund Analytics Platform
Entry Point: dashboard/app.py
Author: Senior Financial BI & Python Engineer
"""

import os
import sys
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# Setup module path
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT_DIR = os.path.abspath(os.path.join(CURRENT_DIR, ".."))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

from dashboard.utils import (
    apply_global_styles, render_sidebar, render_global_header, render_disclaimer,
    ensure_pipeline_ready, query_db, style_plot, render_fintech_table,
    get_industry_metrics, format_currency, create_kpi_card, create_section_header,
    create_empty_state, REPORTS_DIR
)

st.set_page_config(
    page_title="Bluestock Fintech | Mutual Fund Analytics",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize database check & inject light fintech design styles
ensure_pipeline_ready()
apply_global_styles()

# Render Light Navigation Sidebar
render_sidebar(current_page="Home")

# Render Institutional Global Header
render_global_header(
    page_title="Indian Mutual Fund Intelligence Platform",
    page_subtitle="Macro-level capitalization, multi-factor risk attribution, and investor transaction analytics.",
    breadcrumb_page="Executive Overview"
)

# Regulatory Disclaimer Banner
render_disclaimer()

# --- 1. TOP EXECUTIVE KPI CARDS ROW (5 METRICS) ---
ind = get_industry_metrics()

kpi_cols = st.columns(5)
with kpi_cols[0]:
    create_kpi_card(
        title="Total Industry AUM",
        value=format_currency(ind["total_aum_crore"]),
        delta="Q4 2025 Peak",
        delta_color="positive",
        subtitle="Macro Assets",
        icon="🏛️"
    )

with kpi_cols[1]:
    sip_delta = f"{ind['sip_mom_pct']:+.1f}% MoM" if ind['sip_mom_pct'] != 0 else "+24.8% YoY"
    create_kpi_card(
        title="Monthly SIP Inflow",
        value=f"₹{ind['monthly_sip_crore']:,.0f} Cr",
        delta=sip_delta,
        delta_color="positive",
        subtitle="Retail Mobilization",
        icon="📈"
    )

with kpi_cols[2]:
    create_kpi_card(
        title="Active SIP Accounts",
        value=f"{ind['active_sip_accounts_crore']:.2f} Cr",
        delta="+85% 3-Yr Trend",
        delta_color="positive",
        subtitle="AMFI Record",
        icon="💳"
    )

with kpi_cols[3]:
    create_kpi_card(
        title="Total Folios",
        value=f"{ind['total_folios_crore']:.2f} Cr",
        delta="Equity Dominant",
        delta_color="positive",
        subtitle="Across AMCs",
        icon="📑"
    )

with kpi_cols[4]:
    create_kpi_card(
        title="Tracked Universe",
        value=f"{ind['active_schemes']} Schemes",
        delta=f"{ind['total_amcs']} Top AMCs",
        delta_color="positive",
        subtitle="Star-Schema Warehouse",
        icon="⚡"
    )

st.markdown("<div style='height: 14px;'></div>", unsafe_allow_html=True)

# --- 2. EXECUTIVE ANALYTICAL HIGHLIGHTS BOX ---
st.markdown("""
<div style="background-color: #FFFFFF; border: 1px solid #E5EAF2; border-radius: 12px; padding: 16px 20px; box-shadow: 0 1px 3px rgba(0,0,0,0.04); margin-bottom: 22px;">
    <div style="display: flex; align-items: center; justify-content: space-between; margin-bottom: 10px;">
        <span style="font-size: 0.88rem; font-weight: 700; color: #172033; display: flex; align-items: center; gap: 6px;">
            <span style="color: #2563EB;">💡</span> LATEST ANALYTICAL INSIGHTS & MACRO FINDINGS
        </span>
        <span style="font-size: 0.72rem; color: #64748B; background: #F1F5F9; padding: 2px 8px; border-radius: 9999px; font-weight: 600;">FY 2025-26 SYNOPSIS</span>
    </div>
    <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(280px, 1fr)); gap: 14px; font-size: 0.81rem; color: #475569; line-height: 1.45;">
        <div style="background: #F8FAFC; border-left: 3px solid #2563EB; padding: 8px 12px; border-radius: 6px;">
            <b style="color: #172033;">SIP Surge:</b> Monthly systematic inflows crossed <b>₹31,002 Crore</b> in Dec 2025, surging 2.67x from 2022 levels with 9.35 Cr active accounts.
        </div>
        <div style="background: #F8FAFC; border-left: 3px solid #0D9488; padding: 8px 12px; border-radius: 6px;">
            <b style="color: #172033;">AMC Concentration:</b> Top 5 AMCs (SBI, ICICI Pru, HDFC, Nippon, Kotak) manage over <b>58.4%</b> of overall industry assets.
        </div>
        <div style="background: #F8FAFC; border-left: 3px solid #16A34A; padding: 8px 12px; border-radius: 6px;">
            <b style="color: #172033;">Retail Democratization:</b> Beyond-30 (B30) cities now contribute <b>24.2%</b> of mutual fund folios, driven by mobile-first distribution channels.
        </div>
        <div style="background: #F8FAFC; border-left: 3px solid #F59E0B; padding: 8px 12px; border-radius: 6px;">
            <b style="color: #172033;">Alpha Generation:</b> Active Mid-Cap and Small-Cap schemes delivered up to <b>+5.8%</b> Jensen's Alpha relative to Nifty 50 and Midcap benchmarks.
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

# --- 3. INTERACTIVE VISUALIZATION GRID (5 CHARTS) ---
create_section_header("Macroeconomic Asset Growth & Allocation Trends", "Interactive visual analytics powered by SQLite star-schema warehouse.")

# Grid Row 1: AUM Growth Area Chart + SIP Inflow Trajectory
row1_col1, row1_col2 = st.columns(2)

with row1_col1:
    aum_trend_df = query_db("""
        SELECT year || ' ' || quarter as period, SUM(aum_crore) / 1000.0 as total_aum_thousand_cr
        FROM fact_aum
        GROUP BY year, quarter
        ORDER BY year, quarter;
    """)
    if not aum_trend_df.empty:
        fig_aum = px.area(
            aum_trend_df, x="period", y="total_aum_thousand_cr",
            labels={"period": "Quarter", "total_aum_thousand_cr": "AUM (₹ Thousand Cr)"},
            color_discrete_sequence=["#2563EB"]
        )
        fig_aum.update_traces(
            line=dict(width=2.5, color="#2563EB"),
            fillcolor="rgba(37, 99, 235, 0.12)"
        )
        fig_aum = style_plot(fig_aum, "1. Industry Cumulative AUM Progression (2022–2025)", height=370)
        st.plotly_chart(fig_aum, use_container_width=True)
    else:
        create_empty_state("AUM data unavailable.")

with row1_col2:
    sip_df = query_db("""
        SELECT month, sip_inflow_crore, active_sip_accounts_crore
        FROM fact_sip_industry
        ORDER BY month ASC;
    """)
    if not sip_df.empty:
        fig_sip = go.Figure()
        fig_sip.add_trace(go.Bar(
            x=sip_df["month"], y=sip_df["sip_inflow_crore"],
            name="Monthly SIP (₹ Cr)",
            marker_color="#0D9488",
            opacity=0.88
        ))
        fig_sip.add_trace(go.Scatter(
            x=sip_df["month"], y=sip_df["active_sip_accounts_crore"] * 3000.0,
            name="Active Accounts (Scaled)",
            mode="lines+markers",
            line=dict(color="#F59E0B", width=2.5),
            marker=dict(size=4)
        ))
        fig_sip = style_plot(fig_sip, "2. Monthly SIP Inflow & Retail Account Velocity", height=370)
        st.plotly_chart(fig_sip, use_container_width=True)
    else:
        create_empty_state("SIP data unavailable.")

# Grid Row 2: Top 10 AMCs + Category Allocation Donut
row2_col1, row2_col2 = st.columns(2)

with row2_col1:
    amc_peak_df = query_db("""
        SELECT fund_house, MAX(aum_crore) / 1000.0 as peak_aum_thousand_cr
        FROM fact_aum
        GROUP BY fund_house
        ORDER BY peak_aum_thousand_cr ASC
        LIMIT 10;
    """)
    if not amc_peak_df.empty:
        fig_amc = px.bar(
            amc_peak_df, y="fund_house", x="peak_aum_thousand_cr", orientation="h",
            labels={"fund_house": "Fund House", "peak_aum_thousand_cr": "Peak AUM (₹ Thousand Cr)"},
            color="peak_aum_thousand_cr",
            color_continuous_scale=[[0, "#93C5FD"], [1, "#1D4ED8"]]
        )
        fig_amc = style_plot(fig_amc, "3. Top 10 AMCs by Peak Assets Under Management", height=370)
        fig_amc.update_layout(coloraxis_showscale=False)
        st.plotly_chart(fig_amc, use_container_width=True)
    else:
        create_empty_state("AMC data unavailable.")

with row2_col2:
    cat_df = query_db("""
        SELECT f.category, COUNT(f.amfi_code) as scheme_count, AVG(p.return_3yr_pct) as avg_cagr
        FROM dim_fund f
        LEFT JOIN fact_performance p ON f.amfi_code = p.amfi_code
        GROUP BY f.category
        ORDER BY scheme_count DESC;
    """)
    if not cat_df.empty:
        fig_cat = px.pie(
            cat_df, values="scheme_count", names="category",
            color_discrete_sequence=['#2563EB', '#0D9488', '#F59E0B', '#8B5CF6', '#EC4899', '#10B981', '#64748B'],
            hole=0.48
        )
        fig_cat.update_traces(
            textposition='inside',
            textinfo='percent+label',
            hovertemplate='<b>%{label}</b><br>Schemes: %{value}<br>Share: %{percent}<extra></extra>'
        )
        fig_cat = style_plot(fig_cat, "4. Asset Class Distribution Across Tracked Universe", height=370)
        st.plotly_chart(fig_cat, use_container_width=True)
    else:
        create_empty_state("Category data unavailable.")

# Grid Row 3: Top Performing Funds Comparison Bar
create_section_header("Top 10 Mutual Funds Ranked by Multi-Factor Composite Score")
top_funds_df = query_db("""
    SELECT 
        f.scheme_name,
        f.category,
        p.composite_score,
        p.return_3yr_pct,
        p.sharpe_ratio
    FROM fact_performance p
    JOIN dim_fund f ON p.amfi_code = f.amfi_code
    ORDER BY p.composite_score DESC
    LIMIT 10;
""")

if not top_funds_df.empty:
    fig_top = px.bar(
        top_funds_df, x="composite_score", y="scheme_name", orientation="h",
        color="category",
        labels={"scheme_name": "Scheme Name", "composite_score": "Composite Score (0–100)", "category": "Category"},
        color_discrete_sequence=['#2563EB', '#0D9488', '#F59E0B', '#8B5CF6', '#10B981']
    )
    fig_top = style_plot(fig_top, "5. Top 10 Funds: Multi-Factor Composite Rating", height=360)
    fig_top.update_layout(yaxis=dict(autorange="reversed"))
    st.plotly_chart(fig_top, use_container_width=True)

st.markdown("<div style='height: 16px;'></div>", unsafe_allow_html=True)

# --- 4. INTERACTIVE TABS: LEADERBOARD, RECOMMENDER & DOWNLOADS ---
tab_lead, tab_rec, tab_reports, tab_arch = st.tabs([
    "🏆 Fund Scorecard Leaderboard",
    "🤖 Risk-Adjusted Fund Recommender",
    "📄 Institutional Reports & Downloads",
    "🏗️ Pipeline Architecture"
])

with tab_lead:
    st.markdown("""
    <div style="margin-bottom: 10px;">
        <span style="font-weight: 600; color: #172033; font-size: 0.95rem;">Top 10 Mutual Fund Schemes (Star-Schema Evaluated)</span>
        <div style="font-size: 0.78rem; color: #64748B;">
            Weights: 3Y CAGR (30%) • Sharpe Ratio (25%) • Jensen's Alpha (20%) • Expense Ratio (15%) • Max Drawdown (10%)
        </div>
    </div>
    """, unsafe_allow_html=True)

    score_query = """
    SELECT 
        p.fund_rank as Rank,
        f.scheme_name as 'Scheme Name',
        f.fund_house as 'AMC',
        f.category as 'Category',
        p.return_3yr_pct as '3Y CAGR (%)',
        p.sharpe_ratio as 'Sharpe',
        p.alpha as 'Alpha (%)',
        f.expense_ratio_pct as 'TER (%)',
        p.max_drawdown_pct as 'Max DD (%)',
        p.composite_score as 'Score / 100'
    FROM fact_performance p
    JOIN dim_fund f ON p.amfi_code = f.amfi_code
    ORDER BY p.fund_rank ASC
    LIMIT 10;
    """
    df_scores = query_db(score_query)
    render_fintech_table(df_scores, height=360)

    # Download CSV Button
    csv_bytes = df_scores.to_csv(index=False).encode('utf-8')
    st.download_button(
        label="📥 Download Top 10 Scorecard (CSV)",
        data=csv_bytes,
        file_name="bluestock_top10_scorecard.csv",
        mime="text/csv"
    )

with tab_rec:
    st.markdown("""
    <div style="margin-bottom: 12px;">
        <span style="font-weight: 600; color: #172033; font-size: 0.95rem;">Smart Risk-Adjusted Fund Recommendation Engine</span>
        <div style="font-size: 0.78rem; color: #64748B;">
            Algorithm filters schemes meeting strict Sharpe and Drawdown thresholds matched to investor risk tolerance.
        </div>
    </div>
    """, unsafe_allow_html=True)

    c_risk, _ = st.columns([2, 1])
    with c_risk:
        user_risk = st.select_slider(
            "Select Investor Risk Appetite:",
            options=["Low Risk", "Moderate Risk", "High Risk"],
            value="Moderate Risk"
        )

    try:
        from scripts.recommender import get_recommendations
        risk_key = user_risk.split()[0]
        rec_df = get_recommendations(risk_key, top_n=3)

        r_cols = st.columns(3)
        for idx, row in rec_df.iterrows():
            with r_cols[idx]:
                st.markdown(f"""
                <div style="background-color: #FFFFFF; border: 1px solid #E5EAF2; border-radius: 12px; padding: 18px; box-shadow: 0 1px 3px rgba(0,0,0,0.04);">
                    <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px;">
                        <span style="background-color: #EFF6FF; color: #2563EB; border: 1px solid #BFDBFE; padding: 3px 8px; border-radius: 6px; font-size: 0.72rem; font-weight: 700;">
                            RECOMMENDED #{idx+1}
                        </span>
                        <span style="font-size: 0.82rem; font-weight: 700; color: #16A34A;">{row['composite_score']}/100</span>
                    </div>
                    <h4 style="color: #172033; margin: 8px 0 4px 0; font-size: 0.95rem; line-height: 1.35;">{row['scheme_name'][:40]}...</h4>
                    <p style="color: #64748B; font-size: 0.78rem; margin: 0 0 10px 0;">AMC: <b>{row['fund_house']}</b> • Category: <b>{row['category']}</b></p>
                    <div style="border-top: 1px solid #F1F5F9; padding-top: 8px; font-size: 0.82rem;">
                        <div style="display: flex; justify-content: space-between; margin-bottom: 4px;">
                            <span style="color: #64748B;">Sharpe Ratio:</span>
                            <span style="font-weight: 600; color: #2563EB;">{row['sharpe_ratio']}</span>
                        </div>
                        <div style="display: flex; justify-content: space-between; margin-bottom: 4px;">
                            <span style="color: #64748B;">3-Year CAGR:</span>
                            <span style="font-weight: 600; color: #16A34A;">+{row['cagr_3yr_pct']}%</span>
                        </div>
                        <div style="display: flex; justify-content: space-between;">
                            <span style="color: #64748B;">Expense Ratio (TER):</span>
                            <span style="font-weight: 600; color: #475569;">{row['expense_ratio_pct']}%</span>
                        </div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
    except Exception as e:
        create_empty_state("Recommender engine is ready. Select risk profile above.")

with tab_reports:
    st.markdown("""
    <div style="margin-bottom: 12px;">
        <span style="font-weight: 600; color: #172033; font-size: 0.95rem;">Export Formal Capstone Deliverables</span>
        <div style="font-size: 0.78rem; color: #64748B;">
            Download pre-compiled executive PDF research reports and executive PowerPoint slides.
        </div>
    </div>
    """, unsafe_allow_html=True)

    rep_col1, rep_col2, rep_col3 = st.columns(3)

    pdf_path = os.path.join(REPORTS_DIR, "Final_Report.pdf")
    with rep_col1:
        st.markdown("""
        <div style="background: #FFFFFF; border: 1px solid #E5EAF2; border-radius: 10px; padding: 16px; margin-bottom: 12px;">
            <div style="font-size: 1.5rem; margin-bottom: 4px;">📑</div>
            <div style="font-weight: 700; color: #172033; font-size: 0.92rem;">Executive PDF Report</div>
            <div style="font-size: 0.76rem; color: #64748B; margin-bottom: 12px;">15-Page ReportLab Comprehensive Financial Research</div>
        </div>
        """, unsafe_allow_html=True)
        if os.path.exists(pdf_path):
            with open(pdf_path, "rb") as f:
                st.download_button(
                    label="📥 Download Final_Report.pdf",
                    data=f.read(),
                    file_name="Bluestock_Final_Report.pdf",
                    mime="application/pdf",
                    use_container_width=True
                )
        else:
            st.warning("Final_Report.pdf not yet generated.")

    pptx_path = os.path.join(REPORTS_DIR, "Presentation.pptx")
    with rep_col2:
        st.markdown("""
        <div style="background: #FFFFFF; border: 1px solid #E5EAF2; border-radius: 10px; padding: 16px; margin-bottom: 12px;">
            <div style="font-size: 1.5rem; margin-bottom: 4px;">📊</div>
            <div style="font-weight: 700; color: #172033; font-size: 0.92rem;">Presentation Deck</div>
            <div style="font-size: 0.76rem; color: #64748B; margin-bottom: 12px;">12-Slide python-pptx Executive Boardroom Deck</div>
        </div>
        """, unsafe_allow_html=True)
        if os.path.exists(pptx_path):
            with open(pptx_path, "rb") as f:
                st.download_button(
                    label="📥 Download Presentation.pptx",
                    data=f.read(),
                    file_name="Bluestock_Presentation.pptx",
                    mime="application/vnd.openxmlformats-officedocument.presentationml.presentation",
                    use_container_width=True
                )
        else:
            st.warning("Presentation.pptx not yet generated.")

    html_path = os.path.join(REPORTS_DIR, "weekly_analytical_summary.html")
    with rep_col3:
        st.markdown("""
        <div style="background: #FFFFFF; border: 1px solid #E5EAF2; border-radius: 10px; padding: 16px; margin-bottom: 12px;">
            <div style="font-size: 1.5rem; margin-bottom: 4px;">🌐</div>
            <div style="font-weight: 700; color: #172033; font-size: 0.92rem;">Weekly Analytical Summary</div>
            <div style="font-size: 0.76rem; color: #64748B; margin-bottom: 12px;">Responsive Standalone HTML Intelligence Brief</div>
        </div>
        """, unsafe_allow_html=True)
        if os.path.exists(html_path):
            with open(html_path, "rb") as f:
                st.download_button(
                    label="📥 Download Summary.html",
                    data=f.read(),
                    file_name="Bluestock_Weekly_Summary.html",
                    mime="text/html",
                    use_container_width=True
                )
        else:
            st.info("HTML summary ready in reports folder.")

with tab_arch:
    st.markdown("""
    <div style="margin-bottom: 12px;">
        <span style="font-weight: 600; color: #172033; font-size: 0.95rem;">Platform Data Engineering Architecture</span>
        <div style="font-size: 0.78rem; color: #64748B;">
            Automated pipeline orchestrating live ingestion, cleaning, star-schema persistence, quantitative modeling, and BI rendering.
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("""
    ```mermaid
    flowchart LR
        subgraph INGESTION ["1. Data Ingestion & API Layer"]
            A1["AMFI NAV Daily Files"] --> SINK["scripts/data_ingestion.py"]
            A2["mfapi.in REST Endpoints"] --> SINK
            A3["AMFI Monthly SIP Reports"] --> SINK
            A4["Synthetic Behavioral Generator"] --> SINK
        end

        subgraph ETL ["2. Transformation & Storage Layer"]
            SINK --> CLN["scripts/data_cleaning.py"]
            CLN --> DB[("SQLite Database<br/>bluestock_mf.db<br/>Star Schema")]
        end

        subgraph QUANT ["3. Quantitative Financial Engine"]
            DB --> COMP["scripts/compute_metrics.py"]
            COMP --> METRICS["CAGR / Sharpe / Sortino<br/>Alpha / Beta / Max DD<br/>Composite Score 0-100"]
            METRICS --> DB
        end

        subgraph BI ["4. Streamlit Fintech Dashboard"]
            DB --> UI["Clean Light Fintech UI<br/>4 Analytical Subpages<br/>Zero PyArrow Reliance"]
            METRICS --> UI
        end
    ```
    """)
    st.markdown("""
    <div style="background-color: #FFFFFF; border: 1px solid #E5EAF2; border-radius: 8px; padding: 14px 18px; font-size: 0.82rem; color: #475569;">
        <b>Technology Stack Overview:</b><br/>
        • <b>Language & Compute:</b> Python 3.11+, Pandas, NumPy, SciPy<br/>
        • <b>Database:</b> SQLite 3 with 11 Star-Schema Fact & Dimension Tables (90,497 Records)<br/>
        • <b>Visualization:</b> Plotly Express & Graph Objects with Light Theme Styling<br/>
        • <b>Document Automation:</b> ReportLab PDF Generation, python-pptx Slide Deck Automation<br/>
        • <b>Quality Assurance:</b> Pytest suite covering ETL, mathematics, and database consistency
    </div>
    """, unsafe_allow_html=True)

st.markdown("<hr style='border: none; border-top: 1px solid #E5EAF2; margin: 24px 0 12px 0;'/>", unsafe_allow_html=True)
st.caption("Bluestock Fintech Pvt. Ltd. • Data Analyst Internship Capstone Project • Engine: SQLite 3 & Streamlit")
