import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

st.set_page_config(page_title="Renewable Readiness Score", layout="wide")
st.title("🌿 Renewable Transition Readiness Score Dashboard")

# --- Load Data ---
@st.cache_data
def load_data():
    df = pd.read_csv("data/Renewable_Energy.csv")
    df.columns = df.columns.str.strip()

    df['Date'] = pd.to_datetime(df['Date'], format='%d-%b', errors='coerce')
    df.dropna(subset=['Date'], inplace=True)

    df.rename(columns={
        'Solar power plants Installed capacity': 'Solar',
        'Wind power plants Installed capacity': 'Wind',
        'Hydro power plants Installed capacity': 'Hydro',
        'Budgetary allocation for infrastructure sector': 'Budget',
        'Power Consumption': 'Consumption'
    }, inplace=True)

    df['Month'] = df['Date'].dt.strftime('%b-%y')
    df['Quarter'] = df['Date'].dt.to_period('Q').astype(str)

    for col in ['Solar', 'Wind', 'Hydro', 'Budget', 'Consumption']:
        df[col] = pd.to_numeric(df[col], errors='coerce')

    df.dropna(inplace=True)

    # Derived columns
    df['Total Renewable'] = df['Solar'] + df['Wind'] + df['Hydro']
    df['Renewable Share (%)'] = (df['Total Renewable'] / df['Consumption']) * 100

    # Normalize and score
    df['Norm_Budget'] = (df['Budget'] - df['Budget'].min()) / (df['Budget'].max() - df['Budget'].min())
    df['Norm_Share'] = (df['Renewable Share (%)'] - df['Renewable Share (%)'].min()) / (df['Renewable Share (%)'].max() - df['Renewable Share (%)'].min())
    df['Readiness Score'] = 0.5 * df['Norm_Budget'] + 0.5 * df['Norm_Share']

    df = df.sort_values('Date')

    return df

df = load_data()

# --- KPI Cards (Latest) ---
latest_row = df.iloc[-1]
latest_period = latest_row['Month']
latest_score = round(latest_row['Readiness Score'] * 100, 2)
latest_consumption = f"{int(latest_row['Consumption']):,}"

colA, colB, colC = st.columns(3)
colA.metric("📅 Latest Period", latest_period)
colB.metric("⚡ Readiness Score", f"{latest_score}")
colC.metric("🔌 Power Consumption", f"{latest_consumption} units")

# --- Dropdowns ---
st.markdown("---")
col_view, col_select = st.columns([1, 2])

with col_view:
    view_type = st.selectbox("View Type", ['Monthly', 'Quarterly'])

if view_type == 'Monthly':
    period_options = df['Month'].unique()
    period_col = 'Month'
else:
    # Group by quarter
    df = df.groupby('Quarter').agg({
        'Solar': 'sum',
        'Wind': 'sum',
        'Hydro': 'sum',
        'Budget': 'sum',
        'Consumption': 'sum'
    }).reset_index()

    df['Total Renewable'] = df['Solar'] + df['Wind'] + df['Hydro']
    df['Renewable Share (%)'] = (df['Total Renewable'] / df['Consumption']) * 100

    df['Norm_Budget'] = (df['Budget'] - df['Budget'].min()) / (df['Budget'].max() - df['Budget'].min())
    df['Norm_Share'] = (df['Renewable Share (%)'] - df['Renewable Share (%)'].min()) / (df['Renewable Share (%)'].max() - df['Renewable Share (%)'].min())
    df['Readiness Score'] = 0.5 * df['Norm_Budget'] + 0.5 * df['Norm_Share']
    df.rename(columns={'Quarter': 'Period'}, inplace=True)
    period_col = 'Period'

    df['Month'] = df['Period']  # for uniformity

with col_select:
    selected_period = st.selectbox(f"Select {view_type}", df[period_col].unique())

# --- Filtered Row ---
row = df[df[period_col] == selected_period].iloc[0]

# --- Donut Chart (Renewable Mix) ---
fig_donut = go.Figure(
    data=[go.Pie(
        labels=['Solar', 'Wind', 'Hydro'],
        values=[row['Solar'], row['Wind'], row['Hydro']],
        hole=0.5,
        marker=dict(colors=['#FDB813', '#76B041', '#1E90FF'])
    )]
)
fig_donut.update_layout(title=f"🔆 Renewable Capacity Mix – {selected_period}", showlegend=True)

# --- Line Chart for Readiness Score ---
fig_line = px.line(
    df,
    x=period_col,
    y='Readiness Score',
    title="📈 Readiness Score Over Time",
    markers=True
)
fig_line.update_traces(line=dict(color="#6A5ACD", width=3))

# --- Layout Display ---
st.markdown("---")
col1, col2 = st.columns(2)

with col1:
    st.plotly_chart(fig_donut, use_container_width=True)

with col2:
    st.plotly_chart(fig_line, use_container_width=True)

# --- Data Table ---
with st.expander("🧾 View Data Table"):
    st.dataframe(df[[period_col, 'Readiness Score', 'Consumption', 'Solar', 'Wind', 'Hydro']])