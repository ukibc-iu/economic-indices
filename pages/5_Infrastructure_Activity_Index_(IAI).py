import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime

# Page config
st.set_page_config(page_title="Infrastructure Activity Index (IAI)", layout="wide")
st.title("🏗️ Infrastructure Activity Index (IAI)")
st.markdown("""
A composite indicator to monitor and forecast infrastructure development across sectors in India.
Useful for cement/steel producers, infrastructure contractors, investors, and policy planners.
""")

# Load data
@st.cache_data
def load_data():
    df = pd.read_csv("data/Infrastructure_Activity.csv")
    df.columns = df.columns.str.strip()
    df['Date'] = pd.to_datetime(df['Date'], errors='coerce')
    df['Month'] = df['Date'].dt.strftime('%b-%Y')
    return df.dropna(subset=['Date'])

df = load_data()

# Normalize selected columns
cols_to_normalize = [
    'Highway construction actual',
    'Railway line construction actual',
    'Power T&D line constr (220KV plus)',
    'Cement price',
    'GVA: construction (Basic Price)',
    'Budgetary allocation for infrastructure sector'
]

for col in cols_to_normalize:
    norm_col = f'Norm_{col}'
    df[norm_col] = (df[col] - df[col].min()) / (df[col].max() - df[col].min())

# Invert Cement Price (higher cement price is a negative indicator)
df['Norm_Cement_Inverted'] = 1 - df['Norm_Cement price']

# Calculate IAI Score
df['IAI Score'] = (
    0.2 * df['Norm_Highway construction actual'] +
    0.2 * df['Norm_Railway line construction actual'] +
    0.15 * df['Norm_Power T&D line constr (220KV plus)'] +
    0.1 * df['Norm_Cement_Inverted'] +
    0.25 * df['Norm_GVA: construction (Basic Price)'] +
    0.1 * df['Norm_Budgetary allocation for infrastructure sector']
)

# Latest data
latest = df.sort_values('Date').iloc[-1]

# KPI Cards
st.subheader("📌 Latest Snapshot")
col1, col2, col3 = st.columns(3)
col1.metric("🗓 Month", latest['Month'])
col2.metric("📊 IAI Score", f"{latest['IAI Score']:.2f}")
col3.metric("📈 GVA: Construction", f"{latest['GVA: construction (Basic Price)']:,}")

# IAI Line Chart
st.subheader("📈 Infrastructure Activity Index Trend")
fig_iai = px.line(df, x='Date', y='IAI Score', markers=True,
                  title="IAI Score Over Time",
                  labels={"Date": "Month", "IAI Score": "Index Score"},
                  color_discrete_sequence=["#0074D9"])
fig_iai.update_layout(height=450)
st.plotly_chart(fig_iai, use_container_width=True)

# Component Trends
st.subheader("🔍 Component-wise Trends")
selected_component = st.selectbox("Choose component to view trend:", [
    'Highway construction actual',
    'Railway line construction actual',
    'Power T&D line constr (220KV plus)',
    'Cement price',
    'GVA: construction (Basic Price)',
    'Budgetary allocation for infrastructure sector'
])

fig_component = px.line(df, x='Date', y=selected_component, markers=True,
                        title=f"{selected_component} Over Time",
                        color_discrete_sequence=["#FF4136"])
st.plotly_chart(fig_component, use_container_width=True)

# Show data table
with st.expander("📂 View Full Dataset"):
    display_cols = ['Date', 'Month'] + cols_to_normalize + ['IAI Score']
    st.dataframe(df[display_cols].sort_values('Date'), use_container_width=True)

# Download as CSV
st.download_button(
    label="📥 Download IAI Data as CSV",
    data=df.to_csv(index=False).encode('utf-8'),
    file_name="Infrastructure_Activity_Index.csv",
    mime="text/csv"
)