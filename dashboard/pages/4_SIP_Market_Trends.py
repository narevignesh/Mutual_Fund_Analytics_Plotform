"""
Bluestock Fintech - Mutual Fund Analytics Platform
Page 4: Monthly SIP & Market Benchmark Trends
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
    get_sip_metrics, format_currency, create_kpi_card, create_section_header,
    create_empty_state
)

st.set_page_config(
    page_title="SIP & Market Trends | Bluestock Fintech",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded"
)

ensure_pipeline_ready()
apply_global_styles()

# Sidebar Navigation & Trend Filters
render_sidebar(current_page="SIP & Market Trends")

with st.sidebar:
    st.markdown("### 🎛️ Market & SIP Filters")
    
    # 1. Year Filter (Safe substring extraction from 'YYYY-MM')
    raw_years = query_db("SELECT DISTINCT substr(month, 1, 4) as yr FROM fact_sip_industry ORDER BY yr")["yr"].dropna().tolist()
    sip_years = [str(y) for y in raw_years if str(y).strip()]
    sel_years = st.multiselect("Calendar Years", sip_years, default=sip_years)
    
    # 2. Benchmark Index Multiselect
    b_names = query_db("SELECT DISTINCT index_name FROM fact_benchmark_indices ORDER BY index_name")["index_name"].dropna().tolist()
    default_benchmarks = [b for b in ["Nifty 50", "Nifty Midcap 150", "BSE SmallCap", "CRISIL Liquid"] if b in b_names]
    sel_benchmarks = st.multiselect("Select Benchmarks", b_names, default=default_benchmarks if default_benchmarks else b_names[:4])
    
    # 3. Category Inflows Filter
    cats = query_db("SELECT DISTINCT category FROM fact_category_inflows ORDER BY category")["category"].dropna().tolist()
    default_cats = [c for c in ["Large Cap", "Mid Cap", "Small Cap", "Flexi Cap", "Hybrid"] if c in cats]
    sel_cats = st.multiselect("Categories for Inflow Analysis", cats, default=default_cats if default_cats else cats[:5])

    st.markdown("<hr style='border: none; border-top: 1px solid #E5EAF2; margin: 15px 0;'/>", unsafe_allow_html=True)

# Institutional Header
render_global_header(
    page_title="Systematic Investment Plan (SIP) & Market Trends",
    page_subtitle="National retail savings mobilization, macroeconomic SIP expansion, benchmark indices, and category liquidity flows.",
    breadcrumb_page="SIP & Market Trends"
)

render_disclaimer()

# --- 1. TOP 4 SIP KPI METRIC CARDS ---
sip_m = get_sip_metrics()

k1, k2, k3, k4 = st.columns(4)
with k1:
    create_kpi_card(
        title="Monthly SIP Inflow",
        value=f"₹{sip_m['inflow_crore']:,.0f} Cr",
        delta="Dec 2025 AMFI Record",
        delta_color="positive",
        subtitle="Gross Inflow",
        icon="📈"
    )

with k2:
    create_kpi_card(
        title="Active SIP Accounts",
        value=f"{sip_m['active_accounts_crore']:.2f} Cr",
        delta="+85% Since 2022",
        delta_color="positive",
        subtitle="Retail Systematic",
        icon="💳"
    )

with k3:
    create_kpi_card(
        title="Cumulative SIP AUM",
        value=f"₹{sip_m['sip_aum_lakh_crore']:.2f} Lakh Cr",
        delta="22.1% of Total AUM",
        delta_color="positive",
        subtitle="Retail Assets",
        icon="🏛️"
    )

with k4:
    create_kpi_card(
        title="YoY SIP Growth",
        value=f"+{sip_m['yoy_growth_pct']:.1f}%",
        delta="Annual Acceleration",
        delta_color="positive",
        subtitle="Structural Compounding",
        icon="🚀"
    )

st.markdown("<div style='height: 14px;'></div>", unsafe_allow_html=True)

# --- 2. EXECUTIVE SIP INSIGHTS BOX ---
st.markdown("""
<div style="background-color: #FFFFFF; border: 1px solid #E5EAF2; border-radius: 12px; padding: 14px 18px; box-shadow: 0 1px 3px rgba(0,0,0,0.04); margin-bottom: 20px;">
    <div style="font-size: 0.84rem; font-weight: 700; color: #172033; margin-bottom: 6px; display: flex; align-items: center; gap: 6px;">
        <span style="color: #2563EB;">📌</span> SYSTEMATIC INVESTMENT PLAN (SIP) MACRO SUMMARY
    </div>
    <div style="font-size: 0.80rem; color: #475569; line-height: 1.5;">
        • <b>Structural Retail Financialization:</b> Monthly SIP inflows expanded from ₹11,591 Cr in Jan 2022 to an unprecedented <b>₹31,002 Cr</b> in Dec 2025, resisting secondary market volatility.<br/>
        • <b>Account Proliferation:</b> Active SIP accounts grew from 5.05 Cr to <b>9.35 Cr</b> (+85.1%), driven by seamless automated mandates and micro-SIP allocations.<br/>
        • <b>Benchmark Decoupling:</b> Nifty Midcap 150 and BSE SmallCap indices significantly outperformed Nifty 50 over 2022–2025, directing heavy institutional and retail flows into Mid and Small-Cap schemes.
    </div>
</div>
""", unsafe_allow_html=True)

# Defensive SQL Year Filtering
clean_years = [str(y) for y in sel_years if y is not None and str(y).strip()]
if not clean_years:
    clean_years = sip_years

yrs_str = "','".join(clean_years)
year_filter_sql = f"WHERE substr(month, 1, 4) IN ('{yrs_str}')"

df_sip_filtered = query_db(f"SELECT * FROM fact_sip_industry {year_filter_sql} ORDER BY month ASC")

if df_sip_filtered.empty:
    create_empty_state("No SIP records match the chosen calendar year filter.")
    st.stop()

# --- 3. VISUALIZATION ROW 1: SIP INFLOW TRAJECTORY & BENCHMARK INDEX TRENDS ---
create_section_header("Systematic Mobilization & Benchmark Performance")

row1_col1, row1_col2 = st.columns(2)

with row1_col1:
    fig_sip = px.bar(
        df_sip_filtered, x="month", y="sip_inflow_crore",
        labels={"month": "Month", "sip_inflow_crore": "Inflow (₹ Cr)"},
        color="sip_inflow_crore",
        color_continuous_scale=[[0, "#A7F3D0"], [1, "#0D9488"]]
    )
    # Milestone annotation for peak month
    if "2025-12" in df_sip_filtered["month"].values:
        fig_sip.add_annotation(
            x="2025-12", y=31002.0, text="Peak: ₹31,002 Cr",
            showarrow=True, arrowhead=2, arrowcolor="#2563EB",
            font=dict(color="#2563EB", size=10, family="Inter")
        )
    fig_sip = style_plot(fig_sip, "1. Monthly SIP Inflow Expansion Trajectory (2022–2025)", height=370)
    fig_sip.update_layout(coloraxis_showscale=False)
    st.plotly_chart(fig_sip, use_container_width=True)

with row1_col2:
    if sel_benchmarks:
        clean_bmk = [b.replace("'", "''") for b in sel_benchmarks if b]
        b_str = "','".join(clean_bmk)
        df_bench = query_db(f"SELECT * FROM fact_benchmark_indices WHERE index_name IN ('{b_str}') ORDER BY date ASC")
        
        if not df_bench.empty:
            bench_norm_list = []
            for b_name, group in df_bench.groupby("index_name"):
                g = group.sort_values("date").copy()
                g["normalized"] = (g["close_value"] / g["close_value"].iloc[0]) * 100.0
                bench_norm_list.append(g)
                
            df_bench_norm = pd.concat(bench_norm_list, ignore_index=True) if bench_norm_list else pd.DataFrame()
            fig_bench = px.line(
                df_bench_norm, x="date", y="normalized", color="index_name",
                labels={"date": "Date", "normalized": "Index Base (100)", "index_name": "Benchmark"},
                color_discrete_sequence=['#2563EB', '#0D9488', '#F59E0B', '#8B5CF6', '#EC4899', '#10B981']
            )
            fig_bench = style_plot(fig_bench, "2. Market Benchmark Indices Normalized Performance (Base = 100)", height=370)
            st.plotly_chart(fig_bench, use_container_width=True)
        else:
            create_empty_state("No data found for selected benchmarks.")
    else:
        st.info("Select at least one benchmark index from the sidebar.")

# --- 4. VISUALIZATION ROW 2: CATEGORY NET INFLOWS & DENSITY HEATMAP ---
create_section_header("Cross-Category Net Flow Dynamics & Liquidity Density")

row2_col1, row2_col2 = st.columns(2)

with row2_col1:
    if sel_cats:
        clean_c = [c.replace("'", "''") for c in sel_cats if c]
        cat_str = "','".join(clean_c)
        df_cat = query_db(f"SELECT * FROM fact_category_inflows WHERE category IN ('{cat_str}') ORDER BY month ASC")
        if not df_cat.empty:
            fig_cat = px.line(
                df_cat, x="month", y="net_inflow_crore", color="category", markers=True,
                labels={"month": "Month", "net_inflow_crore": "Net Inflow (₹ Cr)", "category": "Category"},
                color_discrete_sequence=['#2563EB', '#0D9488', '#F59E0B', '#8B5CF6', '#EC4899', '#10B981']
            )
            fig_cat = style_plot(fig_cat, "3. Category-Wise Monthly Net Inflow Mobilization", height=370)
            st.plotly_chart(fig_cat, use_container_width=True)
        else:
            create_empty_state("No category inflow records found.")
    else:
        st.info("Select categories from sidebar to inspect net flows.")

with row2_col2:
    df_all_cat = query_db("SELECT month, category, net_inflow_crore FROM fact_category_inflows ORDER BY month ASC")
    if not df_all_cat.empty:
        cat_matrix = df_all_cat.pivot_table(index="category", columns="month", values="net_inflow_crore", aggfunc="mean")
        fig_heat = px.imshow(
            cat_matrix, color_continuous_scale="Blues", aspect="auto",
            labels=dict(x="Month", y="Category", color="Net Inflow (₹ Cr)")
        )
        fig_heat = style_plot(fig_heat, "4. Category Net Flow Intensity Heatmap", height=370)
        st.plotly_chart(fig_heat, use_container_width=True)
    else:
        create_empty_state("Cross-category matrix data unavailable.")

# --- 5. VISUALIZATION ROW 3: TOP CATEGORIES & ACCOUNT VELOCITY ---
create_section_header("Category Cumulative Rankings & Retail Account Growth")

row3_col1, row3_col2 = st.columns(2)

with row3_col1:
    if not df_all_cat.empty:
        top_cat_agg = df_all_cat.groupby("category")["net_inflow_crore"].sum().reset_index()
        top_cat_agg = top_cat_agg.sort_values("net_inflow_crore", ascending=True)
        fig_top_cat = px.bar(
            top_cat_agg, y="category", x="net_inflow_crore", orientation="h",
            labels={"category": "Asset Category", "net_inflow_crore": "Cumulative Net Inflow (₹ Cr)"},
            color="net_inflow_crore",
            color_continuous_scale=[[0, "#A7F3D0"], [1, "#059669"]]
        )
        fig_top_cat = style_plot(fig_top_cat, "5. Cumulative Net Mobilization by Fund Category", height=370)
        fig_top_cat.update_layout(coloraxis_showscale=False)
        st.plotly_chart(fig_top_cat, use_container_width=True)
    else:
        create_empty_state("Category rankings unavailable.")

with row3_col2:
    fig_acc = go.Figure()
    fig_acc.add_trace(go.Scatter(
        x=df_sip_filtered["month"], y=df_sip_filtered["active_sip_accounts_crore"],
        name="Active SIP Accounts (Cr)",
        line=dict(color="#2563EB", width=2.5)
    ))
    fig_acc.add_trace(go.Bar(
        x=df_sip_filtered["month"], y=df_sip_filtered["new_sip_accounts_lakh"] / 100.0,
        name="New Registrations (Cr)",
        marker_color="rgba(245, 158, 11, 0.7)"
    ))
    fig_acc = style_plot(fig_acc, "6. Retail Account Growth Velocity & New Monthly Registrations", height=370)
    st.plotly_chart(fig_acc, use_container_width=True)

# --- 6. VISUALIZATION ROW 4: SIP AUM EXPANSION & BENCHMARK RISK-RETURN ---
create_section_header("Retail Asset Expansion & Benchmark Returns")

row4_col1, row4_col2 = st.columns(2)

with row4_col1:
    fig_aum_sip = px.area(
        df_sip_filtered, x="month", y="sip_aum_lakh_crore",
        labels={"month": "Month", "sip_aum_lakh_crore": "SIP AUM (₹ Lakh Cr)"},
        color_discrete_sequence=["#0D9488"]
    )
    fig_aum_sip.update_traces(
        line=dict(width=2.5, color="#0D9488"),
        fillcolor="rgba(13, 148, 136, 0.12)"
    )
    fig_aum_sip = style_plot(fig_aum_sip, "7. Cumulative SIP Assets Under Management (AUM)", height=370)
    st.plotly_chart(fig_aum_sip, use_container_width=True)

with row4_col2:
    bench_stat_query = """
    SELECT 
        index_name,
        ROUND((EXP(SUM(daily_return_pct / 100.0)) - 1.0) * 100.0, 1) as cumulative_return_pct
    FROM fact_benchmark_indices
    GROUP BY index_name
    ORDER BY cumulative_return_pct DESC;
    """
    df_bmk_stat = query_db(bench_stat_query)
    if not df_bmk_stat.empty:
        fig_bmk_bar = px.bar(
            df_bmk_stat, x="cumulative_return_pct", y="index_name", orientation="h",
            labels={"cumulative_return_pct": "Cumulative Return (%)", "index_name": "Benchmark Index"},
            color="cumulative_return_pct",
            color_continuous_scale=[[0, "#93C5FD"], [1, "#1D4ED8"]]
        )
        fig_bmk_bar = style_plot(fig_bmk_bar, "8. Benchmark Indices Cumulative Return (2022–2025)", height=370)
        fig_bmk_bar.update_layout(coloraxis_showscale=False, yaxis=dict(autorange="reversed"))
        st.plotly_chart(fig_bmk_bar, use_container_width=True)
    else:
        create_empty_state("Benchmark return statistics unavailable.")

# --- 7. MONTHLY SIP INDUSTRY HISTORICAL DATA TABLE ---
create_section_header("Historical Monthly SIP Macroeconomic Time Series")

disp_sip = df_sip_filtered.rename(columns={
    "month": "Month",
    "sip_inflow_crore": "SIP Inflow (₹ Cr)",
    "active_sip_accounts_crore": "Active Accounts (Cr)",
    "new_sip_accounts_lakh": "New Accounts (Lakh)",
    "sip_aum_lakh_crore": "SIP AUM (₹ Lakh Cr)",
    "yoy_growth_pct": "YoY Growth (%)"
})
render_fintech_table(disp_sip, height=360)

# Export Filtered SIP CSV
col_dl1, col_dl2 = st.columns([1, 3])
with col_dl1:
    csv_data = disp_sip.to_csv(index=False).encode('utf-8')
    st.download_button(
        label="📥 Download SIP Time Series (CSV)",
        data=csv_data,
        file_name="monthly_sip_industry_trends.csv",
        mime="text/csv"
    )

st.markdown("<hr style='border: none; border-top: 1px solid #E5EAF2; margin: 24px 0 12px 0;'/>", unsafe_allow_html=True)
st.caption("Bluestock Fintech Pvt. Ltd. • Monthly SIP & Market Benchmark Trends • AMFI Macroeconomic Disclosure Series")
