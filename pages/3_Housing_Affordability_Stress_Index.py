import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

st.set_page_config(page_title="Housing Affordability Stress Index", layout="wide")
st.title("🏠 Housing Affordability Stress Index (HASI)")

# --- Load Data ---
@st.cache_data
def load_data():
    df = pd.read_csv("data/Housing_Affordability.csv")
    df.columns = df.columns.str.strip()

    df['Date'] = pd.to_datetime(df['Date'], errors='coerce')
    df.dropna(subset=['Date'], inplace=True)

    df['Month'] = df['Date'].dt.strftime('%b-%Y')
    df['Quarter'] = df['Date'].dt.to_period('Q').astype(str)

    # Convert % and clean numeric values
    df['Housing Loan Interest Rate'] = df['Housing Loan Interest Rate'].str.replace('%', '').astype(float) / 100
    df['Urbanization Rate'] = df['Urbanization Rate'].str.replace('%', '').astype(float) / 100
    df['Per Capita NNI'] = df['Per Capita NNI'].astype(float)

    # Calculate Affordability Ratio using only index
    loan_eligibility_factor = 5
    df['Affordability Ratio'] = df['Property Price Index'] / (df['Per Capita NNI'] * loan_eligibility_factor)

    # Normalize Affordability Stress Score
    df['Stress Score'] = (df['Affordability Ratio'] - df['Affordability Ratio'].min()) / (
        df['Affordability Ratio'].max() - df['Affordability Ratio'].min()
    )

    return df

df = load_data()

# --- Latest Snapshot ---
latest = df.iloc[-1]
st.subheader(f"📅 Latest: {latest['Month']}")
col1, col2, col3 = st.columns(3)

col1.metric("🏠 Property Price Index", f"{latest['Property Price Index']:.2f}")
col2.metric("🧮 Affordability Ratio", f"{latest['Affordability Ratio']:.2f}")
col3.metric("🔥 Stress Score", f"{latest['Stress Score']:.2f}")

# --- Line Chart ---
st.plotly_chart(
    px.line(df, x="Month", y="Stress Score", markers=True,
            title="Housing Affordability Stress Score Over Time",
            color_discrete_sequence=["red"])
    .update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font_color='white'),
    use_container_width=True
)

# --- Gauge Chart ---
fig_gauge = go.Figure(go.Indicator(
    mode="gauge+number",
    value=latest['Stress Score'],
    gauge={
        'axis': {'range': [0, 1]},
        'bar': {'color': "darkred"},
        'steps': [
            {'range': [0, 0.3], 'color': "lightgreen"},
            {'range': [0.3, 0.6], 'color': "yellow"},
            {'range': [0.6, 1], 'color': "red"},
        ],
    },
    number={'suffix': "", 'font': {'color': "white"}}
))
fig_gauge.update_layout(height=350, title="Current Housing Stress Score", font_color="white")
st.plotly_chart(fig_gauge, use_container_width=True)

# --- Data Table ---
with st.expander("🔍 View Full Data Table"):
    st.dataframe(df[['Month', 'Property Price Index', 'Per Capita NNI', 'Affordability Ratio', 'Stress Score']])