import streamlit as st
import pandas as pd
from sklearn.decomposition import PCA
from sklearn.preprocessing import MinMaxScaler, StandardScaler
import plotly.graph_objects as go

st.set_page_config(layout="wide")
st.title("Consumer Demand Index")

# Path to your default data file (place your CSV here)
DEFAULT_DATA_PATH = "data/Consumer_Demand_Index.csv"

# Load the data automatically
try:
    df = pd.read_csv(DEFAULT_DATA_PATH)
except Exception as e:
    st.error(f"Error loading data file: {e}")
    st.stop()

df.columns = df.columns.str.strip()

# Parse date column
df['Date'] = pd.to_datetime(df['Date'], dayfirst=False, errors='coerce')
df = df.dropna(subset=['Date'])

# Features for PCA
features = ['UPI Transactions', 'GST Revenue', 'Vehicle Sales', 'Housing Sales', 'Power Consumption']
missing_cols = [col for col in features if col not in df.columns]
if missing_cols:
    st.error(f"Missing columns in data: {missing_cols}")
    st.stop()

df = df.dropna(subset=features)

# Standardize features
scaler_std = StandardScaler()
scaled_features = scaler_std.fit_transform(df[features])

# PCA
pca = PCA(n_components=1)
pca_components = pca.fit_transform(scaled_features)

# Scale PCA output to -5 to +5
pca_shifted = pca_components - pca_components.min()
scaler_mm = MinMaxScaler(feature_range=(0, 1))
pca_normalized = scaler_mm.fit_transform(pca_shifted)
cdi_scaled = pca_normalized * 10 - 5  # scale to [-5,5]

df['CDI'] = cdi_scaled

# Monthly labels
df['Month'] = df['Date'].dt.strftime('%b-%Y')

# Fiscal quarter function (Apr-Mar FY)
def get_fiscal_quarter(date):
    month = date.month
    year = date.year
    if month in [4, 5, 6]:
        quarter = "Q1"
        fy_start = year
    elif month in [7, 8, 9]:
        quarter = "Q2"
        fy_start = year
    elif month in [10, 11, 12]:
        quarter = "Q3"
        fy_start = year
    else:  # Jan to Mar
        quarter = "Q4"
        fy_start = year - 1
    fy_label = f"{fy_start}-{str(fy_start + 1)[-2:]}"
    return f"{quarter} {fy_label}"

df['Fiscal_Quarter'] = df['Date'].apply(get_fiscal_quarter)

# View mode toggle
mode = st.radio("📅 View Mode", ['Monthly', 'Quarterly'], horizontal=True)

if mode == 'Monthly':
    selected_month = st.selectbox("Select a month", df['Month'].unique())
    selected_value = df.loc[df['Month'] == selected_month, 'CDI'].values[0]
    display_label = selected_month
    line_x = df['Date']
    line_y = df['CDI']
    line_title = "CDI Over Time (Monthly)"
    xaxis_title = "Date"
else:
    quarter_df = df.groupby('Fiscal_Quarter')['CDI'].mean().reset_index()
    selected_quarter = st.selectbox("Select a fiscal quarter", quarter_df['Fiscal_Quarter'].unique())
    selected_value = quarter_df.loc[quarter_df['Fiscal_Quarter'] == selected_quarter, 'CDI'].values[0]
    display_label = selected_quarter
    line_x = quarter_df['Fiscal_Quarter']
    line_y = quarter_df['CDI']
    line_title = "CDI Over Time (Quarterly)"
    xaxis_title = "Fiscal Quarter"

# Plot CDI scale
fig = go.Figure()

fig.add_trace(go.Scatter(
    x=[selected_value],
    y=[0],
    mode='markers+text',
    marker=dict(size=20, color='crimson'),
    text=[f"{selected_value:.2f}"],
    textposition="top center"
))

fig.add_shape(
    type='line',
    x0=selected_value, x1=selected_value,
    y0=-0.3, y1=0.3,
    line=dict(color='crimson', dash='dot')
)

fig.add_shape(
    type='line',
    x0=0, x1=0,
    y0=-0.5, y1=0.5,
    line=dict(color='gray', dash='dash')
)

fig.update_layout(
    title=f"Consumer Demand Index for {display_label}",
    xaxis=dict(
        range=[-5.5, 5.5],
        tickmode='linear',
        tick0=-5,
        dtick=1,
        title='CDI Scale (-5 to +5)',
        showgrid=False
    ),
    yaxis=dict(visible=False),
    height=220,
    margin=dict(l=30, r=30, t=50, b=30),
    showlegend=False
)

st.plotly_chart(fig, use_container_width=True)

# Line Graph of CDI over time
line_fig = go.Figure()
line_fig.add_trace(go.Scatter(
    x=line_x,
    y=line_y,
    mode='lines+markers',
    line=dict(color='royalblue', width=3),
    marker=dict(size=6),
    name='CDI'
))

line_fig.update_layout(
    title=line_title,
    xaxis_title=xaxis_title,
    yaxis_title="CDI (-5 to +5)",
    yaxis=dict(range=[-5.5, 5.5]),
    height=400,
    margin=dict(l=40, r=40, t=50, b=40)
)

st.plotly_chart(line_fig, use_container_width=True)

if st.checkbox("🔍 Show raw data with CDI"):
    st.dataframe(df[['Date', 'Month', 'Fiscal_Quarter', 'CDI'] + features])