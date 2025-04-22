import streamlit as st
from PIL import Image
import pandas as pd
import plotly.graph_objects as go

# --- Helper functions for styled metrics and captions ---
def metric_block(label, value, color="#00FFAA", border="#00FFAA", suffix=""):
    return f"""
    <div style='\n        background-color: #111;\n        border: 2px solid {border};\n        border-radius: 12px;\n        padding: 15px;\n        width: fit-content;\n        margin-bottom: 25px;\n    '>
        <div style='color: white; font-size: 16px; margin-bottom: 5px;'>{label}</div>
        <div style='color: {color}; font-size: 36px; font-weight: bold;'>{value:,.1f} {suffix}</div>
    </div>
    """

def caption(text):
    return f"<div style='color: white; font-size: 15px; margin-bottom: 10px;'>{text}</div>"

# Load logo
logo = Image.open("connexus_logo.png")

# App configuration
st.set_page_config(page_title="ConnexUS AI ROI Calculator", layout="wide")

# --- SIDEBAR INPUTS ---
st.sidebar.image(logo, use_container_width=True)
st.sidebar.header("📊 Input Your Call Center Data")

# Revenue & Volume
st.sidebar.subheader("📈 Revenue & Volume")
monthly_revenue   = st.sidebar.number_input("Monthly Revenue ($)", value=250000, step=10000)
weekly_interactions = st.sidebar.number_input("Weekly Interactions", value=10000, step=100)
aht             = st.sidebar.slider("Average Handle Time (minutes)", 1, 20, 6)

# Workforce & Agent Metrics
st.sidebar.subheader("👥 Workforce & Agent Metrics")
agents          = st.sidebar.slider("Agents (FTE)", 1, 100, 25)
hourly_cost     = st.sidebar.slider("Agent Hourly Cost ($)", 10.0, 60.0, 15.0)
hours_per_week  = st.sidebar.slider("Weekly Hours per Agent", 35, 45, 40)
shift_hours     = st.sidebar.number_input("Shift Length (hours)", value=8.5, step=0.5)

# Business Impact Assumptions
st.sidebar.subheader("💼 Business Impact Assumptions")
production_percent = st.sidebar.number_input("Production Improvement (%)", value=25.0, step=0.1)
upsell_percent     = st.sidebar.number_input("Upsell Improvement (%)", value=10.0, step=0.1)

# AI Cost Inputs
st.sidebar.markdown("---")
st.sidebar.subheader("🤖 AI Cost Inputs")
automation       = st.sidebar.slider("AI Automation % Target", 0, 100, 50)
subscription      = st.sidebar.number_input("AI Monthly Subscription ($)", value=2000, step=100)
integration       = st.sidebar.number_input("One-time Integration Fee ($)", value=15000, step=1000)
ai_cost_per_min  = st.sidebar.number_input("AI Cost per Minute ($)", value=0.18, step=0.01)

# ROI Calculation Toggles
st.sidebar.markdown("---")
use_indirects    = st.sidebar.checkbox("Include Indirect Value in ROI Calculation", value=True)
use_hr_impact    = st.sidebar.checkbox("Include Strategic HR Savings in ROI", value=False)

# --- MAIN LAYOUT ---
st.markdown("# ConnexUS AI ROI Calculator")
st.markdown("### Powered by ConnexUS")
st.markdown("---")

# --- 1. Total Monthly Workload ---
monthly_minutes = weekly_interactions * aht * 4.33

# --- 2. AI vs Residual Human Cost ---
ai_minutes       = (automation / 100) * monthly_minutes
residual_minutes = monthly_minutes - ai_minutes

# AI spend
aio_cost         = ai_minutes * ai_cost_per_min

# Residual human labor after automation, with fully-loaded multiplier
fully_loaded_multiplier = 1.222431
residual_cost    = (residual_minutes / 60) * hourly_cost * fully_loaded_multiplier

aio_enabled_cost      = ai_cost + residual_cost + subscription
# Cost excluding residual labor (pure AI spend + subscription)
total_ai_monthly_cost  = ai_cost + subscription

# --- 3. Indirect Value (Production & Upsell) ---
production_multiplier = production_percent / 100
upsell_multiplier     = upsell_percent / 100

# Convert saved minutes to dollar savings for production
production_minutes_saved = monthly_minutes * production_multiplier
production_hours_saved   = production_minutes_saved / 60
production_dollar_savings = production_hours_saved * hourly_cost * fully_loaded_multiplier

# Upsell tied to incremental revenue lift\_dollar_savings = monthly_revenue * upsell_multiplier
upsell_dollar_savings   = monthly_revenue * upsell_multiplier

# Total indirect savings in $ 
indirect_savings = production_dollar_savings + upsell_dollar_savings

total_monthly_value = (aio_enabled_cost := ai_enabled_cost)  # to preserve ai_enabled_cost name
net_savings           = None  # placeholder below

# --- 4. Baseline Human Cost Calculation ---
agent_monthly_hours = hours_per_week * 4.33
minutes_per_agent   = agent_monthly_hours * 60
required_agents     = monthly_minutes / minutes_per_agent
effective_agents   = max(agents, required_agents)

base_labor_cost     = effective_agents * agent_monthly_hours * hourly_cost
baseline_human_cost = base_labor_cost * fully_loaded_multiplier

# --- 5. Net Direct Savings ---
net_savings         = baseline_human_cost - ai_enabled_cost

# --- 6. ROI Value Basis (Direct + Optional Indirect + HR) ---
value_basis = net_savings
if use_indirects:
    value_basis += indirect_savings

# Placeholder for strategic (HR) impact; will be added later if toggled
strategic_total = 0

# --- 7. ROI & Payback on Operating Cost ---
roi_percent          = (value_basis / ai_enabled_cost) * 100 if ai_enabled_cost > 0 else 0
annual_roi_percent   = roi_percent * 12
payback_days         = (integration / value_basis) * 30 if value_basis > 0 else float('inf')

# --- 8. ROI vs Investment (Integration) ---
annual_net_savings    = total_monthly_value * 12
investment_roi       = ((annual_net_savings - integration) / integration) * 100 if integration > 0 else 0
investment_payback_months = (integration / annual_net_savings) * 12 if annual_net_savings > 0 else float('inf')

dollar_saved_per_ai_dollar = (value_basis / total_ai_monthly_cost) if total_ai_monthly_cost > 0 else 0

# --- 9. Build the Streamlit UI ---
# Core Financial Metrics
st.markdown("### 📊 Core Financial Metrics (Operating Basis)")
st.markdown(caption("These values reflect cost savings compared to your human-only baseline."), unsafe_allow_html=True)
col1, col2, col3, col4 = st.columns(4)
with col1:
    st.markdown(metric_block("💰 Net Monthly Savings", net_savings), unsafe_allow_html=True)
with col2:
    st.markdown(metric_block("🧾 Break-even Period", payback_days, suffix=" days"), unsafe_allow_html=True)
with col3:
    st.markdown(metric_block("📈 ROI on Operating Cost (Monthly)", roi_percent, suffix="%"), unsafe_allow_html=True)
with col4:
    st.markdown(metric_block("📈 ROI on Operating Cost (Annual)", annual_roi_percent, suffix="%"), unsafe_allow_html=True)

# Indirect Impact
st.markdown("### 🧩 Indirect Impact from AI (Performance Uplift)" )
st.markdown(caption("These gains reflect enhanced output from improved efficiency and revenue uplift..."), unsafe_allow_html=True)
col1, col2, col3 = st.columns(3)
with col1:
    st.markdown(metric_block("🧠 Production Dollar Savings", production_dollar_savings), unsafe_allow_html=True)
with col2:
    st.markdown(metric_block("🛒 Upsell Dollar Savings", upsell_dollar_savings, color="#1f77b4", border="#1f77b4"), unsafe_allow_html=True)
with col3:
    st.markdown(metric_block("🎯 Total Monthly Value", net_savings + indirect_savings, color="#FFD700", border="#FFD700"), unsafe_allow_html=True)

# AI Investment Impact
st.markdown("### 💡 AI Investment Impact")
st.markdown(caption("Shows how much value is returned for every dollar spent on AI — includes cost savings and indirect gains."), unsafe_allow_html=True)
st.markdown(f"For every <span style='color:#FFD700;'>$1</span> you invest in AI, you save: <span style='color:#00FFAA; font-size:32px;'>${dollar_saved_per_ai_dollar:,.2f}</span>", unsafe_allow_html=True)

# ROI & Break-even (Investment)
st.markdown("### 💼 ROI & Break-even Based on Investment")
col1, col2 = st.columns(2)
with col1:
    inv_fig = go.Figure(go.Indicator(
        mode="gauge+number+delta",
        value=investment_roi,
        delta={'reference': 100},
        gauge={'axis':{'range':[0,200]}},
        title={'text':'Investment ROI (%)'}))
    st.plotly_chart(inv_fig, use_container_width=True)
with col2:
    pay_fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=some_value,
        title={'text': "Some Title"},
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
    st.plotly_chart(pay_fig, use_container_width=True)

# Cost Comparison Waterfall
st.markdown("### 💧 Monthly Cost Breakdown (Waterfall)")
waterfall_fig = go.Figure(go.Waterfall(
    measure=["absolute","relative","relative","relative","absolute"],
    x=["100% Human Cost","- Reduced Labor","+ AI Usage","+ Subscription","Net AI-Enabled Cost"],
    y=[baseline_human_cost, -residual_cost, ai_cost, subscription, ai_enabled_cost],
    connector={'line':{'color':'rgb(63,63,63)'}}
))
waterfall_fig.update_layout(plot_bgcolor='rgba(0,0,0,0)', yaxis_title='Monthly Cost ($)')
st.plotly_chart(waterfall_fig, use_container_width=True)

# Line Chart: Savings vs Integration Cost
df = pd.DataFrame({
    'Month': list(range(1,13)),
    'Cumulative Savings': [net_savings*m for m in range(1,13)],
    'Integration Cost': [integration]*12
})
line_fig = go.Figure()
line_fig.add_trace(go.Scatter(x=df['Month'], y=df['Cumulative Savings'], mode='lines+markers', name='Savings', line=dict(color='green')))
line_fig.add_trace(go.Scatter(x=df['Month'], y=df['Integration Cost'], mode='lines', name='Integration Cost', line=dict(color='red', dash='dash')))
line_fig.update_layout(plot_bgcolor='rgba(0,0,0,0)', xaxis_title='Month', yaxis_title='Cumulative Savings ($)')
st.plotly_chart(line_fig, use_container_width=True)

# Donut Chart: AI Cost Composition
donut_fig = go.Figure(data=[go.Pie(labels=["AI Usage","Residual Labor","Subscription"],
                                    values=[ai_cost, residual_cost, subscription], hole=.5, textinfo='label+percent+value')])
donut_fig.update_layout(plot_bgcolor='rgba(0,0,0,0)', title='AI-Enabled Monthly Cost Breakdown')
st.plotly_chart(donut_fig, use_container_width=True)

# Monthly Cost Efficiency\st.markdown("### 💸 Monthly Cost Efficiency")
st.markdown(f"<div style='color:#00FFAA; font-size:36px; font-weight:bold;'>{(net_savings/baseline_human_cost*100):.2f}%</div>", unsafe_allow_html=True)

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

# --- Strategic HR Placeholder Values (to prevent NameErrors if HR toggle is off) ---
absentee_cost = 0
seasonal_savings = 0
recruiting_savings = 0

# --- Strategic Value Calculations (Updated to Use Sidebar Inputs) ---
if use_hr_impact:
    total_annual_attrition = hr_attrition / 100 * effective_agents * 12
    absence_rate = (hr_no_show / 100) + (hr_pto_days / 260)
    recruiting_savings = total_annual_attrition * hr_new_hire_cost
    seasonal_hours = (hr_peak_staffing / 100) * required_agents * shift_hours * hr_peak_frequency
    seasonal_savings = seasonal_hours * hourly_cost * fully_loaded_multiplier
    absentee_cost = absence_rate * base_labor_cost
    strategic_total = recruiting_savings + absentee_cost + seasonal_savings
    value_basis += strategic_total
else:
    strategic_total = 0

# --- Display 3 Metrics in Boxes ---
col1, col2, col3 = st.columns(3)

col1, col2, col3 = st.columns(3)

with col1:
    st.markdown(metric_block("🧾 Recruiting Savings", recruiting_savings, color="#1f77b4", border="#1f77b4"), unsafe_allow_html=True)

with col2:
    st.markdown(metric_block("🚫 Absenteeism Savings", absentee_cost, color="#bcbd22", border="#bcbd22"), unsafe_allow_html=True)

with col3:
    st.markdown(metric_block("📈 Seasonal Staffing Savings", seasonal_savings, color="#17becf", border="#17becf"), unsafe_allow_html=True)

# --- Total Strategic HR Impact
st.markdown("### 💼 Total Strategic HR Efficiency Impact")
st.markdown(metric_block("⭐ Combined HR Efficiency Gains", strategic_total, color="#FFD700", border="#FFD700", suffix="$"), unsafe_allow_html=True)

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
