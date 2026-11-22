"""
Mutual Fund Analytics — Plotly Visualizations Engine
Module: charts.py
Objective: Reusable, responsive, lightweight Plotly charts styled with
the minimal light fintech theme (#FFFFFF cards, #2563EB, #0D9488, Inter font).
"""

import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go

# Clean fintech color sequences
FINTECH_COLORS = ['#2563EB', '#0D9488', '#F59E0B', '#8B5CF6', '#10B981', '#EC4899', '#06B6D4', '#64748B']

def base_layout(fig, title: str = "", height: int = 360):
    """
    Applies unified light fintech theme to Plotly figures.
    """
    fig.update_layout(
        template="plotly_white",
        title={"text": title, "font": {"size": 13, "color": "#172033", "family": "Inter, sans-serif"}},
        paper_bgcolor="#FFFFFF",
        plot_bgcolor="#FFFFFF",
        font={"color": "#64748B", "family": "Inter, sans-serif", "size": 11},
        margin=dict(l=35, r=25, t=42, b=35),
        height=height,
        colorway=FINTECH_COLORS,
        xaxis=dict(
            gridcolor="#F1F5F9",
            zerolinecolor="#E8ECF3",
            showline=True,
            linecolor="#E8ECF3",
            tickfont=dict(color="#64748B", size=10)
        ),
        yaxis=dict(
            gridcolor="#F1F5F9",
            zerolinecolor="#E8ECF3",
            showline=True,
            linecolor="#E8ECF3",
            tickfont=dict(color="#64748B", size=10)
        ),
        legend=dict(
            bgcolor="rgba(255, 255, 255, 0.95)",
            bordercolor="#E8ECF3",
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
# 1. OVERVIEW PAGE CHARTS (4 CHARTS)
# =============================================================================
def chart_industry_aum_growth(df: pd.DataFrame):
    """CHART 1: Industry AUM Growth (Quarterly Area Chart Matching Reference UI)"""
    if df.empty:
        return None
    d = df.copy()
    d["aum_lakh_cr"] = d["aum_thousand_cr"] / 100.0
    
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=d["period"],
        y=d["aum_lakh_cr"],
        mode="lines+markers",
        name="Industry AUM",
        line=dict(color="#2563EB", width=3, shape="spline"),
        marker=dict(size=6, color="#2563EB"),
        fill="tozeroy",
        fillcolor="rgba(37, 99, 235, 0.12)",
        hovertemplate="<b>%{x}</b><br>AUM: ₹%{y:.2f} Lakh Cr<extra></extra>"
    ))
    
    # Add callout pill for the latest point
    last_idx = len(d) - 1
    last_val = d["aum_lakh_cr"].iloc[last_idx]
    fig.add_annotation(
        x=d["period"].iloc[last_idx],
        y=last_val,
        text=f"<b>₹{last_val:.2f} L Cr</b>",
        showarrow=True,
        arrowhead=0,
        arrowcolor="#2563EB",
        arrowwidth=1.5,
        ax=0,
        ay=-28,
        bgcolor="#2563EB",
        font=dict(color="#FFFFFF", size=11, family="Inter, sans-serif"),
        borderpad=4,
        bordercolor="#2563EB",
        borderwidth=1,
        opacity=0.95
    )
    
    fig = base_layout(fig, "", height=320)
    
    # Yearly ticks for x axis (2022, 2023, 2024, 2025)
    tick_periods = []
    tick_labels = []
    for yr in ["2022", "2023", "2024", "2025"]:
        matches = d[d["period"].str.startswith(yr)]
        if not matches.empty:
            tick_periods.append(matches["period"].iloc[0])
            tick_labels.append(yr)
            
    fig.update_layout(
        margin=dict(l=45, r=20, t=25, b=30),
        xaxis=dict(
            title="",
            tickvals=tick_periods,
            ticktext=tick_labels,
            showgrid=False
        ),
        yaxis=dict(
            title="AUM (₹ Lakh Cr)",
            range=[0, 52],
            tickvals=[0, 10, 20, 30, 40, 50],
            gridcolor="#F1F5F9"
        )
    )
    return fig

def chart_monthly_sip_trend(df: pd.DataFrame):
    """CHART 2: Monthly SIP Investment Trend Matching Reference UI"""
    if df.empty:
        return None
    d = df.copy()
    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=d["month"],
        y=d["sip_inflow_crore"],
        name="SIP Inflow",
        marker_color="#2563EB",
        opacity=0.92,
        hovertemplate="<b>%{x}</b><br>Inflow: ₹%{y:,.0f} Cr<extra></extra>"
    ))
    
    # Add callout box for latest bar
    last_sip = d["sip_inflow_crore"].iloc[-1]
    fig.add_annotation(
        x=d["month"].iloc[-1],
        y=last_sip,
        text=f"<b>₹{int(last_sip):,} Cr</b>",
        showarrow=False,
        yshift=14,
        bgcolor="#FFFFFF",
        font=dict(color="#101B45", size=11, family="Inter, sans-serif"),
        borderpad=4,
        bordercolor="#CBD5E1",
        borderwidth=1
    )
    
    fig = base_layout(fig, "", height=320)
    
    # Yearly ticks for x axis (2022, 2023, 2024, 2025)
    tick_months = []
    tick_labels = []
    for yr in ["2022", "2023", "2024", "2025"]:
        matches = d[d["month"].str.startswith(yr)]
        if not matches.empty:
            tick_months.append(matches["month"].iloc[0])
            tick_labels.append(yr)
            
    fig.update_layout(
        margin=dict(l=50, r=20, t=25, b=30),
        xaxis=dict(
            title="",
            tickvals=tick_months,
            ticktext=tick_labels,
            showgrid=False
        ),
        yaxis=dict(
            title="SIP Inflow (₹ Cr)",
            range=[0, 36000],
            tickvals=[0, 10000, 20000, 30000, 40000],
            ticktext=["0", "10K", "20K", "30K", "40K"],
            gridcolor="#F1F5F9"
        )
    )
    return fig

def chart_top_amcs_aum(df: pd.DataFrame):
    """CHART 3: Top 10 Fund Houses by AUM"""
    if df.empty:
        return None
    fig = px.bar(
        df, y="fund_house", x="peak_aum_thousand_cr", orientation="h",
        labels={"fund_house": "Fund House", "peak_aum_thousand_cr": "Peak AUM (₹ Thousand Cr)"},
        color="peak_aum_thousand_cr",
        color_continuous_scale=[[0, "#BFDBFE"], [1, "#1D4ED8"]]
    )
    fig.update_layout(coloraxis_showscale=False)
    return base_layout(fig, "Top 10 Fund Houses by AUM", height=340)

def chart_category_distribution(df: pd.DataFrame):
    """CHART 4: Mutual Fund Category Distribution"""
    if df.empty:
        return None
    fig = px.pie(
        df, values="scheme_count", names="category",
        hole=0.48,
        color_discrete_sequence=FINTECH_COLORS
    )
    fig.update_traces(
        textposition='inside',
        textinfo='percent+label',
        hovertemplate='<b>%{label}</b><br>Schemes: %{value}<br>Share: %{percent}<extra></extra>'
    )
    return base_layout(fig, "Mutual Fund Category Distribution", height=340)

# =============================================================================
# 2. INDUSTRY OVERVIEW CHARTS (5 CHARTS)
# =============================================================================
def chart_industry_aum_progression(df: pd.DataFrame):
    """1. Industry AUM Growth (Filtered)"""
    if df.empty:
        return None
    fig = px.area(
        df, x="period", y="aum_thousand_cr",
        labels={"period": "Quarter", "aum_thousand_cr": "AUM (₹ Thousand Cr)"},
        color_discrete_sequence=["#2563EB"]
    )
    fig.update_traces(line=dict(width=2.4, color="#2563EB"), fillcolor="rgba(37, 99, 235, 0.10)")
    return base_layout(fig, "Quarterly Industry AUM Progression", height=350)

def chart_top_amcs_bar(df: pd.DataFrame):
    """2. Top 10 AMCs by AUM"""
    if df.empty:
        return None
    fig = px.bar(
        df, y="fund_house", x="peak_aum_thousand_cr", orientation="h",
        labels={"fund_house": "AMC", "peak_aum_thousand_cr": "Peak AUM (₹ Thousand Cr)"},
        color="peak_aum_thousand_cr",
        color_continuous_scale=[[0, "#BFDBFE"], [1, "#2563EB"]]
    )
    fig.update_layout(coloraxis_showscale=False)
    return base_layout(fig, "Top AMCs by Peak Assets Under Management", height=350)

def chart_amc_market_share_donut(df: pd.DataFrame):
    """3. AMC Market Share"""
    if df.empty:
        return None
    fig = px.pie(
        df, values="aum", names="fund_house",
        hole=0.48,
        color_discrete_sequence=FINTECH_COLORS
    )
    fig.update_traces(
        textposition='inside',
        textinfo='percent+label',
        hovertemplate='<b>%{label}</b><br>AUM: ₹%{value:,.0f} Cr<br>Market Share: %{percent}<extra></extra>'
    )
    return base_layout(fig, "AMC Market Share Breakdown", height=350)

def chart_category_aum_bar(df: pd.DataFrame):
    """4. Category-wise AUM Distribution"""
    if df.empty:
        return None
    fig = px.bar(
        df, x="category", y="scheme_count",
        labels={"category": "Category", "scheme_count": "Number of Schemes"},
        color="scheme_count",
        color_continuous_scale=[[0, "#A7F3D0"], [1, "#0D9488"]]
    )
    fig.update_layout(coloraxis_showscale=False)
    return base_layout(fig, "Mutual Fund Schemes by Category", height=350)

def chart_folio_growth_trend(df: pd.DataFrame):
    """5. Folio Growth Trend"""
    if df.empty:
        return None
    fig = px.area(
        df, x="month", y=["equity_folios_crore", "debt_folios_crore", "hybrid_folios_crore"],
        labels={"value": "Folios (Crores)", "month": "Date", "variable": "Asset Class"},
        color_discrete_map={
            "equity_folios_crore": "#16A34A",
            "debt_folios_crore": "#2563EB",
            "hybrid_folios_crore": "#8B5CF6"
        }
    )
    fig.update_traces(opacity=0.75)
    return base_layout(fig, "Folio Growth Trend by Asset Class (2020–2025)", height=350)

# =============================================================================
# 3. FUND PERFORMANCE CHARTS (4 CHARTS)
# =============================================================================
def chart_historical_nav_trend(nav_df: pd.DataFrame, scheme_name: str):
    """1. Historical NAV Trend"""
    if nav_df.empty:
        return None
    fig = px.line(
        nav_df, x="date", y="nav",
        labels={"date": "Date", "nav": "NAV (₹)"},
        color_discrete_sequence=["#2563EB"]
    )
    fig.update_traces(line=dict(width=2.2))
    return base_layout(fig, f"Historical NAV Trend: {scheme_name[:32]}", height=350)

def chart_fund_vs_benchmark(nav_df: pd.DataFrame, bmk_df: pd.DataFrame, scheme_name: str, bmk_name: str):
    """2. Fund vs Benchmark (Normalized to 100)"""
    if nav_df.empty or bmk_df.empty:
        return None
    merged = pd.merge(nav_df, bmk_df, on="date").dropna()
    if merged.empty:
        return None
    merged["Fund_Norm"] = (merged["nav"] / merged["nav"].iloc[0]) * 100.0
    merged["Bmk_Norm"] = (merged["close_value"] / merged["close_value"].iloc[0]) * 100.0

    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=merged["date"], y=merged["Fund_Norm"],
        name=f"Fund: {scheme_name[:22]}",
        line=dict(color="#2563EB", width=2.4)
    ))
    fig.add_trace(go.Scatter(
        x=merged["date"], y=merged["Bmk_Norm"],
        name=f"Benchmark: {bmk_name}",
        line=dict(color="#F59E0B", width=1.8, dash="dash")
    ))
    return base_layout(fig, "Normalized Growth vs Benchmark (Base = 100)", height=350)

def chart_risk_return_scatter(df: pd.DataFrame):
    """3. Risk vs Return Scatter Plot"""
    if df.empty:
        return None
    fig = px.scatter(
        df, x="std_dev_ann_pct", y="return_3yr_pct",
        color="category", size="composite_score", hover_name="scheme_name",
        labels={"std_dev_ann_pct": "Annualized Volatility (σ %)", "return_3yr_pct": "3-Year CAGR (%)", "composite_score": "Score"},
        color_discrete_sequence=FINTECH_COLORS
    )
    fig.add_vline(x=15.0, line_dash="dash", line_color="#CBD5E1")
    fig.add_hline(y=15.0, line_dash="dash", line_color="#CBD5E1")
    return base_layout(fig, "Risk vs Return Positioning (Bubble Size = Composite Score)", height=350)

def chart_category_performance(df: pd.DataFrame):
    """4. Category Performance Comparison"""
    if df.empty:
        return None
    cat_agg = df.groupby("category").agg(
        avg_cagr=("return_3yr_pct", "mean"),
        avg_alpha=("alpha", "mean")
    ).reset_index()
    fig = px.bar(
        cat_agg, x="category", y=["avg_cagr", "avg_alpha"], barmode="group",
        labels={"value": "Percentage (%)", "category": "Category", "variable": "Indicator"},
        color_discrete_map={"avg_cagr": "#2563EB", "avg_alpha": "#0D9488"}
    )
    return base_layout(fig, "Average 3Y CAGR vs Jensen's Alpha by Category", height=350)

# =============================================================================
# 4. INVESTOR ANALYTICS CHARTS (6 CHARTS)
# =============================================================================
def chart_investor_age_dist(df: pd.DataFrame):
    """1. Investor Age Distribution"""
    if df.empty:
        return None
    age_counts = df["age_group"].value_counts().reset_index()
    age_counts.columns = ["Age Group", "Orders"]
    fig = px.bar(
        age_counts, x="Age Group", y="Orders",
        labels={"Age Group": "Age Cohort", "Orders": "Transactions"},
        color="Orders", color_continuous_scale=[[0, "#BFDBFE"], [1, "#2563EB"]]
    )
    fig.update_layout(coloraxis_showscale=False)
    return base_layout(fig, "Investor Age Cohort Distribution", height=350)

def chart_state_investment_bar(df: pd.DataFrame):
    """2. State-wise Investment Distribution"""
    if df.empty:
        return None
    state_df = df.groupby("state")["amount_inr"].sum().reset_index()
    state_df["amount_cr"] = (state_df["amount_inr"] / 10000000.0).round(2)
    state_df = state_df.sort_values("amount_cr", ascending=True).tail(10)
    fig = px.bar(
        state_df, y="state", x="amount_cr", orientation="h",
        labels={"state": "State", "amount_cr": "Capital Volume (₹ Cr)"},
        color="amount_cr", color_continuous_scale=[[0, "#A7F3D0"], [1, "#0D9488"]]
    )
    fig.update_layout(coloraxis_showscale=False)
    return base_layout(fig, "Top 10 States by Investment Volume", height=350)

def chart_sip_vs_lumpsum_donut(df: pd.DataFrame):
    """3. SIP vs Lumpsum vs Redemption"""
    if df.empty:
        return None
    type_counts = df["transaction_type"].value_counts().reset_index()
    type_counts.columns = ["Type", "Count"]
    fig = px.pie(
        type_counts, values="Count", names="Type",
        hole=0.48,
        color="Type",
        color_discrete_map={"SIP": "#16A34A", "Lumpsum": "#2563EB", "Redemption": "#DC2626"}
    )
    fig.update_traces(textposition='inside', textinfo='percent+label')
    return base_layout(fig, "Order Type Breakdown: SIP vs Lumpsum vs Redemption", height=350)

def chart_monthly_tx_trend(df: pd.DataFrame):
    """4. Monthly Transaction Trends"""
    if df.empty:
        return None
    df_copy = df.copy()
    df_copy["month"] = pd.to_datetime(df_copy["transaction_date"]).dt.strftime("%Y-%m")
    m_vol = df_copy.groupby(["month", "transaction_type"])["amount_inr"].sum().reset_index()
    m_vol["amount_cr"] = m_vol["amount_inr"] / 10000000.0
    fig = px.area(
        m_vol, x="month", y="amount_cr", color="transaction_type",
        labels={"month": "Month", "amount_cr": "Volume (₹ Cr)", "transaction_type": "Order Type"},
        color_discrete_map={"SIP": "#16A34A", "Lumpsum": "#2563EB", "Redemption": "#DC2626"}
    )
    fig.update_traces(opacity=0.8)
    return base_layout(fig, "Monthly Capital Inflows vs Outflows", height=350)

def chart_t30_b30_bar(df: pd.DataFrame):
    """5. T30 vs B30 Comparison"""
    if df.empty:
        return None
    tier_agg = df.groupby("city_tier").agg(
        volume_cr=("amount_inr", lambda x: round(x.sum() / 10000000.0, 2))
    ).reset_index()
    fig = px.bar(
        tier_agg, x="city_tier", y="volume_cr",
        labels={"city_tier": "City Classification", "volume_cr": "Volume (₹ Cr)"},
        color="city_tier",
        color_discrete_map={"T30": "#2563EB", "B30": "#F59E0B"}
    )
    return base_layout(fig, "Metro (T30) vs Emerging (B30) Capital Allocation", height=350)

def chart_investment_by_age_bar(df: pd.DataFrame):
    """6. Investment by Age Group (Average Ticket Size)"""
    if df.empty:
        return None
    age_ticket = df.groupby("age_group")["amount_inr"].mean().reset_index()
    fig = px.bar(
        age_ticket, x="age_group", y="amount_inr",
        labels={"age_group": "Age Group", "amount_inr": "Average Ticket Size (₹)"},
        color="amount_inr",
        color_continuous_scale=[[0, "#DDD6FE"], [1, "#8B5CF6"]]
    )
    fig.update_layout(coloraxis_showscale=False)
    return base_layout(fig, "Average Investment Ticket Size by Age Group", height=350)

# =============================================================================
# 5. SIP & MARKET TRENDS CHARTS (6 CHARTS)
# =============================================================================
def chart_sip_inflow_trend(df: pd.DataFrame):
    """1. Monthly SIP Inflow Trend"""
    if df.empty:
        return None
    fig = px.bar(
        df, x="month", y="sip_inflow_crore",
        labels={"month": "Month", "sip_inflow_crore": "Inflow (₹ Cr)"},
        color="sip_inflow_crore",
        color_continuous_scale=[[0, "#A7F3D0"], [1, "#0D9488"]]
    )
    fig.update_layout(coloraxis_showscale=False)
    return base_layout(fig, "Monthly SIP Inflow Trend (2022–2025)", height=350)

def chart_active_sip_growth(df: pd.DataFrame):
    """2. Active SIP Account Growth"""
    if df.empty:
        return None
    fig = px.line(
        df, x="month", y="active_sip_accounts_crore",
        labels={"month": "Month", "active_sip_accounts_crore": "Active Accounts (Cr)"},
        color_discrete_sequence=["#2563EB"]
    )
    fig.update_traces(line=dict(width=2.5))
    return base_layout(fig, "Active SIP Accounts Expansion", height=350)

def chart_category_net_inflows(df: pd.DataFrame):
    """3. Category-wise Net Inflows"""
    if df.empty:
        return None
    fig = px.line(
        df, x="month", y="net_inflow_crore", color="category", markers=True,
        labels={"month": "Month", "net_inflow_crore": "Net Inflow (₹ Cr)", "category": "Category"},
        color_discrete_sequence=FINTECH_COLORS
    )
    return base_layout(fig, "Category-wise Monthly Net Inflows", height=350)

def chart_benchmark_performance(df: pd.DataFrame):
    """4. Benchmark Index Performance (Normalized to 100)"""
    if df.empty:
        return None
    norm_list = []
    for b_name, grp in df.groupby("index_name"):
        g = grp.sort_values("date").copy()
        g["normalized"] = (g["close_value"] / g["close_value"].iloc[0]) * 100.0
        norm_list.append(g)
    df_norm = pd.concat(norm_list, ignore_index=True) if norm_list else pd.DataFrame()
    if df_norm.empty:
        return None
    fig = px.line(
        df_norm, x="date", y="normalized", color="index_name",
        labels={"date": "Date", "normalized": "Index Level (Base = 100)", "index_name": "Benchmark"},
        color_discrete_sequence=FINTECH_COLORS
    )
    return base_layout(fig, "Comparative Benchmark Index Trends", height=350)

def chart_sip_growth_by_year(df: pd.DataFrame):
    """5. SIP Growth by Year"""
    if df.empty:
        return None
    df_copy = df.copy()
    df_copy["year"] = df_copy["month"].str.slice(0, 4)
    yr_agg = df_copy.groupby("year")["sip_inflow_crore"].mean().reset_index()
    fig = px.bar(
        yr_agg, x="year", y="sip_inflow_crore",
        labels={"year": "Calendar Year", "sip_inflow_crore": "Average Monthly SIP (₹ Cr)"},
        color="sip_inflow_crore",
        color_continuous_scale=[[0, "#BFDBFE"], [1, "#1D4ED8"]]
    )
    fig.update_layout(coloraxis_showscale=False)
    return base_layout(fig, "Average Monthly SIP Inflows by Year", height=350)

def chart_category_inflow_heatmap(df: pd.DataFrame):
    """6. Category-wise Inflow Heatmap"""
    if df.empty:
        return None
    matrix = df.pivot_table(index="category", columns="month", values="net_inflow_crore", aggfunc="mean")
    fig = px.imshow(
        matrix, color_continuous_scale="Blues", aspect="auto",
        labels=dict(x="Month", y="Category", color="Net Inflow (₹ Cr)")
    )
    return base_layout(fig, "Category Inflow Intensity Heatmap", height=350)
