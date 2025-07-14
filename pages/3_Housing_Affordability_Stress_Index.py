import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import streamlit.components.v1 as components

st.set_page_config(page_title="Housing Affordability Score", layout="wide")
st.title("🏠 Housing Affordability Score")
st.markdown("*This index reflects how affordable urban housing is based on income (NNI), housing prices (PPI), and loan interest rates.*")

# --- Load Data ---
@st.cache_data
def load_data():
    try:
        df = pd.read_csv("data/Housing_Affordability.csv")
    except FileNotFoundError:
        st.error("❌ Could not find 'data/Housing_Affordability.csv'.")
        return None

    df.columns = df.columns.str.strip()
    expected_cols = [
        'Date', 'Housing Loan Interest Rate',
        'Property Price Index', 'Urbanization Rate', 'Per Capita NNI'
    ]
    for col in expected_cols:
        if col not in df.columns:
            st.error(f"❌ Missing column: `{col}`")
            return None

    df['Date'] = pd.to_datetime(df['Date'], errors='coerce')
    df.dropna(subset=['Date'], inplace=True)
    df['Month'] = df['Date'].dt.strftime('%b-%y')

    for col in ['Housing Loan Interest Rate', 'Property Price Index', 'Urbanization Rate', 'Per Capita NNI']:
        df[col] = df[col].replace('[%,]', '', regex=True).astype(float)

    # Loan Factor: decreases with higher interest rate
    df['Loan Factor'] = np.exp(-df['Housing Loan Interest Rate'] / 10)

    # Affordability Index
    df['Affordability Index'] = (df['Per Capita NNI'] / df['Property Price Index']) * df['Loan Factor']

    # Normalize for Score (0 to 1)
    min_ai, max_ai = df['Affordability Index'].min(), df['Affordability Index'].max()
    df['Affordability Score'] = (df['Affordability Index'] - min_ai) / (max_ai - min_ai)

    df = df.sort_values('Date')
    return df

df = load_data()
if df is None or df.empty:
    st.stop()

# --- Latest KPIs ---
latest = df.iloc[-1]
kpi_style = """
<style>
.card {
    padding: 1rem;
    border-radius: 16px;
    box-shadow: 0 4px 12px rgba(0,0,0,0.1);
    color: white;
    font-weight: bold;
    text-align: center;
}
.green-card { background: linear-gradient(#003366, #006699, #3399CC); }
.grey-card { background: linear-gradient(#006666, #009999, #33CCCC); }
.red-card { background: linear-gradient(#660000, #993333, #CC6666); }
</style>
"""
st.markdown(kpi_style, unsafe_allow_html=True)

col1, col2, col3 = st.columns(3)
with col1:
    st.markdown(f"""
        <div class="card green-card">
            <div style="font-size: 1.2rem;">🗓 Latest Period</div>
            <div style="font-size: 2rem;">{latest['Month']}</div>
        </div>
    """, unsafe_allow_html=True)
with col2:
    st.markdown(f"""
        <div class="card grey-card">
            <div style="font-size: 1.2rem;">🏡 Affordability Score</div>
            <div style="font-size: 2rem;">{latest['Affordability Score']:.2f}</div>
        </div>
    """, unsafe_allow_html=True)
with col3:
    st.markdown(f"""
        <div class="card red-card">
            <div style="font-size: 1.2rem;">💰 NNI (Per Capita)</div>
            <div style="font-size: 2rem;">₹{latest['Per Capita NNI']:,.0f}</div>
        </div>
    """, unsafe_allow_html=True)

# --- Preview Options ---
selected_month = st.selectbox("📅 Select Month", df['Month'].unique()[::-1])

selected_row = df[df['Month'] == selected_month].iloc[0]

# === CHART WRAPPER ===
def wrapped_chart(title, fig, height=420):
    chart_html = fig.to_html(include_plotlyjs="cdn", full_html=False)
    components.html(f"""
    <div style="
        background-color: #1e1e1e;
        padding: 1rem;
        border-radius: 12px;
        margin-bottom: 1.5rem;
        box-shadow: 0 2px 5px rgba(0,0,0,0.2);
        color: white;
    ">
        <h4 style="margin-top: 0; margin-bottom: 10px;">{title}</h4>
        {chart_html}
    </div>
    """, height=height + 60)

# --- Radar Chart ---
radar = pd.DataFrame({
    'Metric': ['Loan Factor', 'PPI', 'Urbanization', 'NNI'],
    'Value': [
        selected_row['Loan Factor'],
        selected_row['Property Price Index'] / df['Property Price Index'].max(),  # Normalize
        selected_row['Urbanization Rate'] / 100,
        selected_row['Per Capita NNI'] / df['Per Capita NNI'].max()
    ]
})
radar_fig = px.line_polar(radar, r='Value', theta='Metric', line_close=True,
                          color_discrete_sequence=['cyan'])
radar_fig.update_traces(fill='toself')
radar_fig.update_layout(polar=dict(bgcolor='rgba(0,0,0,0)'), paper_bgcolor='rgba(0,0,0,0)', font_color='white')
wrapped_chart(f"Housing Input Factors – {selected_month}", radar_fig)

# --- Gauge Chart ---
gauge = go.Figure(go.Indicator(
    mode="gauge+number",
    value=selected_row['Affordability Score'],
    number={'font': {'color': 'white'}},
    domain={'x': [0, 1], 'y': [0, 1]},
    gauge={
        'axis': {'range': [0, 1], 'tickcolor': 'white'},
        'bar': {'color': "black"},
        'steps': [
            {'range': [0, 0.2], 'color': "#800000"},
            {'range': [0.2, 0.4], 'color': "#CC6600"},
            {'range': [0.4, 0.6], 'color': "#CCCC00"},
            {'range': [0.6, 0.8], 'color': "#66CC00"},
            {'range': [0.8, 1.0], 'color': "#008000"},
        ]
    }
))
gauge.update_layout(height=400, paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font_color='white')
wrapped_chart(f"Affordability Score – {selected_month}", gauge)

# --- Line Chart Over Time ---
st.subheader("📈 Affordability Score Over Time")
score_line = px.line(df, x='Month', y='Affordability Score', markers=True,
                     color_discrete_sequence=['#33CC33'])
score_line.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font_color='white')
st.plotly_chart(score_line, use_container_width=True)

# --- Data Table ---
with st.expander("🔍 View Underlying Data Table"):
    st.dataframe(df[[
        'Month', 'Housing Loan Interest Rate', 'Property Price Index',
        'Urbanization Rate', 'Per Capita NNI', 'Loan Factor',
        'Affordability Index', 'Affordability Score'
    ]])