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
.bg-1 { background: linear-gradient(#0060C0, #003A74, #002142); }
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

# === Scale Bar ===
color_map = {
    -3: ("#800000", "Very Low"),
    -2: ("#fc4e2a", "Low"),
    -1: ("#fd8d3c", "Slightly Low"),
     0: ("#fecc5c", "Neutral"),
     1: ("#78c679", "Slightly High"),
     2: ("#31a354", "High"),
     3: ("#006837", "Very High")
}

fig = go.Figure()

for val in range(-3, 4):
    color, label = color_map[val]
    
    fig.add_shape(
        type="rect", 
        x0=val - 0.5, x1=val + 0.5, 
        y0=-0.3, y1=0.3,
        line=dict(color="black", width=1), 
        fillcolor=color,
        layer="below"
    )
    
    text_color = 'black' if val == 0 else 'white'
    
    fig.add_trace(go.Scatter(
        x=[val], y=[0], 
        mode='text', 
        text=[str(val)],
        hovertext=[f"{label} ({val})"],
        showlegend=False,
        textfont=dict(color=text_color, size=16),
    ))

fig.add_shape(
    type="rect", 
    x0=selected_value - 0.5, x1=selected_value + 0.5,
    y0=-0.35, y1=0.35,
    line=dict(color="crimson", width=2.5, dash="dot"),
    fillcolor="rgba(0,0,0,0)", 
    layer="above"
)

fig.add_trace(go.Scatter(
    x=[selected_value], y=[0.5], 
    mode='text',
    text=[f"{selected_value:.2f}"],
    showlegend=False,
    textfont=dict(size=16, color='crimson')
))

fig.update_layout(
    title=f"IMP Index for {label_period} (Scale: {selected_value:.2f})",
    xaxis=dict(range=[-3.5, 3.5], title='IMP Index Scale (-3 to +3)', showticklabels=False, showgrid=False, zeroline=False),
    yaxis=dict(visible=False), 
    height=280,
    margin=dict(l=30, r=30, t=60, b=30), 
    showlegend=False,
    plot_bgcolor='rgba(0,0,0,0)',
    paper_bgcolor='rgba(0,0,0,0)',
)

st.plotly_chart(fig, use_container_width=True)

st.markdown("### 💡 Expert Opinion")

# Expert opinion (static for now)
expert_opinion = "IMP Index is currently neutral."

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
    "Factor": list(contrib_weights.keys()),
    "Weight": list(contrib_weights.values())
}).sort_values(by="Weight", ascending=False)

color_map = {
    40: "#003366",
    20: "#3399cc",
    10: "#99ccff"
}
bar_colors = contrib_df["Weight"].map(color_map)

bar_fig = go.Figure(go.Bar(
    y=contrib_df["Factor"],
    x=contrib_df["Weight"],
    orientation='h',
    marker=dict(color=bar_colors, line=dict(color='black', width=1)),
    text=[f"{w}%" for w in contrib_df["Weight"]],
    textposition='auto'
))

bar_fig.update_layout(
    height=400,
    title="Factor Contributions to IMP Index",
    xaxis_title="Weight (%)",
    yaxis=dict(categoryorder='total ascending'),
    margin=dict(l=30, r=30, t=40, b=30),
)
st.plotly_chart(bar_fig, use_container_width=True)

# === Line Graph of IMP Index Over Time ===
st.markdown("### IMP Index Trend Over Time")

if mode == "Monthly":
    time_series = df.sort_values("Date")[["Date", "Scale"]]
    x_vals = time_series["Date"]
else:
    quarter_df = df.groupby("Fiscal_Quarter")["Scale"].mean().reset_index()
    q_info = quarter_df["Fiscal_Quarter"].str.extract(r'Q(?P<q>\d) (?P<year>\d{4})')
    q_info["q"] = q_info["q"].astype(int)
    q_info["year"] = q_info["year"].astype(int)

    quarter_start_dates = []
    for _, row in q_info.iterrows():
        q = row["q"]
        fy = row["year"]
        if q == 4:
            start_date = pd.Timestamp(year=fy + 1, month=1, day=1)
        else:
            start_month = 3 * (q - 1) + 4
            start_date = pd.Timestamp(year=fy, month=start_month, day=1)
        quarter_start_dates.append(start_date)

    quarter_df["Quarter_Start"] = quarter_start_dates
    time_series = quarter_df.sort_values("Quarter_Start")[["Quarter_Start", "Scale"]]
    x_vals = time_series["Quarter_Start"]

line_fig = go.Figure()
line_fig.add_trace(go.Scatter(
    x=x_vals,
    y=time_series["Scale"],
    mode="lines",
    line=dict(color="#3f51b5", width=3),
    name="IMP Index",
    hovertemplate="Date: %{x}<br>IMP Index: %{y:.2f}<extra></extra>",
    showlegend=False
))

line_fig.update_layout(
    height=400,
    title=f"IMP Index Trend Over Time ({mode})",
    xaxis_title="Date",
    yaxis_title="IMP Index Value",
    margin=dict(l=30, r=30, t=50, b=30),
    xaxis=dict(showgrid=False, zeroline=False),
    yaxis=dict(showgrid=True, zeroline=False),
    plot_bgcolor='rgba(0,0,0,0)',
    paper_bgcolor='rgba(0,0,0,0)',
    hoverlabel=dict(bgcolor="white", font_size=12, font_color="black"),
)
st.plotly_chart(line_fig, use_container_width=True)

# === Optional Data Table ===
if st.checkbox("🔍 Show IMP Index Data Table"):
    st.dataframe(df)