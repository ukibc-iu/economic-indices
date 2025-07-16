import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import os
import json

st.set_page_config(layout="wide")

# === KPI Styling ===
st.markdown("""
<style>
.kpi-container {
    display: flex;
    gap: 1rem;
    flex-wrap: wrap;
    margin-bottom: 1rem;
}
.kpi-card {
    flex: 1;
    padding: 1rem;
    border-radius: 16px;
    background: rgba(255, 255, 255, 0.08);
    backdrop-filter: blur(12px);
    -webkit-backdrop-filter: blur(12px);
    color: white;
    min-width: 200px;
    border: 1px solid rgba(255, 255, 255, 0.15);
    box-shadow: 0 4px 20px rgba(0, 0, 0, 0.3);
}
.kpi-title {
    font-size: 1rem;
    font-weight: 600;
    margin-bottom: 0.3rem;
    color: #ddd;
}
.kpi-value {
    font-size: 1.8rem;
    font-weight: bold;
}
.bg-1 { background: linear-gradient(#1C2740, #2E416C, #6D87C1); }
.bg-2 { background: linear-gradient(135deg, #0f2027, #203a43, #2c5364); }
.bg-3 { background: linear-gradient(135deg, #134E5E, #71B280); }
</style>
""", unsafe_allow_html=True)

st.title("IMP Index Dashboard")
st.markdown("*India’s Macroeconomic Performance (IMP) Index measures India's overall economic well‑being based on multiple macro indicators.*")

# === Load Data ===
data_path = "data/IMP_Index.csv"
df = pd.read_csv(data_path)
df.columns = df.columns.str.strip()
df['Date'] = pd.to_datetime(df['Date'], format='%b-%y', errors='coerce')
df = df.dropna(subset=['Date'])
df['Month'] = df['Date'].dt.strftime('%b-%Y')

def get_fiscal_quarter(date):
    m, y = date.month, date.year
    if m in [4, 5, 6]: q, fy = 'Q1', y
    elif m in [7, 8, 9]: q, fy = 'Q2', y
    elif m in [10, 11, 12]: q, fy = 'Q3', y
    else: q, fy = 'Q4', y - 1
    return f"{q} {fy}-{str(fy+1)[-2:]}"

df['Fiscal_Quarter'] = df['Date'].apply(get_fiscal_quarter)

# === Mode Selection ===
mode = st.radio("Select View Mode", ["Monthly", "Quarterly"], horizontal=True)

# === Prepare Data for KPIs and Dropdown ===
if mode == "Monthly":
    latest_row = df.sort_values("Date").iloc[-1]
    latest_value = latest_row["Scale"]
    latest_label = latest_row["Month"]
    all_labels = sorted(df['Month'].unique())
else:
    latest_q = df.sort_values("Date")["Fiscal_Quarter"].iloc[-1]
    latest_value = df[df["Fiscal_Quarter"] == latest_q]["Scale"].mean()
    latest_label = latest_q
    all_labels = sorted(df["Fiscal_Quarter"].unique())

# === KPI Cards ===
st.markdown(f"""
<div class="kpi-container">
  <div class="kpi-card bg-1">
    <div class="kpi-title">IMP Index Value</div>
    <div class="kpi-value">{latest_value:.2f}</div>
  </div>
  <div class="kpi-card bg-2">
    <div class="kpi-title">Latest Period</div>
    <div class="kpi-value">{latest_label}</div>
  </div>
  <div class="kpi-card bg-3">
    <div class="kpi-title">View Mode</div>
    <div class="kpi-value">{mode}</div>
  </div>
</div>
""", unsafe_allow_html=True)

# === Dropdown Selector Below KPIs ===
selected_label = st.selectbox(f"Select {mode}", options=all_labels, index=all_labels.index(latest_label))

# === Selected Value & Label ===
if mode == "Monthly":
    selected_value = df[df['Month'] == selected_label]['Scale'].values[0]
    label_period = selected_label
else:
    selected_value = df[df['Fiscal_Quarter'] == selected_label]['Scale'].mean()
    label_period = selected_label

# === Chart Wrapper ===
def chart_wrapper(fig, title=None):
    if title:
        st.markdown(f"#### {title}")
    st.plotly_chart(fig, use_container_width=True)

# === Gauge Chart ===
gauge_fig = go.Figure(go.Indicator(
    mode="gauge+number",
    value=selected_value,
    title={'text': f"IMP Index for {label_period}", 'font': {'size': 20}},
    gauge={
        'axis': {'range': [-3, 3], 'tickwidth': 1, 'tickcolor': "white"},
        'bar': {'color': "white"},
        'steps': [
            {'range': [-3, -2], 'color': '#0B1D51'},
            {'range': [-2, -1], 'color': '#2C3E70'},
            {'range': [-1,  0], 'color': '#6C8EBF'},
            {'range': [ 0,  1], 'color': '#AED9E0'},
            {'range': [ 1,  2], 'color': '#3095B1'},
            {'range': [ 2,  3], 'color': '#005377'},
        ],
        'threshold': {
            'line': {'color': "crimson", 'width': 4},
            'thickness': 0.75,
            'value': selected_value
        }
    }
))
gauge_fig.update_layout(
    margin=dict(l=40, r=40, t=40, b=40),
    paper_bgcolor="rgba(0,0,0,0)",
    font=dict(color="white", family="Arial")
)
chart_wrapper(gauge_fig)

# === Expert Opinion ===
st.markdown("### 💡 Expert Opinion")
expert_opinion = "IMP Index is currently neutral."
st.markdown(f"""
<div style="
    background-color: rgba(100, 100, 100, 0.3);
    padding: 1rem;
    border-radius: 10px;
    border: 1px solid rgba(255, 255, 255, 0.2);
    color: white;
    font-style: italic;
    font-size: 1rem;">
    {expert_opinion}
</div>
""", unsafe_allow_html=True)

# === Contribution Breakdown ===
st.markdown("### Contribution Breakdown")
contrib_weights = {
    "Real GDP": 40,
    "Balance of Trade": 20,
    "Inflation": 20,
    "Fiscal Balance": 10,
    "Unemployment": 10
}
contrib_df = pd.DataFrame({
    "Factor": contrib_weights.keys(),
    "Weight": contrib_weights.values()
}).sort_values("Weight", ascending=False)

color_map = {40: "#003366", 20: "#3399cc", 10: "#99ccff"}
bar_colors = contrib_df["Weight"].map(color_map)

bar_fig = go.Figure(go.Bar(
    y=contrib_df["Factor"],
    x=contrib_df["Weight"],
    orientation="h",
    marker=dict(color=bar_colors, line=dict(color="black", width=1)),
    text=[f"{w}%" for w in contrib_df["Weight"]],
    textposition="auto"
))
bar_fig.update_layout(
    height=400,
    xaxis_title="Weight (%)",
    yaxis=dict(categoryorder="total ascending"),
    margin=dict(l=30, r=30, t=40, b=30)
)
chart_wrapper(bar_fig, title="Factor Contributions to IMP Index")

# === Line Chart ===
st.markdown("### IMP Index Trend Over Time")
if mode == "Monthly":
    time_series = df.sort_values("Date")[["Date", "Scale"]]
    x_vals = time_series["Date"]
else:
    quarter_df = df.groupby("Fiscal_Quarter")["Scale"].mean().reset_index()
    q_info = quarter_df["Fiscal_Quarter"].str.extract(r'Q(?P<q>\d) (?P<year>\d{4})')
    q_info = q_info.astype(int)
    start_dates = []
    for _, row in q_info.iterrows():
        q, y = row["q"], row["year"]
        if q == 4:
            start_dates.append(pd.Timestamp(y + 1, 1, 1))
        else:
            start_dates.append(pd.Timestamp(y, 3 * (q - 1) + 4, 1))
    quarter_df["Quarter_Start"] = start_dates
    time_series = quarter_df.sort_values("Quarter_Start")[["Quarter_Start", "Scale"]]
    x_vals = time_series["Quarter_Start"]

line_fig = go.Figure(go.Scatter(
    x=x_vals,
    y=time_series["Scale"],
    mode="lines+markers",
    line=dict(color="#3f51b5", width=3),
    marker=dict(size=6),
    hovertemplate="Date: %{x}<br>IMP Index: %{y:.2f}<extra></extra>",
    showlegend=False
))
line_fig.update_layout(
    height=400,
    xaxis_title="Date",
    yaxis_title="IMP Index Value",
    margin=dict(l=30, r=30, t=50, b=30),
    xaxis=dict(showgrid=False, zeroline=False),
    yaxis=dict(showgrid=True, zeroline=False),
    plot_bgcolor='rgba(0,0,0,0)',
    paper_bgcolor='rgba(0,0,0,0)',
    hoverlabel=dict(bgcolor="white", font_size=12, font_color="black"),
)
chart_wrapper(line_fig, title=f"IMP Index Trend ({mode})")

# === Optional Data Table ===
if st.checkbox("🔍 Show IMP Index Data Table"):
    st.dataframe(df)