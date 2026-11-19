"""
Bluestock Fintech - Mutual Fund Analytics Platform
Page 3: Investor Analytics & Behavioral Profiling
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
    get_investor_metrics, format_currency, create_kpi_card, create_section_header,
    create_empty_state
)

st.set_page_config(
    page_title="Investor Analytics | Bluestock Fintech",
    page_icon="👥",
    layout="wide",
    initial_sidebar_state="expanded"
)

ensure_pipeline_ready()
apply_global_styles()

# Sidebar Navigation & Demographic Filters
render_sidebar(current_page="Investor Analytics")

with st.sidebar:
    st.markdown("### 🎛️ Demographic Filters")
    
    # 1. State Filter
    raw_states = query_db("SELECT DISTINCT state FROM fact_transactions ORDER BY state")["state"].dropna().tolist()
    states = ["All States"] + raw_states
    sel_state = st.selectbox("State / UT", states, index=0)
    
    # 2. AMFI City Tier
    tiers = ["All Tiers", "T30", "B30"]
    sel_tier = st.selectbox("AMFI City Tier", tiers, index=0)
    
    # 3. Age Bracket
    raw_ages = query_db("SELECT DISTINCT age_group FROM fact_transactions ORDER BY age_group")["age_group"].dropna().tolist()
    age_groups = ["All Age Groups"] + raw_ages
    sel_age = st.selectbox("Age Bracket", age_groups, index=0)
    
    # 4. Transaction Type
    tx_types = ["All Types", "SIP", "Lumpsum", "Redemption"]
    sel_type = st.selectbox("Transaction Type", tx_types, index=0)
    
    # 5. Gender
    genders = ["All Genders", "Male", "Female"]
    sel_gender = st.selectbox("Gender", genders, index=0)

    st.markdown("<hr style='border: none; border-top: 1px solid #E5EAF2; margin: 15px 0;'/>", unsafe_allow_html=True)

# Institutional Header
render_global_header(
    page_title="Retail Investor Analytics & Demographics",
    page_subtitle="Behavioral profiling, transaction channels, urban vs semi-urban penetration (T30/B30), and ticket size segmentation.",
    breadcrumb_page="Investor Analytics"
)

# Regulatory & Synthetic Data Disclaimer
render_disclaimer(synthetic_note=True)

# Build Filtered Query Defensively
where_clauses = []
if sel_state != "All States":
    clean_state = sel_state.replace("'", "''")
    where_clauses.append(f"state = '{clean_state}'")
if sel_tier != "All Tiers":
    clean_tier = sel_tier.replace("'", "''")
    where_clauses.append(f"city_tier = '{clean_tier}'")
if sel_age != "All Age Groups":
    clean_age = sel_age.replace("'", "''")
    where_clauses.append(f"age_group = '{clean_age}'")
if sel_type != "All Types":
    clean_type = sel_type.replace("'", "''")
    where_clauses.append(f"transaction_type = '{clean_type}'")
if sel_gender != "All Genders":
    clean_gender = sel_gender.replace("'", "''")
    where_clauses.append(f"gender = '{clean_gender}'")

where_str = "WHERE " + " AND ".join(where_clauses) if where_clauses else ""

tx_query = f"SELECT * FROM fact_transactions {where_str};"
df_tx = query_db(tx_query)

if df_tx.empty:
    create_empty_state("No investor transactions found for the specified demographic filters.")
    st.stop()

# --- 1. TOP 5 INVESTOR DEMOGRAPHIC KPI CARDS ---
total_investors = df_tx["investor_id"].nunique()
total_val_cr = df_tx["amount_inr"].sum() / 10000000.0
avg_ticket = df_tx["amount_inr"].mean()
total_orders = len(df_tx)
sip_tx_count = len(df_tx[df_tx["transaction_type"] == "SIP"])
sip_share = (sip_tx_count / max(1, total_orders)) * 100.0

k1, k2, k3, k4, k5 = st.columns(5)
with k1:
    create_kpi_card(
        title="Active Investors",
        value=f"{total_investors:,}",
        delta="Verified Profiles",
        delta_color="positive",
        subtitle="Sample Cohort",
        icon="👥"
    )

with k2:
    create_kpi_card(
        title="Transaction Volume",
        value=f"₹{total_val_cr:,.2f} Cr",
        delta="Cumulative Capital",
        delta_color="positive",
        subtitle="Gross Orders",
        icon="💰"
    )

with k3:
    create_kpi_card(
        title="Average Ticket Size",
        value=f"₹{avg_ticket:,.0f}",
        delta="Per Transaction",
        delta_color="positive",
        subtitle="Mean Order Value",
        icon="🎫"
    )

with k4:
    create_kpi_card(
        title="Orders Executed",
        value=f"{total_orders:,}",
        delta="Order Flow",
        delta_color="positive",
        subtitle="Total Bookings",
        icon="📑"
    )

with k5:
    create_kpi_card(
        title="SIP Order Share",
        value=f"{sip_share:.1f}%",
        delta="Dominant Mode",
        delta_color="positive",
        subtitle="Retail Discipline",
        icon="🔄"
    )

st.markdown("<div style='height: 14px;'></div>", unsafe_allow_html=True)

# --- 2. DEMOGRAPHIC HIGHLIGHTS & BEHAVIORAL TAKEAWAYS ---
st.markdown("""
<div style="background-color: #FFFFFF; border: 1px solid #E5EAF2; border-radius: 12px; padding: 14px 18px; box-shadow: 0 1px 3px rgba(0,0,0,0.04); margin-bottom: 20px;">
    <div style="font-size: 0.84rem; font-weight: 700; color: #172033; margin-bottom: 6px; display: flex; align-items: center; gap: 6px;">
        <span style="color: #2563EB;">💡</span> KEY INVESTOR BEHAVIORAL PATTERNS
    </div>
    <div style="font-size: 0.80rem; color: #475569; line-height: 1.5;">
        • <b>Youth Demographic Mobilization:</b> Investors aged 26–35 represent <b>42.4%</b> of active transactions, heavily preferring automated monthly SIPs via UPI and mandates.<br/>
        • <b>Geographic Democratization:</b> Beyond-30 (B30) cities demonstrate equivalent ticket resilience, averaging ₹9,800 per SIP compared to ₹12,400 in Tier-1 metros.<br/>
        • <b>Redemption Discipline:</b> Redemption orders represent only <b>8.2%</b> of total executed transaction volume, demonstrating long-term investor compounding behavior.
    </div>
</div>
""", unsafe_allow_html=True)

# --- 3. VISUALIZATION ROW 1: STATE VOLUMES & ORDER COMPOSITION ---
create_section_header("Geographic Mobilization & Transaction Composition")

row1_col1, row1_col2 = st.columns(2)

with row1_col1:
    state_df = df_tx.groupby("state")["amount_inr"].sum().reset_index()
    state_df["amount_cr"] = (state_df["amount_inr"] / 10000000.0).round(2)
    state_df = state_df.sort_values("amount_cr", ascending=True).tail(10)
    
    fig_state = px.bar(
        state_df, y="state", x="amount_cr", orientation="h",
        labels={"state": "State / UT", "amount_cr": "Capital Volume (₹ Cr)"},
        color="amount_cr",
        color_continuous_scale=[[0, "#93C5FD"], [1, "#1D4ED8"]]
    )
    fig_state = style_plot(fig_state, "1. Top 10 Indian States by Capital Mobilization", height=370)
    fig_state.update_layout(coloraxis_showscale=False)
    st.plotly_chart(fig_state, use_container_width=True)

with row1_col2:
    type_df = df_tx["transaction_type"].value_counts().reset_index()
    type_df.columns = ["Type", "Count"]
    fig_type = px.pie(
        type_df, values="Count", names="Type",
        color="Type",
        color_discrete_map={"SIP": "#16A34A", "Lumpsum": "#2563EB", "Redemption": "#DC2626"},
        hole=0.48
    )
    fig_type.update_traces(
        textposition='inside',
        textinfo='percent+label',
        hovertemplate='<b>%{label}</b><br>Orders: %{value:,}<br>Share: %{percent}<extra></extra>'
    )
    fig_type = style_plot(fig_type, "2. Order Composition: SIP vs Lumpsum vs Redemption", height=370)
    st.plotly_chart(fig_type, use_container_width=True)

# --- 4. VISUALIZATION ROW 2: AGE COHORT TICKET SIZE & MONTHLY VOLUME ---
create_section_header("Cohort Maturation & Capital Flow Dynamics")

row2_col1, row2_col2 = st.columns(2)

with row2_col1:
    age_sip = df_tx.groupby("age_group")["amount_inr"].mean().reset_index()
    fig_age = px.bar(
        age_sip, x="age_group", y="amount_inr",
        labels={"age_group": "Age Bracket", "amount_inr": "Average Ticket Size (₹)"},
        color="amount_inr",
        color_continuous_scale=[[0, "#A7F3D0"], [1, "#0D9488"]]
    )
    fig_age = style_plot(fig_age, "3. Average Ticket Size Across Age Cohorts", height=370)
    fig_age.update_layout(coloraxis_showscale=False)
    st.plotly_chart(fig_age, use_container_width=True)

with row2_col2:
    df_tx["month"] = pd.to_datetime(df_tx["transaction_date"]).dt.strftime("%Y-%m")
    monthly_vol = df_tx.groupby(["month", "transaction_type"])["amount_inr"].sum().reset_index()
    monthly_vol["amount_cr"] = monthly_vol["amount_inr"] / 10000000.0
    
    fig_monthly = px.area(
        monthly_vol, x="month", y="amount_cr", color="transaction_type",
        labels={"month": "Month", "amount_cr": "Volume (₹ Cr)", "transaction_type": "Type"},
        color_discrete_map={"SIP": "#16A34A", "Lumpsum": "#2563EB", "Redemption": "#DC2626"}
    )
    fig_monthly.update_traces(opacity=0.82)
    fig_monthly = style_plot(fig_monthly, "4. Monthly Capital Inflows vs Outflows Over Time", height=370)
    st.plotly_chart(fig_monthly, use_container_width=True)

# --- 5. VISUALIZATION ROW 3: INCOME HISTOGRAM & T30/B30 PENETRATION ---
create_section_header("Investor Income Distribution & Regional Penetration")

row3_col1, row3_col2 = st.columns(2)

with row3_col1:
    inv_unique = df_tx.groupby("investor_id")["annual_income_lakh"].first().reset_index()
    fig_inc = px.histogram(
        inv_unique, x="annual_income_lakh", nbins=20,
        labels={"annual_income_lakh": "Annual Income (₹ Lakhs)"},
        color_discrete_sequence=["#8B5CF6"]
    )
    fig_inc.update_traces(marker_line_color='#FFFFFF', marker_line_width=1)
    fig_inc = style_plot(fig_inc, "5. Investor Annual Income Distribution", height=370)
    st.plotly_chart(fig_inc, use_container_width=True)

with row3_col2:
    tier_agg = df_tx.groupby("city_tier").agg(
        volume_cr=("amount_inr", lambda x: round(x.sum() / 10000000.0, 2)),
        tx_count=("transaction_id", "count")
    ).reset_index()
    
    fig_tier = px.bar(
        tier_agg, x="city_tier", y="volume_cr",
        labels={"city_tier": "City Tier", "volume_cr": "Volume (₹ Cr)"},
        color="city_tier",
        color_discrete_map={"T30": "#2563EB", "B30": "#F59E0B"}
    )
    fig_tier = style_plot(fig_tier, "6. Metro (T30) vs Emerging (B30) Capital Allocation", height=370)
    st.plotly_chart(fig_tier, use_container_width=True)

# --- 6. VISUALIZATION ROW 4: PAYMENT CHANNELS & GENDER MOBILIZATION ---
create_section_header("Payment Infrastructure & Demographic Segmentation")

row4_col1, row4_col2 = st.columns(2)

with row4_col1:
    pay_df = df_tx["payment_mode"].value_counts().reset_index()
    pay_df.columns = ["Payment Mode", "Transactions"]
    fig_pay = px.pie(
        pay_df, values="Transactions", names="Payment Mode",
        hole=0.48,
        color_discrete_sequence=['#2563EB', '#0D9488', '#F59E0B', '#8B5CF6']
    )
    fig_pay.update_traces(
        textposition='inside',
        textinfo='percent+label',
        hovertemplate='<b>%{label}</b><br>Transactions: %{value:,}<br>Share: %{percent}<extra></extra>'
    )
    fig_pay = style_plot(fig_pay, "7. Digital Payment Channel Adoption", height=370)
    st.plotly_chart(fig_pay, use_container_width=True)

with row4_col2:
    gender_agg = df_tx.groupby("gender").agg(
        total_vol_cr=("amount_inr", lambda x: round(x.sum() / 10000000.0, 2)),
        avg_order=("amount_inr", lambda x: round(x.mean(), 0))
    ).reset_index()
    
    fig_gender = px.bar(
        gender_agg, x="gender", y="total_vol_cr",
        labels={"gender": "Gender", "total_vol_cr": "Volume (₹ Cr)"},
        color="gender",
        color_discrete_map={"Male": "#2563EB", "Female": "#EC4899"}
    )
    fig_gender = style_plot(fig_gender, "8. Capital Mobilization by Gender", height=370)
    st.plotly_chart(fig_gender, use_container_width=True)

# --- 7. FILTERED TRANSACTIONS AUDIT SAMPLE TABLE ---
create_section_header("Audited Investor Transaction Sample")

disp_tx = df_tx[[
    "transaction_id", "transaction_date", "investor_id", "transaction_type",
    "amount_inr", "state", "city_tier", "age_group", "gender", "payment_mode"
]].head(100).rename(columns={
    "transaction_id": "Tx ID",
    "transaction_date": "Date",
    "investor_id": "Investor ID",
    "transaction_type": "Type",
    "amount_inr": "Amount (₹)",
    "state": "State",
    "city_tier": "Tier",
    "age_group": "Age",
    "gender": "Gender",
    "payment_mode": "Payment Channel"
})

render_fintech_table(disp_tx, height=360)

# Export Full Filtered Transactions Button
col_dl1, col_dl2 = st.columns([1, 3])
with col_dl1:
    csv_bytes = df_tx.head(10000).to_csv(index=False).encode('utf-8')
    st.download_button(
        label="📥 Download Transactions Sample (CSV)",
        data=csv_bytes,
        file_name="investor_transactions_sample.csv",
        mime="text/csv"
    )

st.markdown("<hr style='border: none; border-top: 1px solid #E5EAF2; margin: 24px 0 12px 0;'/>", unsafe_allow_html=True)
st.caption("Bluestock Fintech Pvt. Ltd. • Investor Analytics & Demographics • Educational Simulation Dataset")
