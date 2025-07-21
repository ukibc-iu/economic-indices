import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA
import plotly.express as px

# === Load and Prepare Data ===
df = pd.read_csv("data/Retail_Health.csv")
df.columns = df.columns.str.strip()
df['Date'] = pd.to_datetime(df['Date'], errors='coerce')
df = df.dropna(subset=['Date'])
df['Month'] = df['Date'].dt.strftime('%b-%y')
df['Quarter'] = df['Date'].dt.to_period('Q').astype(str)

numeric_cols = ['CCI', 'Inflation', 'Private Consumption', 'UPI Transactions', 'Repo Rate', 'Per Capita NNI']
for col in numeric_cols:
    df[col] = pd.to_numeric(df[col], errors='coerce')

# Adjust directionality
df['Inflation'] = -df['Inflation']
df['Repo Rate'] = -df['Repo Rate']
df_clean = df.dropna(subset=numeric_cols).copy()

# === PCA Calculation ===
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

# === Streamlit UI ===
st.set_page_config(layout="wide")
st.title("🛍️ Retail Health Index Dashboard")
st.markdown("*A PCA-based index combining key retail indicators.*")

# === KPI Cards ===
latest_row = df_clean.sort_values("Date").iloc[-1]
st.markdown("### 📊 Latest Retail KPI Summary")
col1, col2, col3 = st.columns(3)
with col1:
    with st.container(border=True):
        st.metric("Retail Index", f"{latest_row['Retail Index'] * 100:.1f}%")
with col2:
    with st.container(border=True):
        st.metric("Latest Month", latest_row['Month'])
with col3:
    with st.container(border=True):
        st.metric("Latest Quarter", latest_row['Quarter'])

# === Controls Below KPI ===
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

selected_latest = filtered_df.sort_values("Date").iloc[-1]

# === Chart Wrapper ===
def chart_wrapper(title, fig):
    with st.container(border=True):
        st.markdown(f"#### {title}")
        st.plotly_chart(fig, use_container_width=True)

# === Gauge Chart ===
gauge_fig = go.Figure(go.Indicator(
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
gauge_fig.update_layout(height=350)

# === PCA Component Doughnut ===
component_weights = pca.components_[0]
component_labels = numeric_cols
doughnut_fig = go.Figure(data=[go.Pie(
    labels=component_labels,
    values=abs(component_weights),
    hole=0.5,
    marker=dict(colors=px.colors.qualitative.Pastel),
    textinfo='label+percent'
)])
doughnut_fig.update_layout(title="PCA Component Breakdown", height=350, showlegend=True)

# === Display Charts in Row ===
col1, col2 = st.columns(2)
with col1:
    chart_wrapper("🧭 Retail Index Gauge", gauge_fig)
with col2:
    chart_wrapper("📊 PCA Contribution Breakdown", doughnut_fig)

# === Line Chart ===
line_fig = go.Figure()
line_fig.add_trace(go.Scatter(
    x=df_clean['Date'],
    y=df_clean['Retail Index'],
    mode='lines',
    name='Retail Index',
    line=dict(color='deepskyblue')
))
line_fig.update_layout(
    title="📈 Retail Index Over Time",
    xaxis_title='Date',
    yaxis_title='Retail Index (0–1)',
    template='plotly_white',
    height=400
)
chart_wrapper("Retail Index Over Time", line_fig)

# === Raw Data ===
with st.expander("🔍 Show Raw Data"):
    st.dataframe(df_clean[['Date', 'Month', 'Quarter'] + numeric_cols + ['Retail Index']])