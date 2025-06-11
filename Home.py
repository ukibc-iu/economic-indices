import streamlit as st
import plotly.graph_objects as go

st.set_page_config(layout="wide", page_title="Economic Indices Overview")
st.title("📊 Economic Indices Dashboard")

st.markdown("Select an index below to explore its detailed trends and analysis.")

# Mapping names to page filenames (must match what’s in /pages/)
indices = {
    "Consumer Demand Index (CDI)": "1_CDI_Dashboard",
    "Retail Activity Index": "2_Retail_Index",
    "Energy Usage Index": "3_Energy_Index",
    "Transport Movement Index": "4_Transport_Index",
    "Financial Sentiment Index": "5_Sentiment_Index",
    "Real Estate Index": "6_Housing_Index",
}

cols = st.columns(3)
for i, (name, page) in enumerate(indices.items()):
    with cols[i % 3]:
        st.subheader(name)

        # Sample mini line chart
        fig = go.Figure()
        fig.add_trace(go.Scatter(y=[1, 2, 1.5, 2.5, 3], mode="lines", line=dict(color="blue")))
        fig.update_layout(
            height=150,
            margin=dict(l=10, r=10, t=10, b=10),
            xaxis=dict(visible=False),
            yaxis=dict(visible=False),
        )
        st.plotly_chart(fig, use_container_width=True)

        st.caption("An overview of recent trends in " + name.split('(')[0].strip())

        if st.button(f"Go to {name}", key=name):
            st.switch_page(f"pages/{page}.py")