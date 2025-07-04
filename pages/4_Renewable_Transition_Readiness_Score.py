import streamlit as st
import pandas as pd
import plotly.graph_objects as go

st.set_page_config(layout="wide")

# === Load Data ===
df = pd.read_csv("data/Renewable_Energy.csv")

# === Clean Column Names ===
df.columns = df.columns.str.encode('ascii', 'ignore').str.decode('ascii')  # remove non-ascii
df.columns = df.columns.str.replace(r'[\r\n]+', '', regex=True).str.strip()

# Rename columns for consistency
df.rename(columns={
    'Solar power plants Installed capacity': 'Solar',
    'Wind power plants Installed capacity': 'Wind',
    'Hydro power plants Installed capacity': 'Hydro',
    'Budgetary allocation for infrastructure sector': 'Budget',
    'Power Consumption': 'Consumption'
}, inplace=True)

# === Parse Date ===
df['Date'] = pd.to_datetime(df['Date'], format='%b-%y', errors='coerce')
df = df.dropna(subset=['Date'])
df = df.sort_values('Date')
df['Month'] = df['Date'].dt.strftime('%b-%Y')

# === Convert Numeric Columns ===
for col in ['Solar', 'Wind', 'Hydro', 'Budget', 'Consumption']:
    df[col] = pd.to_numeric(df[col], errors='coerce')

# === Create Computed Columns ===
df['Installed RE Capacity'] = df['Solar'] + df['Wind'] + df['Hydro']
df['Renewable Share'] = df['Installed RE Capacity'] / df['Consumption']

# === Readiness Score ===
# We'll use a basic formula here — scale each factor to 0-1, and average them
from sklearn.preprocessing import MinMaxScaler

scaler = MinMaxScaler()
df[['RE Capacity Score', 'Budget Score', 'Share Score']] = scaler.fit_transform(df[['Installed RE Capacity', 'Budget', 'Renewable Share']])
df['Readiness Score'] = df[['RE Capacity Score', 'Budget Score', 'Share Score']].mean(axis=1)

# === Header ===
st.title("Renewable Transition Readiness Score")
st.markdown("*An index measuring readiness for renewable transition using capacity, budget, and deployment ratio.*")

# === KPIs ===
latest = df.iloc[-1]
col1, col2, col3, col4 = st.columns(4)
col1.metric("Installed RE Capacity", f"{latest['Installed RE Capacity']:.0f} MW")
col2.metric("Power Consumption", f"{latest['Consumption']:.0f} GW")
col3.metric("Renewable Share", f"{latest['Renewable Share']*100:.2f}%")
col4.metric("Readiness Score", f"{latest['Readiness Score']*100:.1f}")

# === Line Chart: Renewable Share ===
fig_share = go.Figure()
fig_share.add_trace(go.Scatter(
    x=df['Date'], y=df['Renewable Share'] * 100,
    mode='lines+markers',
    name='Renewable Share (%)',
    line=dict(color='green')
))
fig_share.update_layout(title="Renewable Share Over Time", yaxis_title="%", xaxis_title="Date", height=400)
st.plotly_chart(fig_share, use_container_width=True)

# === Line Chart: Readiness Score ===
fig_score = go.Figure()
fig_score.add_trace(go.Scatter(
    x=df['Date'], y=df['Readiness Score'] * 100,
    mode='lines+markers',
    name='Readiness Score',
    line=dict(color='orange')
))
fig_score.update_layout(title="Readiness Score Over Time", yaxis_title="Score (0–100)", xaxis_title="Date", height=400)
st.plotly_chart(fig_score, use_container_width=True)

# === Stacked Bar: Components of Readiness Score ===
fig_bar = go.Figure()
fig_bar.add_trace(go.Bar(x=df['Date'], y=df['RE Capacity Score'], name="RE Capacity"))
fig_bar.add_trace(go.Bar(x=df['Date'], y=df['Budget Score'], name="Budget Allocation"))
fig_bar.add_trace(go.Bar(x=df['Date'], y=df['Share Score'], name="Renewable Share"))
fig_bar.update_layout(
    barmode='stack',
    title='Components of Readiness Score',
    xaxis_title="Date",
    yaxis_title="Normalized Score (0–1)",
    height=400
)
st.plotly_chart(fig_bar, use_container_width=True)

# === Raw Data Toggle ===
if st.checkbox("📊 Show Raw Data"):
    st.dataframe(df)