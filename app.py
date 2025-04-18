
import streamlit as st
import matplotlib.pyplot as plt
import plotly.graph_objects as go
from PIL import Image

st.set_page_config(page_title="ConnexUS ROI Calculator", layout="wide")
left, right = st.columns([1, 2])

with left:
    logo = Image.open("connexus_logo.png")
    st.image(logo, width=200)
    st.header("ROI Inputs")
    mode = st.radio("Choose Input Method:", ["📞 Monthly Call Volume (Interactions)", "👥 Agent-Based (FTE x Hours)"])

    if mode == "📞 Monthly Call Volume (Interactions)":
        call_volume = st.number_input("Monthly Call Volume (Interactions)", min_value=0, value=5000, step=100)
        aht = st.number_input("Average Handle Time (minutes)", min_value=1.0, value=6.0, step=0.5)
        total_minutes = call_volume * aht
    else:
        agent_count = st.number_input("Number of Agents (FTE)", min_value=1, value=10)
        hours_per_agent = st.number_input("Monthly Hours per Agent", min_value=1, value=160)
        total_minutes = agent_count * hours_per_agent * 60

    hourly_cost = st.number_input("Human Agent Hourly Cost ($)", min_value=1.0, value=25.0)
    automation_pct = st.slider("AI Automation %", min_value=0, max_value=100, value=70, step=5)
    ai_per_min = st.number_input("AI Cost per Minute ($)", min_value=0.01, value=0.18)
    ai_monthly_fee = st.number_input("AI Platform Monthly Fee ($)", min_value=0.0, value=2000.0)
    integration_cost = st.number_input("One-Time Integration Fee ($)", min_value=0.0, value=15000.0)

# --- Calculations ---
human_monthly = (total_minutes / 60) * hourly_cost
ai_minutes = total_minutes * (automation_pct / 100)
residual_minutes = total_minutes - ai_minutes
ai_usage_cost = ai_minutes * ai_per_min
residual_human_cost = (residual_minutes / 60) * hourly_cost
ai_total_cost = ai_monthly_fee + ai_usage_cost + residual_human_cost
savings = human_monthly - ai_total_cost
roi = (savings / ai_total_cost * 100) if ai_total_cost > 0 else 0

with right:
    st.title("📊 ConnexUS ROI Results")

    # 1. Summary table first
    st.subheader("📄 Scenario Summary")
    st.table({
        "Scenario": ["Human", "AI-Enabled"],
        "Monthly Cost ($)": [f"{human_monthly:,.2f}", f"{ai_total_cost:,.2f}"],
        "Annual Cost ($)": [f"{human_monthly*12:,.2f}", f"{ai_total_cost*12:,.2f}"],
        "ROI %": ["-", f"{roi:.1f}%"],
        "Savings ($/mo)": ["-", f"{savings:,.2f}"],
        "Break-even (months)": ["-", f"{(integration_cost / savings):.1f}" if savings > 0 else "N/A"]
    })

    # 2. ROI Gauge
    st.subheader("🎯 ROI Gauge")
    fig_gauge = go.Figure(go.Indicator(
        mode="gauge+number+delta",
        value=roi,
        title={'text': "ROI (%)"},
        gauge={
            'axis': {'range': [None, 200]},
            'steps': [
                {'range': [0, 50], 'color': "lightgray"},
                {'range': [50, 100], 'color': "lightblue"},
                {'range': [100, 200], 'color': "lightgreen"}
            ],
            'threshold': {'line': {'color': "red", 'width': 4}, 'value': roi}
        }
    ))
    st.plotly_chart(fig_gauge)

    # 3. Waterfall
    st.subheader("📉 AI Cost Composition (Waterfall)")
    fig_waterfall = go.Figure(go.Waterfall(
        name="Cost Breakdown", orientation="v",
        measure=["absolute", "relative", "relative", "relative"],
        x=["Human Cost", "AI Platform", "AI Usage", "Residual Labor"],
        y=[human_monthly, -savings, ai_usage_cost, residual_human_cost],
        connector={"line": {"color": "gray"}}
    ))
    fig_waterfall.update_layout(title="Waterfall: Human → AI", showlegend=False)
    st.plotly_chart(fig_waterfall)

    # 4. Monthly Cost Breakdown
    st.subheader("📊 Monthly Cost Breakdown")
    fig, ax = plt.subplots()
    labels = ['Human Agent', 'AI-Enabled']
    human_bar = [human_monthly, 0]
    ai_bars = [0, ai_monthly_fee]
    ai_usage = [0, ai_usage_cost]
    ai_residual = [0, residual_human_cost]

    ax.bar(labels, human_bar, label='Human Labor')
    ax.bar(labels, ai_bars, bottom=human_bar, label='AI Platform Fee')
    ax.bar(labels, ai_usage, bottom=[sum(x) for x in zip(human_bar, ai_bars)], label='AI Usage')
    ax.bar(labels, ai_residual, bottom=[sum(x) for x in zip(human_bar, ai_bars, ai_usage)], label='Residual Human')
    ax.set_ylabel('Monthly Cost ($)')
    ax.legend()
    st.pyplot(fig)

    # 5. Net savings over time
    st.subheader("📈 Cumulative Net Savings (12 months)")
    months = list(range(1, 13))
    cumulative = [savings * m for m in months]
    fig_line, ax_line = plt.subplots()
    ax_line.plot(months, cumulative, marker='o')
    ax_line.axhline(integration_cost, linestyle='--', color='red', label='Integration Cost')
    ax_line.set_xlabel("Month")
    ax_line.set_ylabel("Cumulative Savings ($)")
    ax_line.legend()
    st.pyplot(fig_line)
