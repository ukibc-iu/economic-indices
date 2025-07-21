import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA

# === Set Page Config ===
st.set_page_config(layout="wide")
st.title("🛍️ Retail Health Index Dashboard")
st.markdown("*A PCA-based index combining key retail indicators.*")

# === Load and Prepare Data ===
df = pd.read_csv("data/Retail_Health.csv")
df.columns = df.columns.str.strip()
df['Date'] = pd.to_datetime(df['Date'], errors='coerce')
df = df.dropna(subset=['Date'])
df['Month'] = df['Date'].dt.strftime('%b-%y')

# Custom Fiscal Quarter Format
def get_fiscal_quarter(date):
    month = date.month
    year = date.year
    if 4 <= month <= 6:
        return f"Q1 {year}-{str(year+1)[-2:]}"
    elif 7 <= month <= 9:
        return f"Q2 {year}-{str(year+1)[-2:]}"
    elif 10 <= month <= 12:
        return f"Q3 {year}-{str(year+1)[-2:]}"
    else:  # Jan-Mar
        return f"Q4 {year-1}-{str(year)[-2:]}"
df['Quarter'] = df['Date'].apply(get_fiscal_quarter)

# Clean numeric fields
numeric_cols = ['CCI', 'Inflation', 'Private Consumption', 'UPI Transactions', 'Repo Rate', 'Per Capita NNI']
for col in numeric_cols:
    df[col] = pd.to_numeric(df[col], errors='coerce')

# Reverse negative economic indicators
df['Inflation'] = -df['Inflation']
df['Repo Rate'] = -df['Repo Rate']

df_clean = df.dropna(subset=numeric_cols).copy()

# === PCA ===
training_end = pd.to_datetime("2024-03-01")
df_train = df_clean[df_clean['Date'] <= training_end].copy()

scaler = StandardScaler()
X_train_scaled = scaler.fit_transform(df_train[numeric_cols])
pca = PCA(n_components=1)
train_index = pca.fit_transform(X_train_scaled)

X_all_scaled = scaler.transform(df_clean[numeric_cols])
df_clean['Retail Index Raw'] = pca.transform(X_all_scaled)

# Normalize to 0–1
min_val, max_val = train_index.min(), train_index.max()
df_clean['Retail Index'] = (df_clean['Retail Index Raw'] - min_val) / (max_val - min_val)
df_clean['Retail Index'] = df_clean['Retail Index'].clip(0, 1)

# === Latest Month/Quarter KPIs ===
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

# === View Controls ===
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

selected_row = filtered_df.sort_values("Date").iloc[-1]

# === Chart Wrapper ===
def chart_wrapper(title, fig, height=350):
    st.markdown(f"### {title}")
    fig.update_layout(height=height, margin=dict(t=40, b=20, l=10, r=10))
    st.plotly_chart(fig, use_container_width=True)

# === Gauge Chart ===
gauge_fig = go.Figure(go.Indicator(
    mode="gauge+number",
    value=selected_row["Retail Index"] * 100,
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

# === PCA Contribution Doughnut ===
pca_weights = pca.components_[0]
labels = numeric_cols
values = [abs(w) for w in pca_weights]

donut_fig = go.Figure(go.Pie(
    labels=labels,
    values=values,
    hole=0.5,
    showlegend=True,
    textinfo='none',  # Remove inner % labels
))
donut_fig.update_traces(marker=dict(colors=px.colors.qualitative.Pastel))
donut_fig.update_layout(title="PCA Component Breakdown")

# === Chart Row ===
c1, c2 = st.columns(2)
with c1:
    chart_wrapper("🧭 Retail Index Gauge", gauge_fig)
with c2:
    chart_wrapper("📊 PCA Contribution Breakdown", donut_fig)

# === Trend Over Time ===
line_fig = go.Figure()
line_fig.add_trace(go.Scatter(
    x=df_clean['Date'],
    y=df_clean['Retail Index'],
    mode='lines',
    name='Retail Index',
    line=dict(color='deepskyblue')
))
line_fig.update_layout(
    xaxis_title='Date',
    yaxis_title='Retail Index (0–1)',
    template='plotly_white'
)
chart_wrapper("📈 Retail Index Over Time", line_fig)

# === Optional Data Table ===
with st.expander("🔍 Show Raw Data"):
    st.dataframe(df_clean[['Date', 'Month', 'Quarter'] + numeric_cols + ['Retail Index']])