import streamlit as st
import pandas as pd
import plotly.graph_objects as go

# === Streamlit Setup ===
st.set_page_config(layout="wide")
st.title("IMP Index Dashboard")

# === Load IMP Index Data ===
imp_data_path = "data/IMP_Index.csv"
try:
    imp_df = pd.read_csv(imp_data_path)
except Exception as e:
    st.error(f"Error loading IMP Index data: {e}")
    st.stop()

imp_df.columns = imp_df.columns.str.strip()
imp_df['Date'] = pd.to_datetime(imp_df['Date'], format='%b-%y', errors='coerce')
imp_df = imp_df.dropna(subset=['Date'])

imp_df['Month'] = imp_df['Date'].dt.strftime('%b-%Y')

# Get Fiscal Quarter
def get_fiscal_quarter(date):
    m, y = date.month, date.year
    if m in [4, 5, 6]: q, fy = 'Q1', y
    elif m in [7, 8, 9]: q, fy = 'Q2', y
    elif m in [10, 11, 12]: q, fy = 'Q3', y
    else: q, fy = 'Q4', y - 1
    return f"{q} {fy}-{str(fy+1)[-2:]}"

imp_df['Fiscal_Quarter'] = imp_df['Date'].apply(get_fiscal_quarter)

# === Latest Info ===
latest_row = imp_df.sort_values('Date').iloc[-1]
latest_scale = latest_row['Scale']
latest_month = latest_row['Month']
latest_quarter = latest_row['Fiscal_Quarter']

# === Mode Selection ===
mode = st.radio("Select View Mode", ['Monthly', 'Quarterly'], horizontal=True)

# === Time Filter ===
if mode == 'Monthly':
    months = sorted(imp_df['Month'].unique())
    selected_month = st.selectbox("Select Month", months, index=months.index(latest_month))
    df_filtered = imp_df[imp_df['Month'] == selected_month]
    label_period = selected_month
    selected_value = df_filtered['Scale'].values[0]
else:
    quarters = sorted(imp_df['Fiscal_Quarter'].unique())
    selected_quarter = st.selectbox("Select Quarter", quarters, index=quarters.index(latest_quarter))
    df_filtered = imp_df[imp_df['Fiscal_Quarter'] == selected_quarter]
    label_period = selected_quarter
    selected_value = df_filtered['Scale'].mean()

# === Scale Bar ===
fig = go.Figure()
color_map = {
    -3: ("#800000", "Very Low"),
    -2: ("#fc4e2a", "Low"),
    -1: ("#fd8d3c", "Slightly Low"),
     0: ("#fecc5c", "Neutral"),
     1: ("#78c679", "Slightly High"),
     2: ("#31a354", "High"),
     3: ("#006837", "Very High")
}

for val in range(-3, 4):
    color, label = color_map[val]
    fig.add_shape(type="rect", x0=val-0.5, x1=val+0.5, y0=-0.3, y1=0.3,
                  line=dict(color="black", width=1), fillcolor=color)
    fig.add_trace(go.Scatter(x=[val], y=[0], mode='text', text=[str(val)],
                             hovertext=[f"{label} ({val})"], showlegend=False,
                             textfont=dict(color='white', size=16)))

fig.add_shape(type="rect", x0=selected_value-0.5, x1=selected_value+0.5,
              y0=-0.35, y1=0.35, line=dict(color="crimson", width=3, dash="dot"),
              fillcolor="rgba(0,0,0,0)", layer="above")
fig.add_trace(go.Scatter(x=[selected_value], y=[0.45], mode='text',
                         text=[f"{selected_value:.2f}"], showlegend=False,
                         textfont=dict(size=16, color='crimson')))

fig.update_layout(title=f"IMP Index for {label_period} (Scale: {selected_value:.2f})",
                  xaxis=dict(range=[-3.5, 3.5], title='IMP Index Scale (-3 to +3)',
                             showticklabels=False, showgrid=False),
                  yaxis=dict(visible=False), height=280,
                  margin=dict(l=30, r=30, t=60, b=30), showlegend=False)

st.plotly_chart(fig, use_container_width=True)

# === IMP Contribution Bar (like funnel) ===
st.markdown("### Contribution Breakdown")

# Define contributions
contrib_weights = {
    "Real GDP": 40,
    "Balance of Trade": 20,
    "Inflation": 20,
    "Fiscal Balance": 10,
    "Unemployment": 10
}

# Sort by weight descending
contrib_df = pd.DataFrame({
    "Factor": list(contrib_weights.keys()),
    "Weight": list(contrib_weights.values())
}).sort_values(by="Weight", ascending=False)

funnel_fig = go.Figure(go.Bar(
    y=contrib_df["Factor"],
    x=contrib_df["Weight"],
    orientation='h',
    marker=dict(
        color=['#003f5c', '#58508d', '#bc5090', '#ff6361', '#ffa600'],
        line=dict(color='black', width=1)
    ),
    text=[f"{w}%" for w in contrib_df["Weight"]],
    textposition='auto'
))

funnel_fig.update_layout(
    height=400,
    title=f"Factor Contributions to IMP Index",
    xaxis_title="Weight (%)",
    yaxis_title="",
    yaxis=dict(categoryorder='total ascending'),
    margin=dict(l=30, r=30, t=40, b=30),
)

st.plotly_chart(funnel_fig, use_container_width=True)
# === Show Raw Data ===
if st.checkbox("\U0001F50D Show raw IMP data"):
    st.dataframe(imp_df)