import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

st.set_page_config(page_title="Renewable Readiness Score", layout="wide")
st.title("🌿 Renewable Transition Readiness Score Dashboard")

# --- Load and preprocess data ---
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

    # Add proper datetime index starting from Apr 2017
    start_month = pd.to_datetime('2017-04-01')
    df['Parsed Date'] = pd.date_range(start=start_month, periods=len(df), freq='MS')
    df['Month'] = df['Parsed Date'].dt.strftime('%b-%y')

    # Convert numeric columns
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

# Normalize values for score
df['Norm_Budget'] = (
    (df['Budgetary allocation for infrastructure sector'] - df['Budgetary allocation for infrastructure sector'].min()) /
    (df['Budgetary allocation for infrastructure sector'].max() - df['Budgetary allocation for infrastructure sector'].min())
)

df['Norm_Share'] = (
    (df['Renewable Share (%)'] - df['Renewable Share (%)'].min()) /
    (df['Renewable Share (%)'].max() - df['Renewable Share (%)'].min())
)

df['Readiness Score'] = 0.5 * df['Norm_Budget'] + 0.5 * df['Norm_Share']
df = df.sort_values('Parsed Date')

# --- Month Selection ---
st.markdown("### 📅 Select Month to View Renewable Mix")
month_selected = st.selectbox("Choose a Month", df['Month'].unique()[::-1])
selected_row = df[df['Month'] == month_selected].iloc[0]

# --- Donut Chart ---
st.subheader(f"🔆 Renewable Energy Mix — {month_selected}")
fig_donut = go.Figure(data=[go.Pie(
    labels=["Solar", "Wind", "Hydro"],
    values=[
        selected_row['Solar power plants Installed capacity'],
        selected_row['Wind power plants Installed capacity'],
        selected_row['Hydro power plants Installed capacity']
    ],
    hole=0.5,
    marker=dict(colors=['#F7DC6F', '#58D68D', '#5DADE2']),
    hoverinfo='label+percent',
    textinfo='label+value'
)])
fig_donut.update_layout(height=400, margin=dict(t=10, b=10))
st.plotly_chart(fig_donut, use_container_width=True)

# --- Readiness Score Line Chart ---
st.subheader("📈 Readiness Score Over Time")
fig_line = px.line(df, x='Month', y='Readiness Score', markers=True)
fig_line.update_traces(line=dict(color="#2E86DE", width=3))
fig_line.update_layout(height=400)
st.plotly_chart(fig_line, use_container_width=True)

# --- Data Table ---
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