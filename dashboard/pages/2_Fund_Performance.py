"""
Bluestock Fintech - Mutual Fund Analytics Platform
Page 2: Fund Performance Analytics & Scorecard
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
    get_fund_metrics, create_kpi_card, create_section_header, create_empty_state
)

st.set_page_config(
    page_title="Fund Performance | Bluestock Fintech",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

ensure_pipeline_ready()
apply_global_styles()

# Sidebar Navigation & Filter Controls
render_sidebar(current_page="Fund Performance")

with st.sidebar:
    st.markdown("### 🎛️ Performance Filters")
    
    # 1. Fund House Filter
    fhs = ["All Fund Houses"] + query_db("SELECT DISTINCT fund_house FROM dim_fund ORDER BY fund_house")["fund_house"].dropna().tolist()
    sel_fh = st.selectbox("Fund House", fhs, index=0)
    
    # 2. Category Filter
    cats = ["All Categories"] + query_db("SELECT DISTINCT category FROM dim_fund ORDER BY category")["category"].dropna().tolist()
    sel_cat = st.selectbox("Category", cats, index=0)
    
    # 3. SEBI Risk Profile
    risks = ["All Risk Profiles"] + query_db("SELECT DISTINCT risk_category FROM dim_fund ORDER BY risk_category")["risk_category"].dropna().tolist()
    sel_risk = st.selectbox("SEBI Risk Category", risks, index=0)

    # 4. Plan Filter
    plans = ["All Plans"] + query_db("SELECT DISTINCT plan FROM dim_fund ORDER BY plan")["plan"].dropna().tolist()
    sel_plan = st.selectbox("Plan Type", plans, index=0)

    st.markdown("<hr style='border: none; border-top: 1px solid #E5EAF2; margin: 15px 0;'/>", unsafe_allow_html=True)

# Institutional Header
render_global_header(
    page_title="Mutual Fund Performance & Risk Analytics",
    page_subtitle="Quantitative attribution, risk-adjusted Sharpe/Sortino ratios, benchmark comparison, and multi-factor rankings.",
    breadcrumb_page="Fund Performance"
)

render_disclaimer()

# --- 1. TOP 4 PERFORMANCE KPI CARDS ---
f_metrics = get_fund_metrics()

k1, k2, k3, k4 = st.columns(4)
with k1:
    create_kpi_card(
        title="Best 3Y CAGR",
        value=f"+{f_metrics['best_3yr_cagr']:.2f}%",
        delta="Nippon Small Cap",
        delta_color="positive",
        subtitle="Annualized Return",
        icon="🚀"
    )

with k2:
    create_kpi_card(
        title="Highest Sharpe Ratio",
        value=f"{f_metrics['highest_sharpe']:.2f}",
        delta="Risk-Adjusted Alpha",
        delta_color="positive",
        subtitle="Rf = 6.50%",
        icon="⚖️"
    )

with k3:
    create_kpi_card(
        title="Lowest Expense Ratio",
        value=f"{f_metrics['lowest_ter']:.2f}%",
        delta="Direct Index / Large Cap",
        delta_color="positive",
        subtitle="Low Drag TER",
        icon="🏷️"
    )

with k4:
    create_kpi_card(
        title="Top Composite Score",
        value=f"{f_metrics['best_score']:.1f} / 100",
        delta="Rank #1 Multi-Factor",
        delta_color="positive",
        subtitle="Optimal Balance",
        icon="🏆"
    )

st.markdown("<div style='height: 14px;'></div>", unsafe_allow_html=True)

# Build Query Based on Defensive Filters
where_clauses = []
if sel_fh != "All Fund Houses":
    clean_fh = sel_fh.replace("'", "''")
    where_clauses.append(f"f.fund_house = '{clean_fh}'")
if sel_cat != "All Categories":
    clean_cat = sel_cat.replace("'", "''")
    where_clauses.append(f"f.category = '{clean_cat}'")
if sel_risk != "All Risk Profiles":
    clean_risk = sel_risk.replace("'", "''")
    where_clauses.append(f"f.risk_category = '{clean_risk}'")
if sel_plan != "All Plans":
    clean_plan = sel_plan.replace("'", "''")
    where_clauses.append(f"f.plan = '{clean_plan}'")

where_str = "WHERE " + " AND ".join(where_clauses) if where_clauses else ""

perf_query = f"""
SELECT 
    f.amfi_code,
    f.scheme_name,
    f.fund_house,
    f.category,
    f.plan,
    f.benchmark,
    f.risk_category,
    f.expense_ratio_pct,
    p.return_1yr_pct,
    p.return_3yr_pct,
    p.return_5yr_pct,
    p.benchmark_3yr_pct,
    p.alpha,
    p.beta,
    p.sharpe_ratio,
    p.sortino_ratio,
    p.std_dev_ann_pct,
    p.max_drawdown_pct,
    p.composite_score,
    p.fund_rank,
    p.morningstar_rating
FROM dim_fund f
JOIN fact_performance p ON f.amfi_code = p.amfi_code
{where_str}
ORDER BY p.fund_rank ASC;
"""
df_perf = query_db(perf_query)

if df_perf.empty:
    create_empty_state("No mutual fund schemes match the chosen filter combinations.")
    st.stop()

# --- 2. SINGLE SCHEME DEEP-DIVE RESEARCH TERMINAL ---
create_section_header("Single Scheme Deep-Dive Research Terminal", "Select any scheme to inspect risk factors, benchmark alpha, and asset holdings.")

available_schemes = df_perf["scheme_name"].tolist()
sel_scheme = st.selectbox("🔍 Select Mutual Fund Scheme for In-Depth Attribution:", available_schemes, index=0)

scheme_sub = df_perf[df_perf["scheme_name"] == sel_scheme]
if scheme_sub.empty:
    scheme_sub = df_perf.head(1)

sr = scheme_sub.iloc[0]
amfi_code = int(sr["amfi_code"])
stars_str = "★" * int(sr["morningstar_rating"]) + "☆" * (5 - int(sr["morningstar_rating"]))

# Scheme Header Card
st.markdown(f"""
<div style="background-color: #FFFFFF; border: 1px solid #E5EAF2; border-radius: 12px; padding: 18px 22px; box-shadow: 0 1px 3px rgba(0,0,0,0.04); margin-bottom: 18px;">
    <div style="display: flex; justify-content: space-between; align-items: flex-start; flex-wrap: wrap; gap: 10px;">
        <div>
            <div style="font-size: 0.76rem; color: #64748B; font-weight: 600; text-transform: uppercase;">AMFI Code: {amfi_code} • {sr['plan']} Plan • {sr['risk_category']}</div>
            <h3 style="margin: 4px 0 6px 0; color: #172033; font-size: 1.25rem;">{sr['scheme_name']}</h3>
            <div style="font-size: 0.82rem; color: #475569;">
                AMC: <b style="color: #172033;">{sr['fund_house']}</b> &nbsp;|&nbsp; 
                Category: <b style="color: #172033;">{sr['category']}</b> &nbsp;|&nbsp; 
                Benchmark: <b style="color: #2563EB;">{sr['benchmark']}</b>
            </div>
        </div>
        <div style="text-align: right;">
            <div style="color: #F59E0B; font-size: 1.15rem; letter-spacing: 2px;">{stars_str}</div>
            <div style="font-size: 0.75rem; color: #64748B; margin-top: 2px;">Bluestock Rating</div>
            <div style="font-size: 0.95rem; font-weight: 700; color: #2563EB; margin-top: 4px;">Rank #{sr['fund_rank']} of {len(df_perf)}</div>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

# 9 Micro-KPIs for Selected Scheme
m1, m2, m3, m4, m5, m6, m7, m8, m9 = st.columns(9)
m1.metric("1Y Return", f"{sr['return_1yr_pct']:+.2f}%")
m2.metric("3Y CAGR", f"{sr['return_3yr_pct']:+.2f}%", f"Bmk: {sr['benchmark_3yr_pct']}%")
m3.metric("5Y CAGR", f"{sr['return_5yr_pct']:+.2f}%")
m4.metric("Sharpe", f"{sr['sharpe_ratio']:.2f}")
m5.metric("Sortino", f"{sr['sortino_ratio']:.2f}")
m6.metric("Alpha", f"{sr['alpha']:+.2f}%")
m7.metric("Beta", f"{sr['beta']:.2f}")
m8.metric("Max DD", f"{sr['max_drawdown_pct']:.2f}%")
m9.metric("TER", f"{sr['expense_ratio_pct']:.2f}%")

st.markdown("<div style='height: 14px;'></div>", unsafe_allow_html=True)

# --- 3. VISUALIZATION ROW 1: NAV VS BENCHMARK & SECTOR ALLOCATION ---
row1_col1, row1_col2 = st.columns(2)

with row1_col1:
    nav_df = query_db(f"SELECT date, nav FROM fact_nav WHERE amfi_code = {amfi_code} ORDER BY date ASC")
    clean_bench_name = sr['benchmark'].replace("'", "''")
    bench_df = query_db(f"SELECT date, close_value FROM fact_benchmark_indices WHERE index_name = '{clean_bench_name}' ORDER BY date ASC")
    
    if not nav_df.empty and not bench_df.empty:
        merged = pd.merge(nav_df, bench_df, on="date").dropna()
        if not merged.empty:
            merged["Fund_Norm"] = (merged["nav"] / merged["nav"].iloc[0]) * 100.0
            merged["Bench_Norm"] = (merged["close_value"] / merged["close_value"].iloc[0]) * 100.0
            
            fig_nav_bench = go.Figure()
            fig_nav_bench.add_trace(go.Scatter(
                x=merged["date"], y=merged["Fund_Norm"],
                name=f"Scheme: {sr['scheme_name'][:24]}",
                line=dict(color="#2563EB", width=2.4)
            ))
            fig_nav_bench.add_trace(go.Scatter(
                x=merged["date"], y=merged["Bench_Norm"],
                name=f"Benchmark: {sr['benchmark']}",
                line=dict(color="#F59E0B", width=1.8, dash="dash")
            ))
            fig_nav_bench = style_plot(fig_nav_bench, "1. Normalized Growth vs Benchmark (Base = 100)", height=370)
            st.plotly_chart(fig_nav_bench, use_container_width=True)
        else:
            create_empty_state("No overlapping date records between fund and benchmark.")
    else:
        create_empty_state("Historical NAV time series loading.")

with row1_col2:
    # Portfolio Sector Breakdown for this fund
    sec_df = query_db(f"""
        SELECT sector, SUM(weight_pct) as total_weight
        FROM fact_portfolio
        WHERE amfi_code = {amfi_code}
        GROUP BY sector
        ORDER BY total_weight DESC;
    """)
    if not sec_df.empty:
        fig_sec = px.pie(
            sec_df, values="total_weight", names="sector",
            hole=0.48,
            color_discrete_sequence=['#2563EB', '#0D9488', '#F59E0B', '#8B5CF6', '#EC4899', '#06B6D4', '#10B981']
        )
        fig_sec.update_traces(
            textposition='inside',
            textinfo='percent+label',
            hovertemplate='<b>%{label}</b><br>Weight: %{value:.2f}%<extra></extra>'
        )
        fig_sec = style_plot(fig_sec, "2. Scheme Sector Concentration & Allocation", height=370)
        st.plotly_chart(fig_sec, use_container_width=True)
    else:
        # Fallback to category average if specific portfolio is not in synthetic subset
        top_holdings = query_db(f"""
            SELECT company_name, weight_pct, sector
            FROM fact_portfolio
            WHERE amfi_code = {amfi_code}
            ORDER BY weight_pct DESC
            LIMIT 6;
        """)
        if not top_holdings.empty:
            fig_holdings = px.bar(
                top_holdings, x="weight_pct", y="company_name", orientation="h",
                labels={"company_name": "Company", "weight_pct": "Portfolio Weight (%)"},
                color="weight_pct", color_continuous_scale="Blues"
            )
            fig_holdings = style_plot(fig_holdings, "2. Top Holdings Concentration", height=370)
            st.plotly_chart(fig_holdings, use_container_width=True)
        else:
            create_empty_state("Portfolio holding data mapped to category benchmarks.")

# --- 4. VISUALIZATION ROW 2: RISK-RETURN SCATTER & CATEGORY COMPARISON ---
create_section_header("Universe Risk-Return Attribution & Category Benchmarks")

row2_col1, row2_col2 = st.columns(2)

with row2_col1:
    fig_scatter = px.scatter(
        df_perf, x="std_dev_ann_pct", y="return_3yr_pct",
        color="category", size="composite_score", hover_name="scheme_name",
        labels={"std_dev_ann_pct": "Annualized Volatility (σ %)", "return_3yr_pct": "3-Year CAGR (%)", "composite_score": "Score"},
        color_discrete_sequence=['#2563EB', '#0D9488', '#F59E0B', '#8B5CF6', '#EC4899', '#10B981']
    )
    # Add benchmark quadrant crosshairs
    fig_scatter.add_vline(x=15.0, line_dash="dash", line_color="#CBD5E1")
    fig_scatter.add_hline(y=15.0, line_dash="dash", line_color="#CBD5E1")
    fig_scatter = style_plot(fig_scatter, "3. Risk-Return Positioning (Bubble Size = Composite Score)", height=370)
    st.plotly_chart(fig_scatter, use_container_width=True)

with row2_col2:
    cat_agg = df_perf.groupby("category").agg(
        avg_cagr=("return_3yr_pct", "mean"),
        avg_alpha=("alpha", "mean")
    ).reset_index()
    
    fig_cat_bar = px.bar(
        cat_agg, x="category", y=["avg_cagr", "avg_alpha"], barmode="group",
        labels={"value": "Percentage (%)", "category": "Category", "variable": "Metric"},
        color_discrete_map={"avg_cagr": "#2563EB", "avg_alpha": "#0D9488"}
    )
    fig_cat_bar = style_plot(fig_cat_bar, "4. Average 3Y CAGR vs Jensen's Alpha by Category", height=370)
    st.plotly_chart(fig_cat_bar, use_container_width=True)

# --- 5. VISUALIZATION ROW 3: DRAWDOWN VS SHARPE & TOP RANKINGS ---
row3_col1, row3_col2 = st.columns(2)

with row3_col1:
    fig_dd = px.scatter(
        df_perf, x="max_drawdown_pct", y="sharpe_ratio", color="category",
        hover_name="scheme_name",
        labels={"max_drawdown_pct": "Maximum Drawdown (%)", "sharpe_ratio": "Sharpe Ratio"},
        color_discrete_sequence=['#2563EB', '#0D9488', '#F59E0B', '#8B5CF6', '#EC4899', '#10B981']
    )
    fig_dd = style_plot(fig_dd, "5. Sharpe Ratio vs Downside Drawdown Vulnerability", height=370)
    st.plotly_chart(fig_dd, use_container_width=True)

with row3_col2:
    top10_rank = df_perf.sort_values("composite_score", ascending=True).tail(10)
    fig_rank = px.bar(
        top10_rank, x="composite_score", y="scheme_name", orientation="h",
        color="category",
        labels={"composite_score": "Composite Score (0–100)", "scheme_name": "Scheme"},
        color_discrete_sequence=['#2563EB', '#0D9488', '#F59E0B', '#8B5CF6', '#10B981']
    )
    fig_rank = style_plot(fig_rank, "6. Top Ranked Schemes by Composite Score", height=370)
    st.plotly_chart(fig_rank, use_container_width=True)

# --- 6. MULTI-SCHEME COMPARISON TOOL ---
create_section_header("Multi-Scheme Head-to-Head Comparison Tool", "Select up to 4 schemes to evaluate risk-adjusted metrics side-by-side.")

default_schemes = df_perf["scheme_name"].head(3).tolist()
comp_schemes = st.multiselect(
    "Choose Schemes to Compare (Max 4):",
    options=df_perf["scheme_name"].tolist(),
    default=default_schemes[:3]
)

if comp_schemes:
    comp_df = df_perf[df_perf["scheme_name"].isin(comp_schemes)]
    comp_disp = comp_df[[
        "scheme_name", "category", "fund_house", "return_3yr_pct", 
        "sharpe_ratio", "alpha", "beta", "expense_ratio_pct", "composite_score"
    ]].rename(columns={
        "scheme_name": "Scheme",
        "category": "Category",
        "fund_house": "AMC",
        "return_3yr_pct": "3Y CAGR (%)",
        "sharpe_ratio": "Sharpe",
        "alpha": "Alpha (%)",
        "beta": "Beta",
        "expense_ratio_pct": "TER (%)",
        "composite_score": "Composite Score"
    })
    render_fintech_table(comp_disp, height=220)
else:
    st.info("Select at least one scheme to activate head-to-head comparison.")

# --- 7. COMPLETE FILTERED SCORECARD TABLE ---
create_section_header("Complete Filtered Multi-Factor Performance Scorecard")

display_cols = [
    "fund_rank", "scheme_name", "category", "fund_house", "return_1yr_pct",
    "return_3yr_pct", "return_5yr_pct", "sharpe_ratio", "alpha", "beta",
    "expense_ratio_pct", "max_drawdown_pct", "composite_score"
]
clean_df = df_perf[display_cols].rename(columns={
    "fund_rank": "Rank", "scheme_name": "Scheme Name", "category": "Category",
    "fund_house": "AMC", "return_1yr_pct": "1Y Return (%)", "return_3yr_pct": "3Y CAGR (%)",
    "return_5yr_pct": "5Y CAGR (%)", "sharpe_ratio": "Sharpe", "alpha": "Alpha (%)",
    "beta": "Beta", "expense_ratio_pct": "TER (%)", "max_drawdown_pct": "Max DD (%)",
    "composite_score": "Score"
})
render_fintech_table(clean_df, height=380)

# Export Scorecard
col_dl1, col_dl2 = st.columns([1, 3])
with col_dl1:
    csv_bytes = clean_df.to_csv(index=False).encode('utf-8')
    st.download_button(
        label="📥 Download Scorecard (CSV)",
        data=csv_bytes,
        file_name="mutual_fund_performance_scorecard.csv",
        mime="text/csv"
    )

st.markdown("<hr style='border: none; border-top: 1px solid #E5EAF2; margin: 24px 0 12px 0;'/>", unsafe_allow_html=True)
st.caption("Bluestock Fintech Pvt. Ltd. • Fund Performance & Risk Analytics • Risk Free Rate: 6.50% (RBI 91-Day T-Bill)")
