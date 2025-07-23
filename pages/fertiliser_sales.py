import streamlit as st
import pandas as pd
import plotly.graph_objects as go

st.markdown("### Quarterly Potash Demand (MMT): Actual vs Predicted")
st.markdown("---")

# Load Excel file
df = pd.read_excel("data/Agri_Model.xlsx")

# Clean column names just in case
df.columns = [col.strip() for col in df.columns]

# Fill missing Actuals with 0 or NaN as needed
df['Actual'] = pd.to_numeric(df['Actual'], errors='coerce')
df['Predicted'] = pd.to_numeric(df['Predicted'], errors='coerce')

# Reverse order so latest quarter appears on top
df = df[::-1].reset_index(drop=True)

# Horizontal Grouped Bar Chart
fig = go.Figure()

fig.add_trace(go.Bar(
    y=df['Quarter'],
    x=df['Actual'],
    name='Actual',
    orientation='h',
    marker_color='seagreen',
    text=df['Actual'].apply(lambda x: f"{x:.2f}" if pd.notnull(x) else ""),
    textposition='auto'
))

fig.add_trace(go.Bar(
    y=df['Quarter'],
    x=df['Predicted'],
    name='Predicted',
    orientation='h',
    marker_color='darkorange',
    text=df['Predicted'].apply(lambda x: f"{x:.2f}" if pd.notnull(x) else ""),
    textposition='auto'
))

fig.update_layout(
    barmode='group',
    xaxis_title='Potash Demand (MMT)',
    yaxis_title='Quarter',
    height=450,
    legend=dict(orientation='h', yanchor='bottom', y=1.02, xanchor='right', x=1)
)

st.plotly_chart(fig, use_container_width=True)