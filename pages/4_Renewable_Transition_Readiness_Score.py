import streamlit as st
import pandas as pd
import plotly.graph_objects as go

st.set_page_config(layout="wide")

# === Load Data ===
df = pd.read_csv("data/Renewable_Energy.csv")  # <-- Correct filename
df.columns = df.columns.str.strip()

# === Parse Date ===
df['Date'] = pd.to_datetime(df['Date'], format='%b-%y', errors='coerce')
df = df.dropna(subset=['Date'])
df['Month'] = df['Date'].dt.strftime('%b-%Y')

# === Convert numeric columns ===
cols_to_numeric = [
    'Solar power plants Installed capacity',
    'Wind power plants Installed capacity',
    'Hydro power plants Installed capacity',
    'Budgetary allocation for infrastructure sector ',
    'Power Consumption'
]
for col in cols_to_numeric:
    df[col] = pd.to_numeric(df[col], errors='coerce')

# === Derived Metrics ===
df['Installed RE Capacity'] = (
    df['Solar power plants Installed capacity'] +
    df['Wind power plants Installed capacity'] +
    df['Hydro power plants Installed capacity']
)

df['Renewable Share'] = df['Installed RE Capacity'] / df['Power Consumption']

# === Header ===
st.title("Renewable Transition Readiness Score")
st.markdown("*An index reflecting renewable energy capacity and its correlation with power consumption and policy support (budget allocations).*")

# === KPI Cards ===
latest = df.sort_values('Date').iloc[-1]
col1, col2, col3 = st.columns(3)
with col1:
    st.metric("Installed RE Capacity (MW)", f"{latest['Installed RE Capacity']:.0f}")
with col2:
    st.metric("Renewable Share", f"{latest['Renewable Share']*100:.2f}%")
with col3:
    st.metric("Power Consumption (GW)", f"{latest['Power Consumption']:.2f}")

# === Line Chart: Installed RE vs Power Consumption ===
fig = go.Figure()
fig.add_trace(go.Scatter(
    x=df['Date'],
    y=df['Installed RE Capacity'],
    name='Installed RE Capacity (MW)',
    mode='lines+markers'
))
fig.add_trace(go.Scatter(
    x=df['Date'],
    y=df['Power Consumption'] * 1000,  # Convert GW to MW
    name='Power Consumption (MW)',
    mode='lines+markers'
))
fig.update_layout(
    title="Installed Renewable Energy Capacity vs Power Consumption",
    xaxis_title="Date",
    yaxis_title="MW",
    height=450,
    plot_bgcolor='rgba(0,0,0,0)',
    paper_bgcolor='rgba(0,0,0,0)'
)
st.plotly_chart(fig, use_container_width=True)

# === Line Chart: Renewable Share Over Time ===
fig2 = go.Figure(go.Scatter(
    x=df['Date'],
    y=df['Renewable Share'] * 100,
    mode='lines+markers',
    line=dict(color='green'),
    name="Renewable Share (%)"
))
fig2.update_layout(
    title="Renewable Share in Power Consumption Over Time",
    xaxis_title="Date",
    yaxis_title="Share (%)",
    height=400,
    plot_bgcolor='rgba(0,0,0,0)',
    paper_bgcolor='rgba(0,0,0,0)'
)
st.plotly_chart(fig2, use_container_width=True)

# === Show Raw Data Toggle ===
if st.checkbox("📄 Show Raw Data"):
    st.dataframe(df.sort_values("Date", ascending=False))