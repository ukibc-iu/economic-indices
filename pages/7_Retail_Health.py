import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA
import numpy as np

# === Set up page ===
st.set_page_config(layout="wide")
st.title("🛍️ Retail Health Index Dashboard")
st.markdown("*A PCA-based index combining key retail indicators.*")

# === Load and Clean Data ===
df = pd.read_csv("data/Retail_Health.csv")
df.columns = df.columns.str.strip()
df['Date'] = pd.to_datetime(df['Date'], errors='coerce')
df = df.dropna(subset=['Date'])
df['Month'] = df['Date'].dt.strftime('%b-%y')

# --- Create Indian Fiscal Quarters ---
def get_fiscal_quarter(date):
    month = date.month
    year = date.year
    if 4 <= month <= 6:
        qtr = "Q1"
        fy = f"{year}-{str(year + 1)[-2:]}"
    elif 7 <= month <= 9:
        qtr = "Q2"
        fy = f"{year}-{str(year + 1)[-2:]}"
    elif 10 <= month <= 12:
        qtr = "Q3"
        fy = f"{year}-{str(year + 1)[-2:]}"
    else:  # Jan–Mar
        qtr = "Q4"
        fy = f"{year - 1}-{str(year)[-2:]}"
    return f"{qtr} {fy}"

df['Quarter'] = df['Date'].apply(get_fiscal_quarter)

# Clean numeric columns
numeric_cols = ['CCI', 'Inflation', 'Private Consumption', 'UPI Transactions', 'Repo Rate', 'Per Capita NNI']
for col in numeric_cols:
    df[col] = pd.to_numeric(df[col], errors='coerce')

# Adjust directionality for negative indicators
df['Inflation'] = -df['Inflation']
df['Repo Rate'] = -df['Repo Rate']

df_clean = df.dropna(subset=numeric_cols).copy()

# === PCA Index Calculation ===
training_end = pd.to_datetime("2024-03-01")
df_train = df_clean[df_clean['Date'] <= training_end].copy()

scaler = StandardScaler()
X_train_scaled = scaler.fit_transform(df_train[numeric_cols])
pca = PCA(n_components=1)
train_index = pca.fit_transform(X_train_scaled)

X_all_scaled = scaler.transform(df_clean[numeric_cols])
df_clean['Retail Index Raw'] = pca.transform(X_all_scaled)
min_val, max_val = train_index.min(), train_index.max()
df_clean['Retail Index'] = (df_clean['Retail Index Raw'] - min_val) / (max_val - min_val)
df_clean['Retail Index'] = df_clean['Retail Index'].clip(0, 1)

# === KPI Cards (Latest Overall) ===
latest = df_clean.sort_values("Date").iloc[-1]

col1, col2, col3 = st.columns(3)
with col1:
    with st.container(border=True):
        st.metric("Retail Index", f"{latest['Retail Index'] * 100:.1f}%")
with col2:
    with st.container(border=True):
        st.metric("Month", latest["Month"])
with col3:
    with st.container(border=True):
        st.metric("Quarter", latest["Quarter"])

# === View Selection ===
st.markdown("### 🔍 Select Period to Explore")
view_option = st.radio("View Mode", ["Monthly", "Quarterly"], horizontal=True)

if view_option == "Monthly":
    unique_periods = df_clean['Month'].unique()[::-1]
    period_col = 'Month'
else:
    unique_periods = df_clean['Quarter'].unique()[::-1]
    period_col = 'Quarter'

selected_period = st.selectbox(f"Select {view_option}:", unique_periods)
filtered_df = df_clean[df_clean[period_col] == selected_period]

if filtered_df.empty:
    st.warning(f"No data for {selected_period}")
    st.stop()

selected_latest = filtered_df.sort_values("Date").iloc[-1]

# === Chart Wrapper ===
def chart_wrapper(title, figure):
    with st.container(border=True):
        st.markdown(f"**{title}**")
        st.plotly_chart(figure, use_container_width=True)

# === Gauge and Donut Side by Side ===
col_gauge, col_donut = st.columns(2)

with col_gauge:
    gauge = go.Figure(go.Indicator(
        mode="gauge+number",
        value=selected_latest["Retail Index"] * 100,
        number={'suffix': "%"},
        gauge={
            'axis': {'range': [0, 100]},
            'bar': {'color': "limegreen"},
            'steps': [
                {'range': [0, 40], 'color': "crimson"},
                {'range': [40, 70], 'color': "gold"},
                {'range': [70, 100], 'color': "lightgreen"},
            ],
        },
        title={'text': f"Retail Index - {selected_period}"}
    ))
    gauge.update_layout(height=350)
    chart_wrapper("Retail Index Gauge", gauge)

with col_donut:
    explained = np.abs(pca.components_[0])
    explained = explained / explained.sum()

    labels = numeric_cols
    values = explained * 100

    donut = go.Figure(data=[go.Pie(
        labels=labels,
        values=values,
        hole=0.5,
        sort=False,
        direction="clockwise",
        textinfo='none',
        marker=dict(colors=[
            "#FFA07A", "#DDA0DD", "#87CEFA", "#FFD700", "#90EE90", "#00CED1"
        ])
    )])
    donut.update_layout(
        showlegend=True,
        height=350,
        legend=dict(orientation="v", x=1, y=0.5),
    )
    chart_wrapper("PCA Component Breakdown", donut)

# === Trend Line ===
st.markdown("### 📈 Retail Index Over Time")
trend = go.Figure()
trend.add_trace(go.Scatter(
    x=df_clean['Date'],
    y=df_clean['Retail Index'],
    mode='lines',
    name='Retail Index',
    line=dict(color='deepskyblue')
))
trend.update_layout(
    xaxis_title='Date',
    yaxis_title='Retail Index (0–1)',
    template='plotly_white',
    height=400
)
st.plotly_chart(trend, use_container_width=True)

# === Raw Data (Optional) ===
with st.expander("🔍 Show Raw Data"):
    st.dataframe(df_clean[['Date', 'Month', 'Quarter'] + numeric_cols + ['Retail Index']])