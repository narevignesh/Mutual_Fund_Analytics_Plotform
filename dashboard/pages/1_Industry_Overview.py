"""
Bluestock Fintech - Mutual Fund Analytics Platform
Page 1: Industry Overview
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
ROOT_DIR = os.path.abspath(os.path.join(CURRENT_DIR, "..", ".."))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

from dashboard.utils import (
    apply_global_styles, render_sidebar, render_global_header, render_disclaimer,
    ensure_pipeline_ready, query_db, style_plot, render_fintech_table,
    get_industry_metrics, format_currency, create_kpi_card, create_section_header,
    create_empty_state
)

st.set_page_config(
    page_title="Industry Overview | Bluestock Fintech",
    page_icon="🏢",
    layout="wide",
    initial_sidebar_state="expanded"
)

ensure_pipeline_ready()
apply_global_styles()

# Sidebar Navigation & Filter Controls
render_sidebar(current_page="Industry Overview")

with st.sidebar:
    st.markdown("### 🎛️ Industry Filters")
    
    # 1. Fund House Multiselect (Defensive fallback)
    raw_fhs = query_db("SELECT DISTINCT fund_house FROM fact_aum ORDER BY fund_house")["fund_house"].dropna().tolist()
    all_fh_opts = ["All Fund Houses"] + raw_fhs
    sel_fh = st.multiselect("Select Fund Houses", all_fh_opts, default=["All Fund Houses"])
    
    # 2. Benchmark Year Selectbox
    years = query_db("SELECT DISTINCT year FROM fact_aum ORDER BY year")["year"].dropna().tolist()
    sel_year = st.selectbox("Select Calendar Year", ["All Years"] + years, index=0)

    # 3. Quarter Filter
    quarters = ["All Quarters", "Q1", "Q2", "Q3", "Q4"]
    sel_qtr = st.selectbox("Select Quarter", quarters, index=0)
    
    st.markdown("<hr style='border: none; border-top: 1px solid #E5EAF2; margin: 15px 0;'/>", unsafe_allow_html=True)

# Institutional Header
render_global_header(
    page_title="Indian Mutual Fund Industry Overview",
    page_subtitle="Macro-level asset growth, AMC market concentration, folio expansion, and systematic mobilization.",
    breadcrumb_page="Industry Overview"
)

render_disclaimer()

# --- 1. TOP KPI METRIC CARDS (5 METRICS) ---
ind = get_industry_metrics()

kpi_c1, kpi_c2, kpi_c3, kpi_c4, kpi_c5 = st.columns(5)
with kpi_c1:
    create_kpi_card(
        title="Total Industry AUM",
        value=format_currency(ind["total_aum_crore"]),
        delta="Q4 2025 Peak",
        delta_color="positive",
        subtitle="Across All AMCs",
        icon="🏛️"
    )

with kpi_c2:
    create_kpi_card(
        title="Monthly SIP Inflow",
        value=f"₹{ind['monthly_sip_crore']:,.0f} Cr",
        delta="+24.8% YoY",
        delta_color="positive",
        subtitle="Dec 2025 Record",
        icon="📈"
    )

with kpi_c3:
    create_kpi_card(
        title="Total Folios",
        value=f"{ind['total_folios_crore']:.2f} Cr",
        delta="Equity Dominant (69%)",
        delta_color="positive",
        subtitle="Investor Accounts",
        icon="📑"
    )

with kpi_c4:
    create_kpi_card(
        title="Number of Schemes",
        value=f"{ind['active_schemes']}",
        delta="AMFI Universe",
        delta_color="positive",
        subtitle="Direct & Growth",
        icon="⚡"
    )

with kpi_c5:
    create_kpi_card(
        title="Active Fund Houses",
        value=f"{ind['total_amcs']}",
        delta="Tier-1 AMCs",
        delta_color="positive",
        subtitle="Institutional Scale",
        icon="🏢"
    )

st.markdown("<div style='height: 14px;'></div>", unsafe_allow_html=True)

# --- 2. EXECUTIVE MACRO INSIGHTS SUMMARY ---
st.markdown("""
<div style="background-color: #FFFFFF; border: 1px solid #E5EAF2; border-radius: 12px; padding: 14px 18px; box-shadow: 0 1px 3px rgba(0,0,0,0.04); margin-bottom: 20px;">
    <div style="font-size: 0.84rem; font-weight: 700; color: #172033; margin-bottom: 6px; display: flex; align-items: center; gap: 6px;">
        <span style="color: #2563EB;">📌</span> MACRO INDUSTRY HIGHLIGHTS & KEY TAKEAWAYS
    </div>
    <div style="font-size: 0.80rem; color: #475569; line-height: 1.5;">
        • <b>Rapid Capital Accumulation:</b> Indian Mutual Fund industry AUM grew from ₹37.5 Lakh Cr in early 2022 to an all-time peak of <b>₹66.85 Lakh Cr</b> by Q4 2025, recording an annualized growth rate exceeding 18.5%.<br/>
        • <b>High Industry Concentration:</b> The top 3 AMCs (SBI, ICICI Prudential, and HDFC) account for <b>42.1%</b> of total industry AUM, reflecting significant scale advantages in retail distribution.<br/>
        • <b>Equity Inflow Pivot:</b> Equity mutual fund folios doubled from 6.3 Cr in 2020 to <b>14.1 Cr</b> in 2025, catalyzed by digital onboarding platforms and rising domestic participation.
    </div>
</div>
""", unsafe_allow_html=True)

# Build Filter Clauses Defensively
where_conditions = []
if "All Fund Houses" not in sel_fh and len(sel_fh) > 0:
    clean_fhs = [f.replace("'", "''") for f in sel_fh if f]
    fh_str = "','".join(clean_fhs)
    where_conditions.append(f"fund_house IN ('{fh_str}')")

if sel_year != "All Years":
    where_conditions.append(f"year = {int(sel_year)}")

if sel_qtr != "All Quarters":
    where_conditions.append(f"quarter = '{sel_qtr}'")

filter_clause = "WHERE " + " AND ".join(where_conditions) if where_conditions else ""

# --- 3. VISUALIZATION ROW 1: AUM TREND & TOP 10 AMCS ---
create_section_header("Asset Progression & AMC Concentration")

row1_col1, row1_col2 = st.columns(2)

with row1_col1:
    aum_trend_df = query_db(f"""
        SELECT year || ' ' || quarter as period, SUM(aum_crore) / 1000.0 as total_aum_thousand_cr
        FROM fact_aum
        {filter_clause}
        GROUP BY year, quarter
        ORDER BY year, quarter;
    """)
    if not aum_trend_df.empty:
        fig_aum_trend = px.area(
            aum_trend_df, x="period", y="total_aum_thousand_cr",
            labels={"period": "Quarter", "total_aum_thousand_cr": "AUM (₹ Thousand Cr)"},
            color_discrete_sequence=["#2563EB"]
        )
        fig_aum_trend.update_traces(
            line=dict(width=2.5, color="#2563EB"),
            fillcolor="rgba(37, 99, 235, 0.12)"
        )
        fig_aum_trend = style_plot(fig_aum_trend, "1. Quarterly Industry AUM Progression (2022–2025)", height=370)
        st.plotly_chart(fig_aum_trend, use_container_width=True)
    else:
        create_empty_state("No AUM data matching the current filter selection.")

with row1_col2:
    amc_peak_df = query_db("""
        SELECT fund_house, MAX(aum_crore) / 1000.0 as peak_aum_thousand_cr
        FROM fact_aum
        GROUP BY fund_house
        ORDER BY peak_aum_thousand_cr ASC;
    """)
    if not amc_peak_df.empty:
        fig_top_amcs = px.bar(
            amc_peak_df, y="fund_house", x="peak_aum_thousand_cr", orientation="h",
            labels={"fund_house": "AMC", "peak_aum_thousand_cr": "Peak AUM (₹ Thousand Cr)"},
            color="peak_aum_thousand_cr",
            color_continuous_scale=[[0, "#93C5FD"], [1, "#1D4ED8"]]
        )
        fig_top_amcs = style_plot(fig_top_amcs, "2. Peak Assets Under Management by Fund House", height=370)
        fig_top_amcs.update_layout(coloraxis_showscale=False)
        st.plotly_chart(fig_top_amcs, use_container_width=True)
    else:
        create_empty_state("No AMC peak data found.")

# --- 4. VISUALIZATION ROW 2: MARKET SHARE DONUT & AMC TRAJECTORY ---
create_section_header("Market Share Dynamics & Fund House Growth")

row2_col1, row2_col2 = st.columns(2)

with row2_col1:
    market_share_df = query_db("""
        SELECT fund_house, SUM(aum_crore) as latest_aum
        FROM fact_aum
        WHERE (year, quarter) = (SELECT MAX(year), MAX(quarter) FROM fact_aum)
        GROUP BY fund_house
        ORDER BY latest_aum DESC;
    """)
    if not market_share_df.empty:
        fig_donut = px.pie(
            market_share_df, values="latest_aum", names="fund_house",
            hole=0.48,
            color_discrete_sequence=['#2563EB', '#0D9488', '#F59E0B', '#8B5CF6', '#EC4899', '#06B6D4']
        )
        fig_donut.update_traces(
            textposition='inside',
            textinfo='percent+label',
            hovertemplate='<b>%{label}</b><br>AUM: ₹%{value:,.0f} Cr<br>Market Share: %{percent}<extra></extra>'
        )
        fig_donut = style_plot(fig_donut, "3. AMC Market Share Distribution (Q4 2025)", height=370)
        st.plotly_chart(fig_donut, use_container_width=True)
    else:
        create_empty_state("Market share data unavailable.")

with row2_col2:
    fh_trend_df = query_db("""
        SELECT year || ' ' || quarter as period, fund_house, aum_crore / 1000.0 as aum_thousand_cr
        FROM fact_aum
        ORDER BY year, quarter;
    """)
    if not fh_trend_df.empty:
        # If user filtered specific AMCs, highlight them
        if "All Fund Houses" not in sel_fh and len(sel_fh) > 0:
            fh_trend_df = fh_trend_df[fh_trend_df["fund_house"].isin(sel_fh)]
        
        fig_fh_trend = px.line(
            fh_trend_df, x="period", y="aum_thousand_cr", color="fund_house", markers=True,
            labels={"period": "Quarter", "aum_thousand_cr": "AUM (₹ Thousand Cr)", "fund_house": "AMC"},
            color_discrete_sequence=['#2563EB', '#0D9488', '#F59E0B', '#8B5CF6', '#EC4899', '#06B6D4']
        )
        fig_fh_trend = style_plot(fig_fh_trend, "4. AMC Quarter-on-Quarter Growth Trajectory", height=370)
        st.plotly_chart(fig_fh_trend, use_container_width=True)
    else:
        create_empty_state("AMC trajectory data unavailable.")

# --- 5. VISUALIZATION ROW 3: FOLIO EXPANSION & CATEGORY INFLOWS ---
create_section_header("Folio Count Expansion & Asset Class Inflows")

row3_col1, row3_col2 = st.columns(2)

with row3_col1:
    folios_df = query_db("SELECT * FROM fact_industry_folios ORDER BY month")
    if not folios_df.empty:
        fig_folios = px.area(
            folios_df, x="month", y=["equity_folios_crore", "debt_folios_crore", "hybrid_folios_crore"],
            labels={"value": "Folios (Crores)", "month": "Milestone Date", "variable": "Asset Class"},
            color_discrete_map={
                "equity_folios_crore": "#16A34A",
                "debt_folios_crore": "#2563EB",
                "hybrid_folios_crore": "#8B5CF6"
            }
        )
        fig_folios.update_traces(opacity=0.8)
        fig_folios = style_plot(fig_folios, "5. Folio Expansion by Asset Class (2020–2025)", height=370)
        st.plotly_chart(fig_folios, use_container_width=True)
    else:
        create_empty_state("Folio data unavailable.")

with row3_col2:
    cat_inflows_df = query_db("""
        SELECT category, SUM(net_inflow_crore) as cumulative_inflow_cr
        FROM fact_category_inflows
        GROUP BY category
        ORDER BY cumulative_inflow_cr DESC;
    """)
    if not cat_inflows_df.empty:
        fig_cat_inflow = px.bar(
            cat_inflows_df, x="category", y="cumulative_inflow_cr",
            labels={"category": "Asset Category", "cumulative_inflow_cr": "Net Inflow (₹ Cr)"},
            color="cumulative_inflow_cr",
            color_continuous_scale=[[0, "#A7F3D0"], [1, "#059669"]]
        )
        fig_cat_inflow = style_plot(fig_cat_inflow, "6. Cumulative Net Mobilization by Category", height=370)
        fig_cat_inflow.update_layout(coloraxis_showscale=False)
        st.plotly_chart(fig_cat_inflow, use_container_width=True)
    else:
        create_empty_state("Category inflow data unavailable.")

# --- 6. AMC COMPREHENSIVE RANKING TABLE ---
create_section_header("Institutional AMC Market Share & Scale Leaderboard")

amc_table_query = """
SELECT 
    fund_house as 'Fund House',
    MAX(scheme_count) as 'Active Schemes',
    ROUND(MIN(aum_crore), 2) as '2022 Base AUM (₹ Cr)',
    ROUND(MAX(aum_crore), 2) as 'Peak AUM (₹ Cr)',
    ROUND(((MAX(aum_crore) - MIN(aum_crore)) / MIN(aum_crore)) * 100.0, 1) as '3Y Growth (%)',
    ROUND((MAX(aum_crore) / (SELECT SUM(aum_crore) FROM fact_aum WHERE (year, quarter) = (SELECT MAX(year), MAX(quarter) FROM fact_aum))) * 100.0, 2) as 'Market Share (%)'
FROM fact_aum
GROUP BY fund_house
ORDER BY MAX(aum_crore) DESC;
"""
df_amc_table = query_db(amc_table_query)
render_fintech_table(df_amc_table, height=360)

# Export Filtered Data
st.markdown("<div style='height: 8px;'></div>", unsafe_allow_html=True)
col_dl1, col_dl2 = st.columns([1, 3])
with col_dl1:
    if not df_amc_table.empty:
        csv_data = df_amc_table.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="📥 Download AMC Leaderboard (CSV)",
            data=csv_data,
            file_name="amc_market_share_leaderboard.csv",
            mime="text/csv"
        )

st.markdown("<hr style='border: none; border-top: 1px solid #E5EAF2; margin: 24px 0 12px 0;'/>", unsafe_allow_html=True)
st.caption("Bluestock Fintech Pvt. Ltd. • Industry Overview • Source: AMFI Monthly & Quarterly Disclosure Data")
