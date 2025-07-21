import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA

# === Chart Wrapper Function ===
def chart_wrapper(title, chart_obj):
    with st.container(border=True):
        st.subheader(title)
        st.plotly_chart(chart_obj, use_container_width=True)

# === Load and Prepare Data ===
df = pd.read_csv("data/Retail_Health.csv")
df.columns = df.columns.str.strip()
df['Date'] = pd.to_datetime(df['Date'], errors='coerce')
df = df.dropna(subset=['Date'])
df['Month'] = df['Date'].dt.strftime('%b-%y')
df['Quarter'] = df['Date'].dt.to_period('Q').astype(str)

# Clean numeric columns
numeric_cols = ['CCI', 'Inflation', 'Private Consumption', 'UPI Transactions', 'Repo Rate', 'Per Capita NNI']
for col in numeric_cols:
    df[col] = pd.to_numeric(df[col], errors='coerce')

# Adjust for directionality
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

# === UI Setup ===
st.set_page_config(layout="wide")
st.title("🛍️ Retail Health Index Dashboard")
st.markdown("*A PCA-based index combining key retail indicators.*")

# === KPI Cards with Latest Data ===
latest_row = df_clean.sort_values("Date").iloc[-1]
st.markdown("### 📊 Latest Retail KPIs")
col1, col2, col3 = st.columns(3)
with col1:
    with st.container(border=True):
        st.metric("Retail Index", f"{latest_row['Retail Index'] * 100:.1f}%")
with col2:
    with st.container(border=True):
        st.metric("CCI", f"{latest_row['CCI']:.1f}")
with col3:
    with st.container(border=True):
        st.metric("UPI Transactions (B)", f"{latest_row['UPI Transactions']:.2f}")

# === Controls for Exploring Historical Data ===
st.markdown("### 🔎 Explore Historical Data")
view_option = st.radio("View Mode", ["Monthly", "Quarterly"], horizontal=True)

if view_option == "Monthly":
    unique_periods = df_clean['Month'].unique()[::-1]
    period_col = 'Month'
else:
    unique_periods = df_clean['Quarter'].unique()[::-1]
    period_col = 'Quarter'

selected_period = st.selectbox(f"Select {view_option}:", unique_periods)
filtered_df = df_clean[df_clean[period_col] == selected_period].copy()

if filtered_df.empty:
    st.warning(f"No data available for {selected_period}.")
    st.stop()

# Use selected data for visuals only
latest = filtered_df.sort_values("Date").iloc[-1]

# === Gauge and Doughnut Charts ===
st.markdown("### 🧭 Retail Health Index Insights")
col_g1, col_g2 = st.columns(2)

with col_g1:
    gauge_fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=latest["Retail Index"] * 100,
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
    ))
    gauge_fig.update_layout(height=300, margin=dict(t=30, b=0))
    chart_wrapper(f"Retail Index – {selected_period}", gauge_fig)

with col_g2:
    pca_weights = pca.components_[0]
    weight_labels = numeric_cols
    weight_values = abs(pca_weights) / abs(pca_weights).sum()

    donut_fig = go.Figure(data=[go.Pie(
        labels=weight_labels,
        values=weight_values,
        hole=0.6,
        textinfo='label+percent',
        marker=dict(line=dict(color='#000000', width=1))
    )])
    donut_fig.update_layout(height=300, margin=dict(t=30, b=0), showlegend=False)
    chart_wrapper("PCA Component Contributions", donut_fig)

# === Line Chart ===
st.markdown("### 📈 Retail Index Over Time")
trend_fig = go.Figure()
trend_fig.add_trace(go.Scatter(
    x=df_clean['Date'],
    y=df_clean['Retail Index'],
    mode='lines',
    name='Retail Index',
    line=dict(color='deepskyblue')
))
trend_fig.update_layout(
    xaxis_title='Date',
    yaxis_title='Retail Index (0–1)',
    template='plotly_white',
    height=400
)
st.plotly_chart(trend_fig, use_container_width=True)

# === Optional: Show Raw Data Table ===
with st.expander("🔍 Show Raw Data"):
    st.dataframe(df_clean[['Date', 'Month', 'Quarter'] + numeric_cols + ['Retail Index']])