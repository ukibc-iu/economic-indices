import streamlit as st
import pandas as pd
import plotly.graph_objects as go

st.set_page_config(layout="wide")

# === Load Data ===
df = pd.read_csv("data/EV_Adoption.csv")
df.columns = df.columns.str.strip()

# === Parse Date ===
df['Date'] = pd.to_datetime(df['Date'], format='%m/%d/%Y', errors='coerce')
df = df.dropna(subset=['Date'])
df['Month'] = df['Date'].dt.strftime('%b-%Y')

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

# === UI Header ===
st.title("EV Market Adoption Rate Dashboard")
st.markdown("*The EV Market Adoption Rate represents the share of electric vehicles in total vehicle sales, indicating the extent of EV presence in the automotive market.*")

# === KPIs ===
latest_row = df.sort_values("Date").iloc[-1]
latest_month = latest_row["Month"]
latest_ev_rate = latest_row["EV Adoption Rate"]
latest_total_sales = int(latest_row["Total Vehicle Sales"])
latest_ev_sales = int(latest_row["EV Total Sales"])

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

# === Month Selection ===
selected_month = st.selectbox("Select Month", df['Month'].unique()[::-1])
selected_row = df[df['Month'] == selected_month].iloc[0]
selected_ev_rate = selected_row["EV Adoption Rate"]

# === Donut - Gauge - Donut Layout ===
donut_left, gauge_col, donut_right = st.columns([2, 2.5, 2])

# --- Left Donut Chart: EV Sales Breakdown by Segment ---
with donut_left:
    st.markdown("### 🔍 EV Sales by Segment")
    selected_segment_sales = selected_row[ev_cols]

    ev_segment_fig = go.Figure(data=[go.Pie(
        labels=["Four-wheeler", "Two-wheeler", "Three-wheeler"],
        values=selected_segment_sales,
        hole=0.5,
        marker=dict(colors=["#339933", "#CCCC00", "#a50f15"]),
        textinfo='none'
    )])

    ev_segment_fig.update_layout(
        title_text=f"EV Segment Split - {selected_month}",
        showlegend=True,
        height=350,
        legend=dict(orientation="h", y=-0.2)
    )

    st.plotly_chart(ev_segment_fig, use_container_width=True)

# --- Center Gauge Chart ---
with gauge_col:
    st.markdown("#### Display Format")
    display_format = st.radio(
        "",
        options=["Percentage", "Decimal"],
        horizontal=True,
        index=0,
        format_func=lambda x: "Percentage" if x == "Percentage" else "Decimal"
    )

    gauge_fig = go.Figure()
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
        title = f"EV Adoption Rate - {selected_month} (%)"
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
        title = f"EV Adoption Rate - {selected_month} (0–1)"

    gauge_fig.add_trace(go.Indicator(
        mode="gauge+number",
        value=gauge_value,
        title={'text': title},
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
    gauge_fig.update_layout(height=300)
    st.plotly_chart(gauge_fig, use_container_width=True)

# --- Right Donut Chart: Total Vehicle Category Sales ---
with donut_right:
    st.markdown("### 🚘 Total Vehicle Sales by Category")

    selected_total_sales = selected_row[vehicle_sales_cols]

    total_sales_fig = go.Figure(data=[go.Pie(
        labels=["Passenger", "Two-wheeler", "Three-wheeler", "Commercial"],
        values=selected_total_sales,
        hole=0.5,
        marker=dict(colors=["#339933", "#CCCC00", "#a50f15", "#888888"]),
        textinfo='none'
    )])

    total_sales_fig.update_layout(
        title_text=f"Vehicle Type Split - {selected_month}",
        showlegend=True,
        height=350,
        legend=dict(orientation="h", y=-0.2)
    )

    st.plotly_chart(total_sales_fig, use_container_width=True)

# === Line Chart ===
st.markdown("### 📈 EV Adoption Rate Over Time")
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
    margin=dict(l=30, r=30, t=40, b=30)
)
st.plotly_chart(line_fig, use_container_width=True)

# === Optional Raw Data ===
if st.checkbox("🧾 Show Raw Data"):
    st.dataframe(df[['Date', 'Month', 'EV Total Sales', 'Total Vehicle Sales', 'EV Adoption Rate']].sort_values("Date", ascending=False))