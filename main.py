"""
VoxTel Churn Prediction — UI Draft
====================================
Static layout preview — no model, no data, no charts.
Run with: streamlit run voxtel_app.py
"""

import numpy as np
import pandas as pd
import plotly.graph_objects as go
import streamlit as st

# ══════════════════════════════════════════════════════════════════════════════
# PAGE CONFIG
# ══════════════════════════════════════════════════════════════════════════════
st.set_page_config(
    page_title="VoxTel · Churn Predictor",
    page_icon="📡",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ══════════════════════════════════════════════════════════════════════════════
# BRAND PALETTE & CSS
# ══════════════════════════════════════════════════════════════════════════════
MAIN   = "#FFDBBB"
ACCENT = "#E55934"
BG     = "#FFFFFF"
TEXT   = "#2D2D2D"
MID    = "#888888"

st.markdown(f"""
<style>
    .stApp {{ background-color: #F7F7F7; }}

    [data-testid="stSidebar"] {{ background-color: {TEXT}; }}

    /* Make every text node in the sidebar readable */
    [data-testid="stSidebar"] * {{ color: #F0F0F0 !important; }}

    /* Section headings use the brand peach */
    [data-testid="stSidebar"] h1,
    [data-testid="stSidebar"] h2,
    [data-testid="stSidebar"] h3,
    [data-testid="stSidebar"] h4 {{ color: {MAIN} !important; }}

    /* Multiselect: chip/tag background so selected items are visible */
    [data-testid="stSidebar"] [data-baseweb="tag"] {{
        background-color: rgba(229,89,52,0.35) !important;
        border-radius: 4px !important;
    }}

    /* Slider track fill */
    [data-testid="stSidebar"] [data-testid="stSlider"] [role="slider"] {{
        background-color: {ACCENT} !important;
    }}

    /* Dropdown / select input background */
    [data-testid="stSidebar"] [data-baseweb="select"] div {{
        background-color: #3A3A3A !important;
    }}

    /* Horizontal rule */
    [data-testid="stSidebar"] hr {{
        border-color: rgba(255,219,187,0.25) !important;
    }}

    .kpi-card {{
        background: {BG}; border-radius: 12px;
        padding: 18px 22px; border-left: 5px solid {ACCENT};
        box-shadow: 0 2px 8px rgba(0,0,0,0.07);
    }}
    .kpi-value {{
        font-size: 30px; font-weight: 700;
        color: {ACCENT}; margin: 4px 0 2px; font-family: monospace;
    }}
    .kpi-label {{
        font-size: 12px; color: {MID};
        text-transform: uppercase; letter-spacing: 0.6px;
    }}
    .kpi-sub {{ font-size: 12px; color: {MID}; margin-top: 4px; }}

    .section-title {{
        font-size: 17px; font-weight: 700; color: {TEXT};
        margin: 20px 0 10px; padding-bottom: 5px;
        border-bottom: 2px solid {MAIN};
    }}

    .timing-banner {{
        background: #FFF3E0; border: 1px solid {ACCENT};
        border-radius: 8px; padding: 12px 18px;
        font-size: 13px; color: #BF360C; margin-bottom: 20px;
    }}

    .chart-placeholder {{
        background: #F5F5F5;
        border: 2px dashed #DDDDDD;
        border-radius: 10px;
        display: flex;
        align-items: center;
        justify-content: center;
        color: {MID};
        font-size: 14px;
        font-style: italic;
    }}

    .stTabs [aria-selected="true"] {{
        color: {ACCENT} !important;
        border-bottom-color: {ACCENT} !important;
    }}
</style>
""", unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
# HELPERS
# ══════════════════════════════════════════════════════════════════════════════
def kpi_card(label: str, value: str, sub: str = "") -> str:
    sub_html = f'<div class="kpi-sub">{sub}</div>' if sub else ""
    return f"""
    <div class="kpi-card">
        <div class="kpi-label">{label}</div>
        <div class="kpi-value">{value}</div>
        {sub_html}
    </div>"""


PLOTLY_BASE = dict(
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(0,0,0,0)",
    font=dict(family="sans-serif", color=TEXT),
)


def chart_risk_donut() -> go.Figure:
    fig = go.Figure(go.Pie(
        labels=["High", "Medium", "Low"],
        values=[1662, 140, 3198],
        hole=0.58,
        sort=False,
        marker=dict(
            colors=[ACCENT, "#FF9800", "#4CAF50"],
            line=dict(color=BG, width=4),
        ),
        textinfo="percent",
        textfont=dict(size=12),
        hovertemplate="<b>%{label}</b><br>%{value:,} subscribers — %{percent}<extra></extra>",
    ))
    fig.update_layout(
        **PLOTLY_BASE,
        title=dict(text="Subscriber Risk Distribution",
                   font=dict(size=15, color=TEXT), x=0.01),
        annotations=[dict(
            text="5,000<br><span style='font-size:11px;color:#888'>scored</span>",
            x=0.5, y=0.5, showarrow=False,
            font=dict(size=18, color=TEXT),
        )],
        legend=dict(orientation="v", x=1.0, y=0.5,
                    font=dict(size=12, color=TEXT)),
        margin=dict(t=60, b=20, l=20, r=120),
        height=340,
    )
    return fig


def chart_churn_by_contract() -> go.Figure:
    contracts  = ["Two-year", "One-year", "Month-to-month"]
    churn_pcts = [0.08, 0.18, 0.52]

    fig = go.Figure(go.Bar(
        x=churn_pcts, y=contracts, orientation="h",
        marker=dict(
            color=[MAIN, MAIN, ACCENT],
            line=dict(color=BG, width=1),
        ),
        text=[f"{v:.0%}" for v in churn_pcts],
        textposition="outside",
        textfont=dict(size=12, color=TEXT),
        cliponaxis=False,
        hovertemplate="<b>%{y}</b><br>Avg churn probability: %{x:.1%}<extra></extra>",
    ))
    fig.update_layout(
        **PLOTLY_BASE,
        title=dict(text="Avg. Churn Probability by Contract",
                   font=dict(size=15, color=TEXT), x=0.01),
        xaxis=dict(visible=False, range=[0, 0.70]),
        yaxis=dict(tickfont=dict(size=12, color=TEXT),
                   tickcolor="rgba(0,0,0,0)"),
        margin=dict(t=60, b=20, l=10, r=70),
        bargap=0.45,
        height=300,
    )
    return fig


def chart_prob_distribution() -> go.Figure:
    np.random.seed(42)
    probs = np.concatenate([
        np.random.beta(1.2, 8,  3198),   # Low risk cluster
        np.random.beta(3,   4,   140),   # Medium risk cluster
        np.random.beta(7,   2,  1662),   # High risk cluster
    ])

    fig = go.Figure(go.Histogram(
        x=probs, nbinsx=40,
        marker=dict(color=MAIN, line=dict(color=BG, width=0.5)),
        hovertemplate="P(churn) ≈ %{x:.2f}<br>Subscribers: %{y}<extra></extra>",
    ))

    for thresh, label, color in [
        (0.30, "Medium risk (0.30)", "#FF9800"),
        (0.60, "High risk (0.60)",   ACCENT),
    ]:
        fig.add_vline(x=thresh, line=dict(color=color, width=2, dash="dash"))
        fig.add_annotation(
            x=thresh + 0.02, y=0.93, yref="paper",
            text=label, showarrow=False,
            font=dict(color=color, size=11), xanchor="left",
        )

    fig.update_layout(
        **PLOTLY_BASE,
        title=dict(
            text="Churn Probability Distribution",
            subtitle=dict(
                text="Most subscribers cluster near 0 — focus intervention on the right tail"
            ),
            font=dict(size=15, color=TEXT), x=0.01,
        ),
        xaxis=dict(
            title="Predicted Churn Probability", range=[0, 1],
            tickfont=dict(color=TEXT),
        ),
        yaxis=dict(visible=False),
        showlegend=False,
        margin=dict(t=80, b=50, l=10, r=20),
        bargap=0.05,
        height=300,
    )
    return fig


# ══════════════════════════════════════════════════════════════════════════════
# SAMPLE DATA  (hardcoded — no CSV or model needed)
# ══════════════════════════════════════════════════════════════════════════════
SAMPLE_CUSTOMERS = pd.DataFrame([
    {"Customer ID": "C-00103", "Churn Prob.": "87%", "Risk Tier": "High",
     "Plan": "Basic",    "Contract": "Month-to-month", "CLV ($)": "$312",
     "Pay. Delay": 18, "Data (GB)": 0.4, "Support Tickets": 4,
     "Days Since Login": 62, "Recommended Strategy": "Targeted Discount"},
    {"Customer ID": "C-00247", "Churn Prob.": "79%", "Risk Tier": "High",
     "Plan": "Standard", "Contract": "Month-to-month", "CLV ($)": "$890",
     "Pay. Delay": 9,  "Data (GB)": 2.1, "Support Tickets": 3,
     "Days Since Login": 45, "Recommended Strategy": "Proactive Retention Call"},
    {"Customer ID": "C-00891", "Churn Prob.": "71%", "Risk Tier": "High",
     "Plan": "Premium",  "Contract": "Month-to-month", "CLV ($)": "$1,540",
     "Pay. Delay": 3,  "Data (GB)": 5.8, "Support Tickets": 2,
     "Days Since Login": 38, "Recommended Strategy": "Proactive Retention Call"},
    {"Customer ID": "C-01204", "Churn Prob.": "44%", "Risk Tier": "Medium",
     "Plan": "Standard", "Contract": "One-year",       "CLV ($)": "$720",
     "Pay. Delay": 5,  "Data (GB)": 7.2, "Support Tickets": 1,
     "Days Since Login": 12, "Recommended Strategy": "Contract Lock-In Incentive"},
    {"Customer ID": "C-01589", "Churn Prob.": "38%", "Risk Tier": "Medium",
     "Plan": "Premium",  "Contract": "One-year",       "CLV ($)": "$2,100",
     "Pay. Delay": 0,  "Data (GB)": 18.4,"Support Tickets": 1,
     "Days Since Login": 4,  "Recommended Strategy": "Service Upgrade"},
    {"Customer ID": "C-02034", "Churn Prob.": "12%", "Risk Tier": "Low",
     "Plan": "Basic",    "Contract": "Two-year",       "CLV ($)": "$480",
     "Pay. Delay": 0,  "Data (GB)": 3.1, "Support Tickets": 0,
     "Days Since Login": 2,  "Recommended Strategy": "Personalized Re-engagement"},
])

STRATEGIES = [
    "Proactive Retention Call",
    "Targeted Discount",
    "Service Upgrade",
    "Contract Lock-In Incentive",
    "Loyalty Program Enrollment",
    "Personalized Re-engagement",
    "Priority Tech Support",
]

SAMPLE_ROI = pd.DataFrame([
    {"Strategy": "Proactive Retention Call",   "Subscribers": 842,  "Revenue Saved ($)": "$32,410", "Campaign Cost ($)": "$21,050", "Net Savings ($)": "$11,360"},
    {"Strategy": "Targeted Discount",          "Subscribers": 631,  "Revenue Saved ($)": "$14,220", "Campaign Cost ($)": "$9,465",  "Net Savings ($)": "$4,755"},
    {"Strategy": "Contract Lock-In Incentive", "Subscribers": 140,  "Revenue Saved ($)": "$7,980",  "Campaign Cost ($)": "$1,400",  "Net Savings ($)": "$6,580"},
    {"Strategy": "Service Upgrade",            "Subscribers": 72,   "Revenue Saved ($)": "$9,120",  "Campaign Cost ($)": "$1,440",  "Net Savings ($)": "$7,680"},
])


# ══════════════════════════════════════════════════════════════════════════════
# SIDEBAR
# ══════════════════════════════════════════════════════════════════════════════
with st.sidebar:
    st.markdown("## 📡 VoxTel")
    st.markdown("### Churn Prediction Dashboard")
    st.markdown("---")
    st.markdown("#### 🎯 Filter Subscribers")

    st.multiselect("Risk Tier",
        options=["High", "Medium", "Low"],
        default=["High", "Medium", "Low"])

    st.multiselect("Plan Type",
        options=["Basic", "Standard", "Premium"],
        default=["Basic", "Standard", "Premium"])

    st.multiselect("Contract Type",
        options=["Month-to-month", "One-year", "Two-year"],
        default=["Month-to-month", "One-year", "Two-year"])

    st.slider("Min. Churn Probability",
        min_value=0.0, max_value=1.0, value=0.30, step=0.05, format="%.0f%%")

    st.markdown("---")
    st.markdown("#### ⚙️ Model Info")
    st.markdown(
        "**Model:** Logistic Regression  \n"
        "**Source:** champion.pkl  \n"
        "**Prediction window:** next 2 months  \n"
        "**Scoring frequency:** Monthly  \n"
        "**Subscribers scored:** 5,000"
    )


# ══════════════════════════════════════════════════════════════════════════════
# HEADER
# ══════════════════════════════════════════════════════════════════════════════
st.markdown(f"""
<h1 style="color:{TEXT}; margin-bottom:0;">
    📡 VoxTel — Churn Prediction & Retention Planner
</h1>
<p style="color:{MID}; margin-top:4px; font-size:15px;">
    Identifying subscribers likely to churn in the next 2 months ·
    Enabling targeted retention before the window closes
</p>
""", unsafe_allow_html=True)

st.markdown("""
<div class="timing-banner">
    ⚠️ <strong>Operational reminder:</strong>
    This model flags subscribers projected to churn within the
    <strong>next 2 months</strong>.
    Retention campaigns require ~3–4 weeks from approval to execution.
    Launch all selected strategies within <strong>2–3 weeks</strong> of
    this scoring date to reach subscribers before they churn.
</div>
""", unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
# TABS
# ══════════════════════════════════════════════════════════════════════════════
tab1, tab2, tab3 = st.tabs([
    "📊  Portfolio Overview",
    "👥  At-Risk Customers",
    "💰  ROI Simulator",
])


# ─────────────────────────────────────────────────────────────────────────────
# TAB 1 — PORTFOLIO OVERVIEW
# ─────────────────────────────────────────────────────────────────────────────
with tab1:
    k1, k2, k3, k4 = st.columns(4)
    with k1:
        st.markdown(kpi_card("Total Subscribers Scored", "5,000",
            "1,662 High · 140 Medium risk"), unsafe_allow_html=True)
    with k2:
        st.markdown(kpi_card("High-Risk Subscribers", "1,662",
            "33.2% of subscriber base"), unsafe_allow_html=True)
    with k3:
        st.markdown(kpi_card("Revenue at Risk", "$337,270",
            "Σ P(churn) × CLV across all subscribers"), unsafe_allow_html=True)
    with k4:
        st.markdown(kpi_card("Avg. Customer Lifetime Value", "$1,205",
            "Basis for intervention prioritisation"), unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    c1, c2 = st.columns(2)
    with c1:
        st.plotly_chart(chart_risk_donut(), use_container_width=True)
    with c2:
        st.plotly_chart(chart_churn_by_contract(), use_container_width=True)

    st.markdown('<div class="section-title">Churn Probability Distribution</div>',
                unsafe_allow_html=True)
    st.plotly_chart(chart_prob_distribution(), use_container_width=True)


# ─────────────────────────────────────────────────────────────────────────────
# TAB 2 — AT-RISK CUSTOMERS
# ─────────────────────────────────────────────────────────────────────────────
with tab2:
    st.markdown("Showing **6** subscribers matching current filters.")
    st.dataframe(SAMPLE_CUSTOMERS, use_container_width=True, height=280)

    st.markdown('<div class="section-title">Customer Detail</div>',
                unsafe_allow_html=True)

    selected_id = st.selectbox(
        "Select a subscriber to inspect:",
        options=SAMPLE_CUSTOMERS["Customer ID"].tolist(),
    )

    row = SAMPLE_CUSTOMERS[SAMPLE_CUSTOMERS["Customer ID"] == selected_id].iloc[0]

    d1, d2, d3 = st.columns(3)
    with d1:
        st.markdown(f"""
        **{row['Customer ID']}**
        - **Risk Tier:** {row['Risk Tier']}
        - **Churn Probability:** `{row['Churn Prob.']}`
        - **Plan:** {row['Plan']}
        - **Contract:** {row['Contract']}
        """)
    with d2:
        st.markdown(f"""
        **Engagement signals**
        - **Days since login:** {row['Days Since Login']} days
        - **Support tickets:** {row['Support Tickets']}
        - **Payment delay:** {row['Pay. Delay']} days
        - **Data usage:** {row['Data (GB)']} GB
        """)
    with d3:
        st.markdown(f"""
        **Financials**
        - **CLV estimate:** {row['CLV ($)']}
        - **Tenure:** — months
        - **Monthly charges:** —
        - **Streaming addon:** —
        """)

    st.markdown("**Retention strategy**")
    col_strat, col_override = st.columns(2)
    with col_strat:
        st.info(f"📌 Recommended: **{row['Recommended Strategy']}**")
    with col_override:
        st.selectbox("Override strategy (optional):",
            options=["— keep recommendation —"] + STRATEGIES)


# ─────────────────────────────────────────────────────────────────────────────
# TAB 3 — ROI SIMULATOR
# ─────────────────────────────────────────────────────────────────────────────
with tab3:
    st.markdown(
        "Applies the **Projected Savings formula** from the Business Understanding "
        "to the current filtered subscriber list. "
        "Only Medium and High risk subscribers are included in the campaign scope."
    )

    r1, r2, r3, r4 = st.columns(4)
    with r1:
        st.markdown(kpi_card("Revenue at Risk", "$337,270",
            "Σ P(churn) × CLV — full exposure"), unsafe_allow_html=True)
    with r2:
        st.markdown(kpi_card("Gross Revenue Saved", "$63,730",
            "Before intervention costs"), unsafe_allow_html=True)
    with r3:
        st.markdown(kpi_card("Intervention Cost", "$33,355",
            "1,685 subscribers contacted"), unsafe_allow_html=True)
    with r4:
        st.markdown(kpi_card("Net Projected Savings", "$30,375",
            "~476 subscribers retained"), unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    c1, c2 = st.columns(2)
    with c1:
        chart_placeholder("Campaign ROI Waterfall", height=300)
    with c2:
        chart_placeholder("Net Savings by Strategy", height=300)

    st.markdown('<div class="section-title">Strategy Breakdown</div>',
                unsafe_allow_html=True)
    st.dataframe(SAMPLE_ROI, use_container_width=True)

    st.markdown("""
    <div class="timing-banner" style="margin-top:20px;">
        ⏱️ <strong>Campaign execution timeline:</strong>
        Budget approval (3–5 days) → Campaign design (5–7 days) →
        Execution (3–5 days) → Customer response window (7–14 days).
        Total minimum lead time: <strong>~3–4 weeks</strong>.
        Campaigns must launch within <strong>2–3 weeks</strong> of this
        scoring date to reach subscribers before they churn.
    </div>
    """, unsafe_allow_html=True)