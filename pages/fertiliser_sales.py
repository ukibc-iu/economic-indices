import streamlit as st
import pandas as pd
import plotly.graph_objects as go

st.markdown("### Quarterly Potash Demand (MMT): Actual vs Predicted")
st.markdown("---")

# Load Excel
df = pd.read_excel("data/Agri_Model.xlsx")
df.columns = [c.strip() for c in df.columns]

# Convert numeric safely
df['Actual'] = pd.to_numeric(df['Actual'], errors='coerce')
df['Predicted'] = pd.to_numeric(df['Predicted'], errors='coerce')

# Show each quarter as a separate chart
for _, row in df.iterrows():
    quarter = row['Quarter']
    actual = row['Actual']
    predicted = row['Predicted']
    
    fig = go.Figure()

    # Actual bar (if available)
    if pd.notna(actual):
        fig.add_trace(go.Bar(
            y=["Actual"],
            x=[actual],
            orientation='h',
            name='Actual',
            marker_color='seagreen',
            text=[f"{actual:.2f}"],
            textposition='auto'
        ))

    # Predicted bar
    if pd.notna(predicted):
        fig.add_trace(go.Bar(
            y=["Predicted"],
            x=[predicted],
            orientation='h',
            name='Predicted',
            marker_color='darkorange',
            text=[f"{predicted:.2f}"],
            textposition='auto'
        ))

    # Layout tweaks
    fig.update_layout(
        title=f"{quarter}",
        xaxis_title='',
        yaxis_title='',
        height=200,
        barmode='group',
        showlegend=False,
        margin=dict(l=60, r=20, t=40, b=40),
        xaxis=dict(showticklabels=False)
    )

    st.plotly_chart(fig, use_container_width=True)