import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

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

    df['Date'] = pd.to_datetime(df['Date'], format='%d-%b', errors='coerce')
    df.dropna(subset=['Date'], inplace=True)
    df['Month'] = df['Date'].dt.strftime('%b-%y')

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

df['Norm_Budget'] = (
    (df['Budgetary allocation for infrastructure sector'] - df['Budgetary allocation for infrastructure sector'].min())
    / (df['Budgetary allocation for infrastructure sector'].max() - df['Budgetary allocation for infrastructure sector'].min())
)
df['Norm_Share'] = (
    (df['Renewable Share (%)'] - df['Renewable Share (%)'].min())
    / (df['Renewable Share (%)'].max() - df['Renewable Share (%)'].min())
)

df['Readiness Score'] = 0.5 * df['Norm_Budget'] + 0.5 * df['Norm_Share']
df = df.sort_values('Date')

# --- UI: Month Selection ---
st.sidebar.title("📅 Select Month")
month_selected = st.sidebar.selectbox("Choose a Month", df['Month'].unique()[::-1])  # latest first
selected_row = df[df['Month'] == month_selected].iloc[0]

# --- Doughnut Chart for Renewable Mix ---
st.subheader(f"🔆 Renewable Energy Mix — {month_selected}")
fig_donut = go.Figure(data=[go.Pie(
    labels=["Solar", "Wind", "Hydro"],
    values=[
        selected_row['Solar power plants Installed capacity'],
        selected_row['Wind power plants Installed capacity'],
        selected_row['Hydro power plants Installed capacity']
    ],
    hole=0.5,
    marker=dict(colors=['#F7DC6F', '#58D68D', '#5DADE2'])
)])
fig_donut.update_layout(height=400, margin=dict(t=10, b=10, l=10, r=10))
st.plotly_chart(fig_donut, use_container_width=True)

# --- Line Chart for Readiness Score ---
st.subheader("📈 Readiness Score Over Time")
fig_line = px.line(df, x='Month', y='Readiness Score', markers=True)
fig_line.update_traces(line=dict(color="#2E86DE", width=3))
st.plotly_chart(fig_line, use_container_width=True)

# --- Optional: View Raw Data ---
with st.expander("📊 View Data Table"):
    st.dataframe(df[[
        'Month',
        'Readiness Score',
        'Solar power plants Installed capacity',
        'Wind power plants Installed capacity',
        'Hydro power plants Installed capacity',
        'Power Consumption',
        'Budgetary allocation for infrastructure sector',
        'Renewable Share (%)'
    ]])