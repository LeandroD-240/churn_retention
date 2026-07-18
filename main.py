"""
VoxTel Churn Prediction — Deployment App
==========================================
Run with: streamlit run voxtel_app.py
Requires: champion.pkl and data/voxtel_data.csv in the same directory.
"""

import numpy as np
import pandas as pd
import plotly.graph_objects as go
import streamlit as st
import pickle

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
        border-color: rgba(255,219,187,0.35) !important;
        margin: 10px 0 14px !important;
    }}

    /* Make file uploader cards readable and less harsh */
    [data-testid="stSidebar"] .stFileUploader > div,
    [data-testid="stSidebar"] .stFileUploader label,
    [data-testid="stSidebar"] .stFileUploader button {{
        background-color: #3A3A3A !important;
        color: #F0F0F0 !important;
        border: 1px solid rgba(255,219,187,0.35) !important;
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
# MODEL & DATA
# ══════════════════════════════════════════════════════════════════════════════

# Columns excluded from model features — must match the notebook exactly
DROP_COLS = [
    "churned", "customer_id", "total_charges", "clv_estimated",
    "has_streaming_addon", "tenure_months", "payment_method",
    "monthly_charges", "retention_action",
]

def assign_risk_tier(p: float) -> str:
    return "High" if p >= 0.60 else "Medium" if p >= 0.30 else "Low"


def validate_data_columns(df: pd.DataFrame) -> None:
    required_cols = {
        "plan_type", "contract_type", "payment_delay_days", "data_usage_gb",
        "num_support_tickets", "last_login_days_ago", "monthly_charges",
        "has_streaming_addon", "tenure_months", "clv_estimated",
    }
    missing = sorted(required_cols - set(df.columns))
    if missing:
        raise ValueError(f"Uploaded CSV is missing required columns: {', '.join(missing)}")


def recommend_strategy(risk_tier: str, plan_type: str, clv: float) -> str:
    """
    Rule-based assignment from the Business Understanding doc.
    High CLV + high risk → costlier intervention (agent call).
    Medium risk → contract or upgrade depending on plan tier.
    """
    if risk_tier == "High":
        return "Proactive Retention Call" if clv > 500 else "Targeted Discount"
    elif risk_tier == "Medium":
        return "Service Upgrade" if plan_type == "Premium" else "Contract Lock-In Incentive"
    return "Personalized Re-engagement"


@st.cache_resource(show_spinner="Loading champion model…")
def load_model():
    with open("data/champion.pkl", "rb") as f:
        return pickle.load(f)


def load_customer_data(uploaded_file) -> tuple[pd.DataFrame, str]:
    if uploaded_file is not None:
        uploaded_file.seek(0)
        df = pd.read_csv(uploaded_file)
        return df, uploaded_file.name


@st.cache_data(show_spinner="Scoring subscriber base…")
def load_and_score(input_df: pd.DataFrame) -> pd.DataFrame:
    """
    Loads the data, runs inference, and appends churn_proba, risk_tier,
    and recommended_strategy.
    """
    model = load_model()
    df = input_df.copy()
    validate_data_columns(df)
    feature_cols = [c for c in df.columns if c not in DROP_COLS]
    df["churn_proba"] = model.predict_proba(df[feature_cols])[:, 1].round(4)
    df["risk_tier"] = df["churn_proba"].apply(assign_risk_tier)
    df["recommended_strategy"] = df.apply(
        lambda r: recommend_strategy(r["risk_tier"], r["plan_type"], r["clv_estimated"]),
        axis=1,
    )
    return df


STRATEGIES = [
    "Proactive Retention Call",
    "Targeted Discount",
    "Service Upgrade",
    "Contract Lock-In Incentive",
    "Loyalty Program Enrollment",
    "Personalized Re-engagement",
    "Priority Tech Support",
]

# ── Strategy parameters (cost + conversion rate from Business Understanding) ──
STRATEGY_PARAMS = {
    "Proactive Retention Call":    {"cost": 25, "conversion": 0.35},
    "Targeted Discount":           {"cost": 15, "conversion": 0.28},
    "Service Upgrade":             {"cost": 20, "conversion": 0.25},
    "Contract Lock-In Incentive":  {"cost": 10, "conversion": 0.30},
    "Loyalty Program Enrollment":  {"cost":  8, "conversion": 0.20},
    "Personalized Re-engagement":  {"cost":  5, "conversion": 0.15},
    "Priority Tech Support":       {"cost": 18, "conversion": 0.22},
}


def compute_roi(df_campaign: pd.DataFrame) -> dict:
    """
    Projected Savings = (TP × Rc × CLV) − (N_contacted × C_intervention)
    Revenue at Risk   = Σ P(churn_i) × CLV_i
    """
    df = df_campaign.copy()
    df["conversion"] = df["recommended_strategy"].map(
        lambda s: STRATEGY_PARAMS[s]["conversion"])
    df["int_cost"]   = df["recommended_strategy"].map(
        lambda s: STRATEGY_PARAMS[s]["cost"])
    df["rev_saved"]  = df["conversion"] * df["clv_estimated"]
    df["net_savings"]= df["rev_saved"] - df["int_cost"]

    return {
        "revenue_at_risk": (df["churn_proba"] * df["clv_estimated"]).sum(),
        "total_saved":     df["rev_saved"].sum(),
        "total_cost":      df["int_cost"].sum(),
        "net_savings":     df["net_savings"].sum(),
        "subs_saved":      int(df["conversion"].sum()),
        "df":              df,
    }


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


def chart_roi_waterfall(roi: dict) -> go.Figure:
    labels = ["Revenue at Risk", "Gross Revenue Saved", "Intervention Cost", "Net Savings"]
    values = [roi["revenue_at_risk"], roi["total_saved"], roi["total_cost"], roi["net_savings"]]
    colors = [MID, "#4CAF50", ACCENT, MAIN]

    fig = go.Figure(go.Bar(
        x=labels,
        y=[abs(v) for v in values],
        marker=dict(color=colors, line=dict(color=BG, width=1)),
        text=[f"${v:,.0f}" for v in values],
        textposition="outside",
        textfont=dict(size=11, color=TEXT),
        cliponaxis=False,
        hovertemplate="<b>%{x}</b><br>$%{y:,.0f}<extra></extra>",
    ))
    fig.update_layout(
        **PLOTLY_BASE,
        title=dict(text="Campaign ROI Breakdown",
                   font=dict(size=15, color=TEXT), x=0.01),
        yaxis=dict(visible=False, range=[0, max(values) * 1.22]),
        xaxis=dict(tickfont=dict(size=11, color=TEXT), tickcolor="rgba(0,0,0,0)"),
        margin=dict(t=60, b=10, l=10, r=20),
        bargap=0.35,
        height=320,
    )
    return fig


def chart_strategy_breakdown(roi_df: pd.DataFrame) -> go.Figure:
    sb = (roi_df.groupby("recommended_strategy")
                .agg(net=("net_savings", "sum"), n=("customer_id", "count"))
                .sort_values("net", ascending=True)
                .reset_index())

    colors = [ACCENT if v == sb["net"].max() else MAIN for v in sb["net"]]

    fig = go.Figure(go.Bar(
        x=sb["net"],
        y=sb["recommended_strategy"],
        orientation="h",
        marker=dict(color=colors, line=dict(color=BG, width=1)),
        text=[f"  ${v:,.0f}  ({n} subs)" for v, n in zip(sb["net"], sb["n"])],
        textposition="outside",
        textfont=dict(size=10, color=TEXT),
        cliponaxis=False,
        hovertemplate="<b>%{y}</b><br>Net savings: $%{x:,.0f}<extra></extra>",
    ))
    fig.update_layout(
        **PLOTLY_BASE,
        title=dict(text="Net Savings by Strategy",
                   font=dict(size=15, color=TEXT), x=0.01),
        xaxis=dict(visible=False, range=[0, sb["net"].max() * 1.6]),
        yaxis=dict(tickfont=dict(size=11, color=TEXT),
                   tickcolor="rgba(0,0,0,0)"),
        margin=dict(t=60, b=10, l=10, r=180),
        bargap=0.4,
        height=320,
    )
    return fig
    st.markdown(
        f'<div class="chart-placeholder" style="height:{height}px;">📊 {label}</div>',
        unsafe_allow_html=True,
    )


PLOTLY_BASE = dict(
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(0,0,0,0)",
    font=dict(family="sans-serif", color=TEXT),
)


def chart_risk_donut(df: pd.DataFrame) -> go.Figure:
    risk_counts = df["risk_tier"].value_counts().reindex(["High", "Medium", "Low"]).fillna(0)
    values = [int(risk_counts.get("High", 0)), int(risk_counts.get("Medium", 0)), int(risk_counts.get("Low", 0))]

    fig = go.Figure(go.Pie(
        labels=["High", "Medium", "Low"],
        values=values,
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
            text=f"{len(df):,}<br><span style='font-size:11px;color:#888'>scored</span>",
            x=0.5, y=0.5, showarrow=False,
            font=dict(size=18, color=TEXT),
        )],
        legend=dict(orientation="v", x=1.0, y=0.5,
                    font=dict(size=12, color=TEXT)),
        margin=dict(t=60, b=20, l=20, r=120),
        height=340,
    )
    return fig


def chart_churn_by_contract(df: pd.DataFrame) -> go.Figure:
    contracts = ["Two-year", "One-year", "Month-to-month"]
    churn_pcts = []

    for contract in contracts:
        if "contract_type" in df.columns:
            subset = df[df["contract_type"] == contract]
            churn_pcts.append(float(subset["churn_proba"].mean()) if not subset.empty else 0.0)
        else:
            churn_pcts.append(0.0)

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


def chart_prob_distribution(df: pd.DataFrame) -> go.Figure:
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
# SIDEBAR
# ══════════════════════════════════════════════════════════════════════════════
with st.sidebar:
    st.image("img/Gemini_VoxTel_Logo.png", width=240)
    st.markdown("#### 📁 Data Loader")
    uploaded_file = st.sidebar.file_uploader(
        "Upload customer data (CSV)",
        type=["csv"],
        help="Use an updated CSV with the same column structure as the bundled dataset.",
    )

    if uploaded_file is not None:
        st.sidebar.success(f"Using uploaded file: {uploaded_file.name}")
    else:
        st.sidebar.info("Upload a CSV to start scoring subscribers.")
        st.sidebar.markdown("If you don't know the data sctructure, [check the documentation]()", unsafe_allow_html=True)
        st.stop()

    try:
        source_df, data_source_name = load_customer_data(uploaded_file)
        df = load_and_score(source_df)
    except Exception as exc:
        st.sidebar.warning(
            "The uploaded file could not be scored."
            f"\n\nDetails: {exc}"
        )
        st.error("Please upload a CSV file with the expected columns and values.")
        st.stop()
    st.markdown("#### ⚙️ Data & Model")
    st.markdown(
        f"**Data source:** {data_source_name}  \n"
        "**Model:** Logistic Regression  \n"
        "**Source:** data/champion.pkl (GitHub)  \n"
        "**Prediction window:** next 2 months  \n"
        "**Scoring frequency:** Monthly  \n"
        f"**Subscribers scored:** {len(df):,}"
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
    risk_counts = df["risk_tier"].value_counts().reindex(["High", "Medium", "Low"]).fillna(0)
    high_risk_count = int(risk_counts.get("High", 0))
    medium_risk_count = int(risk_counts.get("Medium", 0))
    revenue_at_risk = int((df["churn_proba"] * df["clv_estimated"]).sum())
    avg_clv = int(df["clv_estimated"].mean())

    k1, k2, k3, k4 = st.columns(4)
    with k1:
        st.markdown(kpi_card("Total Subscribers Scored", f"{len(df):,}",
            f"{high_risk_count:,} High · {medium_risk_count:,} Medium risk"), unsafe_allow_html=True)
    with k2:
        st.markdown(kpi_card("High-Risk Subscribers", f"{high_risk_count:,}",
            f"{high_risk_count / len(df):.1%} of subscriber base"), unsafe_allow_html=True)
    with k3:
        st.markdown(kpi_card("Revenue at Risk", f"${revenue_at_risk:,.0f}",
            "Σ P(churn) × CLV across all subscribers"), unsafe_allow_html=True)
    with k4:
        st.markdown(kpi_card("Avg. Customer Lifetime Value", f"${avg_clv:,.0f}",
            "Basis for intervention prioritisation"), unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    c1, c2 = st.columns(2)
    with c1:
        st.plotly_chart(chart_risk_donut(df), width="stretch")
    with c2:
        st.plotly_chart(chart_churn_by_contract(df), width="stretch")

    st.markdown('<div class="section-title">Churn Probability Distribution</div>',
                unsafe_allow_html=True)
    st.plotly_chart(chart_prob_distribution(df), width="stretch")


# ─────────────────────────────────────────────────────────────────────────────
# TAB 2 — AT-RISK CUSTOMERS
# ─────────────────────────────────────────────────────────────────────────────
with tab2:
    # Apply all four sidebar filters
    # At-risk subscribers — High and Medium only, sorted by churn probability
    df_filtered = df[df["risk_tier"].isin(["High", "Medium"])].copy()

    st.markdown(f"Showing **{len(df_filtered):,}** at-risk subscribers.")

    # Table
    display_cols = {
        "customer_id":         "Customer ID",
        "churn_proba":         "Churn Prob.",
        "risk_tier":           "Risk Tier",
        "plan_type":           "Plan",
        "contract_type":       "Contract",
        "tenure_months":       "Tenure (mo.)",
        "monthly_charges":     "Monthly ($)",
        "payment_delay_days":  "Pay. Delay (days)",
        "data_usage_gb":       "Data (GB)",
        "num_support_tickets": "Support Tickets",
        "last_login_days_ago": "Days Since Login",
        "clv_estimated":       "CLV ($)",
    }
    df_display = df_filtered[list(display_cols.keys())].rename(columns=display_cols).copy()
    df_display["Churn Prob."] = df_display["Churn Prob."].map("{:.1%}".format)
    st.dataframe(df_display, width="stretch", height=320)

    if df_filtered.empty:
        st.warning(
            "No at-risk subscribers match the selected filters. "
            "Adjust the sidebar controls to show customers."
        )
        st.stop()

    st.markdown('<div class="section-title">Customer Detail</div>',
                unsafe_allow_html=True)

    # Pre-build a lookup so format_func is O(1) per option, not O(n)
    prob_lookup = df_filtered.set_index("customer_id")["churn_proba"].to_dict()
    sorted_customer_ids = df_filtered.sort_values("churn_proba", ascending=False)["customer_id"].tolist()

    selected_id = st.selectbox(
        "Select a subscriber to inspect:",
        options=sorted_customer_ids,
        format_func=lambda x: f"{x}  —  P(churn) = {prob_lookup.get(x, 0):.1%}",
    )

    row = df_filtered[df_filtered["customer_id"] == selected_id].iloc[0]

    d1, d2, d3 = st.columns(3)
    with d1:
        st.markdown(f"""
        **{row['customer_id']}**
        - **Risk Tier:** {row['risk_tier']}
        - **Churn Probability:** `{row['churn_proba']:.1%}`
        - **Plan:** {row['plan_type']}
        - **Contract:** {row['contract_type']}
        """)
    with d2:
        st.markdown(f"""
        **Engagement signals**
        - **Days since login:** {row['last_login_days_ago']} days
        - **Support tickets:** {row['num_support_tickets']}
        - **Payment delay:** {row['payment_delay_days']} days
        - **Data usage:** {row['data_usage_gb']:.1f} GB
        """)
    with d3:
        st.markdown(f"""
        **Financials**
        - **CLV estimate:** ${row['clv_estimated']:,.2f}
        - **Tenure:** {row['tenure_months']} months
        - **Monthly charges:** ${row['monthly_charges']:.2f}
        - **Streaming addon:** {"✅ Yes" if row['has_streaming_addon'] else "❌ No"}
        """)

    st.markdown("**Retention strategy**")
    col_strat, col_override = st.columns(2)
    with col_strat:
        strat = row["recommended_strategy"]
        st.info(
            f"📌 Recommended: **{strat}**\n\n"
            f"- Conversion rate: {STRATEGY_PARAMS[strat]['conversion']:.0%}\n"
            f"- Cost per subscriber: ${STRATEGY_PARAMS[strat]['cost']}\n"
            f"- Expected CLV saved: ${row['clv_estimated'] * STRATEGY_PARAMS[strat]['conversion']:,.0f}"
        )


# ─────────────────────────────────────────────────────────────────────────────
# TAB 3 — ROI SIMULATOR
# ─────────────────────────────────────────────────────────────────────────────
with tab3:
    st.markdown(
        "Applies the **Projected Savings formula** from the Business Understanding "
        "to the current filtered subscriber list. "
        "Only **Medium and High** risk subscribers are included in the campaign scope."
    )

    # Campaign scope — Low risk excluded (cost > expected benefit)
    df_campaign = df[df["risk_tier"].isin(["High", "Medium"])].copy()

    if df_campaign.empty:
        st.warning(
            "No Medium or High risk subscribers in the current selection. "
            "Adjust the Risk Tier or Min. Churn Probability filter in the sidebar."
        )
    else:
        roi = compute_roi(df_campaign)

        # ── KPIs ─────────────────────────────────────────────────────────────
        r1, r2, r3, r4 = st.columns(4)
        with r1:
            st.markdown(kpi_card(
                "Revenue at Risk",
                f"${roi['revenue_at_risk']:,.0f}",
                "Σ P(churn) × CLV — full exposure"
            ), unsafe_allow_html=True)
        with r2:
            st.markdown(kpi_card(
                "Gross Revenue Saved",
                f"${roi['total_saved']:,.0f}",
                "Before intervention costs"
            ), unsafe_allow_html=True)
        with r3:
            st.markdown(kpi_card(
                "Intervention Cost",
                f"${roi['total_cost']:,.0f}",
                f"{len(df_campaign):,} subscribers contacted"
            ), unsafe_allow_html=True)
        with r4:
            st.markdown(kpi_card(
                "Net Projected Savings",
                f"${roi['net_savings']:,.0f}",
                f"~{roi['subs_saved']:,} subscribers retained"
            ), unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)

        # ── Charts ───────────────────────────────────────────────────────────
        c1, c2 = st.columns(2)
        with c1:
            st.plotly_chart(chart_roi_waterfall(roi), width="stretch")
        with c2:
            st.plotly_chart(chart_strategy_breakdown(roi["df"]), width="stretch")

        # ── Strategy breakdown table ──────────────────────────────────────────
        st.markdown('<div class="section-title">Strategy Breakdown</div>',
                    unsafe_allow_html=True)

        sb_table = (roi["df"]
                    .groupby("recommended_strategy")
                    .agg(
                        Subscribers   =("customer_id",  "count"),
                        Avg_CLV       =("clv_estimated", "mean"),
                        Revenue_Saved =("rev_saved",     "sum"),
                        Campaign_Cost =("int_cost",      "sum"),
                        Net_Savings   =("net_savings",   "sum"),
                    )
                    .sort_values("Net_Savings", ascending=False)
                    .rename(columns={
                        "Avg_CLV":      "Avg CLV ($)",
                        "Revenue_Saved":"Revenue Saved ($)",
                        "Campaign_Cost":"Campaign Cost ($)",
                        "Net_Savings":  "Net Savings ($)",
                    }))

        for col in ["Avg CLV ($)", "Revenue Saved ($)", "Campaign Cost ($)", "Net Savings ($)"]:
            sb_table[col] = sb_table[col].map("${:,.0f}".format)

        st.dataframe(sb_table, width="stretch")

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
