import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import streamlit.components.v1 as components

st.set_page_config(layout="wide")

# === Load Data ===
df = pd.read_csv("data/EV_Adoption.csv")
df.columns = df.columns.str.strip()

# === Parse Date ===
df['Date'] = pd.to_datetime(df['Date'], format='%m/%d/%Y', errors='coerce')
df = df.dropna(subset=['Date'])
df['Month'] = df['Date'].dt.strftime('%b-%y')

# === Clean & Convert Numeric Columns ===
ev_cols = ['EV Four-wheeler Sales', 'EV Two-wheeler Sales', 'EV Three-wheeler Sales']
for col in ev_cols:
    df[col] = pd.to_numeric(df[col].astype(str).str.replace(',', ''), errors='coerce')

vehicle_sales_cols = ["Passenger Vehicle Sales", "Two-wheeler Sales", "Three-wheeler Sales", "Commercial Vehicle Sales"]
for col in vehicle_sales_cols:
    df[col] = pd.to_numeric(df[col].astype(str).str.replace(',', ''), errors='coerce')

df['Total Vehicle Sales'] = pd.to_numeric(df['Total Vehicle Sales'].astype(str).str.replace(',', ''), errors='coerce')
df['Auto Loan Rate'] = df['Auto Loan Rate'].astype(str).str.replace('%', '').astype(float)

# === Add Calculated Columns ===
df['EV Total Sales'] = df['EV Four-wheeler Sales'] + df['EV Two-wheeler Sales'] + df['EV Three-wheeler Sales']
df['EV Adoption Rate'] = df['EV Total Sales'] / df['Total Vehicle Sales']

# === Header ===
st.title("EV Market Adoption Rate")
st.markdown("*The EV Market Adoption Rate represents the share of electric vehicles in total vehicle sales, indicating the extent of EV presence in the automotive market.*")

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
.green-card { background: linear-gradient(#003300, #006600, #339933); }
.grey-card { background: linear-gradient(#009900, #669900, #99CC00); }
.red-card { background: linear-gradient(#CCCC00, #CC9900, #996600); }
</style>
"""
st.markdown(kpi_style, unsafe_allow_html=True)

# === KPIs ===
latest_row = df.sort_values("Date").iloc[-1]
latest_month = latest_row["Month"]
latest_ev_rate = latest_row["EV Adoption Rate"]
latest_total_sales = int(latest_row["Total Vehicle Sales"])
latest_ev_sales = int(latest_row["EV Total Sales"])

col1, col2, col3 = st.columns(3)
with col1:
    st.markdown(f"""
    <div class="card green-card">
        <div style="font-size: 16px;">EV Adoption Rate</div>
        <div style="font-size: 28px;">{latest_ev_rate*100:.2f}%</div>
    </div>
    """, unsafe_allow_html=True)
with col2:
    st.markdown(f"""
    <div class="card grey-card">
        <div style="font-size: 16px;">Latest Month</div>
        <div style="font-size: 28px;">{latest_month}</div>
    </div>
    """, unsafe_allow_html=True)
with col3:
    st.markdown(f"""
    <div class="card red-card">
        <div style="font-size: 16px;">EV Units Sold</div>
        <div style="font-size: 24px;">{latest_ev_sales:,}</div>
    </div>
    """, unsafe_allow_html=True)

# === Controls ===
sel_col1, sel_col2 = st.columns([3, 1.5])
with sel_col1:
    selected_month = st.selectbox("Select Month", df['Month'].unique()[::-1])
    selected_row = df[df['Month'] == selected_month].iloc[0]
    selected_ev_rate = selected_row["EV Adoption Rate"]
with sel_col2:
    display_format = st.selectbox("Display Format", ["Percentage", "Decimal"])

selected_segment_sales = selected_row[ev_cols]
selected_total_sales = selected_row[vehicle_sales_cols]

# === CHART WRAPPER ===
def wrapped_chart(title, fig, height=420):  # Keep consistent height
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

# === Donut - Gauge - Donut Charts ===
donut_left, gauge_col, donut_right = st.columns([2, 2.5, 2])

with donut_left:
    ev_segment_fig = go.Figure(data=[go.Pie(
        labels=["Four-wheeler", "Two-wheeler", "Three-wheeler"],
        values=selected_segment_sales,
        hole=0.5,
        marker=dict(colors=["#CCFF99", "#99FF33", "#66CC00"]),
        textinfo='percent',
        hoverinfo='label+value+percent',
        domain=dict(x=[0, 1], y=[0.2, 1.0])
    )])
    ev_segment_fig.update_layout(
        showlegend=True,
        height=400,
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font=dict(color='white'),
        margin=dict(t=20, b=20),
        legend=dict(orientation="h", y=-0.2, x=0.5, xanchor="center")
    )
    wrapped_chart(f"EV Sales by Segment - {selected_month}", ev_segment_fig)

with gauge_col:
    if display_format == "Percentage":
        gauge_value = selected_ev_rate * 100
        gauge_range = [0, 100]
        steps = [
            {'range': [0, 5], 'color': '#fee5d9'},
            {'range': [5, 10], 'color': '#fcae91'},
            {'range': [10, 20], 'color': '#fb6a4a'},
            {'range': [20, 40], 'color': '#de2d26'},
            {'range': [40, 100], 'color': '#a50f15'}
        ]
    else:
        gauge_value = selected_ev_rate
        gauge_range = [0, 1]
        steps = [
            {'range': [0.00, 0.05], 'color': '#fee5d9'},
            {'range': [0.05, 0.10], 'color': '#fcae91'},
            {'range': [0.10, 0.20], 'color': '#fb6a4a'},
            {'range': [0.20, 0.40], 'color': '#de2d26'},
            {'range': [0.40, 1.00], 'color': '#a50f15'}
        ]

    gauge_fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=gauge_value,
        gauge={
            'axis': {'range': gauge_range, 'tickwidth': 1, 'tickcolor': "darkblue"},
            'bar': {'color': "green"},
            'steps': steps,
            'threshold': {
                'line': {'color': "red", 'width': 4},
                'thickness': 0.75,
                'value': gauge_value
            }
        }
    ))
    gauge_fig.update_layout(
        height=400,
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font_color='white'
    )
    wrapped_chart(f"EV Adoption Rate - {selected_month}", gauge_fig)

with donut_right:
    total_sales_fig = go.Figure(data=[go.Pie(
        labels=["Passenger", "Two-wheeler", "Three-wheeler", "Commercial"],
        values=selected_total_sales,
        hole=0.5,
        marker=dict(colors=["#8B0000", "#E94E1B", "#FF8C42", "#FFD580"]),
        textinfo='percent',
        hoverinfo='label+value+percent',
        domain=dict(x=[0, 1], y=[0.2, 1.0])
    )])
    total_sales_fig.update_layout(
        showlegend=True,
        height=400,
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font=dict(color='white'),
        margin=dict(t=20, b=20),
        legend=dict(orientation="h", y=-0.2, x=0.5, xanchor="center")
    )
    wrapped_chart(f"Total Vehicle Sales by Category - {selected_month}", total_sales_fig)

# === Line Chart ===
if display_format == "Percentage":
    y_data = df["EV Adoption Rate"] * 100
    y_title = "EV Adoption Rate (%)"
    hover_format = "%{y:.2f}%"
else:
    y_data = df["EV Adoption Rate"]
    y_title = "EV Adoption Rate (0–1)"
    hover_format = "%{y:.3f}"

line_fig = go.Figure()
line_fig.add_trace(go.Scatter(
    x=df["Date"],
    y=y_data,
    mode="lines+markers",
    line=dict(color="green"),
    name="EV Adoption Rate",
    hovertemplate="Date: %{x|%b %Y}<br>Rate: " + hover_format + "<extra></extra>"
))
line_fig.update_layout(
    xaxis_title="Date",
    yaxis_title=y_title,
    height=400,
    margin=dict(l=50, r=30, t=40, b=30),
    plot_bgcolor='rgba(0,0,0,0)',
    paper_bgcolor='rgba(0,0,0,0)',
    font_color='white',
    xaxis=dict(showgrid=False),
    yaxis=dict(showgrid=False)
)
wrapped_chart("EV Adoption Rate Over Time", line_fig)

# === Raw Data Toggle ===
if st.checkbox("\U0001F9FE Show Raw Data"):
    st.dataframe(df[['Date', 'Month', 'EV Total Sales', 'Total Vehicle Sales', 'EV Adoption Rate']].sort_values("Date", ascending=False))