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
        st.error("❌ Could not find 'data/Renewable_Energy.csv'.")
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

    def fiscal_quarter(row):
        m = row.month
        y = row.year
        if m in [4, 5, 6]:
            return f"Q1 {y}-{str(y+1)[-2:]}"
        elif m in [7, 8, 9]:
            return f"Q2 {y}-{str(y+1)[-2:]}"
        elif m in [10, 11, 12]:
            return f"Q3 {y}-{str(y+1)[-2:]}"
        else:
            return f"Q4 {y-1}-{str(y)[-2:]}"
    df['Quarter'] = df['Date'].apply(fiscal_quarter)

    for col in expected_cols[1:]:
        df[col] = pd.to_numeric(df[col], errors='coerce')

    df.dropna(inplace=True)

    df['Total Renewable Capacity'] = (
        df['Solar power plants Installed capacity'] +
        df['Wind power plants Installed capacity'] +
        df['Hydro power plants Installed capacity']
    )
    df['Renewable Share (%)'] = (df['Total Renewable Capacity'] / df['Power Consumption']) * 100

    df['Norm_Budget'] = (
        (df['Budgetary allocation for infrastructure sector'] - df['Budgetary allocation for infrastructure sector'].min()) /
        (df['Budgetary allocation for infrastructure sector'].max() - df['Budgetary allocation for infrastructure sector'].min())
    )
    df['Norm_Share'] = (
        (df['Renewable Share (%)'] - df['Renewable Share (%)'].min()) /
        (df['Renewable Share (%)'].max() - df['Renewable Share (%)'].min())
    )
    df['Readiness Score'] = 0.5 * df['Norm_Budget'] + 0.5 * df['Norm_Share']
    df = df.sort_values('Date')
    return df

df = load_data()
if df is None:
    st.stop()

# --- KPIs (Latest Values) ---
latest = df.iloc[-1]
kpi1, kpi2, kpi3 = st.columns(3)
kpi1.metric("🔆 Latest Solar Capacity", f"{latest['Solar power plants Installed capacity']:.0f} MW")
kpi2.metric("🌬️ Latest Wind Capacity", f"{latest['Wind power plants Installed capacity']:.0f} MW")
kpi3.metric("💧 Latest Hydro Capacity", f"{latest['Hydro power plants Installed capacity']:.0f} MW")

# --- Selections ---
preview_type = st.selectbox("Preview Type", ["Monthly", "Quarterly"])

if preview_type == "Monthly":
    options = df['Month'].unique().tolist()
else:
    options = df['Quarter'].unique().tolist()

selected_time = st.selectbox(f"Select {preview_type}", options[::-1])  # latest on top

if preview_type == "Monthly":
    selected_df = df[df['Month'] == selected_time]
else:
    selected_df = df[df['Quarter'] == selected_time]

# --- Donut Chart ---
st.subheader("🔄 Renewable Energy Mix")

solar = selected_df['Solar power plants Installed capacity'].sum()
wind = selected_df['Wind power plants Installed capacity'].sum()
hydro = selected_df['Hydro power plants Installed capacity'].sum()

fig_donut = go.Figure(
    data=[
        go.Pie(
            labels=['Solar', 'Wind', 'Hydro'],
            values=[solar, wind, hydro],
            hole=0.5,
            marker=dict(colors=["#FDB813", "#5DADE2", "#58D68D"])
        )
    ]
)
fig_donut.update_layout(
    showlegend=True,
    margin=dict(t=30, b=0),
    height=400
)
st.plotly_chart(fig_donut, use_container_width=True)

# --- Readiness Score Over Time ---
st.subheader("📈 Readiness Score Over Time")
if preview_type == "Monthly":
    fig_line = px.line(df, x='Month', y='Readiness Score', markers=True)
else:
    grouped = df.groupby('Quarter', as_index=False).mean(numeric_only=True)
    fig_line = px.line(grouped, x='Quarter', y='Readiness Score', markers=True)

st.plotly_chart(fig_line, use_container_width=True)

# --- Data Table ---
with st.expander("📊 View Data Table"):
    st.dataframe(df[[
        'Month',
        'Quarter',
        'Renewable Share (%)',
        'Readiness Score',
        'Solar power plants Installed capacity',
        'Wind power plants Installed capacity',
        'Hydro power plants Installed capacity',
        'Power Consumption',
        'Budgetary allocation for infrastructure sector'
    ]])