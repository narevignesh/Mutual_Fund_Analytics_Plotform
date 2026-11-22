"""
Mutual Fund Analytics Platform
Entry Point: app.py
Objective: Commercial financial analytics product interface matching reference UI.
Minimal, elegant, high-contrast fintech light theme (#F4F7FF, #FFFFFF, #2563EB, #101B45).
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
    get_overview_kpis, get_market_insights, get_overview_charts_data, get_key_market_insights_cards,
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

# Helper: Render Page Header with Breadcrumbs & Visual Illustration
def render_page_header(title: str, subtitle: str, current_nav: str = "Overview", show_illustration: bool = True):
    coins_svg = """
    <svg width="190" height="95" viewBox="0 0 190 95" fill="none" xmlns="http://www.w3.org/2000/svg">
        <!-- Background Chart Bars -->
        <rect x="120" y="55" width="9" height="35" rx="3" fill="#BFDBFE" opacity="0.6"/>
        <rect x="135" y="42" width="9" height="48" rx="3" fill="#93C5FD" opacity="0.7"/>
        <rect x="150" y="26" width="9" height="64" rx="3" fill="#60A5FA" opacity="0.8"/>
        <rect x="165" y="12" width="9" height="78" rx="3" fill="#3B82F6" opacity="0.9"/>
        
        <!-- Rising Arrow Curve -->
        <path d="M105 65 C125 50 150 28 172 14" stroke="#93C5FD" stroke-width="3.5" stroke-linecap="round"/>
        <polygon points="172,10 180,14 173,21" fill="#3B82F6"/>

        <!-- Coin Stacks (3 Stacks) -->
        <!-- Stack 1 (left, lowest) -->
        <g transform="translate(15, 58)">
            <ellipse cx="16" cy="18" rx="13" ry="4.5" fill="#D97706"/>
            <ellipse cx="16" cy="14" rx="13" ry="4.5" fill="#F59E0B"/>
            <ellipse cx="16" cy="10" rx="13" ry="4.5" fill="#FBBF24"/>
            <ellipse cx="16" cy="6" rx="13" ry="4.5" fill="#FDE68A"/>
        </g>

        <!-- Stack 2 (middle) -->
        <g transform="translate(36, 44)">
            <ellipse cx="17" cy="26" rx="14" ry="4.8" fill="#D97706"/>
            <ellipse cx="17" cy="21" rx="14" ry="4.8" fill="#F59E0B"/>
            <ellipse cx="17" cy="16" rx="14" ry="4.8" fill="#FBBF24"/>
            <ellipse cx="17" cy="11" rx="14" ry="4.8" fill="#FCD34D"/>
            <ellipse cx="17" cy="6" rx="14" ry="4.8" fill="#FEF3C7"/>
        </g>

        <!-- Stack 3 (right, tallest with sprout) -->
        <g transform="translate(58, 28)">
            <ellipse cx="18" cy="38" rx="15" ry="5" fill="#B45309"/>
            <ellipse cx="18" cy="33" rx="15" ry="5" fill="#D97706"/>
            <ellipse cx="18" cy="28" rx="15" ry="5" fill="#F59E0B"/>
            <ellipse cx="18" cy="23" rx="15" ry="5" fill="#FBBF24"/>
            <ellipse cx="18" cy="18" rx="15" ry="5" fill="#FCD34D"/>
            <ellipse cx="18" cy="13" rx="15" ry="5" fill="#FDE68A"/>
            <ellipse cx="18" cy="8" rx="15" ry="5" fill="#FFFBEB"/>
            <ellipse cx="18" cy="7" rx="13" ry="3.5" fill="#FEF08A"/>
            
            <!-- Sprouting Plant -->
            <path d="M18 7 C18 -3 13 -11 9 -14 C12 -12 20 -5 18 7 Z" fill="#22C55E"/>
            <path d="M18 5 C20 -2 27 -8 33 -11 C30 -9 22 -3 18 5 Z" fill="#16A34A"/>
            <path d="M18 7 L18 1" stroke="#15803D" stroke-width="1.8" stroke-linecap="round"/>
        </g>
    </svg>
    """
    illus_html = f'<div class="header-illustration-box">{coins_svg}</div>' if show_illustration else ''
    
    st.markdown(f"""
    <div class="breadcrumb-container">
        <div class="breadcrumb-left">
            <span class="breadcrumb-home-icon">🏠</span>
            <span>Mutual Fund Analytics</span>
            <span class="breadcrumb-sep">&gt;</span>
            <span class="breadcrumb-current">{current_nav}</span>
        </div>
        <div class="header-actions-right">
            <div class="live-data-pill">
                <span class="live-pulse-dot"></span>
                <span>Live Data</span>
            </div>
            <div class="refresh-icon-btn" title="Refreshed from database">🔄</div>
        </div>
    </div>
    <div class="header-banner-card">
        <div class="header-title-box">
            <h1 class="page-title-v2">{title}</h1>
            <p class="page-subtitle-v2">{subtitle}</p>
        </div>
        {illus_html}
    </div>
    """, unsafe_allow_html=True)

# Helper: Render 4 Equal-Width KPI Cards (Matching Reference UI)
def render_kpi_row_v2(cards: list):
    icons_svg = {
        "rupee": '<svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"><line x1="12" y1="1" x2="12" y2="23"></line><path d="M17 5H9.5a3.5 3.5 0 0 0 0 7h5a3.5 3.5 0 0 1 0 7H6"></path></svg>',
        "calendar": '<svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"><rect x="3" y="4" width="18" height="18" rx="2" ry="2"></rect><line x1="16" y1="2" x2="16" y2="6"></line><line x1="8" y1="2" x2="8" y2="6"></line><line x1="3" y1="10" x2="21" y2="10"></line></svg>',
        "users": '<svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"><path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2"></path><circle cx="9" cy="7" r="4"></circle><path d="M23 21v-2a4 4 0 0 0-3-3.87"></path><path d="M16 3.13a4 4 0 0 1 0 7.75"></path></svg>',
        "doc": '<svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"></path><polyline points="14 2 14 8 20 8"></polyline><line x1="16" y1="13" x2="8" y2="13"></line><line x1="16" y1="17" x2="8" y2="17"></line><polyline points="10 9 9 9 8 9"></polyline></svg>'
    }

    cols = st.columns(len(cards))
    for idx, c in enumerate(cards):
        color_cls = f"kpi-icon-{c.get('color', 'blue')}"
        svg_code = icons_svg.get(c.get('icon', 'rupee'), icons_svg['rupee'])
        tooltip_txt = c.get('tooltip', '')
        tooltip_html = f'<span class="info-tooltip" data-tooltip="{tooltip_txt}">ⓘ</span>' if tooltip_txt else ''
        
        with cols[idx]:
            st.markdown(f"""
            <div class="kpi-card-v2">
                <div class="kpi-icon-circle {color_cls}">
                    {svg_code}
                </div>
                <div class="kpi-content-box">
                    <div class="kpi-label-row">
                        <span class="kpi-label-text">{c.get('label', '')}</span>
                        {tooltip_html}
                    </div>
                    <div class="kpi-value-text">{c.get('value', '')}</div>
                    <div class="kpi-trend-text">{c.get('trend', '')}</div>
                </div>
            </div>
            """, unsafe_allow_html=True)

# =============================================================================
# SIDEBAR NAVIGATION (MATCHING REFERENCE UI)
# =============================================================================
with st.sidebar:
    st.markdown("""
    <div class="sidebar-header-box">
        <div class="sidebar-icon-container">
            <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="#2563EB" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round">
                <polyline points="22 7 13.5 15.5 8.5 10.5 2 17"></polyline>
                <polyline points="16 7 22 7 22 13"></polyline>
            </svg>
        </div>
        <h2 class="sidebar-title">Mutual Fund Analytics</h2>
        <div class="sidebar-subtitle">Explore. Analyse. Invest.</div>
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

    nav_icons = {
        "Overview": "🏠",
        "Industry Overview": "📊",
        "Fund Performance": "🏆",
        "Investor Analytics": "👥",
        "SIP & Market Trends": "📈",
        "Dataset Information": "🗄️"
    }

    selected_nav = st.radio(
        "Navigation Menu",
        options=nav_options,
        index=0,
        format_func=lambda x: f"{nav_icons.get(x, '•')}   {x}",
        label_visibility="collapsed"
    )

    st.markdown("""
    <div class="sidebar-insight-card">
        <div class="sidebar-insight-header">
            <span class="insight-bulb">💡</span>
            <span class="insight-title">Quick Insight</span>
        </div>
        <div class="sidebar-insight-body">
            SIPs are the preferred investment choice, growing steadily over time.
        </div>
        <div class="sidebar-insight-wave">
            <svg viewBox="0 0 100 24" preserveAspectRatio="none" style="width: 100%; height: 20px; display: block; opacity: 0.16;">
                <path d="M0,12 C30,4 60,20 100,8 L100,24 L0,24 Z" fill="#2563EB"></path>
            </svg>
        </div>
    </div>
    """, unsafe_allow_html=True)

# =============================================================================
# 1. OVERVIEW PAGE
# =============================================================================
if selected_nav == "Overview":
    render_page_header(
        title="Indian Mutual Fund Market Overview",
        subtitle="A clear picture of mutual fund industry growth and investment trends.",
        current_nav="Overview",
        show_illustration=True
    )

    # 4 Primary KPI Cards matching reference UI
    kpis = get_overview_kpis()
    render_kpi_row_v2([
        {
            "color": "blue",
            "icon": "rupee",
            "label": "Total Industry AUM",
            "value": kpis["total_aum"],
            "trend": "▲ Growing steadily",
            "tooltip": "Assets Under Management (AUM): The total market value of investments managed across all mutual funds in India. Measures overall industry size."
        },
        {
            "color": "purple",
            "icon": "calendar",
            "label": "Monthly SIP Inflow",
            "value": kpis["monthly_sip"],
            "trend": "▲ 19.6% YoY",
            "tooltip": "Systematic Investment Plan (SIP): Total monthly disciplined capital inflow from retail and institutional investors. Shows compounding growth."
        },
        {
            "color": "green",
            "icon": "users",
            "label": "Total Folios",
            "value": kpis["total_folios"],
            "trend": "▲ More investors",
            "tooltip": "Total Folios: The cumulative number of investor accounts registered across all schemes. Reflects retail financial penetration."
        },
        {
            "color": "orange",
            "icon": "doc",
            "label": "Tracked Schemes",
            "value": kpis["tracked_schemes"],
            "trend": "▲ Wide variety",
            "tooltip": "Tracked Schemes: Monitored active mutual fund schemes analyzed across Equity, Debt, and Hybrid categories."
        }
    ])

    st.markdown("<div style='height: 14px;'></div>", unsafe_allow_html=True)

    # Two Main Chart Cards Side by Side (Matching Reference UI)
    df_aum, df_sip, df_amc, df_cat = get_overview_charts_data()
    c1, c2 = st.columns(2)

    with c1:
        st.markdown("""
        <div class="chart-card-v2">
            <div class="chart-header-row">
                <span class="chart-header-icon">📊</span>
                <h3 class="chart-card-title">Industry AUM Growth (2022–2025)</h3>
            </div>
            <p class="chart-card-subtitle">Total assets under management in mutual funds</p>
        """, unsafe_allow_html=True)
        fig1 = charts.chart_industry_aum_growth(df_aum)
        if fig1:
            st.plotly_chart(fig1, use_container_width=True, config={"displayModeBar": False})
        else:
            st.info("No data available for this selection.")
        st.markdown('</div>', unsafe_allow_html=True)

    with c2:
        st.markdown("""
        <div class="chart-card-v2">
            <div class="chart-header-row">
                <span class="chart-header-icon">📈</span>
                <h3 class="chart-card-title">Monthly SIP Investment Trend</h3>
            </div>
            <p class="chart-card-subtitle">Growing participation through SIPs</p>
        """, unsafe_allow_html=True)
        fig2 = charts.chart_monthly_sip_trend(df_sip)
        if fig2:
            st.plotly_chart(fig2, use_container_width=True, config={"displayModeBar": False})
        else:
            st.info("No data available for this selection.")
        st.markdown('</div>', unsafe_allow_html=True)

    # Key Market Insights Wide Card (Matching Reference UI)
    st.markdown("""
    <div class="insights-card-v2">
        <div class="insights-title-row">
            <span class="insights-bulb-icon">💡</span>
            <span class="insights-heading-text">Key Market Insights</span>
        </div>
        <div class="insights-grid-v2">
            <div class="insight-col-v2">
                <div class="insight-icon-blue">
                    <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="#2563EB" stroke-width="2.4" stroke-linecap="round" stroke-linejoin="round">
                        <line x1="18" y1="20" x2="18" y2="10"></line>
                        <line x1="12" y1="20" x2="12" y2="4"></line>
                        <line x1="6" y1="20" x2="6" y2="14"></line>
                    </svg>
                </div>
                <div class="insight-desc-v2">Industry AUM has grown steadily from <b>₹25L Cr</b> to <b>₹44.31L Cr</b>.</div>
            </div>
            <div class="insight-col-v2">
                <div class="insight-icon-blue">
                    <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="#2563EB" stroke-width="2.4" stroke-linecap="round" stroke-linejoin="round">
                        <path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2"></path>
                        <circle cx="9" cy="7" r="4"></circle>
                        <path d="M23 21v-2a4 4 0 0 0-3-3.87"></path>
                        <path d="M16 3.13a4 4 0 0 1 0 7.75"></path>
                    </svg>
                </div>
                <div class="insight-desc-v2">SIP contributions are rising, showing strong investor confidence.</div>
            </div>
            <div class="insight-col-v2">
                <div class="insight-icon-gold">
                    <svg width="20" height="20" viewBox="0 0 24 24" fill="#F59E0B" stroke="#D97706" stroke-width="1.5">
                        <polygon points="12 2 15.09 8.26 22 9.27 17 14.14 18.18 21.02 12 17.77 5.82 21.02 7 14.14 2 9.27 8.91 8.26 12 2"></polygon>
                    </svg>
                </div>
                <div class="insight-desc-v2">Equity funds continue to attract majority of investments.</div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Additional Overview Distribution Cards
    c3, c4 = st.columns(2)
    with c3:
        st.markdown("""
        <div class="chart-card-v2">
            <div class="chart-header-row">
                <span class="chart-header-icon">🏆</span>
                <h3 class="chart-card-title">Top 10 Fund Houses by AUM</h3>
            </div>
            <p class="chart-card-subtitle">Peak assets managed by leading AMCs in India</p>
        """, unsafe_allow_html=True)
        fig3 = charts.chart_top_amcs_aum(df_amc)
        if fig3:
            st.plotly_chart(fig3, use_container_width=True, config={"displayModeBar": False})
        else:
            st.info("No data available for this selection.")
        st.markdown('</div>', unsafe_allow_html=True)

    with c4:
        st.markdown("""
        <div class="chart-card-v2">
            <div class="chart-header-row">
                <span class="chart-header-icon">🍰</span>
                <h3 class="chart-card-title">Mutual Fund Category Distribution</h3>
            </div>
            <p class="chart-card-subtitle">Scheme representation across market capitalizations</p>
        """, unsafe_allow_html=True)
        fig4 = charts.chart_category_distribution(df_cat)
        if fig4:
            st.plotly_chart(fig4, use_container_width=True, config={"displayModeBar": False})
        else:
            st.info("No data available for this selection.")
        st.markdown('</div>', unsafe_allow_html=True)

# =============================================================================
# 2. INDUSTRY OVERVIEW PAGE
# =============================================================================
elif selected_nav == "Industry Overview":
    render_page_header(
        title="Industry Overview & Market Share Analysis",
        subtitle="Macro-level asset growth, fund house market share, and folio expansion trends.",
        current_nav="Industry Overview",
        show_illustration=False
    )

    kpis = get_industry_kpis()
    render_kpi_row_v2([
        {
            "color": "blue",
            "icon": "rupee",
            "label": "Total Industry AUM",
            "value": kpis["total_aum"],
            "trend": "▲ Peak assets",
            "tooltip": "Peak recorded assets under management across all active fund houses."
        },
        {
            "color": "purple",
            "icon": "doc",
            "label": "Active Fund Houses",
            "value": kpis["total_amcs"],
            "trend": "▲ Registered AMCs",
            "tooltip": "Number of asset management companies monitored in this platform."
        },
        {
            "color": "green",
            "icon": "calendar",
            "label": "Tracked Schemes",
            "value": kpis["total_schemes"],
            "trend": "▲ Active offerings",
            "tooltip": "Total investment schemes tracked across equity, debt, and hybrid classes."
        },
        {
            "color": "orange",
            "icon": "users",
            "label": "Total Folios",
            "value": kpis["total_folios"],
            "trend": "▲ Investor accounts",
            "tooltip": "Combined retail and institutional folios across all asset classes."
        }
    ])

    st.markdown("<div style='height: 12px;'></div>", unsafe_allow_html=True)

    # Filters
    years, fhs, cats = get_industry_filter_options()
    f1, f2, f3 = st.columns(3)
    with f1:
        sel_year = st.selectbox("Calendar Year", years, index=0)
    with f2:
        sel_fh = st.selectbox("Asset Management Company", fhs, index=0)
    with f3:
        sel_cat = st.selectbox("Asset Category", cats, index=0)

    df_aum, df_top_amcs, df_market_share, df_cat_aum, df_folios, df_ranking = get_industry_overview_data(sel_year, sel_fh, sel_cat)

    c1, c2 = st.columns(2)
    with c1:
        st.markdown("""
        <div class="chart-card-v2">
            <div class="chart-header-row"><span class="chart-header-icon">📈</span><h3 class="chart-card-title">Quarterly AUM Progression</h3></div>
            <p class="chart-card-subtitle">Historical growth in total managed assets</p>
        """, unsafe_allow_html=True)
        fig1 = charts.chart_industry_aum_progression(df_aum)
        if fig1:
            st.plotly_chart(fig1, use_container_width=True, config={"displayModeBar": False})
        else:
            st.info("No data available for this selection.")
        st.markdown('</div>', unsafe_allow_html=True)

    with c2:
        st.markdown("""
        <div class="chart-card-v2">
            <div class="chart-header-row"><span class="chart-header-icon">🏢</span><h3 class="chart-card-title">Top AMCs by Peak Assets</h3></div>
            <p class="chart-card-subtitle">Market leaders by managed asset base</p>
        """, unsafe_allow_html=True)
        fig2 = charts.chart_top_amcs_bar(df_top_amcs)
        if fig2:
            st.plotly_chart(fig2, use_container_width=True, config={"displayModeBar": False})
        else:
            st.info("No data available for this selection.")
        st.markdown('</div>', unsafe_allow_html=True)

    c3, c4 = st.columns(2)
    with c3:
        st.markdown("""
        <div class="chart-card-v2">
            <div class="chart-header-row"><span class="chart-header-icon">🍩</span><h3 class="chart-card-title">AMC Market Share Breakdown</h3></div>
            <p class="chart-card-subtitle">Asset concentration among leading fund houses</p>
        """, unsafe_allow_html=True)
        fig3 = charts.chart_amc_market_share_donut(df_market_share)
        if fig3:
            st.plotly_chart(fig3, use_container_width=True, config={"displayModeBar": False})
        else:
            st.info("No data available for this selection.")
        st.markdown('</div>', unsafe_allow_html=True)

    with c4:
        st.markdown("""
        <div class="chart-card-v2">
            <div class="chart-header-row"><span class="chart-header-icon">📊</span><h3 class="chart-card-title">Schemes by Category</h3></div>
            <p class="chart-card-subtitle">Scheme concentration across asset classes</p>
        """, unsafe_allow_html=True)
        fig4 = charts.chart_category_aum_bar(df_cat_aum)
        if fig4:
            st.plotly_chart(fig4, use_container_width=True, config={"displayModeBar": False})
        else:
            st.info("No data available for this selection.")
        st.markdown('</div>', unsafe_allow_html=True)

    # Folio growth trend wide card
    st.markdown("""
    <div class="chart-card-v2">
        <div class="chart-header-row"><span class="chart-header-icon">👥</span><h3 class="chart-card-title">Folio Growth Trend by Asset Class (2020–2025)</h3></div>
        <p class="chart-card-subtitle">Expansion of retail investor participation across Equity, Debt, and Hybrid</p>
    """, unsafe_allow_html=True)
    fig5 = charts.chart_folio_growth_trend(df_folios)
    if fig5:
        st.plotly_chart(fig5, use_container_width=True, config={"displayModeBar": False})
    else:
        st.info("No data available for this selection.")
    st.markdown('</div>', unsafe_allow_html=True)

    # Ranking Table
    st.markdown("""
    <div class="analytics-section-card">
        <h3 class="analytics-section-title">Fund House Market Share Leaderboard</h3>
        <p class="analytics-section-subtitle">Comparative ranking of major asset management companies in India.</p>
    """, unsafe_allow_html=True)
    render_table(df_ranking, height=320)
    csv_bytes = df_ranking.to_csv(index=False).encode('utf-8')
    st.download_button("Download Leaderboard (CSV)", data=csv_bytes, file_name="fund_house_rankings.csv", mime="text/csv")
    st.markdown('</div>', unsafe_allow_html=True)

# =============================================================================
# 3. FUND PERFORMANCE PAGE
# =============================================================================
elif selected_nav == "Fund Performance":
    render_page_header(
        title="Mutual Fund Performance & Risk Analysis",
        subtitle="Historical returns, risk-adjusted metrics, Sharpe ratios, and scheme comparisons.",
        current_nav="Fund Performance",
        show_illustration=False
    )

    kpis = get_fund_kpis()
    render_kpi_row_v2([
        {
            "color": "blue",
            "icon": "rupee",
            "label": "Top 3-Year CAGR",
            "value": kpis["best_cagr"],
            "trend": "▲ Highest return",
            "tooltip": "Compound Annual Growth Rate (CAGR): Annualized average rate of return over 3 years."
        },
        {
            "color": "purple",
            "icon": "calendar",
            "label": "Peak Sharpe Ratio",
            "value": kpis["highest_sharpe"],
            "trend": "▲ Risk-adjusted",
            "tooltip": "Sharpe Ratio: Measures excess return per unit of volatility relative to the risk-free rate."
        },
        {
            "color": "green",
            "icon": "doc",
            "label": "Lowest Expense (TER)",
            "value": kpis["lowest_ter"],
            "trend": "▲ Cost-efficient",
            "tooltip": "Total Expense Ratio (TER): Annual percentage fee charged by the AMC to manage the scheme."
        },
        {
            "color": "orange",
            "icon": "users",
            "label": "Best Composite Score",
            "value": kpis["best_score"],
            "trend": "▲ Top rated",
            "tooltip": "Composite Score: Multi-factor quantitative ranking out of 100 assessing returns, volatility, and downside preservation."
        }
    ])

    st.markdown("<div style='height: 12px;'></div>", unsafe_allow_html=True)

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
        # Fund Deep Dive Card
        st.markdown("""
        <div class="analytics-section-card">
            <h3 class="analytics-section-title">Single Fund Deep Dive</h3>
            <p class="analytics-section-subtitle">Select any mutual fund scheme to inspect its verified metrics.</p>
        """, unsafe_allow_html=True)
        
        scheme_list = df_perf["scheme_name"].tolist()
        sel_scheme = st.selectbox("Choose Mutual Fund Scheme", scheme_list, index=0)
        
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
            m7.metric("Jensen's Alpha", prof["alpha"])
            m8.metric("Beta", prof["beta"])

            m9, m10, m11, m12 = st.columns(4)
            m9.metric("Expense Ratio (TER)", prof["expense_ratio"])
            m10.metric("Max Drawdown", prof["max_drawdown"])
            m11.metric("SEBI Category", prof["category"])
            m12.metric("Benchmark Index", prof["benchmark"])
        st.markdown('</div>', unsafe_allow_html=True)

        # Charts: NAV History & Fund vs Benchmark
        if prof:
            nav_df, bmk_df = get_nav_history_series(prof["amfi_code"], prof["benchmark"])
            c1, c2 = st.columns(2)
            with c1:
                st.markdown("""
                <div class="chart-card-v2">
                    <div class="chart-header-row"><span class="chart-header-icon">📈</span><h3 class="chart-card-title">Historical NAV Trend</h3></div>
                    <p class="chart-card-subtitle">Daily Net Asset Value trajectory over time</p>
                """, unsafe_allow_html=True)
                fig1 = charts.chart_historical_nav_trend(nav_df, prof["fund_name"])
                if fig1:
                    st.plotly_chart(fig1, use_container_width=True, config={"displayModeBar": False})
                else:
                    st.info("No data available for this selection.")
                st.markdown('</div>', unsafe_allow_html=True)

            with c2:
                st.markdown("""
                <div class="chart-card-v2">
                    <div class="chart-header-row"><span class="chart-header-icon">🎯</span><h3 class="chart-card-title">Fund vs Benchmark (Base = 100)</h3></div>
                    <p class="chart-card-subtitle">Normalized performance comparison against benchmark</p>
                """, unsafe_allow_html=True)
                fig2 = charts.chart_fund_vs_benchmark(nav_df, bmk_df, prof["fund_name"], prof["benchmark"])
                if fig2:
                    st.plotly_chart(fig2, use_container_width=True, config={"displayModeBar": False})
                else:
                    st.info("No data available for this selection.")
                st.markdown('</div>', unsafe_allow_html=True)

        c3, c4 = st.columns(2)
        with c3:
            st.markdown("""
            <div class="chart-card-v2">
                <div class="chart-header-row"><span class="chart-header-icon">⚡</span><h3 class="chart-card-title">Risk vs Return Matrix</h3></div>
                <p class="chart-card-subtitle">Volatility vs 3-Year CAGR (Bubble size = Score)</p>
            """, unsafe_allow_html=True)
            fig3 = charts.chart_risk_return_scatter(df_perf)
            if fig3:
                st.plotly_chart(fig3, use_container_width=True, config={"displayModeBar": False})
            else:
                st.info("No data available for this selection.")
            st.markdown('</div>', unsafe_allow_html=True)

        with c4:
            st.markdown("""
            <div class="chart-card-v2">
                <div class="chart-header-row"><span class="chart-header-icon">📊</span><h3 class="chart-card-title">Category Performance Comparison</h3></div>
                <p class="chart-card-subtitle">Average 3Y CAGR vs Jensen's Alpha by category</p>
            """, unsafe_allow_html=True)
            fig4 = charts.chart_category_performance(df_perf)
            if fig4:
                st.plotly_chart(fig4, use_container_width=True, config={"displayModeBar": False})
            else:
                st.info("No data available for this selection.")
            st.markdown('</div>', unsafe_allow_html=True)

        # Multi-Fund Comparison Tool
        st.markdown("""
        <div class="analytics-section-card">
            <h3 class="analytics-section-title">Multi-Fund Comparison Tool</h3>
            <p class="analytics-section-subtitle">Select up to 4 funds to evaluate side-by-side.</p>
        """, unsafe_allow_html=True)
        
        default_comp = scheme_list[:3] if len(scheme_list) >= 3 else scheme_list
        selected_comp = st.multiselect("Select schemes to compare", options=scheme_list, default=default_comp)
        
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

        # Full Performance Table
        st.markdown("""
        <div class="analytics-section-card">
            <h3 class="analytics-section-title">Mutual Fund Performance Scorecard</h3>
            <p class="analytics-section-subtitle">Comprehensive ranking across all monitored schemes.</p>
        """, unsafe_allow_html=True)
        
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
        st.download_button("Download Performance Scorecard (CSV)", data=csv_bytes, file_name="fund_performance.csv", mime="text/csv")
        st.markdown('</div>', unsafe_allow_html=True)

# =============================================================================
# 4. INVESTOR ANALYTICS PAGE
# =============================================================================
elif selected_nav == "Investor Analytics":
    render_page_header(
        title="Investor Behavior & Demographic Analytics",
        subtitle="Retail transaction patterns, demographic profiles, ticket sizes, and channel preferences.",
        current_nav="Investor Analytics",
        show_illustration=False
    )

    kpis = get_investor_kpis()
    render_kpi_row_v2([
        {
            "color": "blue",
            "icon": "users",
            "label": "Active Investors",
            "value": kpis["total_investors"],
            "trend": "▲ Sample cohort",
            "tooltip": "Calibrated demographic sample modeling retail investor profiles across India."
        },
        {
            "color": "purple",
            "icon": "calendar",
            "label": "Executed Orders",
            "value": kpis["total_transactions"],
            "trend": "▲ Transaction volume",
            "tooltip": "Total systematic and lump-sum investment transactions analyzed."
        },
        {
            "color": "green",
            "icon": "rupee",
            "label": "Total Order Value",
            "value": kpis["total_value"],
            "trend": "▲ Cumulative capital",
            "tooltip": "Gross transacted capital volume across all demographic cohorts."
        },
        {
            "color": "orange",
            "icon": "doc",
            "label": "Median Ticket Size",
            "value": kpis["avg_value"],
            "trend": "▲ Per order",
            "tooltip": "Representative average investment amount executed per order."
        }
    ])

    st.markdown("<div style='height: 12px;'></div>", unsafe_allow_html=True)

    st.markdown("""
    <div style="background-color: #EFF6FF; border: 1px solid #DBEAFE; border-left: 4px solid #2563EB; border-radius: 8px; padding: 12px 16px; font-size: 13px; color: #1E3A8A; margin-bottom: 20px;">
        <b>Data Provenance Note:</b> Investor transaction records represent a calibrated synthetic sample designed for academic behavioral analytics, modeling realistic retail investment compounding patterns without exposing confidential customer records.
    </div>
    """, unsafe_allow_html=True)

    states, ages, genders, types = get_investor_filter_options()
    f1, f2, f3, f4 = st.columns(4)
    with f1:
        sel_state = st.selectbox("Geographic State", states, index=0)
    with f2:
        sel_age = st.selectbox("Age Cohort", ages, index=0)
    with f3:
        sel_gender = st.selectbox("Gender", genders, index=0)
    with f4:
        sel_type = st.selectbox("Transaction Type", types, index=0)

    df_tx = get_filtered_investor_data(sel_state, sel_age, sel_gender, sel_type)

    if df_tx.empty:
        st.info("No data available for this selection.")
    else:
        c1, c2 = st.columns(2)
        with c1:
            st.markdown("""
            <div class="chart-card-v2">
                <div class="chart-header-row"><span class="chart-header-icon">👥</span><h3 class="chart-card-title">Investor Age Cohort Distribution</h3></div>
                <p class="chart-card-subtitle">Retail participation grouped by demographic brackets</p>
            """, unsafe_allow_html=True)
            fig1 = charts.chart_investor_age_dist(df_tx)
            if fig1:
                st.plotly_chart(fig1, use_container_width=True, config={"displayModeBar": False})
            else:
                st.info("No data available for this selection.")
            st.markdown('</div>', unsafe_allow_html=True)

        with c2:
            st.markdown("""
            <div class="chart-card-v2">
                <div class="chart-header-row"><span class="chart-header-icon">📍</span><h3 class="chart-card-title">Top States by Investment Volume</h3></div>
                <p class="chart-card-subtitle">Geographic capital mobilization across India</p>
            """, unsafe_allow_html=True)
            fig2 = charts.chart_state_investment_bar(df_tx)
            if fig2:
                st.plotly_chart(fig2, use_container_width=True, config={"displayModeBar": False})
            else:
                st.info("No data available for this selection.")
            st.markdown('</div>', unsafe_allow_html=True)

        c3, c4 = st.columns(2)
        with c3:
            st.markdown("""
            <div class="chart-card-v2">
                <div class="chart-header-row"><span class="chart-header-icon">🍩</span><h3 class="chart-card-title">Order Type Breakdown</h3></div>
                <p class="chart-card-subtitle">SIP vs Lumpsum vs Redemption order volume</p>
            """, unsafe_allow_html=True)
            fig3 = charts.chart_sip_vs_lumpsum_donut(df_tx)
            if fig3:
                st.plotly_chart(fig3, use_container_width=True, config={"displayModeBar": False})
            else:
                st.info("No data available for this selection.")
            st.markdown('</div>', unsafe_allow_html=True)

        with c4:
            st.markdown("""
            <div class="chart-card-v2">
                <div class="chart-header-row"><span class="chart-header-icon">📊</span><h3 class="chart-card-title">Monthly Capital Inflows vs Outflows</h3></div>
                <p class="chart-card-subtitle">Temporal momentum of retail investment flows</p>
            """, unsafe_allow_html=True)
            fig4 = charts.chart_monthly_tx_trend(df_tx)
            if fig4:
                st.plotly_chart(fig4, use_container_width=True, config={"displayModeBar": False})
            else:
                st.info("No data available for this selection.")
            st.markdown('</div>', unsafe_allow_html=True)

        c5, c6 = st.columns(2)
        with c5:
            st.markdown("""
            <div class="chart-card-v2">
                <div class="chart-header-row"><span class="chart-header-icon">🏙️</span><h3 class="chart-card-title">T30 vs B30 Capital Allocation</h3></div>
                <p class="chart-card-subtitle">Top 30 metros vs beyond-30 emerging cities</p>
            """, unsafe_allow_html=True)
            fig5 = charts.chart_t30_b30_bar(df_tx)
            if fig5:
                st.plotly_chart(fig5, use_container_width=True, config={"displayModeBar": False})
            else:
                st.info("No data available for this selection.")
            st.markdown('</div>', unsafe_allow_html=True)

        with c6:
            st.markdown("""
            <div class="chart-card-v2">
                <div class="chart-header-row"><span class="chart-header-icon">💵</span><h3 class="chart-card-title">Average Ticket Size by Age</h3></div>
                <p class="chart-card-subtitle">Median capital allocation per demographic cohort</p>
            """, unsafe_allow_html=True)
            fig6 = charts.chart_investment_by_age_bar(df_tx)
            if fig6:
                st.plotly_chart(fig6, use_container_width=True, config={"displayModeBar": False})
            else:
                st.info("No data available for this selection.")
            st.markdown('</div>', unsafe_allow_html=True)

# =============================================================================
# 5. SIP & MARKET TRENDS PAGE
# =============================================================================
elif selected_nav == "SIP & Market Trends":
    render_page_header(
        title="SIP Inflow Dynamics & Market Benchmark Trends",
        subtitle="Systematic investment mobilization, folio milestones, and benchmark performance comparison.",
        current_nav="SIP & Market Trends",
        show_illustration=False
    )

    kpis = get_sip_kpis()
    render_kpi_row_v2([
        {
            "color": "blue",
            "icon": "rupee",
            "label": "Monthly SIP Inflow",
            "value": kpis["monthly_sip"],
            "trend": "▲ Record run-rate",
            "tooltip": "Systematic monthly capital inflows mobilizing into mutual funds across India."
        },
        {
            "color": "purple",
            "icon": "calendar",
            "label": "Active SIP Accounts",
            "value": kpis["active_accounts"],
            "trend": "▲ Retail mandates",
            "tooltip": "Number of live recurring systematic investment accounts active in the market."
        },
        {
            "color": "green",
            "icon": "doc",
            "label": "Cumulative SIP AUM",
            "value": kpis["sip_aum"],
            "trend": "▲ Compounded asset base",
            "tooltip": "Total assets under management accumulated purely through systematic investment plans."
        },
        {
            "color": "orange",
            "icon": "users",
            "label": "Annual SIP Growth",
            "value": kpis["annual_growth"],
            "trend": "▲ YoY momentum",
            "tooltip": "Year-over-year percentage increase in gross monthly SIP mobilization."
        }
    ])

    st.markdown("<div style='height: 12px;'></div>", unsafe_allow_html=True)

    years, bmks, cats = get_sip_filter_options()
    f1, f2, f3 = st.columns(3)
    with f1:
        sel_years = st.multiselect("Calendar Years", years, default=years)
    with f2:
        default_bmks = [b for b in ["Nifty 50", "Nifty Midcap 150", "BSE SmallCap", "CRISIL Liquid"] if b in bmks]
        sel_bmks = st.multiselect("Benchmark Indices", bmks, default=default_bmks if default_bmks else bmks[:4])
    with f3:
        default_cats = [c for c in ["Large Cap", "Mid Cap", "Small Cap", "Flexi Cap", "Hybrid"] if c in cats]
        sel_cats = st.multiselect("Asset Categories", cats, default=default_cats if default_cats else cats[:5])

    df_sip = get_filtered_sip_data(sel_years)
    df_bmk = get_filtered_benchmark_data(sel_bmks)
    df_cat = get_filtered_category_inflow_data(sel_cats)

    if df_sip.empty:
        st.info("No data available for this selection.")
    else:
        c1, c2 = st.columns(2)
        with c1:
            st.markdown("""
            <div class="chart-card-v2">
                <div class="chart-header-row"><span class="chart-header-icon">📈</span><h3 class="chart-card-title">Monthly SIP Inflow Trend (2022–2025)</h3></div>
                <p class="chart-card-subtitle">Monthly disciplined inflows demonstrating retail compounding</p>
            """, unsafe_allow_html=True)
            fig1 = charts.chart_sip_inflow_trend(df_sip)
            if fig1:
                st.plotly_chart(fig1, use_container_width=True, config={"displayModeBar": False})
            else:
                st.info("No data available for this selection.")
            st.markdown('</div>', unsafe_allow_html=True)

        with c2:
            st.markdown("""
            <div class="chart-card-v2">
                <div class="chart-header-row"><span class="chart-header-icon">📊</span><h3 class="chart-card-title">Active SIP Accounts Expansion</h3></div>
                <p class="chart-card-subtitle">Growth in cumulative systematic investor mandates</p>
            """, unsafe_allow_html=True)
            fig2 = charts.chart_active_sip_growth(df_sip)
            if fig2:
                st.plotly_chart(fig2, use_container_width=True, config={"displayModeBar": False})
            else:
                st.info("No data available for this selection.")
            st.markdown('</div>', unsafe_allow_html=True)

        c3, c4 = st.columns(2)
        with c3:
            st.markdown("""
            <div class="chart-card-v2">
                <div class="chart-header-row"><span class="chart-header-icon">⚡</span><h3 class="chart-card-title">Category-wise Monthly Net Inflows</h3></div>
                <p class="chart-card-subtitle">Net capital additions across Equity, Hybrid, and Debt</p>
            """, unsafe_allow_html=True)
            fig3 = charts.chart_category_net_inflows(df_cat)
            if fig3:
                st.plotly_chart(fig3, use_container_width=True, config={"displayModeBar": False})
            else:
                st.info("No data available for this selection.")
            st.markdown('</div>', unsafe_allow_html=True)

        with c4:
            st.markdown("""
            <div class="chart-card-v2">
                <div class="chart-header-row"><span class="chart-header-icon">🎯</span><h3 class="chart-card-title">Benchmark Index Trends (Base = 100)</h3></div>
                <p class="chart-card-subtitle">Comparative price trajectories of key regulatory market indices</p>
            """, unsafe_allow_html=True)
            fig4 = charts.chart_benchmark_performance(df_bmk)
            if fig4:
                st.plotly_chart(fig4, use_container_width=True, config={"displayModeBar": False})
            else:
                st.info("No data available for this selection.")
            st.markdown('</div>', unsafe_allow_html=True)

        c5, c6 = st.columns(2)
        with c5:
            st.markdown("""
            <div class="chart-card-v2">
                <div class="chart-header-row"><span class="chart-header-icon">📅</span><h3 class="chart-card-title">Average Monthly SIP Inflows by Year</h3></div>
                <p class="chart-card-subtitle">Annualized systematic run-rate comparison</p>
            """, unsafe_allow_html=True)
            fig5 = charts.chart_sip_growth_by_year(df_sip)
            if fig5:
                st.plotly_chart(fig5, use_container_width=True, config={"displayModeBar": False})
            else:
                st.info("No data available for this selection.")
            st.markdown('</div>', unsafe_allow_html=True)

        with c6:
            st.markdown("""
            <div class="chart-card-v2">
                <div class="chart-header-row"><span class="chart-header-icon">🌡️</span><h3 class="chart-card-title">Category Inflow Intensity Heatmap</h3></div>
                <p class="chart-card-subtitle">Monthly heat distribution of net capital allocations</p>
            """, unsafe_allow_html=True)
            fig6 = charts.chart_category_inflow_heatmap(df_cat)
            if fig6:
                st.plotly_chart(fig6, use_container_width=True, config={"displayModeBar": False})
            else:
                st.info("No data available for this selection.")
            st.markdown('</div>', unsafe_allow_html=True)

# =============================================================================
# 6. DATASET INFORMATION PAGE
# =============================================================================
elif selected_nav == "Dataset Information":
    render_page_header(
        title="Dataset Information, Provenance & Documentation",
        subtitle="Complete transparency into sources, record counts, field dictionaries, glossary, and data exports.",
        current_nav="Dataset Information",
        show_illustration=False
    )

    overview_df, total_recs = get_dataset_overview_metrics()

    # Overview Matrix
    st.markdown("""
    <div class="analytics-section-card">
        <h3 class="analytics-section-title">Core Dataset Overview Matrix</h3>
        <p class="analytics-section-subtitle">Comprehensive summary of all 10 verified datasets analyzed in this platform.</p>
    """, unsafe_allow_html=True)
    render_table(overview_df, height=360)
    st.markdown('</div>', unsafe_allow_html=True)

    # Section A: DATA COLLECTION
    st.markdown("""
    <div class="analytics-section-card">
        <h3 class="analytics-section-title">A. Data Collection Methodology</h3>
        <p style="font-size: 13.5px; color: #475569; line-height: 1.6;">
            The datasets utilized across this application were sourced through multiple standardized collection channels:
        </p>
        <ul style="font-size: 13px; color: #334155; line-height: 1.65;">
            <li><b>AMFI Official Disclosures:</b> Industry-wide macro metrics, monthly systematic investment mobilization (SIPs), quarterly average assets under management (QAAUM), and folio counts were collected from official publications of the Association of Mutual Funds in India (AMFI).</li>
            <li><b>Public API Endpoints (mfapi.in):</b> Historical daily Net Asset Values (NAV) for premier schemes were ingested via verified open financial endpoints.</li>
            <li><b>Market Benchmark Disclosures:</b> Index price levels for Nifty 50, Nifty Midcap 150, BSE SmallCap, and CRISIL Liquid indices were compiled from published index factsheets.</li>
            <li><b>Simulated Demographic Modeling:</b> Granular investor transaction orders and demographic variables were synthesized using calibrated probabilistic distributions to model realistic retail investor compounding behaviors without exposing proprietary or confidential personal information.</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)

    # Section B: DATA QUALITY
    st.markdown("""
    <div class="analytics-section-card">
        <h3 class="analytics-section-title">B. Data Quality & Integrity Summary</h3>
    """, unsafe_allow_html=True)
    q1, q2, q3, q4, q5 = st.columns(5)
    q1.metric("Total Records", f"{total_recs:,}")
    q2.metric("Total Datasets", "10 Datasets")
    q3.metric("Missing Values", "0 (Cleaned)")
    q4.metric("Valid Records", "99.99%")
    q5.metric("Date Coverage", "2020 – 2025")
    st.markdown("""
        <p style="font-size: 12.5px; color: #64748B; margin-top: 12px; margin-bottom: 0;">
            All ingested records underwent schema standardization, type-casting, deduplication, and boundary validation prior to analytical aggregation.
        </p>
    </div>
    """, unsafe_allow_html=True)

    # Section C: REAL VS SYNTHETIC DATA
    st.markdown("""
    <div class="analytics-section-card">
        <h3 class="analytics-section-title">C. Real vs Synthetic Data Provenance</h3>
        <ul style="font-size: 13px; color: #334155; line-height: 1.65;">
            <li><b>Real & Public Financial Data:</b> Includes fund structural master information, historical daily NAV curves, benchmark index closing prices, AMFI monthly SIP disclosures (e.g. December 2025 milestone of ₹31,002 Crore), and quarterly fund house assets under management.</li>
            <li><b>Synthetic Sample Data:</b> Includes investor transaction records (5,000 synthetic investor profiles modeling age cohorts, geographic tiers T30/B30, and order channels) and representative portfolio company weight snapshots. These are calibrated sample datasets designed strictly for academic and portfolio behavioral analytics.</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)

    # Section D: FINANCIAL TERMINOLOGY GLOSSARY & ABBREVIATIONS
    st.markdown("""
    <div class="analytics-section-card">
        <h3 class="analytics-section-title">D. Financial Terminology & Abbreviations Glossary</h3>
        <p class="analytics-section-subtitle">Clear explanations of financial metrics and abbreviations for non-financial users.</p>
    """, unsafe_allow_html=True)

    terms = [
        ("AUM", "Assets Under Management", "The total market value of all investments managed by a mutual fund company.", "Measures the overall size, investor adoption, and financial scale of a fund house."),
        ("SIP", "Systematic Investment Plan", "An investment method where an investor commits a fixed sum of money at regular monthly intervals.", "Enables disciplined investing, benefits from rupee cost averaging, and eliminates the risk of market timing."),
        ("NAV", "Net Asset Value", "The per-unit market value of a mutual fund scheme, calculated by dividing total net scheme assets by outstanding units.", "Reflects the current purchase or redemption price of one unit of the mutual fund scheme."),
        ("CAGR", "Compound Annual Growth Rate", "The mean annual growth rate of an investment over a multi-year period, smoothing out year-to-year volatility.", "Provides a standardized benchmark to compare long-term scheme performance across different time horizons."),
        ("TER", "Total Expense Ratio", "The annual percentage fee charged by the fund house to cover management fees, administration, and regulatory expenses.", "Directly impacts net returns received by the investor; lower TERs preserve more compounding capital."),
        ("AMC", "Asset Management Company", "A regulated financial institution (fund house) that pools retail and institutional capital to invest in diversified portfolios.", "Oversees investment strategies, asset allocation, compliance, and fund accounting under SEBI regulations."),
        ("Sharpe Ratio", "Risk-Adjusted Return Metric", "The ratio of a fund's excess return above the risk-free rate (6.50%) divided by its annualized standard deviation (volatility).", "Indicates whether higher returns are generated through intelligent security selection or excessive volatility."),
        ("Sortino Ratio", "Downside Risk-Adjusted Ratio", "Similar to Sharpe, but only penalizes downside volatility (negative returns) rather than total volatility.", "Focuses specifically on protecting investors from harmful downside drawdowns while allowing upside variance."),
        ("Alpha (Jensen's)", "Excess Risk-Adjusted Return", "The percentage return generated by the fund manager above the expected return predicted by the Capital Asset Pricing Model (CAPM).", "Measures the fund manager's active skill and value added beyond passive market benchmark movements."),
        ("Beta", "Market Sensitivity Metric", "A measure of the sensitivity of a fund's returns relative to movements in its regulatory benchmark index.", "A Beta of 1.0 moves in tandem with the index; Beta < 1.0 indicates lower volatility and greater defensive stability."),
        ("Max Drawdown", "Maximum Historical Peak-to-Trough Decline", "The maximum observed percentage drop from a peak NAV to a trough before a new peak is reached.", "Identifies capital preservation risk during severe market corrections, stress-testing fund resilience.")
    ]

    for abbr, full_form, desc, why in terms:
        with st.expander(f"📌 {abbr} — {full_form}"):
            st.markdown(f"""
            - **What it is:** {desc}
            - **Why it matters:** {why}
            """)
    st.markdown('</div>', unsafe_allow_html=True)

    # Section E: DATA DICTIONARY
    st.markdown("""
    <div class="analytics-section-card">
        <h3 class="analytics-section-title">E. Data Dictionary & Field Specifications</h3>
        <p class="analytics-section-subtitle">Expand any dataset to view field descriptions, data types, and sample values.</p>
    """, unsafe_allow_html=True)

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

    # Section F: DOWNLOAD DATA
    st.markdown("""
    <div class="analytics-section-card">
        <h3 class="analytics-section-title">F. Data Export & Download Center</h3>
        <p class="analytics-section-subtitle">Export underlying analytical datasets directly in CSV format.</p>
    """, unsafe_allow_html=True)

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
            st.download_button("Download Performance Scorecard (CSV)", data=b3, file_name="scheme_performance.csv", mime="text/csv", use_container_width=True)

    d_col4, d_col5 = st.columns(2)
    b4 = get_csv_download_bytes("02_nav_history.csv")
    with d_col4:
        if b4:
            st.download_button("Download NAV History Sample (CSV)", data=b4, file_name="nav_history.csv", mime="text/csv", use_container_width=True)

    summary_bytes = overview_df.to_csv(index=False).encode('utf-8')
    with d_col5:
        st.download_button("Download Dataset Summary (CSV)", data=summary_bytes, file_name="dataset_summary.csv", mime="text/csv", use_container_width=True)

    st.markdown('</div>', unsafe_allow_html=True)

    # Section G: DATA LIMITATIONS
    st.markdown("""
    <div class="analytics-section-card">
        <h3 class="analytics-section-title">G. Data Limitations & Analytical Boundaries</h3>
        <ul style="font-size: 13px; color: #334155; line-height: 1.65;">
            <li><b>Historical Time Horizon:</b> Ingested daily NAV series span January 2022 through late 2025/early 2026. Prior market cycles are not fully reflected in short-term attribution.</li>
            <li><b>Simulated Demographic Order Books:</b> Investor transaction frequency, payment channel adoption, and urban tier distributions are calibrated against AMFI macro ratios but represent synthetic sample accounts. They should not be utilized for individualized credit profiling.</li>
            <li><b>Cash and Derivative Balances:</b> Portfolio holdings track top representative equity positions and do not account for daily intra-month cash sweeps or hedging derivatives.</li>
            <li><b>Educational Purpose:</b> All performance indicators, Sharpe ratios, and scorecards are calculated for academic evaluation and do not represent guaranteed future returns.</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)
