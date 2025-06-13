import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime

# --- Page Config ---
st.set_page_config(layout="wide")
st.title("📊 IMP Index Dashboard")

# --- Load Data ---
@st.cache_data
def load_imp_data():
    df = pd.read_csv("data/IMP_Index.csv")
    df.columns = df.columns.str.strip()
    df['Date'] = pd.to_datetime(df['Date'], format='%b-%y', errors='coerce')
    df = df.dropna(subset=['Date', 'Scale'])
    df['Month'] = df['Date'].dt.strftime('%b-%Y')
    
    def get_fiscal_quarter(date):
        m, y = date.month, date.year
        if m in [4, 5, 6]: q, fy = 'Q1', y
        elif m in [7, 8, 9]: q, fy = 'Q2', y
        elif m in [10, 11, 12]: q, fy = 'Q3', y
        else: q, fy = 'Q4', y - 1
        return f"{q} {fy}-{str(fy+1)[-2:]}"
    
    df['Fiscal_Quarter'] = df['Date'].apply(get_fiscal_quarter)
    return df

imp_df = load_imp_data()

# --- View Mode ---
view_mode = st.radio("Select View Mode", ['Monthly', 'Quarterly'], horizontal=True)

if view_mode == 'Monthly':
    months = sorted(imp_df['Month'].unique())
    latest_month = imp_df.sort_values('Date').iloc[-1]['Month']
    selected_month = st.selectbox("Select Month", months, index=months.index(latest_month))
    selected_df = imp_df[imp_df['Month'] == selected_month]
    selected_label = selected_month
    selected_scale = selected_df['Scale'].values[0]
else:
    quarters = sorted(imp_df['Fiscal_Quarter'].unique())
    latest_quarter = imp_df.sort_values('Date').iloc[-1]['Fiscal_Quarter']
    selected_quarter = st.selectbox("Select Quarter", quarters, index=quarters.index(latest_quarter))
    selected_df = imp_df[imp_df['Fiscal_Quarter'] == selected_quarter]
    selected_label = selected_quarter
    selected_scale = selected_df['Scale'].mean()

# --- IMP Scale Bar ---
imp_color_map = {
    -3: ("#800000", "Extremely Weak"),
    -2: ("#e31a1c", "Weak"),
    -1: ("#fc4e2a", "Below Avg"),
     0: ("#fecc5c", "Neutral"),
     1: ("#78c679", "Above Avg"),
     2: ("#31a354", "Strong"),
     3: ("#006837", "Extremely Strong"),
}

scale_fig = go.Figure()
for val in range(-3, 4):
    color, label = imp_color_map[val]
    scale_fig.add_shape(type="rect", x0=val-0.5, x1=val+0.5, y0=-0.3, y1=0.3,
                        line=dict(color="black", width=1), fillcolor=color)
    scale_fig.add_trace(go.Scatter(x=[val], y=[0], mode='text', text=[str(val)],
                                   hovertext=[f"{label} ({val})"], showlegend=False,
                                   textfont=dict(color='white', size=16)))

# Highlight Selected
scale_fig.add_shape(type="rect", x0=selected_scale-0.5, x1=selected_scale+0.5,
                    y0=-0.35, y1=0.35, line=dict(color="crimson", width=3, dash="dot"),
                    fillcolor="rgba(0,0,0,0)")

scale_fig.add_trace(go.Scatter(x=[selected_scale], y=[0.45], mode='text',
                               text=[f"{selected_scale:.2f}"], showlegend=False,
                               textfont=dict(size=16, color='crimson')))

scale_fig.update_layout(title=f"IMP Index for {selected_label}",
                        xaxis=dict(range=[-3.5, 3.5], title='IMP Scale (-3 to +3)',
                                   showticklabels=False, showgrid=False),
                        yaxis=dict(visible=False), height=280,
                        margin=dict(l=30, r=30, t=60, b=30), showlegend=False)

st.plotly_chart(scale_fig, use_container_width=True)

# --- Contribution Funnel Chart ---
weights = {
    "1.- Real GDP": 40,
    "2.- Fiscal Balance": 10,
    "3.- Balance of Trade": 20,
    "4.- Inflation": 20,
    "5.- Unemployment": 10
}

labels = list(weights.keys())
values = list(weights.values())

funnel_fig = go.Figure(go.Funnel(
    y=labels,
    x=values,
    textinfo="value+percent previous",
    marker=dict(color=values, colorscale='Blues')
))
funnel_fig.update_layout(title="IMP Index - Contribution Breakdown", height=400)

st.plotly_chart(funnel_fig, use_container_width=True)

# --- Optional: Raw Data View ---
with st.expander("🔍 Show Raw IMP Index Data"):
    st.dataframe(imp_df[['Date', 'Month', 'Fiscal_Quarter', 'Scale']])