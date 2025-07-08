import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit.components.v1 as components

st.set_page_config(page_title="Renewable Readiness Score", layout="wide")
st.title("🌿 Renewable Transition Readiness Score")

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

df = load_data()
if df is None or df.empty:
    st.warning("⚠️ No valid data available. Please check your CSV.")
    st.stop()

# --- KPI Cards ---
latest_row = df.iloc[-1]
latest_month = latest_row['Month']
latest_quarter = latest_row['QuarterFormatted']
latest_score = latest_row['Readiness Score']
latest_consumption = latest_row['Power Consumption']

k1, k2, k3 = st.columns(3)
k1.metric("🗓 Latest Period", f"{latest_month} / {latest_quarter}")
k2.metric("📊 Readiness Score", f"{latest_score:.2f}")
k3.metric("⚡ Total Power Consumption", f"{latest_consumption:,.0f} units")

# --- Preview Type ---
preview_type = st.selectbox("📅 Preview Type", ["Monthly", "Quarterly"])
if preview_type == "Monthly":
    period_list = df['Month'].unique().tolist()
else:
    period_list = df['QuarterFormatted'].unique().tolist()

selected_period = st.selectbox("📆 Select Month or Quarter", period_list)

# --- Filtered Data ---
if preview_type == "Monthly":
    filtered = df[df['Month'] == selected_period]
else:
    filtered = df[df['QuarterFormatted'] == selected_period]

if filtered.empty:
    st.warning("⚠️ No data found for selected period.")
    st.stop()

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
                            plot_bgcolor='rgba(0,0,0,0)',
                            font_color='white')
    wrapped_chart(f"Renewable Energy Mix – {selected_period}", fig_donut)

with right_col:
    score_val = filtered['Readiness Score'].values[0]
    fig_gauge = go.Figure(go.Indicator(
        mode="gauge+number",
        value=score_val,
        number={'font': {'color': 'white'}},
        domain={'x': [0, 1], 'y': [0, 1]},
        title={'text': "Readiness Score", 'font': {'color': 'white'}},
        gauge={
            'axis': {'range': [0, 1], 'tickcolor': 'white'},
            'bar': {'color': "white"},
            'steps': [
                {'range': [0, 0.2], 'color': "#ff0000"},
                {'range': [0.2, 0.4], 'color': "#ffa500"},
                {'range': [0.4, 0.6], 'color': "#ffff00"},
                {'range': [0.6, 0.8], 'color': "#90ee90"},
                {'range': [0.8, 1.0], 'color': "#008000"},
            ]
        }
    ))
    fig_gauge.update_layout(height=400,
                            paper_bgcolor='rgba(0,0,0,0)',
                            plot_bgcolor='rgba(0,0,0,0)',
                            font_color='white')
    wrapped_chart(f"Readiness Score – {selected_period}", fig_gauge)

# === Line Chart ===
st.subheader("📈 Readiness Score Over Time")
fig_score = px.line(df, x='Month', y='Readiness Score', markers=True,
                    line_shape='linear',
                    color_discrete_sequence=['#FF5733'])
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
        'Power Consumption', 'Budgetary allocation for infrastructure sector'
    ]])