import streamlit as st
import pandas as pd
import plotly.graph_objects as go

st.markdown("### Quarterly Potash Demand (MMT): Actual vs Predicted")
st.markdown("---")

# Load Excel
df = pd.read_excel("data/Agri_Model.xlsx")
df.columns = [c.strip() for c in df.columns]

df['Actual'] = pd.to_numeric(df['Actual'], errors='coerce')
df['Predicted'] = pd.to_numeric(df['Predicted'], errors='coerce')

# Always use both categories to reserve height
categories = ["Actual", "Predicted"]

for _, row in df.iterrows():
    quarter = row['Quarter']
    actual = row['Actual']
    predicted = row['Predicted']

    values = []
    texts = []
    colors = []

    # Ensure both positions are filled (None if missing)
    for cat in categories:
        if cat == "Actual":
            val = actual if pd.notna(actual) else 0
            text = f"{actual:.2f}" if pd.notna(actual) else ""
            color = '#007381'
        else:
            val = predicted if pd.notna(predicted) else 0
            text = f"{predicted:.2f}" if pd.notna(predicted) else ""
            color = '#E85412'

        values.append(val)
        texts.append(text)
        colors.append(color)

    fig = go.Figure(go.Bar(
        y=categories,
        x=values,
        orientation='h',
        marker_color=colors,
        text=texts,
        textposition='auto'
    ))

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