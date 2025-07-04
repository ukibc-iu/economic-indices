import streamlit as st
import pandas as pd
import plotly.express as px
import os

st.set_page_config(page_title="Renewable Readiness Score", layout="wide")
st.title("🌿 Renewable Transition Readiness Score Dashboard")

# Load Data
@st.cache_data
def load_data():
    try:
        df = pd.read_csv("data/Renewable_Energy.csv")
    except FileNotFoundError:
        st.error("❌ Could not find 'data/Renewable_Energy.csv'. Make sure it's in the correct folder.")
        return None

    df.columns = df.columns.str.strip()

    # Required columns
    expected_cols = [
        'Date',
        'Solar power plants Installed capacity',
        'Wind power plants Installed capacity',
        'Hydro power plants Installed capacity',
        'Budgetary allocation for infrastructure sector',
        'Power Consumption'
    ]
    for col in expected_cols:
        if col not in df.columns:
            st.error(f"❌ Missing column: `{col}`")
            return None

    # Fix date format (handles '17-Apr' properly)
    df['Date'] = pd.to_datetime(df['Date'], format='%d-%b', errors='coerce')
    df.dropna(subset=['Date'], inplace=True)
    df['Month'] = df['Date'].dt.strftime('%b-%y')

    # Convert all numeric columns
    for col in expected_cols[1:]:
        df[col] = pd.to_numeric(df[col], errors='coerce')

    df.dropna(inplace=True)

    return df

df = load_data()
if df is None:
    st.stop()

# --- Calculations ---
df['Total Renewable Capacity'] = (
    df['Solar power plants Installed capacity'] +
    df['Wind power plants Installed capacity'] +
    df['Hydro power plants Installed capacity']
)

df['Renewable Share (%)'] = (df['Total Renewable Capacity'] / df['Power Consumption']) * 100

# Normalize budget and share
df['Norm_Budget'] = (df['Budgetary allocation for infrastructure sector'] - df['Budgetary allocation for infrastructure sector'].min()) / (df['Budgetary allocation for infrastructure sector'].max() - df['Budgetary allocation for infrastructure sector'].min())
df['Norm_Share'] = (df['Renewable Share (%)'] - df['Renewable Share (%)'].min()) / (df['Renewable Share (%)'].max() - df['Renewable Share (%)'].min())

# Compute Readiness Score
df['Readiness Score'] = 0.5 * df['Norm_Budget'] + 0.5 * df['Norm_Share']
df = df.sort_values('Date')

# --- Dashboard Display ---
col1, col2 = st.columns(2)

with col1:
    st.subheader("📈 Renewable Share Over Time")
    fig1 = px.line(df, x='Month', y='Renewable Share (%)', markers=True)
    st.plotly_chart(fig1, use_container_width=True)

with col2:
    st.subheader("🔋 Readiness Score Over Time")
    fig2 = px.line(df, x='Month', y='Readiness Score', markers=True)
    st.plotly_chart(fig2, use_container_width=True)

# View data
with st.expander("📊 View Data Table"):
    st.dataframe(df[[
        'Month',
        'Renewable Share (%)',
        'Readiness Score',
        'Solar power plants Installed capacity',
        'Wind power plants Installed capacity',
        'Hydro power plants Installed capacity',
        'Power Consumption',
        'Budgetary allocation for infrastructure sector'
    ]])