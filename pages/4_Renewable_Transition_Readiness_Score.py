import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import streamlit.components.v1 as components

st.set_page_config(layout="wide")

# === Load Data ===
df = pd.read_csv("data/Renewable_Energy.csv")
df.columns = df.columns.str.strip()

# === Parse Date ===
df['Date'] = pd.to_datetime(df['Date'], format='%m/%d/%Y', errors='coerce')
df = df.dropna(subset=['Date'])
df['Month'] = df['Date'].dt.strftime('%b-%Y')

# === Numeric Columns ===
df['Renewable Share'] = pd.to_numeric(df['Renewable Share'].astype(str).str.replace('%', ''), errors='coerce')
df['Installed RE Capacity'] = pd.to_numeric(df['Installed RE Capacity'].astype(str).str.replace(',', ''), errors='coerce')
df['Total Installed Capacity'] = pd.to_numeric(df['Total Installed Capacity'].astype(str).str.replace(',', ''), errors='coerce')
df['Grid RE Utilization'] = pd.to_numeric(df['Grid RE Utilization'].astype(str).str.replace('%', ''), errors='coerce')
df['Transition Score'] = pd.to_numeric(df['Transition Score'], errors='coerce')

# === Header ===
st.title("Renewable Transition Readiness Score")
st.markdown("*This score reflects the overall readiness and progress of the power sector toward renewable energy transition.*")

# === KPI Styles ===
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
.green-card { background: linear-gradient(#004d00, #009933, #33cc33); }
.grey-card { background: linear-gradient(#336699, #6699cc, #99ccff); }
.blue-card { background: linear-gradient(#003366, #336699, #6699cc); }
</style>
"""
st.markdown(kpi_style, unsafe_allow_html=True)

# === KPIs ===
latest_row = df.sort_values("Date").iloc[-1]
latest_month = latest_row["Month"]
score = latest_row["Transition Score"]
renewable_share = latest_row["Renewable Share"]
re_capacity = latest_row["Installed RE Capacity"]

d_col1, d_col2, d_col3 = st.columns(3)
with d_col1:
    st.markdown(f"""
    <div class="card green-card">
        <div style="font-size: 16px;">Transition Score</div>
        <div style="font-size: 28px;">{score:.2f}</div>
    </div>
    """, unsafe_allow_html=True)
with d_col2:
    st.markdown(f"""
    <div class="card grey-card">
        <div style="font-size: 16px;">Renewable Share</div>
        <div style="font-size: 28px;">{renewable_share:.1f}%</div>
    </div>
    """, unsafe_allow_html=True)
with d_col3:
    st.markdown(f"""
    <div class="card blue-card">
        <div style="font-size: 16px;">Installed RE Capacity</div>
        <div style="font-size: 24px;">{re_capacity:,.0f} MW</div>
    </div>
    """, unsafe_allow_html=True)

# === Select Month ===
selected_month = st.selectbox("Select Month", df['Month'].unique()[::-1])
selected_row = df[df['Month'] == selected_month].iloc[0]

# === Gauge Chart ===
gauge_fig = go.Figure(go.Indicator(
    mode="gauge+number",
    value=selected_row['Transition Score'],
    gauge={
        'axis': {'range': [0, 100]},
        'bar': {'color': "lightgreen"},
        'steps': [
            {'range': [0, 40], 'color': '#fcae91'},
            {'range': [40, 70], 'color': '#fb6a4a'},
            {'range': [70, 100], 'color': '#de2d26'}
        ],
        'threshold': {
            'line': {'color': "red", 'width': 4},
            'thickness': 0.75,
            'value': selected_row['Transition Score']
        }
    }
))
gauge_fig.update_layout(
    height=400,
    paper_bgcolor='rgba(0,0,0,0)',
    plot_bgcolor='rgba(0,0,0,0)',
    font_color='white'
)
st.plotly_chart(gauge_fig, use_container_width=True)

# === Line Chart ===
line_fig = go.Figure()
line_fig.add_trace(go.Scatter(
    x=df['Date'],
    y=df['Transition Score'],
    mode='lines+markers',
    name='Transition Score',
    line=dict(color='lightgreen'),
    hovertemplate="Date: %{x|%b %Y}<br>Score: %{y:.2f}<extra></extra>"
))
line_fig.update_layout(
    xaxis_title="Date",
    yaxis_title="Transition Score",
    height=400,
    plot_bgcolor='rgba(0,0,0,0)',
    paper_bgcolor='rgba(0,0,0,0)',
    font_color='white'
)
st.plotly_chart(line_fig, use_container_width=True)

# === Raw Data ===
if st.checkbox("\U0001F9FE Show Raw Data"):
    st.dataframe(df.sort_values("Date", ascending=False))