import streamlit as st
import pandas as pd
import plotly.graph_objects as go

st.set_page_config(layout="wide")

# === Load Data ===
df = pd.read_csv("data/Retail_Health.csv")
df.columns = df.columns.str.strip()

# === Parse Date ===
df['Date'] = pd.to_datetime(df['Date'], errors='coerce')
df = df.dropna(subset=['Date'])
df['Month'] = df['Date'].dt.strftime('%b-%y')

# === Clean Numeric Columns ===
numeric_cols = ['CCI', 'Inflation', 'Private Consumption', 'UPI Transactions', 'Repo Rate', 'Per Capita NNI']
for col in numeric_cols:
    df[col] = pd.to_numeric(df[col], errors='coerce')

# === Normalize Variables ===
df_norm = df.copy()
for col in numeric_cols:
    df_norm[col + ' (norm)'] = (df[col] - df[col].min()) / (df[col].max() - df[col].min())

# === Composite Index ===
df_norm['Retail Index'] = df_norm[[col + ' (norm)' for col in numeric_cols]].mean(axis=1)

# === Header ===
st.title("Retail Health Index Dashboard")
st.markdown("*This dashboard presents a composite Retail Health Index derived from economic and consumption indicators.*")

# === Latest Metrics ===
latest = df_norm.sort_values("Date").iloc[-1]
col1, col2, col3 = st.columns(3)
with col1:
    st.metric("Retail Index", f"{latest['Retail Index']*100:.1f}%")
with col2:
    st.metric("Consumer Confidence Index (CCI)", f"{latest['CCI']:.1f}")
with col3:
    st.metric("UPI Transactions (Billion)", f"{latest['UPI Transactions']:.2f}")

# === Line Chart ===
fig = go.Figure()
fig.add_trace(go.Scatter(x=df['Date'], y=df_norm['Retail Index'], mode='lines+markers', name='Retail Index'))
fig.update_layout(
    title='Retail Index Over Time',
    xaxis_title='Date',
    yaxis_title='Normalized Index (0–1)',
    template='plotly_dark',
    height=450
)
st.plotly_chart(fig, use_container_width=True)

# === Breakdown Table ===
if st.checkbox("Show Raw & Normalized Data"):
    st.dataframe(df_norm[['Date', 'Month'] + numeric_cols + [col + ' (norm)' for col in numeric_cols] + ['Retail Index']])