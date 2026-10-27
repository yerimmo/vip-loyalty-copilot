import pandas as pd
import plotly.express as px
import streamlit as st
from pathlib import Path

st.set_page_config(page_title="VIP Loyalty Copilot", page_icon="💎", layout="wide", initial_sidebar_state="expanded")

BG = "#171C1B"
EMERALD = "#123D32"
SAGE = "#A3B9A4"
WHITE = "#F1F4EF"
MUTED = "#AABBB2"
BORDER = "#31463E"
CARD = "#222D29"
GREEN = "#26745D"

st.markdown("""
<style>
:root {color-scheme: dark;}
.stApp, [data-testid="stAppViewContainer"], [data-testid="stMain"] {background: #171C1B; color: #F1F4EF;}
[data-testid="stHeader"] {background: #171C1B !important;}
[data-testid="stToolbar"] {background: transparent !important;}
[data-testid="stSidebar"], [data-testid="stSidebarContent"] {background: #102B25 !important; border-right: 1px solid #31463E;}
[data-testid="stSidebar"] * {color: #F1F4EF;}
[data-testid="stSidebar"] [role="radiogroup"] label:has(input:checked) {background: #205646; border-radius: 9px;}
[data-testid="stSidebar"] [role="radiogroup"] label {padding: 8px 10px;}
h1,h2,h3,h4,p,li,label {color: #F1F4EF;}
[data-testid="stCaptionContainer"], .stCaption {color: #AABBB2 !important;}
[data-testid="stMetric"] {background: #123D32; border: 1px solid #36564A; border-radius: 14px; padding: 20px 22px; min-height: 116px;}
[data-testid="stMetricLabel"] * {color: #A3B9A4 !important;}
[data-testid="stMetricValue"] * {color: #F1F4EF !important;}
[data-testid="stAlert"] {background: #20382F !important; border: 1px solid #36564A !important; border-radius: 10px;}
[data-testid="stAlert"] * {color: #F1F4EF !important;}
[data-testid="stDataFrame"] {border: 1px solid #31463E; border-radius: 12px; overflow: hidden;}
[data-testid="stTextInput"] input, [data-testid="stNumberInput"] input {background: #242E2B !important; color: #F1F4EF !important; border: 1px solid #36564A !important;}
[data-testid="stSelectbox"] > div > div, [data-testid="stMultiSelect"] > div > div {background: #242E2B !important; color: #F1F4EF !important; border-color: #36564A !important;}
[data-testid="stCheckbox"] label, [data-testid="stRadio"] label {color: #F1F4EF !important;}
.stButton > button, [data-testid="stDownloadButton"] button {background: #123D32; color: #F1F4EF; border: 1px solid #36564A; border-radius: 9px;}
.stButton > button:hover, [data-testid="stDownloadButton"] button:hover {background: #205646; color: white;}
hr {border-color: #31463E !important;}
.block-container {padding-top: 5.5rem !important; padding-bottom: 5rem !important;}
html {scroll-padding-top: 5.5rem;}
.dashboard-section {scroll-margin-top: 5.5rem;}
[data-testid='stSidebar'] a.nav-link {display:block; padding:12px 14px; margin:5px 0; border-radius:10px; color:#F1F4EF !important; text-decoration:none; background:#17382F; border:1px solid #31463E; font-weight:600;}
[data-testid='stSidebar'] a.nav-link:hover {background:#205646; border-color:#6C9B86;}
[data-testid='stHeader'] {height:3.5rem;}

.section-note {color: #AABBB2; margin-top: -5px; margin-bottom: 20px;}
.section-kicker {color: #A3B9A4; font-size: .76rem; letter-spacing: .14em; font-weight: 700; margin-bottom: 7px;}
.insight-card {background: #222D29; border: 1px solid #31463E; border-radius: 12px; padding: 18px 20px; margin: 10px 0 20px; color: #F1F4EF;}
.insight-card strong {color: #A3B9A4;}
</style>
""", unsafe_allow_html=True)

TIER_ORDER = ["Jasmine Signature", "Jasmine Black", "Jasmine Blue", "Jasmine", "Club YP", "Sage", "Green", "General"]
MOVEMENT_ORDER = ["New VIP", "Upgrade", "Maintain", "Downgrade", "Lost VIP"]
MOVEMENT_COLORS = {"New VIP": "#4BAF91", "Upgrade": "#26745D", "Maintain": "#A3B9A4", "Downgrade": "#8FAD9D", "Lost VIP": "#C77D78"}

@st.cache_data
def load_data():
    data_path = Path(__file__).resolve().parent / "data" / "dashboard_customers.csv"
    return pd.read_csv(data_path, dtype={"customer_id": "string"})

try:
    customers = load_data()
except FileNotFoundError:
    st.error("Could not find data/dashboard_customers.csv. Place the CSV in the data folder next to app.py.")
    st.stop()

required = {"customer_id", "vip_tier_2026", "projected_vip_tier_2027", "tier_movement", "annual_spend_2025", "ytd_spend_2026", "projected_annual_spend_2026"}
missing = required - set(customers.columns)
if missing:
    st.error("Missing required CSV columns: " + ", ".join(sorted(missing)))
    st.stop()


def style_chart(fig, height=430):
    fig.update_layout(
        paper_bgcolor=BG, plot_bgcolor=BG,
        font=dict(color=WHITE, family="Arial", size=13),
        height=height, margin=dict(l=15, r=15, t=30, b=25),
        xaxis=dict(title_font=dict(color=SAGE), tickfont=dict(color=MUTED), showgrid=False, zeroline=False, linecolor=BORDER),
        yaxis=dict(title_font=dict(color=SAGE), tickfont=dict(color=MUTED), gridcolor=BORDER, zeroline=False),
        legend=dict(font=dict(color=WHITE), bgcolor="rgba(0,0,0,0)"),
        hoverlabel=dict(bgcolor=CARD, font_color=WHITE),
    )
    return fig


def section_title(title, subtitle=None):
    st.subheader(title)
    if subtitle:
        st.markdown(f'<div class="section-note">{subtitle}</div>', unsafe_allow_html=True)


def render_table(df, height=None):

    # Show a friendly message when no customers match the filters
    if df.empty:
        st.info(
            "No customers match the selected filters. "
            "Try selecting another VIP tier or movement category."
        )
        return

    # Apply the dashboard's dark theme to the table
    styled = df.style.set_properties(**{
        "background-color": CARD,
        "color": WHITE,
        "border-color": BORDER,
    }).set_table_styles([
        {
            "selector": "th",
            "props": [
                ("background-color", EMERALD),
                ("color", WHITE)
            ]
        },
        {
            "selector": "td",
            "props": [
                ("background-color", CARD),
                ("color", WHITE)
            ]
        },
    ])

    st.dataframe(
        styled,
        hide_index=True,
        use_container_width=True,
        height=height
    )

with st.sidebar:
    st.markdown("### VIP Loyalty Copilot")
    st.caption("EXECUTIVE ANALYTICS")
    st.divider()
    st.markdown("""
    <a class="nav-link" href="#overview">◉ &nbsp; Overview</a>
    <a class="nav-link" href="#vip-movement">◉ &nbsp; VIP Movement</a>
    <a class="nav-link" href="#at-risk-customers">◉ &nbsp; At-Risk Customers</a>
    <a class="nav-link" href="#customer-lookup">◉ &nbsp; Customer Lookup</a>
    """, unsafe_allow_html=True)
    st.divider()
    st.caption("DATA PERIOD")
    st.markdown("**2026 → 2027**")
    st.caption("Based on transactions through June 30, 2026")
    st.divider()
    st.caption("SYNTHETIC DATA · DEMO")

st.markdown('<div id="overview" class="dashboard-section"></div>', unsafe_allow_html=True)

# Overview
st.markdown('<div class="section-kicker">EXECUTIVE OVERVIEW</div>', unsafe_allow_html=True)
st.title("💎 VIP Loyalty Copilot")
st.write("An analytics-powered decision support dashboard for VIP loyalty forecasting and customer insights.")
st.info("This dashboard uses synthetic customer data. VIP tier projections are based on transactions observed through June 30, 2026.")

total_customers = len(customers)
current_vip = int((customers["vip_tier_2026"] != "General").sum())
projected_vip = int((customers["projected_vip_tier_2027"] != "General").sum())
vip_change = projected_vip - current_vip

section_title("VIP Portfolio Overview")
c1, c2, c3, c4 = st.columns(4)
c1.metric("Total Customers", f"{total_customers:,}")
c2.metric("Current VIP Customers", f"{current_vip:,}")
c3.metric("Projected 2027 VIP", f"{projected_vip:,}")
c4.metric("Projected Net Change", f"{vip_change:+,}")

st.markdown(" ")
section_title("VIP Tier Distribution: 2026 vs. 2027", "Compare current VIP membership with projected tier assignments.")
show_general = st.checkbox("Include General Customers", value=False)
current_counts = customers["vip_tier_2026"].value_counts().reindex(TIER_ORDER, fill_value=0)
projected_counts = customers["projected_vip_tier_2027"].value_counts().reindex(TIER_ORDER, fill_value=0)
tier_comparison = pd.DataFrame({"VIP Tier": TIER_ORDER, "2026 Current": current_counts.values, "2027 Projected": projected_counts.values})
chart_data = tier_comparison.melt(id_vars="VIP Tier", var_name="Year", value_name="Customers")
if not show_general:
    chart_data = chart_data[chart_data["VIP Tier"] != "General"]
fig = px.bar(chart_data, x="VIP Tier", y="Customers", color="Year", barmode="group", text="Customers",
             category_orders={"VIP Tier": TIER_ORDER}, color_discrete_map={"2026 Current": GREEN, "2027 Projected": SAGE})
fig.update_traces(textposition="outside", cliponaxis=False)
style_chart(fig, 485)
fig.update_layout(legend_title_text="", xaxis_title="VIP Tier", yaxis_title="Number of Customers")
st.plotly_chart(fig, use_container_width=True)
st.caption("Projections are estimates based on synthetic data, not confirmed 2027 outcomes.")

st.markdown('<div id="vip-movement" class="dashboard-section"></div>', unsafe_allow_html=True)

st.divider()
# VIP Movement
st.markdown('<div class="section-kicker">MEMBERSHIP DYNAMICS</div>', unsafe_allow_html=True)
st.title("VIP Tier Movement Analysis")
st.write("Understand how customers are expected to move between VIP tiers from 2026 to 2027.")

movement_counts = customers["tier_movement"].value_counts().reindex(MOVEMENT_ORDER, fill_value=0)
movement_summary = pd.DataFrame({"Movement": MOVEMENT_ORDER, "Customers": movement_counts.values})
changed_count = int(movement_summary.loc[movement_summary["Movement"] != "Maintain", "Customers"].sum())
c1, c2, c3 = st.columns(3)
c1.metric("Customers Changing Status", f"{changed_count:,}")
c2.metric("New VIP + Upgrades", f"{int(movement_counts['New VIP'] + movement_counts['Upgrade']):,}")
c3.metric("Downgrades + Lost VIP", f"{int(movement_counts['Downgrade'] + movement_counts['Lost VIP']):,}")

st.markdown(" ")
section_title("Projected VIP Movement Breakdown", "Focus on membership changes by hiding the much larger Maintain category.")
show_maintain = st.checkbox("Include Customers Maintaining Their Tier", value=False)
filtered_movement = movement_summary if show_maintain else movement_summary[movement_summary["Movement"] != "Maintain"]
visible_order = MOVEMENT_ORDER if show_maintain else [x for x in MOVEMENT_ORDER if x != "Maintain"]
fig_movement = px.bar(filtered_movement, x="Movement", y="Customers", color="Movement", text="Customers",
                      category_orders={"Movement": visible_order}, color_discrete_map=MOVEMENT_COLORS)
fig_movement.update_traces(textposition="outside", cliponaxis=False)
style_chart(fig_movement, 430)
fig_movement.update_layout(showlegend=False, xaxis_title="Movement Category", yaxis_title="Number of Customers")
st.plotly_chart(fig_movement, use_container_width=True)

section_title("Movement Summary", "Counts cover all 10,000 customers, including those retaining their existing tier.")
render_table(movement_summary, height=230)

section_title("2026 → 2027 Tier Transition Matrix", "Rows represent current tiers; columns represent projected tiers.")
transition = pd.crosstab(customers["vip_tier_2026"], customers["projected_vip_tier_2027"])
transition = transition.reindex(index=TIER_ORDER, columns=TIER_ORDER, fill_value=0)
transition.index.name = "2026 Current Tier"
transition.columns.name = "2027 Projected Tier"
fig_heat = px.imshow(transition, text_auto=True, aspect="auto", color_continuous_scale=[[0, BG], [0.25, "#205646"], [1, "#6C9B86"]], labels=dict(x="2027 Projected Tier", y="2026 Current Tier", color="Customers"))
style_chart(fig_heat, 520)
fig_heat.update_layout(coloraxis_colorbar=dict(tickfont=dict(color=WHITE)), xaxis=dict(tickangle=-25, tickfont=dict(color=MUTED)), yaxis=dict(tickfont=dict(color=MUTED)))
fig_heat.update_traces(textfont=dict(size=10))
st.plotly_chart(fig_heat, use_container_width=True)

st.markdown('<div id="at-risk-customers" class="dashboard-section"></div>', unsafe_allow_html=True)

st.divider()
# At-Risk Customers
st.markdown('<div class="section-kicker">RETENTION INTELLIGENCE</div>', unsafe_allow_html=True)
st.title("At-Risk Customers")
st.write("Identify customers projected to downgrade or lose VIP status and review possible behavioral drivers.")
at_risk = customers[customers["tier_movement"].isin(["Downgrade", "Lost VIP"])].copy()
c1, c2, c3 = st.columns(3)
c1.metric("At-Risk Customers", f"{len(at_risk):,}")
c2.metric("Projected Downgrades", f"{int((at_risk['tier_movement'] == 'Downgrade').sum()):,}")
c3.metric("Projected VIP Losses", f"{int((at_risk['tier_movement'] == 'Lost VIP').sum()):,}")

st.markdown(" ")
section_title("Explore At-Risk Customers", "Filter customers by movement category and current VIP tier.")
f1, f2 = st.columns(2)
with f1:
    selected_movements = st.multiselect("Movement", ["Downgrade", "Lost VIP"], default=["Downgrade", "Lost VIP"])
with f2:
    tiers_present = [tier for tier in TIER_ORDER if tier in at_risk["vip_tier_2026"].unique()]
    selected_tiers = st.multiselect("Current VIP Tier", tiers_present, default=tiers_present)
filtered_risk = at_risk[at_risk["tier_movement"].isin(selected_movements) & at_risk["vip_tier_2026"].isin(selected_tiers)]
st.caption(f"Showing {len(filtered_risk):,} customers")
cols = ["customer_id", "vip_tier_2026", "projected_vip_tier_2027", "tier_movement", "annual_spend_2025", "projected_annual_spend_2026", "frequency_change_pct", "basket_change_pct", "risk_driver"]
available_cols = [col for col in cols if col in filtered_risk.columns]
render_table(filtered_risk[available_cols], height=430)
st.download_button("Download Filtered Customer List", data=filtered_risk[available_cols].to_csv(index=False).encode("utf-8"), file_name="vip_at_risk_customers.csv", mime="text/csv")

if "risk_driver" in at_risk.columns and not at_risk.empty:
    section_title("Primary Risk Drivers", "Rule-based drivers derived from synthetic customer behavior.")
    drivers = at_risk["risk_driver"].fillna("Unclassified").value_counts().reset_index()
    drivers.columns = ["Risk Driver", "Customers"]
    fig_risk = px.bar(drivers, x="Customers", y="Risk Driver", orientation="h", text="Customers", color_discrete_sequence=[GREEN])
    fig_risk.update_traces(textposition="outside", cliponaxis=False)
    style_chart(fig_risk, max(300, len(drivers) * 60 + 100))
    fig_risk.update_layout(xaxis_title="Customers", yaxis_title="")
    st.plotly_chart(fig_risk, use_container_width=True)

st.markdown('<div id="customer-lookup" class="dashboard-section"></div>', unsafe_allow_html=True)

st.divider()
# Customer Lookup
st.markdown('<div class="section-kicker">CUSTOMER INTELLIGENCE</div>', unsafe_allow_html=True)
st.title("🔎 Customer VIP Lookup")
st.write("Enter a Customer ID to review current VIP status, projected 2027 tier, and spending trends.")
customer_id_input = st.text_input("Customer ID", placeholder="Example: C00142").strip().upper()
if customer_id_input:
    result = customers[customers["customer_id"].str.upper() == customer_id_input]
    if result.empty:
        st.warning("Customer ID not found. Please check the ID and try again.")
    else:
        customer = result.iloc[0]
        section_title("VIP Status")
        c1, c2, c3 = st.columns(3)
        c1.metric("Current VIP Tier (2026)", str(customer["vip_tier_2026"]))
        c2.metric("Projected VIP Tier (2027)", str(customer["projected_vip_tier_2027"]))
        c3.metric("Tier Movement", str(customer["tier_movement"]))
        st.markdown(" ")
        section_title("Customer Spending Overview")
        c4, c5, c6 = st.columns(3)
        c4.metric("2025 Annual Spending", f'${customer["annual_spend_2025"]:,.0f}')
        c5.metric("2026 YTD Spending", f'${customer["ytd_spend_2026"]:,.0f}')
        c6.metric("2026 Projected Spending", f'${customer["projected_annual_spend_2026"]:,.0f}')
        st.markdown(" ")
        section_title("Customer Risk Insights")
        if customer["tier_movement"] in ["Downgrade", "Lost VIP"]:
            st.warning("This customer is projected to downgrade or lose their current VIP status.")
            frequency = customer.get("frequency_change_pct", float("nan"))
            basket = customer.get("basket_change_pct", float("nan"))
            driver = customer.get("risk_driver", "Not available")
            st.markdown(f'<div class="insight-card"><strong>Purchase Frequency Change:</strong> {frequency:.1f}%<br><strong>Average Basket Change:</strong> {basket:.1f}%<br><strong>Primary Risk Driver:</strong> {driver}</div>', unsafe_allow_html=True)
        else:
            st.success("This customer is not currently projected to downgrade or lose VIP status.")
else:
    st.markdown('<div class="insight-card">Enter a customer ID above to see their individual profile.</div>', unsafe_allow_html=True)

st.markdown("---")
st.caption("VIP Loyalty Copilot · Synthetic data demonstration · 2027 VIP tiers are projections, not confirmed assignments")
