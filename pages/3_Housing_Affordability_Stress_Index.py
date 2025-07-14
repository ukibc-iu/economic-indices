import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import streamlit.components.v1 as components

st.set_page_config(page_title="🏠 Housing Affordability Index", layout="wide")
st.title("🏠 Housing Affordability Stress Index")
st.markdown("*A composite score that reflects how affordable housing is in India, considering property prices, income, and interest rates.*")

# --- Load Data ---
@st.cache_data
def load_data():
    df = pd.read_csv("data/Housing_Affordability.csv")
    df.columns = df.columns.str.strip()

    # Clean & convert columns
    df['Date'] = pd.to_datetime(df['Date'], errors='coerce')
    df.dropna(subset=['Date'], inplace=True)

    # Convert percentages to float
    df['Housing Loan Interest Rate'] = df['Housing Loan Interest Rate'].str.replace('%', '').astype(float)
    df['Urbanization Rate'] = df['Urbanization Rate'].str.replace('%', '').astype(float)

    # Ensure numeric
    df['Property Price Index'] = pd.to_numeric(df['Property Price Index'], errors='coerce')
    df['Per Capita NNI'] = pd.to_numeric(df['Per Capita NNI'], errors='coerce')

    df.dropna(inplace=True)
    df.sort_values('Date', inplace=True)

    # Month & Quarter for UI
    df['Month'] = df['Date'].dt.strftime('%b-%y')
    df['Quarter'] = df['Date'].dt.to_period('Q').astype(str)

    # --- Calculate Loan Eligibility Factor ---
    df['LoanFactor'] = np.exp(-df['Housing Loan Interest Rate'] / 10)

    # --- Affordability Index ---
    df['AffordabilityIndex'] = (df['Property Price Index'] / df['Per Capita NNI']) * df['LoanFactor']

    # Normalize for Affordability Score (lower = better)
    min_ai = df['AffordabilityIndex'].min()
    max_ai = df['AffordabilityIndex'].max()
    df['Affordability Score'] = 1 - (df['AffordabilityIndex'] - min_ai) / (max_ai - min_ai)

    return df

df = load_data()
if df.empty:
    st.warning("⚠️ No data available.")
    st.stop()

# --- Latest Stats ---
latest = df.iloc[-1]
st.subheader("📌 Latest Overview")

col1, col2, col3 = st.columns(3)
col1.metric("📅 Latest Period", latest['Month'])
col2.metric("🏠 Affordability Score", f"{latest['Affordability Score']:.2f}")
col3.metric("💸 Interest Rate", f"{latest['Housing Loan Interest Rate']:.2f}%")

# --- Trend Line ---
st.subheader("📈 Affordability Score Over Time")
fig_line = px.line(df, x='Month', y='Affordability Score', markers=True,
                   color_discrete_sequence=["#00cc99"])
fig_line.update_layout(height=450, paper_bgcolor='rgba(0,0,0,0)', font_color='white')
st.plotly_chart(fig_line, use_container_width=True)

# --- Select Month/Quarter ---
preview_type = st.radio("View By", ["Monthly", "Quarterly"])
if preview_type == "Monthly":
    options = df['Month'].unique().tolist()
    selected = st.selectbox("Select Month", options)
    filtered = df[df['Month'] == selected]
else:
    options = df['Quarter'].unique().tolist()
    selected = st.selectbox("Select Quarter", options)
    filtered = df[df['Quarter'] == selected]

if filtered.empty:
    st.warning("No data found for selection.")
    st.stop()

row = filtered.iloc[0]

# --- Donut Chart: Component Contributions ---
fig_donut = go.Figure(data=[go.Pie(
    labels=["PPI", "NNI (inv.)", "Loan Burden"],
    values=[
        row['Property Price Index'],
        1 / row['Per Capita NNI'],
        1 - row['LoanFactor']
    ],
    hole=0.5,
    marker=dict(colors=["#ff9999", "#66b3ff", "#99ff99"])
)])
fig_donut.update_layout(title="Component Stress Breakdown", height=400)
st.plotly_chart(fig_donut, use_container_width=True)

# --- Gauge Chart ---
fig_gauge = go.Figure(go.Indicator(
    mode="gauge+number",
    value=row['Affordability Score'],
    gauge={
        'axis': {'range': [0, 1]},
        'bar': {'color': "black"},
        'steps': [
            {'range': [0, 0.2], 'color': "#ff0000"},
            {'range': [0.2, 0.4], 'color': "#ff9900"},
            {'range': [0.4, 0.6], 'color': "#ffff00"},
            {'range': [0.6, 0.8], 'color': "#99cc00"},
            {'range': [0.8, 1.0], 'color': "#00cc66"}
        ]
    }
))
fig_gauge.update_layout(title="Affordability Score Gauge", height=400)
st.plotly_chart(fig_gauge, use_container_width=True)

# --- Show Raw Data ---
with st.expander("📊 View Data Table"):
    st.dataframe(df)