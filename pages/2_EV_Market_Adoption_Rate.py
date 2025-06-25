import streamlit as st
import pandas as pd
import plotly.graph_objects as go

st.set_page_config(layout="wide")

# === Load Data ===
df = pd.read_csv("data/EV_Adoption.csv")
df.columns = df.columns.str.strip()  # Clean column names

# === Parse Date ===
df['Date'] = pd.to_datetime(df['Date'], format='%m/%d/%Y', errors='coerce')
df = df.dropna(subset=['Date'])
df['Month'] = df['Date'].dt.strftime('%b-%Y')

# === Clean & Convert Numeric Columns ===
ev_cols = ['EV Four-wheeler Sales', 'EV Two-wheeler Sales', 'EV Three-wheeler Sales']
for col in ev_cols:
    df[col] = pd.to_numeric(df[col].astype(str).str.replace(',', ''), errors='coerce')

df['Total Vehicle Sales'] = pd.to_numeric(df['Total Vehicle Sales'].astype(str).str.replace(',', ''), errors='coerce')
df['Auto Loan Rate'] = df['Auto Loan Rate'].astype(str).str.replace('%', '').astype(float)

# === Add Calculated Columns ===
df['EV Total Sales'] = df['EV Four-wheeler Sales'] + df['EV Two-wheeler Sales'] + df['EV Three-wheeler Sales']
df['EV Adoption Rate'] = df['EV Total Sales'] / df['Total Vehicle Sales']

# === UI Header ===
st.title("EV Market Adoption Rate Dashboard")
st.markdown("📊 **Tracking the growth of Electric Vehicle (EV) adoption across India.**")

# === KPIs ===
latest_row = df.sort_values("Date").iloc[-1]
latest_month = latest_row["Month"]
latest_ev_rate = latest_row["EV Adoption Rate"]
latest_total_sales = int(latest_row["Total Vehicle Sales"])
latest_ev_sales = int(latest_row["EV Total Sales"])

col1, col2, col3 = st.columns(3)

col1.metric("🚗 EV Adoption Rate", f"{latest_ev_rate*100:.2f}%")
col2.metric("📆 Latest Month", latest_month)
col3.metric("🔢 EV Units Sold", f"{latest_ev_sales:,} / {latest_total_sales:,}")

# === Month Selection ===
selected_month = st.selectbox("Select Month", df['Month'].unique()[::-1])
selected_row = df[df['Month'] == selected_month].iloc[0]
selected_ev_rate = selected_row["EV Adoption Rate"]

# === Gauge + Format Toggle in One Row ===
left_col, right_col = st.columns([4, 1])  # Gauge takes more space

with right_col:
    st.markdown("#### Display Format")
    display_format = st.radio(
        "",
        options=["Percentage", "Decimal"],
        horizontal=True,
        index=0,
        format_func=lambda x: "Percentage" if x == "Percentage" else "Decimal"
    )

# === Gauge Chart ===
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

left_col.plotly_chart(gauge_fig, use_container_width=True)

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

# === Optional Raw Data Table ===
if st.checkbox("🧾 Show Raw Data"):
    st.dataframe(df[['Date', 'Month', 'EV Total Sales', 'Total Vehicle Sales', 'EV Adoption Rate']].sort_values("Date", ascending=False))