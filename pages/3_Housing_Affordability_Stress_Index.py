import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go

st.set_page_config(page_title="Housing Affordability Index", layout="wide")
st.title("🏡 Housing Affordability Index Dashboard")
st.markdown("*The Housing Affordability Index reflects how affordable residential property is for an average individual, using per capita income and property prices.*")

# --- Load Data ---
@st.cache_data
def load_data():
    df = pd.read_csv("data/Housing_Affordability.csv")
    df.columns = df.columns.str.strip()

    df['Date'] = pd.to_datetime(df['Date'], errors='coerce')
    df.dropna(subset=['Date'], inplace=True)

    df['Month'] = df['Date'].dt.strftime('%b-%y')

    def format_quarter(row):
        q = f"Q{((row['Date'].month - 1) // 3 + 1)}"
        fy = row['Date'].year if row['Date'].month >= 4 else row['Date'].year - 1
        return f"{q} {fy}-{str(fy + 1)[-2:]}"
    df['QuarterFormatted'] = df.apply(format_quarter, axis=1)

    df['Property Price Index'] = pd.to_numeric(df['Property Price Index'], errors='coerce')
    df['Per Capita NNI'] = pd.to_numeric(df['Per Capita NNI'], errors='coerce')

    LOAN_FACTOR = 0.003
    df['Affordability Index'] = (df['Per Capita NNI'] / df['Property Price Index']) * LOAN_FACTOR

    df.dropna(inplace=True)
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
latest_index = latest_row['Affordability Index']
latest_price = latest_row['Property Price Index']

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
.green-card { background: linear-gradient(#004466, #006699, #3399cc); }
.grey-card { background: linear-gradient(#336699, #6699cc, #99ccff); }
.red-card { background: linear-gradient(#cccccc, #999999, #666666); }
</style>
"""
st.markdown(kpi_style, unsafe_allow_html=True)

col1, col2, col3 = st.columns(3)

with col1:
    st.markdown(f"""
        <div class="card green-card">
            <div style="font-size: 1.2rem;">🗓 Latest Period</div>
            <div style="font-size: 2rem;">{latest_month} / {latest_quarter}</div>
        </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown(f"""
        <div class="card grey-card">
            <div style="font-size: 1.2rem;">📊 Affordability Index</div>
            <div style="font-size: 2rem;">{latest_index:.2f}</div>
        </div>
    """, unsafe_allow_html=True)

with col3:
    st.markdown(f"""
        <div class="card red-card">
            <div style="font-size: 1.2rem;">📈 Property Price Index</div>
            <div style="font-size: 2rem;">{latest_price:.2f}</div>
        </div>
    """, unsafe_allow_html=True)

# --- Preview Type ---
preview_type = st.selectbox("🗓 Preview Type", ["Monthly", "Quarterly"])
period_list = df['Month'].unique().tolist() if preview_type == "Monthly" else df['QuarterFormatted'].unique().tolist()
selected_period = st.selectbox("📆 Select Month or Quarter", period_list)

filtered = df[df['Month'] == selected_period] if preview_type == "Monthly" else df[df['QuarterFormatted'] == selected_period]
if filtered.empty:
    st.warning("⚠️ No data found for selected period.")
    st.stop()

# --- Custom Gauge with Needle ---
score_val = filtered['Affordability Index'].values[0]

def create_gauge_with_needle(value):
    scaled_val = value * 100  # Convert from 0–1 to percentage
    degrees = 180 - (scaled_val * 1.8)  # Map 0–100% to 180° arc
    radians = np.deg2rad(degrees)
    radius = 0.4
    x = 0.5 + radius * np.cos(radians)
    y = 0.5 + radius * np.sin(radians)

    needle = {
        'type': 'line',
        'x0': 0.5, 'y0': 0.5,
        'x1': x,   'y1': y,
        'line': {'color': 'black', 'width': 4}
    }

    fig = go.Figure()

    fig.add_trace(go.Pie(
        values=[20, 10, 10, 20, 40, 100],
        labels=["Very Low", "Low", "Moderate", "Good", "Excellent", ""],
        marker_colors=["#ff0000", "#ffa500", "#ffff00", "#90ee90", "#008000", "white"],
        hole=0.5,
        direction='clockwise',
        rotation=180,
        textinfo='label',
        showlegend=False
    ))

    fig.update_layout(
        shapes=[needle],
        annotations=[
            dict(
                x=0.5, y=0.5,
                text=f"<b>{value:.2%}</b>",  # Percent format
                showarrow=False,
                font=dict(size=22, color="white")
            )
        ],
        margin=dict(l=0, r=0, t=0, b=0),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        height=400
    )
    return fig

st.subheader("🧭 Affordability Gauge")
gauge_fig = create_gauge_with_needle(score_val)
st.plotly_chart(gauge_fig, use_container_width=True)

# --- Line Chart ---
st.subheader("📈 Affordability Index Over Time")
fig_line = px.line(df, x='Month', y='Affordability Index', markers=True,
                   line_shape='linear', color_discrete_sequence=['#FF5733'])
fig_line.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
                       font_color='white', height=450)
st.plotly_chart(fig_line, use_container_width=True)

# --- Data Table ---
with st.expander("🔍 View Underlying Data Table"):
    st.dataframe(df[['Month', 'QuarterFormatted', 'Affordability Index', 'Property Price Index', 'Per Capita NNI']])