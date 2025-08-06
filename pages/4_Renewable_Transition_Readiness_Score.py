import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit.components.v1 as components

st.set_page_config(page_title="Renewable Readiness Score", layout="wide")
st.title("Renewable Transition Readiness Score")
st.markdown("*The Renewable Transition Readiness Score is a composite index measuring how prepared India is for clean energy adoption, based on MNRE investment and the share of renewables in total power consumption.*")

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
        'Budgetary allocation for MNRE sector',
        'Power Consumption'
    ]
    for col in expected_cols:
        if col not in df.columns:
            st.error(f"❌ Missing column: `{col}`")
            return None

    df['Date'] = pd.to_datetime(df['Date'], format='%m/%d/%Y', errors='coerce')
    df.dropna(subset=['Date'], inplace=True)

    df['Month'] = df['Date'].dt.strftime('%b-%y')

    def format_quarter(row):
        q = f"Q{((row['Date'].month - 1) // 3 + 1)}"
        fy = row['Date'].year if row['Date'].month >= 4 else row['Date'].year - 1
        return f"{q} {fy}-{str(fy + 1)[-2:]}"
    df['QuarterFormatted'] = df.apply(format_quarter, axis=1)

    for col in expected_cols[1:]:
        df[col] = pd.to_numeric(df[col], errors='coerce')
    df.dropna(inplace=True)

    # --- Calculate Actual Renewable Generation using Capacity Factors ---
    HOURS_PER_MONTH = 720
    CF_SOLAR = 0.2
    CF_WIND = 0.3
    CF_HYDRO = 0.4

    df['Solar Generation (GWh)'] = df['Solar power plants Installed capacity'] * CF_SOLAR * HOURS_PER_MONTH / 1000
    df['Wind Generation (GWh)'] = df['Wind power plants Installed capacity'] * CF_WIND * HOURS_PER_MONTH / 1000
    df['Hydro Generation (GWh)'] = df['Hydro power plants Installed capacity'] * CF_HYDRO * HOURS_PER_MONTH / 1000

    df['Total Renewable Generation (GWh)'] = (
        df['Solar Generation (GWh)'] +
        df['Wind Generation (GWh)'] +
        df['Hydro Generation (GWh)']
    )

    df['Power Consumption (GWh)'] = df['Power Consumption'] * 1000

    df['Renewable Share (%)'] = (df['Total Renewable Generation (GWh)'] / df['Power Consumption (GWh)']) * 100

    df['Norm_Budget'] = (df['Budgetary allocation for MNRE sector'] - df['Budgetary allocation for MNRE sector'].min()) / (
        df['Budgetary allocation for MNRE sector'].max() - df['Budgetary allocation for MNRE sector'].min()
    )
    df['Norm_Share'] = (df['Renewable Share (%)'] - df['Renewable Share (%)'].min()) / (
        df['Renewable Share (%)'].max() - df['Renewable Share (%)'].min()
    )
    df['Readiness Score'] = 0.5 * df['Norm_Budget'] + 0.5 * df['Norm_Share']

    df = df.sort_values('Date')
    return df

df = load_data()
if df is None or df.empty:
    st.warning("⚠️ No valid data available. Please check your CSV.")
    st.stop()

# --- Latest KPIs ---
latest_row = df.iloc[-1]
latest_month = latest_row['Month']
latest_quarter = latest_row['QuarterFormatted']
latest_score = latest_row['Readiness Score']
latest_consumption = latest_row['Power Consumption']

# --- KPI Cards with HTML ---
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
.green-card { background: linear-gradient(#024643, #035955, #047E78); }
.grey-card { background: linear-gradient(#059F98, #06BAB1, #08EEE3); }
.red-card { background: linear-gradient(#08EEE3, #66D7FA, #9AE5FC); }
</style>
"""
st.markdown(kpi_style, unsafe_allow_html=True)

col1, col2, col3 = st.columns(3)

with col1:
    st.markdown(f"""
        <div class="card green-card">
            <div style="font-size: 1.2rem;">Latest Period</div>
            <div style="font-size: 2rem;">{latest_month} / {latest_quarter}</div>
        </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown(f"""
        <div class="card grey-card">
            <div style="font-size: 1.2rem;">Readiness Score</div>
            <div style="font-size: 2rem;">{latest_score:.2f}</div>
        </div>
    """, unsafe_allow_html=True)

with col3:
    st.markdown(f"""
        <div class="card red-card">
            <div style="font-size: 1.2rem;">Total Power Consumption</div>
            <div style="font-size: 2rem;">{latest_consumption:,.0f} BU</div>
        </div>
    """, unsafe_allow_html=True)

# --- Preview Type ---
preview_type = st.selectbox("Preview Type", ["Monthly", "Quarterly"])
if preview_type == "Monthly":
    period_list = df['Month'].unique().tolist()
else:
    period_list = df['QuarterFormatted'].unique().tolist()

# Set default to latest available period
default_period = latest_month if preview_type == "Monthly" else latest_quarter
selected_period = st.selectbox("Select Month or Quarter", period_list, index=period_list.index(default_period))

# --- Filtered Data ---
if preview_type == "Monthly":
    filtered = df[df['Month'] == selected_period]
else:
    filtered = df[df['QuarterFormatted'] == selected_period]

if filtered.empty:
    st.warning("⚠️ No data found for selected period.")
    st.stop()

# === CHART WRAPPER ===
def wrapped_chart(title, figure):
    with st.container(border=True):
        st.markdown(f"**{title}**")
        st.plotly_chart(figure, use_container_width=True)

# === Donut - Gauge ===
left_col, right_col = st.columns(2)

with left_col:
    donut_data = {
        "Source": ["Solar", "Wind", "Hydro"],
        "Capacity": [
            filtered['Solar power plants Installed capacity'].values[0],
            filtered['Wind power plants Installed capacity'].values[0],
            filtered['Hydro power plants Installed capacity'].values[0]
        ]
    }
    bright_colors = ['#FFD700', '#00BFFF', '#32CD32']
    fig_donut = px.pie(donut_data, values='Capacity', names='Source', hole=0.5,
                       color_discrete_sequence=bright_colors)
    fig_donut.update_traces(textposition='inside', textinfo='percent+label')
    fig_donut.update_layout(height=400,
                            paper_bgcolor='rgba(0,0,0,0)',
                            plot_bgcolor='rgba(0,0,0,0)')
    wrapped_chart(f"Renewable Energy Mix – {selected_period}", fig_donut)

with right_col:
    score_val = filtered['Readiness Score'].values[0]
    fig_gauge = go.Figure(go.Indicator(
        mode="gauge+number",
        value=score_val,
        domain={'x': [0, 1], 'y': [0, 1]},
        gauge={
            'axis': {'range': [0, 1], 'tickcolor': 'white'},
            'bar': {'color': "black"},
            'steps': [
                {'range': [0, 0.2], 'color': "#66D7FA"},
                {'range': [0.2, 0.4], 'color': "#08EEE3"},
                {'range': [0.4, 0.6], 'color': "#059F98"},
                {'range': [0.6, 0.8], 'color': "#047E78"},
                {'range': [0.8, 1.0], 'color': "#024643"},
            ]
        }
    ))
    fig_gauge.update_layout(height=400,
                            paper_bgcolor='rgba(0,0,0,0)',
                            plot_bgcolor='rgba(0,0,0,0)')
    wrapped_chart(f"Readiness Score – {selected_period}", fig_gauge)
st.markdown("### 💡 Expert Opinion")

# Expert opinion (static for now)
expert_opinion = "Renewable Transition Readiness Score is currently..."

# Styled display box
st.markdown(f"""
<div style="
    background-color: rgba(100, 100, 100, 0.3);
    padding: 1rem;
    border-radius: 10px;
    border: 1px solid rgba(255, 255, 255, 0.2);
    color: white;
    font-style: italic;
    font-size: 1rem;
">
    {expert_opinion}
</div>
""", unsafe_allow_html=True)

# === Line Chart ===
st.subheader("Readiness Score Over Time")
fig_score = px.line(df, x='Month', y='Readiness Score', markers=False,
                    line_shape='linear',
                    color_discrete_sequence=['#047E78'])
fig_score.update_layout(
    paper_bgcolor='rgba(0,0,0,0)',
    plot_bgcolor='rgba(0,0,0,0)',
    font_color='white',
    height=450
)
st.plotly_chart(fig_score, use_container_width=True)

# === Data Table ===
with st.expander("🔍 View Underlying Data Table"):
    st.dataframe(df[[
        'Month', 'QuarterFormatted', 'Renewable Share (%)',
        'Readiness Score', 'Solar power plants Installed capacity',
        'Wind power plants Installed capacity', 'Hydro power plants Installed capacity',
        'Power Consumption', 'Budgetary allocation for MNRE sector'
    ]])