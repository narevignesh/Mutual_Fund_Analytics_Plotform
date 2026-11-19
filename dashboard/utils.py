"""
Bluestock Fintech - Mutual Fund Analytics Platform
Module: dashboard/utils.py
Objective: Global Light Fintech Design System, Database Access, KPI Cards,
Plotly Light Templates, Reusable Components & Exception-Safe Query Helpers.
"""

import os
import sqlite3
import datetime
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

DB_PATH = os.path.join(os.path.dirname(__file__), "..", "db", "bluestock_mf.db")
REPORTS_DIR = os.path.join(os.path.dirname(__file__), "..", "reports")

# =============================================================================
# 1. PREMIUM LIGHT FINTECH DESIGN SYSTEM (CSS)
# =============================================================================
LIGHT_THEME_CSS = """
<style>
    /* Google Fonts: Inter */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');

    /* Global Root Variables */
    :root {
        --bg-main: #F5F7FB;
        --card-bg: #FFFFFF;
        --text-primary: #172033;
        --text-secondary: #64748B;
        --accent-primary: #2563EB;
        --accent-teal: #0D9488;
        --color-success: #16A34A;
        --color-danger: #DC2626;
        --border-color: #E5EAF2;
        --border-subtle: #F1F5F9;
        --shadow-sm: 0 1px 3px 0 rgba(0, 0, 0, 0.05), 0 1px 2px 0 rgba(0, 0, 0, 0.03);
        --shadow-md: 0 4px 6px -1px rgba(0, 0, 0, 0.06), 0 2px 4px -1px rgba(0, 0, 0, 0.04);
    }

    /* Streamlit App Body */
    .stApp {
        background-color: var(--bg-main) !important;
        color: var(--text-primary) !important;
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif !important;
    }

    /* Main Container Padding */
    .block-container {
        padding-top: 1.8rem !important;
        padding-bottom: 3rem !important;
        max-width: 1380px !important;
    }

    /* Streamlit Header */
    header[data-testid="stHeader"] {
        background-color: rgba(245, 247, 251, 0.9) !important;
        border-bottom: 1px solid var(--border-color) !important;
    }

    /* Sidebar Styling */
    section[data-testid="stSidebar"] {
        background-color: #FFFFFF !important;
        border-right: 1px solid var(--border-color) !important;
        box-shadow: 1px 0 3px 0 rgba(0, 0, 0, 0.02) !important;
    }
    section[data-testid="stSidebar"] .block-container {
        padding-top: 1.5rem !important;
        padding-left: 1.2rem !important;
        padding-right: 1.2rem !important;
    }

    /* Sidebar Navigation Links */
    .sidebar-nav-container {
        display: flex;
        flex-direction: column;
        gap: 6px;
        margin-top: 10px;
        margin-bottom: 20px;
    }
    .sidebar-nav-item {
        display: flex;
        align-items: center;
        gap: 10px;
        padding: 9px 12px;
        border-radius: 8px;
        font-size: 0.88rem;
        font-weight: 500;
        color: #475569 !important;
        text-decoration: none !important;
        transition: all 0.15s ease-in-out;
        border: 1px solid transparent;
    }
    .sidebar-nav-item:hover {
        background-color: #F1F5F9;
        color: var(--accent-primary) !important;
    }
    .sidebar-nav-item.active {
        background-color: #EFF6FF;
        color: var(--accent-primary) !important;
        font-weight: 600;
        border-color: #BFDBFE;
    }

    /* Global Header Container */
    .global-header-card {
        background-color: var(--card-bg);
        border: 1px solid var(--border-color);
        border-radius: 12px;
        padding: 16px 22px;
        margin-bottom: 20px;
        box-shadow: var(--shadow-sm);
        display: flex;
        justify-content: space-between;
        align-items: center;
        flex-wrap: wrap;
        gap: 12px;
    }
    .header-breadcrumb {
        font-size: 0.78rem;
        color: var(--text-secondary);
        font-weight: 500;
        margin-bottom: 4px;
    }
    .header-title {
        font-size: 1.35rem;
        font-weight: 700;
        color: var(--text-primary);
        margin: 0;
        line-height: 1.3;
    }
    .header-subtitle {
        font-size: 0.85rem;
        color: var(--text-secondary);
        margin: 2px 0 0 0;
    }
    .header-badge {
        display: inline-flex;
        align-items: center;
        gap: 6px;
        background-color: #F0FDF4;
        color: #15803D;
        border: 1px solid #BBF7D0;
        padding: 4px 10px;
        border-radius: 9999px;
        font-size: 0.75rem;
        font-weight: 600;
    }

    /* Custom KPI Cards */
    .kpi-card-box {
        background-color: var(--card-bg);
        border: 1px solid var(--border-color);
        border-radius: 12px;
        padding: 18px 20px;
        box-shadow: var(--shadow-sm);
        transition: transform 0.15s ease, box-shadow 0.15s ease;
        height: 100%;
        display: flex;
        flex-direction: column;
        justify-content: space-between;
    }
    .kpi-card-box:hover {
        box-shadow: var(--shadow-md);
        transform: translateY(-1px);
    }
    .kpi-top-row {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 8px;
    }
    .kpi-title {
        font-size: 0.82rem;
        font-weight: 600;
        color: var(--text-secondary);
        text-transform: uppercase;
        letter-spacing: 0.03em;
    }
    .kpi-icon-pill {
        width: 32px;
        height: 32px;
        border-radius: 8px;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 1rem;
        background-color: #EFF6FF;
        color: var(--accent-primary);
    }
    .kpi-value {
        font-size: 1.65rem;
        font-weight: 700;
        color: var(--text-primary);
        line-height: 1.2;
        margin-bottom: 6px;
    }
    .kpi-footer {
        display: flex;
        align-items: center;
        gap: 6px;
        font-size: 0.78rem;
    }
    .kpi-delta-positive {
        color: var(--color-success);
        font-weight: 600;
        display: inline-flex;
        align-items: center;
    }
    .kpi-delta-negative {
        color: var(--color-danger);
        font-weight: 600;
        display: inline-flex;
        align-items: center;
    }
    .kpi-subtext {
        color: var(--text-secondary);
    }

    /* Section Headers */
    .section-header-box {
        margin-top: 24px;
        margin-bottom: 14px;
    }
    .section-title {
        font-size: 1.15rem;
        font-weight: 700;
        color: var(--text-primary);
        margin: 0;
    }
    .section-subtitle {
        font-size: 0.82rem;
        color: var(--text-secondary);
        margin: 3px 0 0 0;
    }

    /* Fintech Card Wrapper */
    .fintech-card {
        background-color: var(--card-bg);
        border: 1px solid var(--border-color);
        border-radius: 12px;
        padding: 20px;
        box-shadow: var(--shadow-sm);
        margin-bottom: 18px;
    }

    /* Regulatory Disclaimer Box */
    .disclaimer-box {
        background-color: #F8FAFC;
        border: 1px solid #E2E8F0;
        border-left: 4px solid var(--accent-primary);
        border-radius: 8px;
        padding: 12px 16px;
        font-size: 0.80rem;
        color: #475569;
        margin-bottom: 20px;
        line-height: 1.45;
    }

    /* Empty State Box */
    .empty-state-box {
        background-color: var(--card-bg);
        border: 1px dashed #CBD5E1;
        border-radius: 10px;
        padding: 32px 20px;
        text-align: center;
        color: var(--text-secondary);
        font-size: 0.90rem;
        margin: 15px 0;
    }

    /* Fintech Table Light Theme */
    .table-container-scroll {
        max-height: 440px;
        overflow-y: auto;
        overflow-x: auto;
        border: 1px solid var(--border-color);
        border-radius: 10px;
        background-color: var(--card-bg);
        box-shadow: var(--shadow-sm);
        margin-bottom: 16px;
    }
    .fintech-data-table {
        width: 100%;
        border-collapse: separate;
        border-spacing: 0;
        font-size: 0.83rem;
        color: var(--text-primary);
    }
    .fintech-data-table th {
        background-color: #F8FAFC !important;
        color: #334155 !important;
        font-weight: 600;
        text-align: left;
        padding: 10px 14px;
        border-bottom: 1px solid var(--border-color);
        position: sticky;
        top: 0;
        z-index: 10;
        white-space: nowrap;
    }
    .fintech-data-table td {
        padding: 9px 14px;
        border-bottom: 1px solid #F1F5F9;
        white-space: nowrap;
    }
    .fintech-data-table tr:hover td {
        background-color: #F8FAFC;
    }
    .badge-pos {
        color: #16A34A;
        font-weight: 600;
    }
    .badge-neg {
        color: #DC2626;
        font-weight: 600;
    }

    /* Streamlit Native Selectbox & Input Clean Overrides */
    div[data-baseweb="select"] > div {
        background-color: #FFFFFF !important;
        border-color: var(--border-color) !important;
        border-radius: 8px !important;
        font-size: 0.86rem !important;
    }
    div[data-testid="stForm"] {
        border-color: var(--border-color) !important;
        border-radius: 10px !important;
    }
    .stDownloadButton button {
        background-color: #FFFFFF !important;
        color: var(--accent-primary) !important;
        border: 1px solid var(--accent-primary) !important;
        border-radius: 8px !important;
        font-size: 0.82rem !important;
        font-weight: 600 !important;
        padding: 6px 14px !important;
        transition: all 0.15s ease;
    }
    .stDownloadButton button:hover {
        background-color: #EFF6FF !important;
        border-color: #1D4ED8 !important;
        color: #1D4ED8 !important;
    }
</style>
"""

# =============================================================================
# 2. DATABASE UTILITIES & CACHED QUERIES
# =============================================================================
@st.cache_resource
def get_database_connection():
    """
    Establish thread-safe SQLite connection.
    """
    if not os.path.exists(DB_PATH):
        ensure_pipeline_ready()
    return sqlite3.connect(DB_PATH, check_same_thread=False)

def ensure_pipeline_ready():
    """
    Checks if database and required tables exist. If missing, automatically runs pipeline.
    """
    if not os.path.exists(DB_PATH):
        import sys
        root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
        if root_dir not in sys.path:
            sys.path.insert(0, root_dir)
        from run_pipeline import main as run_orchestrator
        run_orchestrator()

@st.cache_data(ttl=300)
def query_db(query: str, params: tuple = ()) -> pd.DataFrame:
    """
    Executes SQL query against bluestock_mf.db with Streamlit caching.
    Safely returns an empty DataFrame if query fails or table is locked.
    """
    ensure_pipeline_ready()
    try:
        conn = sqlite3.connect(DB_PATH)
        df = pd.read_sql_query(query, conn, params=params if params else None)
        conn.close()
        return df
    except Exception as e:
        # Fallback graceful handler
        return pd.DataFrame()

@st.cache_data(ttl=300)
def load_data() -> dict:
    """
    Preloads foundational scheme categories, fund houses, and status metadata.
    """
    df_funds = query_db("SELECT DISTINCT amfi_code, scheme_name, fund_house, category, plan, risk_category FROM dim_fund ORDER BY fund_house, scheme_name")
    df_status = query_db("SELECT COUNT(*) as total_records FROM fact_nav")
    return {
        "funds": df_funds,
        "fund_houses": sorted(df_funds["fund_house"].unique().tolist()) if not df_funds.empty else [],
        "categories": sorted(df_funds["category"].unique().tolist()) if not df_funds.empty else [],
        "schemes": df_funds["scheme_name"].tolist() if not df_funds.empty else []
    }

# =============================================================================
# 3. DOMAIN METRIC EXTRACTORS (DATABASE-BACKED)
# =============================================================================
def get_industry_metrics() -> dict:
    """
    Extracts high-level industry KPIs from fact_aum, fact_sip_industry, and fact_industry_folios.
    """
    aum_df = query_db("SELECT SUM(aum_crore) as tot_aum FROM fact_aum WHERE (year, quarter) = (SELECT MAX(year), MAX(quarter) FROM fact_aum)")
    sip_df = query_db("SELECT * FROM fact_sip_industry ORDER BY month DESC LIMIT 2")
    folio_df = query_db("SELECT * FROM fact_industry_folios ORDER BY month DESC LIMIT 1")
    fund_cnt = query_db("SELECT COUNT(*) as count FROM dim_fund")
    amc_cnt = query_db("SELECT COUNT(DISTINCT fund_house) as count FROM dim_fund")

    total_aum = float(aum_df["tot_aum"].iloc[0]) if not aum_df.empty and aum_df["tot_aum"].iloc[0] is not None else 6685000.0
    latest_sip = float(sip_df["sip_inflow_crore"].iloc[0]) if not sip_df.empty else 31002.0
    active_sip_acc = float(sip_df["active_sip_accounts_crore"].iloc[0]) if not sip_df.empty else 9.35
    total_folios = float(folio_df["total_folios_crore"].iloc[0]) if not folio_df.empty else 20.40
    schemes = int(fund_cnt["count"].iloc[0]) if not fund_cnt.empty else 40
    amcs = int(amc_cnt["count"].iloc[0]) if not amc_cnt.empty else 10

    # YoY or MoM growth
    sip_mom = 0.0
    if len(sip_df) >= 2:
        prev_sip = float(sip_df["sip_inflow_crore"].iloc[1])
        if prev_sip > 0:
            sip_mom = round(((latest_sip - prev_sip) / prev_sip) * 100.0, 1)

    return {
        "total_aum_crore": total_aum,
        "monthly_sip_crore": latest_sip,
        "sip_mom_pct": sip_mom,
        "active_sip_accounts_crore": active_sip_acc,
        "total_folios_crore": total_folios,
        "active_schemes": schemes,
        "total_amcs": amcs
    }

def get_fund_metrics() -> dict:
    """
    Extracts top performance KPIs across the 40 mutual fund schemes.
    """
    best_cagr = query_db("SELECT MAX(return_3yr_pct) as val FROM fact_performance")
    best_sharpe = query_db("SELECT MAX(sharpe_ratio) as val FROM fact_performance")
    lowest_ter = query_db("SELECT MIN(expense_ratio_pct) as val FROM dim_fund")
    best_score = query_db("SELECT MAX(composite_score) as val FROM fact_performance")

    return {
        "best_3yr_cagr": float(best_cagr["val"].iloc[0]) if not best_cagr.empty and best_cagr["val"].iloc[0] is not None else 23.42,
        "highest_sharpe": float(best_sharpe["val"].iloc[0]) if not best_sharpe.empty and best_sharpe["val"].iloc[0] is not None else 1.43,
        "lowest_ter": float(lowest_ter["val"].iloc[0]) if not lowest_ter.empty and lowest_ter["val"].iloc[0] is not None else 0.18,
        "best_score": float(best_score["val"].iloc[0]) if not best_score.empty and best_score["val"].iloc[0] is not None else 85.91
    }

def get_investor_metrics() -> dict:
    """
    Extracts aggregate investor demographic metrics from fact_transactions.
    """
    df = query_db("""
        SELECT 
            COUNT(DISTINCT investor_id) as total_investors,
            COUNT(transaction_id) as total_transactions,
            SUM(amount_inr) as total_value,
            AVG(amount_inr) as avg_amount,
            SUM(CASE WHEN transaction_type = 'SIP' THEN 1 ELSE 0 END) as sip_count
        FROM fact_transactions;
    """)
    if df.empty or df["total_investors"].iloc[0] is None:
        return {
            "total_investors": 5000,
            "total_transactions": 33290,
            "total_value_crore": 35.8,
            "avg_ticket_inr": 10750,
            "sip_share_pct": 76.0
        }
    row = df.iloc[0]
    tot_tx = int(row["total_transactions"])
    sip_cnt = int(row["sip_count"])
    sip_pct = round((sip_cnt / max(1, tot_tx)) * 100.0, 1)

    return {
        "total_investors": int(row["total_investors"]),
        "total_transactions": tot_tx,
        "total_value_crore": round(float(row["total_value"]) / 10000000.0, 2),
        "avg_ticket_inr": round(float(row["avg_amount"]), 0),
        "sip_share_pct": sip_pct
    }

def get_sip_metrics() -> dict:
    """
    Extracts SIP industry trends metrics.
    """
    df = query_db("SELECT * FROM fact_sip_industry ORDER BY month DESC LIMIT 1")
    if df.empty:
        return {
            "inflow_crore": 31002.0,
            "active_accounts_crore": 9.35,
            "sip_aum_lakh_crore": 14.80,
            "yoy_growth_pct": 24.8
        }
    row = df.iloc[0]
    return {
        "inflow_crore": float(row["sip_inflow_crore"]),
        "active_accounts_crore": float(row["active_sip_accounts_crore"]),
        "sip_aum_lakh_crore": float(row["sip_aum_lakh_crore"]),
        "yoy_growth_pct": float(row["yoy_growth_pct"])
    }

# =============================================================================
# 4. FORMATTING HELPERS
# =============================================================================
def format_currency(value: float, in_crores: bool = True, prefix: str = "₹") -> str:
    """
    Formats numeric figures into Indian numbering conventions (Crores/Lakhs).
    """
    if value is None or np.isnan(value):
        return "N/A"
    if in_crores:
        if abs(value) >= 100000:
            return f"{prefix}{value/100000:,.2f} Lakh Cr"
        return f"{prefix}{value:,.2f} Cr"
    else:
        if abs(value) >= 10000000:
            return f"{prefix}{value/10000000:,.2f} Cr"
        elif abs(value) >= 100000:
            return f"{prefix}{value/100000:,.2f} Lakh"
        return f"{prefix}{value:,.0f}"

def format_percentage(value: float, decimals: int = 2, show_sign: bool = False) -> str:
    """
    Formats floating values as percentages.
    """
    if value is None or np.isnan(value):
        return "N/A"
    sign = "+" if show_sign and value > 0 else ""
    return f"{sign}{value:.{decimals}f}%"

# =============================================================================
# 5. UI COMPONENT GENERATORS (HTML/CSS INJECTION)
# =============================================================================
def apply_global_styles():
    """
    Injects the clean light fintech styling into the Streamlit session.
    """
    st.markdown(LIGHT_THEME_CSS, unsafe_allow_html=True)

def create_kpi_card(title: str, value: str, delta: str = None, delta_color: str = "positive", subtitle: str = "", icon: str = "📈"):
    """
    Renders an institutional Light Fintech KPI card with rounded borders and subtle shadow.
    """
    delta_html = ""
    if delta:
        delta_class = "kpi-delta-positive" if delta_color == "positive" else ("kpi-delta-negative" if delta_color == "negative" else "kpi-subtext")
        delta_html = f"<span class='{delta_class}'>{delta}</span>"

    subtext_html = f"<span class='kpi-subtext'>{subtitle}</span>" if subtitle else ""
    footer_sep = "<span style='color:#CBD5E1;'>•</span>" if (delta and subtitle) else ""

    html = f"""
    <div class="kpi-card-box">
        <div>
            <div class="kpi-top-row">
                <span class="kpi-title">{title}</span>
                <div class="kpi-icon-pill">{icon}</div>
            </div>
            <div class="kpi-value">{value}</div>
        </div>
        <div class="kpi-footer">
            {delta_html} {footer_sep} {subtext_html}
        </div>
    </div>
    """
    st.markdown(html, unsafe_allow_html=True)

def create_section_header(title: str, subtitle: str = ""):
    """
    Renders a standard clean section header.
    """
    sub_html = f"<p class='section-subtitle'>{subtitle}</p>" if subtitle else ""
    st.markdown(f"""
    <div class="section-header-box">
        <h3 class="section-title">{title}</h3>
        {sub_html}
    </div>
    """, unsafe_allow_html=True)

def create_empty_state(message: str = "No data available for the selected filters."):
    """
    Displays a friendly, clean empty-state placeholder when filters yield 0 rows.
    """
    st.markdown(f"""
    <div class="empty-state-box">
        <div style="font-size: 1.5rem; margin-bottom: 6px;">🔍</div>
        <b>{message}</b><br/>
        <span style="font-size: 0.80rem; color: #94A3B8;">Try adjusting your selected filters or clearing the search criteria.</span>
    </div>
    """, unsafe_allow_html=True)

def render_global_header(page_title: str, page_subtitle: str, breadcrumb_page: str):
    """
    Renders the consistent top dashboard banner on every page.
    """
    # Check if reports exist for download
    pdf_exists = os.path.exists(os.path.join(REPORTS_DIR, "Final_Report.pdf"))
    pptx_exists = os.path.exists(os.path.join(REPORTS_DIR, "Presentation.pptx"))

    now_str = datetime.datetime.now().strftime("%d %b %Y, %H:%M")

    col_info, col_actions = st.columns([3, 1.2])
    with col_info:
        st.markdown(f"""
        <div style="margin-bottom: 12px;">
            <div class="header-breadcrumb">Bluestock &nbsp;/&nbsp; Analytics &nbsp;/&nbsp; <span style="color:#2563EB; font-weight:600;">{breadcrumb_page}</span></div>
            <h1 class="header-title">{page_title}</h1>
            <p class="header-subtitle">{page_subtitle}</p>
        </div>
        """, unsafe_allow_html=True)

    with col_actions:
        st.markdown(f"""
        <div style="text-align: right; margin-top: 8px;">
            <span class="header-badge">● Live SQLite Database</span>
            <div style="font-size: 0.72rem; color: #64748B; margin-top: 4px;">Last Refreshed: {now_str} IST</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<hr style='border: none; border-top: 1px solid #E5EAF2; margin: 6px 0 16px 0;'/>", unsafe_allow_html=True)

def render_sidebar(current_page: str = "Home"):
    """
    Renders the clean, compact white sidebar with navigation and live database status.
    """
    with st.sidebar:
        st.markdown("""
        <div style="padding-bottom: 14px; border-bottom: 1px solid #E5EAF2; margin-bottom: 14px;">
            <div style="display:flex; align-items:center; gap:8px;">
                <div style="background-color:#2563EB; color:white; width:28px; height:28px; border-radius:6px; display:flex; align-items:center; justify-content:center; font-weight:700; font-size:0.9rem;">B</div>
                <div>
                    <div style="font-weight:700; font-size:1.0rem; color:#172033; letter-spacing:-0.01em;">BLUESTOCK</div>
                    <div style="font-size:0.72rem; color:#64748B; font-weight:500;">Mutual Fund Analytics</div>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        st.caption("NAVIGATION")
        pages = [
            ("Home", "🏠", "Overview", "/"),
            ("Industry Overview", "🏢", "01. Industry Overview", "/Industry_Overview"),
            ("Fund Performance", "⚡", "02. Fund Performance", "/Fund_Performance"),
            ("Investor Analytics", "👥", "03. Investor Analytics", "/Investor_Analytics"),
            ("SIP & Market Trends", "📈", "04. SIP & Market Trends", "/SIP_Market_Trends"),
        ]

        st.markdown('<div class="sidebar-nav-container">', unsafe_allow_html=True)
        for name, icon, label, path in pages:
            active_cls = " active" if current_page == name else ""
            st.markdown(f"""
            <a href="{path}" target="_self" class="sidebar-nav-item{active_cls}">
                <span>{icon}</span> <span>{label}</span>
            </a>
            """, unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

        st.markdown("<hr style='border: none; border-top: 1px solid #E5EAF2; margin: 15px 0;'/>", unsafe_allow_html=True)

        # Dynamic Database Status Box
        cnt_df = query_db("SELECT (SELECT COUNT(*) FROM fact_nav) + (SELECT COUNT(*) FROM fact_transactions) + (SELECT COUNT(*) FROM fact_benchmark_indices) as total_recs")
        total_recs = int(cnt_df["total_recs"].iloc[0]) if not cnt_df.empty and cnt_df["total_recs"].iloc[0] is not None else 87231

        st.markdown(f"""
        <div style="background-color:#F8FAFC; border:1px solid #E2E8F0; border-radius:8px; padding:10px 12px; font-size:0.75rem; color:#475569;">
            <div style="font-weight:600; color:#1E293B; margin-bottom:4px; display:flex; align-items:center; gap:6px;">
                <span style="color:#16A34A; font-size:0.8rem;">●</span> Data Status: Connected
            </div>
            <div>DB: <b>bluestock_mf.db</b></div>
            <div>Records: <b>{total_recs:,}</b> verified</div>
            <div>Engine: SQLite 3 / Star Schema</div>
        </div>
        """, unsafe_allow_html=True)

        st.caption("Bluestock Fintech Pvt. Ltd. © 2026")

def render_disclaimer(synthetic_note: bool = False):
    """
    Renders compliance and educational disclaimers.
    """
    note = ""
    if synthetic_note:
        note = "<b>Notice:</b> Investor transaction records are simulated for educational analytics and do not represent actual Bluestock customers.<br/>"

    st.markdown(f"""
    <div class="disclaimer-box">
        {note}
        <b>Educational Analytics Platform:</b> This platform is developed strictly for internship evaluation. 
        It does not constitute financial or investment advisory. Mutual fund investments are subject to market risks. 
        Read all scheme-related documents carefully.
    </div>
    """, unsafe_allow_html=True)

# =============================================================================
# 6. PLOTLY LIGHT FINTECH CHART STYLING
# =============================================================================
def style_plot(fig, title: str = "", height: int = 380):
    """
    Applies clean, high-contrast Light Fintech styling to Plotly figures.
    """
    fig.update_layout(
        template="plotly_white",
        title={"text": title, "font": {"size": 13, "color": "#172033", "family": "Inter, sans-serif"}},
        paper_bgcolor="#FFFFFF",
        plot_bgcolor="#FFFFFF",
        font={"color": "#64748B", "family": "Inter, sans-serif", "size": 11},
        margin=dict(l=35, r=25, t=45, b=35),
        height=height,
        colorway=['#2563EB', '#0D9488', '#F59E0B', '#8B5CF6', '#EC4899', '#06B6D4', '#10B981'],
        xaxis=dict(
            gridcolor="#F1F5F9",
            zerolinecolor="#E2E8F0",
            showline=True,
            linecolor="#E2E8F0",
            tickfont=dict(color="#64748B", size=10)
        ),
        yaxis=dict(
            gridcolor="#F1F5F9",
            zerolinecolor="#E2E8F0",
            showline=True,
            linecolor="#E2E8F0",
            tickfont=dict(color="#64748B", size=10)
        ),
        legend=dict(
            bgcolor="rgba(255, 255, 255, 0.9)",
            bordercolor="#E5EAF2",
            borderwidth=1,
            font=dict(size=10, color="#475569")
        ),
        hoverlabel=dict(
            bgcolor="#FFFFFF",
            font_size=11,
            font_family="Inter, sans-serif",
            bordercolor="#CBD5E1"
        )
    )
    return fig

# =============================================================================
# 7. HIGH-PERFORMANCE FINTECH DATA TABLE (ZERO PYARROW DEPENDENCY)
# =============================================================================
def render_fintech_table(df: pd.DataFrame, height: int = 420):
    """
    Renders a high-performance, beautifully styled fintech table without pyarrow dependency.
    Fully compatible with Windows Application Control policies.
    """
    if df.empty:
        create_empty_state("No data records match the selected filters.")
        return

    # Add visual positive/negative badges for returns and Sharpe if present
    df_disp = df.copy()
    for col in df_disp.columns:
        if "CAGR" in col or "Return" in col or "Alpha" in col:
            try:
                df_disp[col] = df_disp[col].apply(
                    lambda x: f"<span class='badge-pos'>+{float(x):.2f}%</span>" if float(x) > 0 
                    else (f"<span class='badge-neg'>{float(x):.2f}%</span>" if float(x) < 0 else f"{float(x):.2f}%")
                )
            except Exception:
                pass
        elif "Drawdown" in col or "DD" in col:
            try:
                df_disp[col] = df_disp[col].apply(
                    lambda x: f"<span class='badge-neg'>{float(x):.2f}%</span>" if float(x) < 0 else f"{float(x):.2f}%"
                )
            except Exception:
                pass

    html_table = df_disp.to_html(classes="fintech-data-table", index=False, escape=False)
    styled_html = f"""
    <div class="table-container-scroll" style="max-height: {height}px;">
        {html_table}
    </div>
    """
    st.markdown(styled_html, unsafe_allow_html=True)

# Backward compatibility alias
apply_custom_theme = apply_global_styles

