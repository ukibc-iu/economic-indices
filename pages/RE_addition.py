import streamlit as st
import pandas as pd
import plotly.graph_objects as go

st.markdown("### Quarterly Renewable Capacity Addition Forecasts: Actual vs Predicted")
st.markdown("---")

# File and sheet setup
excel_path = "data/Solar&Wind_Model.xlsx"
sheets = ["Solar", "Wind"]

colors = {
    "Actual": "#007381",
    "Predicted": "#E85412"
}

for sheet in sheets:
    st.markdown(f"#### {sheet} (MW)")

    df = pd.read_excel(excel_path, sheet_name=sheet)
    df.columns = [col.strip() for col in df.columns]
    df['Actual'] = pd.to_numeric(df['Actual'], errors='coerce')
    df['Predicted'] = pd.to_numeric(df['Predicted'], errors='coerce')

    for _, row in df.iterrows():
        quarter = row['Quarter']
        actual = row['Actual']
        predicted = row['Predicted']

        values = [
            actual if pd.notna(actual) else 0,
            predicted if pd.notna(predicted) else 0
        ]

        texts = [
            f"{actual:,.0f}" if pd.notna(actual) else "",
            f"{predicted:,.0f}" if pd.notna(predicted) else ""
        ]

        fig = go.Figure(go.Bar(
            y=["Actual", "Predicted"],
            x=values,
            orientation='h',
            marker_color=[colors["Actual"], colors["Predicted"]],
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

    st.markdown("---")  # spacer between Solar and Wind