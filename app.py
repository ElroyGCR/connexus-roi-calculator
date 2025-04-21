
import streamlit as st
from PIL import Image
import pandas as pd
import plotly.graph_objects as go

# Load logo
logo = Image.open("connexus_logo.png")

# App config
st.set_page_config(
    page_title="ConnexUS AI ROI Calculator",
    layout="wide"
)

# --- SIDEBAR ---
st.sidebar.image(logo, use_container_width=True)
st.sidebar.header("📊 Input Your Call Center Data")

# Revenue & Volume
st.sidebar.subheader("📈 Revenue & Volume")
monthly_revenue = st.sidebar.number_input("Monthly Revenue ($)", value=250000, step=10000)
weekly_interactions = st.sidebar.number_input("Weekly Interactions", value=10000, step=100)
aht = st.sidebar.slider("Average Handle Time (minutes)", 1, 20, 6)

# Workforce & Agent Metrics
st.sidebar.subheader("👥 Workforce & Agent Metrics")
agents = st.sidebar.slider("Agents (FTE)", 1, 100, 25)
hourly_cost = st.sidebar.slider("Agent Hourly Cost ($)", 10.0, 60.0, 15.0)
hours_per_week = st.sidebar.slider("Weekly Hours per Agent", 35, 45, 40)
shift_hours = st.sidebar.number_input("Shift Length (hours)", value=8.5, step=0.5)

st.sidebar.subheader("💼 Business Impact Assumptions")
production_percent = st.sidebar.number_input("Production Improvement (%)", value=25.0, step=0.1)
upsell_percent = st.sidebar.number_input("Upsell Improvement (%)", value=10.0, step=0.1)

# AI Cost Inputs
st.sidebar.markdown("---")
st.sidebar.subheader("🤖 AI Cost Inputs")
automation = st.sidebar.slider("AI Automation % Target", 0, 100, 50)
subscription = st.sidebar.number_input("AI Monthly Subscription ($)", value=2000, step=100)
integration = st.sidebar.number_input("One-time Integration Fee ($)", value=15000, step=1000)
ai_cost_per_min = st.sidebar.number_input("AI Cost per Minute ($)", value=0.18, step=0.01)

# --- MAIN ---
st.markdown("# ConnexUS AI ROI Calculator")
st.markdown("### Powered by ConnexUS")
st.markdown("---")
 
# --- TOTAL VALUE + ROI / PAYBACK CALCULATIONS ---

# 1. Monthly workload in minutes
monthly_minutes = weekly_interactions * aht * 4.33

# 2. AI automation vs residual
ai_minutes = (automation / 100) * monthly_minutes
residual_minutes = monthly_minutes - ai_minutes

ai_cost = ai_minutes * ai_cost_per_min
residual_cost = (residual_minutes / 60) * hourly_cost
ai_enabled_cost = ai_cost + residual_cost + subscription
total_ai_monthly_cost = ai_cost + subscription

# 3. Indirect value
production_multiplier = production_percent / 100
upsell_multiplier = upsell_percent / 100

production_savings = monthly_minutes * production_multiplier
upsell_savings = monthly_minutes * upsell_multiplier
indirect_savings = production_savings + upsell_savings

# 4. Baseline human cost (dynamically calculated)
agent_monthly_hours = hours_per_week * 4.33
minutes_per_agent = agent_monthly_hours * 60
required_agents = monthly_minutes / minutes_per_agent
effective_agents = max(agents, required_agents)
base_labor_cost = effective_agents * agent_monthly_hours * hourly_cost
fully_loaded_multiplier = 1.222431
baseline_human_cost = base_labor_cost * fully_loaded_multiplier

# 5. Net savings (Direct only)
net_savings = baseline_human_cost - ai_enabled_cost

# --- Define early strategic_total to avoid NameError ---
strategic_total = 0  # Temporary placeholder in case HR impact is not calculated yet

st.sidebar.markdown("---")

# 6. ROI Calculation Toggles
use_indirects = st.sidebar.checkbox("Include Indirect Value in ROI Calculation", value=True)
use_hr_impact = st.sidebar.checkbox("Include Strategic HR Savings in ROI", value=False)
 
# Apply selected components to ROI basis
value_basis = net_savings
if use_indirects:
    value_basis += indirect_savings

# 7. ROI & Payback
roi_percent = (value_basis / ai_enabled_cost) * 100 if ai_enabled_cost > 0 else 0
annual_roi_percent = roi_percent * 12
payback_days = (integration / value_basis) * 30 if value_basis > 0 else 999

# 8. Additional metrics
monthly_cost_reduction = (net_savings / baseline_human_cost) * 100 if baseline_human_cost > 0 else 0
dollar_saved_per_ai_dollar = (value_basis / total_ai_monthly_cost) if total_ai_monthly_cost > 0 else 0
total_monthly_value = net_savings + indirect_savings
annual_net_savings = total_monthly_value * 12

st.markdown("### 📊 Core Financial Metrics (Operating Basis)")
st.caption("These values reflect cost savings compared to your human-only baseline.")

# --- KPI CARDS ---
col1, col2, col3, col4 = st.columns(4)
col1.metric("💰 Net Monthly Savings", f"${net_savings:,.0f}", help="Cost saved per month by implementing AI vs human-only operations.")
col2.metric("📅 Break-even Period", f"{payback_days:.1f} days", help="Days to recover AI cost from monthly operating savings.")
col3.metric("📈 ROI on Operating Cost (Monthly)", f"{roi_percent:.1f}%", help="Return on monthly operational spend, not total investment.")
col4.metric("📈 ROI on Operating Cost (Annual)", f"{annual_roi_percent:.1f}%", help="Annualized return based on operating savings.")

# --- INDIRECT VALUE KPI DISPLAY ---
st.markdown("### 🧩 Indirect Impact from AI (Performance Uplift)")
st.caption("These gains reflect enhanced output from improved efficiency and upselling performance — not direct cost reduction.")

col1, col2, col3 = st.columns(3)
col1.metric("🧠 Efficiency Gains", f"${production_savings:,.0f}", help="Estimated savings from improved production and performance.")
col2.metric("🛒 Upsell Gains", f"${upsell_savings:,.0f}", help="Revenue uplift from increased conversion or upselling.")
col3.metric("🎯 Total Monthly Value", f"${total_monthly_value:,.0f}", help="Combined monthly value from savings and uplift.")

# --- AI Investment Visual ---
st.markdown("### 💡 AI Investment Impact")
st.caption("Shows how much value is returned for every dollar spent on AI — includes both cost savings and indirect gains.")

st.markdown(
    f"""
    <div style='font-size: 22px; margin-top: 10px;'>
        For every <span style='color:#FFD700; font-weight:600;'>$1</span> you invest in AI, you save:
        <span style='color:#00FFAA; font-size: 28px; font-weight:700;'>${dollar_saved_per_ai_dollar:,.2f}</span>
    </div>
    """,
    unsafe_allow_html=True
)

# --- ROI Composition Chart ---
st.markdown("### 📊 ROI Value Composition Breakdown")
st.markdown(
    """
    <div style='color: white; font-size: 15px; margin-top: -10px; margin-bottom: 20px;'>
        Each bar shows how much that category adds to your monthly ROI. 
        <br>Direct savings come from lower labor costs, indirect value from productivity/upsell gains, 
        and HR impact from avoided hiring and absenteeism costs.
    </div>
    """,
    unsafe_allow_html=True
)

# Prepare data for chart
roi_components = {
    "Direct Savings": net_savings,
    "Indirect Value": indirect_savings if use_indirects else 0,
    "HR Strategic Impact": strategic_total if use_hr_impact else 0
}

roi_df = pd.DataFrame({
    "Component": list(roi_components.keys()),
    "Value ($)": list(roi_components.values())
})

# Bar Chart
roi_bar = go.Figure(go.Bar(
    x=roi_df["Component"],
    y=roi_df["Value ($)"],
    marker=dict(color=["#00FFAA", "#1f77b4", "#FFD700"]),
    text=[f"${v:,.0f}" for v in roi_df["Value ($)"]],
    textposition="auto"
))
roi_bar.update_layout(
    height=400,
    yaxis_title="Monthly Value ($)",
    xaxis_title="ROI Contribution Source",
    plot_bgcolor="rgba(0,0,0,0)",
    showlegend=False
)
st.plotly_chart(roi_bar, use_container_width=True)

# --- ROI & Payback Gauges ---
st.markdown("## 🎯 ROI & Break-even Based on Operating Cost")
st.markdown(
    """
    <div style='color: white; font-size: 15px; margin-top: -10px; margin-bottom: 20px;'>
        These gauges show how much operational return you’re generating each month with AI. 
        <br><strong>ROI (%)</strong> reflects direct cost savings plus optional performance and HR gains.
        <br><strong>Payback Time (Days)</strong> shows how quickly you break even based on monthly savings.
    </div>
    """,
    unsafe_allow_html=True
)
col1, col2 = st.columns(2)

gauge_fig = go.Figure(go.Indicator(
    mode="gauge+number+delta",
    value=roi_percent,
    delta={'reference': 100, 'increasing': {'color': "green"}, 'decreasing': {'color': "red"}},
    gauge={
        'axis': {'range': [0, 200]},
        'bar': {'color': "darkblue"},
        'steps': [
            {'range': [0, 50], 'color': 'lightgray'},
            {'range': [50, 100], 'color': 'lightblue'},
            {'range': [100, 200], 'color': 'lightgreen'}
        ],
        'threshold': {'line': {'color': "red", 'width': 4}, 'thickness': 0.75, 'value': 50}
    },
    title={'text': "ROI (%)"}
))

payback_gauge = go.Figure(go.Indicator(
    mode="gauge+number",
    value=payback_days,
    title={'text': "Payback Time (Days)"},
    gauge={
        'axis': {'range': [0, 30]},
        'bar': {'color': "black"},
        'steps': [
            {'range': [0, 7], 'color': "lightgreen"},
            {'range': [7, 14], 'color': "yellow"},
            {'range': [14, 30], 'color': "tomato"}
        ],
        'threshold': {'line': {'color': "red", 'width': 4}, 'value': 15}
    }
))

with col1:
    st.plotly_chart(gauge_fig, use_container_width=True)
with col2:
    st.plotly_chart(payback_gauge, use_container_width=True)

# Investment-based ROI & Payback (Important: Define these before rendering)
investment_roi = ((annual_net_savings - integration) / integration) * 100 if integration > 0 else 0
investment_payback_months = (integration / annual_net_savings) * 12 if annual_net_savings > 0 else 999

# --- INVESTMENT-BASED ROI & PAYBACK ---
st.markdown("## 💼 ROI & Break-even Based on Investment")
st.markdown(
    """
    <div style='color: white; font-size: 15px; margin-top: -10px; margin-bottom: 20px;'>
        This section measures ROI compared to your up-front investment (integration cost).
        <br><strong>Investment ROI (%)</strong> calculates your return over the course of a year.
        <br><strong>Payback Period (Months)</strong> estimates how many months it takes to recoup initial setup costs.
    </div>
    """,
    unsafe_allow_html=True
)

col1, col2 = st.columns(2)

inv_roi_gauge = go.Figure(go.Indicator(
    mode="gauge+number+delta",
    value=investment_roi,
    delta={'reference': 100, 'increasing': {'color': "green"}, 'decreasing': {'color': "red"}},
    gauge={
        'axis': {'range': [0, 200]},
        'bar': {'color': "darkblue"},
        'steps': [
            {'range': [0, 50], 'color': 'lightgray'},
            {'range': [50, 100], 'color': 'lightblue'},
            {'range': [100, 200], 'color': 'lightgreen'}
        ],
        'threshold': {'line': {'color': "red", 'width': 4}, 'value': 50}
    },
    title={'text': "Investment ROI (%)"}
))

inv_payback_gauge = go.Figure(go.Indicator(
    mode="gauge+number",
    value=investment_payback_months,
    title={'text': "Payback Period (Months)"},
    gauge={
        'axis': {'range': [0, 24]},
        'bar': {'color': "black"},
        'steps': [
            {'range': [0, 6], 'color': "lightgreen"},
            {'range': [6, 12], 'color': "yellow"},
            {'range': [12, 24], 'color': "tomato"}
        ],
        'threshold': {'line': {'color': "red", 'width': 4}, 'value': 12}
    }
))

with col1:
    st.plotly_chart(inv_roi_gauge, use_container_width=True)
with col2:
    st.plotly_chart(inv_payback_gauge, use_container_width=True)
 
# --- COST COMPARISON: Human vs AI ---
st.markdown("### 🧾 Cost Comparison (Human vs. AI)")
st.caption("Shows absolute monthly cost difference between traditional staffing and AI-enhanced operations.")

col1, col2 = st.columns(2)
col1, col2 = st.columns(2)

with col1:
    st.markdown(f"""
        <div style='padding: 10px;'>
            <div style='font-size:18px; color:#AAAAAA;'>👥 Human-Only Cost</div>
            <div style='font-size:42px; font-weight:bold; color:white;'>${baseline_human_cost:,.0f}</div>
        </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown(f"""
        <div style='padding: 10px;'>
            <div style='font-size:18px; color:#AAAAAA;'>🤖 AI-Enabled Cost</div>
            <div style='font-size:42px; font-weight:bold; color:white;'>${ai_enabled_cost:,.0f}</div>
        </div>
    """, unsafe_allow_html=True)
 
# --- WATERFALL ---
st.markdown("## 💧 Monthly Cost Breakdown (Waterfall)")
st.markdown(
    """
    <div style='color: white; font-size: 15px; margin-top: -10px; margin-bottom: 20px;'>
        This chart breaks down your full monthly cost transition from a 100% human-run operation 
        to a partially automated AI-powered one. 
        <br>It visualizes how labor is reduced, AI costs are added, and what the final AI-enabled 
        operating cost looks like — so you can clearly see the shift in monthly spending.
    </div>
    """,
    unsafe_allow_html=True
)

waterfall_fig = go.Figure(go.Waterfall(
    name="Monthly Cost",
    orientation="v",
    measure=[
    "absolute",  # 100% Human
    "relative",  # - Labor removed
    "relative",  # + AI Usage
    "relative",  # + Subscription
    "absolute"   # AI-enabled Net Cost
],
x=[
    "100% Human Cost",
    "Reduced Labor",
    "Add: AI Usage",
    "Add: Subscription",
    "Net AI-Enabled Cost"
],
y=[
    baseline_human_cost,
    -residual_cost,
    ai_cost,
    subscription,
    ai_enabled_cost
],
    connector={"line": {"color": "rgb(63, 63, 63)"}}
))

waterfall_fig.update_layout(
    waterfallgap=0.5,
    height=400,
    showlegend=False,
    yaxis_title="Monthly Cost ($)",
    plot_bgcolor="rgba(0,0,0,0)"
)

st.plotly_chart(waterfall_fig, use_container_width=True)

# --- LINE CHART ---
st.markdown("## 📈 Savings vs Integration Cost Over Time")
st.markdown(
    """
    <div style='color: white; font-size: 15px; margin-top: -10px; margin-bottom: 20px;'>
        This chart compares cumulative monthly savings against your initial integration cost.
        <br>The green line shows how your savings grow over time, while the dashed red line represents 
        the one-time setup investment — giving you a clear visual of when ROI is achieved.
    </div>
    """,
    unsafe_allow_html=True
)

months = list(range(1, 13))
cumulative_savings = [net_savings * m for m in months]
integration_cost_line = [integration for _ in months]
df = pd.DataFrame({
    "Month": months,
    "Cumulative Savings": cumulative_savings,
    "Integration Cost": integration_cost_line
})

line_fig = go.Figure()
line_fig.add_trace(go.Scatter(
    x=df["Month"], y=df["Cumulative Savings"],
    mode='lines+markers', name="Cumulative Savings",
    line=dict(color="green", width=3)
))
line_fig.add_trace(go.Scatter(
    x=df["Month"], y=df["Integration Cost"],
    mode='lines', name="Integration Cost",
    line=dict(color="red", dash="dash")
))
line_fig.update_layout(
    xaxis_title="Month",
    yaxis_title="Cumulative ($)",
    height=400,
    legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
    plot_bgcolor="rgba(0,0,0,0)"
)
st.plotly_chart(line_fig, use_container_width=True)

# --- DONUT CHART ---
st.markdown("## 🍩 AI Cost Composition (Donut Chart)")
st.markdown(
    """
    <div style='color: white; font-size: 15px; margin-top: -10px; margin-bottom: 20px;'>
        This chart visualizes the composition of your AI-enabled monthly operating cost.
        <br>It breaks down how much is spent on AI usage, remaining labor, and platform subscription —
        helping you see where your new cost structure lies.
    </div>
    """,
    unsafe_allow_html=True
)

donut_fig = go.Figure(data=[go.Pie(
    labels=["AI Usage", "Residual Labor", "Subscription"],
    values=[ai_cost, residual_cost, subscription],
    hole=.5,
    textinfo="label+percent+value",
    marker=dict(colors=["#1f77b4", "#ff7f0e", "#2ca02c"])
)])
donut_fig.update_layout(
    height=500,
    showlegend=True,
    title="AI-Enabled Monthly Cost Breakdown",
    plot_bgcolor="rgba(0,0,0,0)"
)
st.plotly_chart(donut_fig, use_container_width=True)

# --- Monthly Cost Reduction ---
monthly_cost_reduction = (net_savings / baseline_human_cost) * 100 if baseline_human_cost > 0 else 0

st.markdown("### 💸 Monthly Cost Efficiency")
st.markdown(
    """
    <div style='color: white; font-size: 15px; margin-top: -10px; margin-bottom: 15px;'>
        This shows how much your monthly costs drop compared to a fully human-run operation.
    </div>
    """,
    unsafe_allow_html=True
)

# Stylized cost efficiency stat
st.markdown(
    f"""
    <div style='
        background-color: #111;
        border: 2px solid #00FFAA;
        border-radius: 12px;
        padding: 15px;
        width: fit-content;
        margin-bottom: 25px;
    '>
        <span style='color:#00FFAA; font-size: 36px; font-weight: bold;'>{monthly_cost_reduction:.2f}%</span>
    </div>
    """,
    unsafe_allow_html=True
)

# ✅ Step 1: Add HR-impact section placeholder at the bottom
# --- HR Efficiency & Operational Impact ---
st.markdown("---")
st.markdown("## 🧠 Strategic Operational Impact (HR & Seasonal Savings)")
st.markdown(
    """
    <div style='color: white; font-size: 15px; margin-top: -10px; margin-bottom: 20px;'>
        These insights reflect cost avoidance and hidden savings from reduced churn, absenteeism, and seasonal volume strain.
    </div>
    """,
    unsafe_allow_html=True
)

if use_hr_impact:
    with st.sidebar.expander("Adjust HR Impact Assumptions"):
        hr_attrition = st.slider("Monthly Attrition Rate (%)", 0, 50, 10, key="bottom_attrition")
        hr_no_show = st.slider("No‑Call/No‑Show Rate (%)", 0, 20, 5, key="bottom_noshow")
        hr_pto_days = st.slider("PTO/Sick‑Leave Days/Year", 0, 30, 5, key="bottom_pto")
        hr_new_hire_cost = st.number_input("Cost per New Hire ($)", value=2000, step=500, key="bottom_hire_cost")
        hr_peak_staffing = st.slider("Peak Volume Staffing Increase (%)", 0, 50, 10, key="bottom_peak_staffing")
        hr_peak_frequency = st.slider("Peak Volume Occurrence (per year)", 0, 12, 3, key="bottom_peak_freq")
else:
    # Fallbacks if HR impact not used
    hr_attrition = 0
    hr_no_show = 0
    hr_pto_days = 0
    hr_new_hire_cost = 0
    hr_peak_staffing = 0
    hr_peak_frequency = 0

# --- Strategic Value Calculations (Updated to Use Sidebar Inputs) ---
if use_hr_impact:
    total_annual_attrition = hr_attrition / 100 * effective_agents * 12
    absence_rate = (hr_no_show / 100) + (hr_pto_days / 260)
    recruiting_savings = total_annual_attrition * hr_new_hire_cost
    seasonal_hours = (hr_peak_staffing / 100) * required_agents * shift_hours * hr_peak_frequency
    seasonal_savings = seasonal_hours * hourly_cost * fully_loaded_multiplier  # ✅ Add this line
    absentee_cost = absence_rate * base_labor_cost
    strategic_total = recruiting_savings + absentee_cost + seasonal_savings
    value_basis += strategic_total
else:
    strategic_total = 0

# --- Display 3 Metrics in Boxes ---
col1, col2, col3 = st.columns(3)

with col1:
    st.markdown("#### 🧾 Recruiting Savings")
    st.markdown(f"""
    <div style='
        background-color: #111;
        border: 2px solid #1f77b4;
        border-radius: 10px;
        padding: 15px;
        width: fit-content;
    '>
        <span style='color:#1f77b4; font-size: 32px; font-weight: bold;'>${strategic_total:,.0f}</span>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown("#### 🚫 Absenteeism Savings")
    st.markdown(f"""
    <div style='
        background-color: #111;
        border: 2px solid #bcbd22;
        border-radius: 10px;
        padding: 15px;
        width: fit-content;
    '>
        <span style='color:#bcbd22; font-size: 32px; font-weight: bold;'>${absentee_cost:,.0f}</span>
    </div>
    """, unsafe_allow_html=True)

with col3:
    st.markdown("#### 📈 Seasonal Staffing Savings")
    st.markdown(f"""
    <div style='
        background-color: #111;
        border: 2px solid #17becf;
        border-radius: 10px;
        padding: 15px;
        width: fit-content;
    '>
        <span style='color:#17becf; font-size: 32px; font-weight: bold;'>${seasonal_savings:,.0f}</span>
    </div>
    """, unsafe_allow_html=True)

# --- Total Strategic HR Impact
st.markdown("### 💼 Total Strategic HR Efficiency Impact")
st.markdown(
    f"""
    <div style='
        background-color: #222;
        border-left: 6px solid #FFD700;
        padding: 20px;
        margin-bottom: 30px;
    '>
        <span style='color:#FFD700; font-size: 36px; font-weight: bold;'>${strategic_total:,.0f}</span>
    </div>
    """,
    unsafe_allow_html=True
)

# --- HR Strategic Donut Chart ---
st.markdown("## 📊 Breakdown of HR & Seasonal Efficiency Gains")
st.markdown(
    """
    <div style='color: white; font-size: 15px; margin-top: -10px; margin-bottom: 20px;'>
        This donut chart shows how your total HR efficiency impact is split across recruiting cost avoidance,
        absenteeism reductions, and seasonal staffing efficiency.
    </div>
    """,
    unsafe_allow_html=True
)

hr_donut = go.Figure(data=[go.Pie(
    labels=["Recruiting Savings", "Absenteeism Savings", "Seasonal Staffing Savings"],
    values=[recruiting_savings, absentee_cost, seasonal_savings],
    hole=0.5,
    textinfo="label+percent+value",
    textfont=dict(size=18),
    marker=dict(colors=["#e377c2", "#bcbd22", "#17becf"])
)])
hr_donut.update_layout(
    height=500,
    showlegend=True,
    title="Strategic Operational Impact Composition",
    plot_bgcolor="rgba(0,0,0,0)",
    font=dict(size=16),
    legend=dict(font=dict(size=14))
)
st.plotly_chart(hr_donut, use_container_width=True)
