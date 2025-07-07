import streamlit as st
import pandas as pd
import plotly.express as px
import calendar

st.set_page_config(page_title="Renewable Readiness Score", layout="wide")
st.title("🌿 Renewable Transition Readiness Score Dashboard")

# --- Load Data ---
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

    # Try parsing '17-Apr' style
    df['Date'] = pd.to_datetime(df['Date'], format='%d-%b', errors='coerce')
    df.dropna(subset=['Date'], inplace=True)

    # Format: Apr-17
    df['Month'] = df['Date'].dt.strftime('%b-%y')
    df['Quarter'] = df['Date'].dt.to_period("Q").astype(str)
    df['Year'] = df['Date'].dt.year

    # Format quarters as: Q1 2024-25
    def format_quarter(row):
        q = f"Q{((row['Date'].month - 1) // 3 + 1)}"
        fy = row['Date'].year if row['Date'].month >= 4 else row['Date'].year - 1
        return f"{q} {fy}-{str(fy + 1)[-2:]}"
    df['QuarterFormatted'] = df.apply(format_quarter, axis=1)

    # Convert numerics
    for col in expected_cols[1:]:
        df[col] = pd.to_numeric(df[col], errors='coerce')
    df.dropna(inplace=True)

    # Calculations
    df['Total Renewable Capacity'] = (
        df['Solar power plants Installed capacity'] +
        df['Wind power plants Installed capacity'] +
        df['Hydro power plants Installed capacity']
    )
    df['Renewable Share (%)'] = (df['Total Renewable Capacity'] / df['Power Consumption']) * 100
    df['Norm_Budget'] = (df['Budgetary allocation for infrastructure sector'] - df['Budgetary allocation for infrastructure sector'].min()) / (
        df['Budgetary allocation for infrastructure sector'].max() - df['Budgetary allocation for infrastructure sector'].min()
    )
    df['Norm_Share'] = (df['Renewable Share (%)'] - df['Renewable Share (%)'].min()) / (
        df['Renewable Share (%)'].max() - df['Renewable Share (%)'].min()
    )
    df['Readiness Score'] = 0.5 * df['Norm_Budget'] + 0.5 * df['Norm_Share']

    df = df.sort_values('Date')
    return df

# --- Load and Validate ---
df = load_data()
if df is None or df.empty:
    st.warning("⚠️ No valid data available. Please check your CSV.")
    st.stop()

# --- Preview Type & Month/Quarter Selection ---
preview_type = st.selectbox("📅 Preview Type", ["Monthly", "Quarterly"])

if preview_type == "Monthly":
    period_list = df['Month'].unique().tolist()
else:
    period_list = df['QuarterFormatted'].unique().tolist()

selected_period = st.selectbox("📆 Select Month or Quarter", period_list)

# --- KPI Cards (always latest month) ---
latest = df.iloc[-1]
kpi1, kpi2, kpi3 = st.columns(3)
kpi1.metric("🔋 Renewable Share (%)", f"{latest['Renewable Share (%)']:.2f}%")
kpi2.metric("💰 Infra Budget (₹ Cr)", f"{latest['Budgetary allocation for infrastructure sector']:.0f}")
kpi3.metric("📊 Readiness Score", f"{latest['Readiness Score']:.2f}")

# --- Filter by Selected Period ---
if preview_type == "Monthly":
    filtered = df[df['Month'] == selected_period]
else:
    filtered = df[df['QuarterFormatted'] == selected_period]

# Fallback in case nothing found
if filtered.empty:
    st.warning("⚠️ No data found for selected period.")
    st.stop()

# --- Charts ---
col1, col2 = st.columns([1, 2])

with col1:
    st.subheader("⚡ Renewable Energy Mix")
    donut_data = {
        "Source": ["Solar", "Wind", "Hydro"],
        "Capacity": [
            filtered['Solar power plants Installed capacity'].values[0],
            filtered['Wind power plants Installed capacity'].values[0],
            filtered['Hydro power plants Installed capacity'].values[0]
        ]
    }
    fig_donut = px.pie(donut_data, values='Capacity', names='Source', hole=0.5,
                       color_discrete_sequence=px.colors.sequential.Blues)
    fig_donut.update_traces(textposition='inside', textinfo='percent+label')
    st.plotly_chart(fig_donut, use_container_width=True)

with col2:
    st.subheader("📈 Readiness Score Over Time")
    fig_score = px.line(df, x='Month', y='Readiness Score', markers=True)
    st.plotly_chart(fig_score, use_container_width=True)

# --- Optional Table ---
with st.expander("🔍 View Underlying Data Table"):
    st.dataframe(df[[
        'Month', 'QuarterFormatted', 'Renewable Share (%)',
        'Readiness Score', 'Solar power plants Installed capacity',
        'Wind power plants Installed capacity', 'Hydro power plants Installed capacity',
        'Power Consumption', 'Budgetary allocation for infrastructure sector'
    ]])