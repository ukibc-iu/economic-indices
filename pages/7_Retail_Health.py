import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA
import joblib
import os

st.set_page_config(layout="wide")

# === Load Data ===
df = pd.read_csv("data/Retail_Health.csv")
df.columns = df.columns.str.strip()

# === Parse Date ===
df['Date'] = pd.to_datetime(df['Date'], errors='coerce')
df = df.dropna(subset=['Date'])
df['Month'] = df['Date'].dt.strftime('%b-%y')

# === Clean Numeric Columns ===
numeric_cols = ['CCI', 'Inflation', 'Private Consumption', 'UPI Transactions', 'Repo Rate', 'Per Capita NNI']
for col in numeric_cols:
    df[col] = pd.to_numeric(df[col], errors='coerce')

# === Adjust Directionality ===
df['Inflation'] = -df['Inflation']
df['Repo Rate'] = -df['Repo Rate']

# === Drop Rows with Missing Values ===
df_clean = df.dropna(subset=numeric_cols).copy()

# === Fixed PCA Training Window ===
training_end = pd.to_datetime("2024-03-01")
df_train = df_clean[df_clean['Date'] <= training_end].copy()

# === Fit PCA only on training data ===
scaler = StandardScaler()
X_train_scaled = scaler.fit_transform(df_train[numeric_cols])
pca = PCA(n_components=1)
train_index = pca.fit_transform(X_train_scaled)

# Save the scaler and PCA model (optional)
# joblib.dump(scaler, "scaler.pkl")
# joblib.dump(pca, "pca.pkl")

# === Apply PCA to all data using trained scaler ===
X_all_scaled = scaler.transform(df_clean[numeric_cols])
df_clean['Retail Index'] = pca.transform(X_all_scaled)

# === Normalize Index based on training min/max ===
min_val, max_val = train_index.min(), train_index.max()
df_clean['Retail Index'] = (df_clean['Retail Index'] - min_val) / (max_val - min_val)

# === Clip to ensure range stays within [0,1] ===
df_clean['Retail Index'] = df_clean['Retail Index'].clip(0, 1)

# === Optional: Rebase to 100-style index ===
# df_clean['Retail Index'] = df_clean['Retail Index'] * 100

# === Header ===
st.title("Retail Health Index Dashboard")
st.markdown("*This dashboard presents a Retail Health Index derived from PCA on key economic indicators, adjusted for inflation and interest rates.*")

# === Latest Metrics ===
latest = df_clean.sort_values("Date").iloc[-1]
col1, col2, col3 = st.columns(3)
with col1:
    st.metric("Retail Index (PCA-based)", f"{latest['Retail Index']*100:.1f}%")
with col2:
    st.metric("Consumer Confidence Index (CCI)", f"{latest['CCI']:.1f}")
with col3:
    st.metric("UPI Transactions (Billion)", f"{latest['UPI Transactions']:.2f}")

# === Line Chart ===
fig = go.Figure()
fig.add_trace(go.Scatter(x=df_clean['Date'], y=df_clean['Retail Index'], mode='lines', name='Retail Index'))
fig.update_layout(
    title='Retail Index Over Time (PCA)',
    xaxis_title='Date',
    yaxis_title='Retail Index (0–1)',
    template='plotly_dark',
    height=450
)
st.plotly_chart(fig, use_container_width=True)

# === Breakdown Table ===
if st.checkbox("Show Raw Data & Retail Index"):
    st.dataframe(df_clean[['Date', 'Month'] + numeric_cols + ['Retail Index']])