import streamlit as st
import plotly.graph_objects as go

st.set_page_config(layout="wide", page_title="Economic Indices Overview")
st.title("📊 Economic Indices Dashboard")

st.markdown("Select an index below to explore its detailed trends and analysis.")

# Updated indices dictionary
indices = {
    "Consumer Demand Index (CDI)": "1_CDI_Dashboard",
    "EV Market Adoption Rate": "2_EV Market Adoption Rate",
    "Housing Affordability Stress Index": "3_Housing Affordability Stress Index",
    "Renewable Transition Readiness Score": "4_Renewable Transition Readiness Score",
    "Infrastructure Activity Index (IAI)": "5_Infrastructure Activity Index (IAI)",
    "IMP Index": "6_IMP Index",
}

cols = st.columns(3)
for i, (name, page) in enumerate(indices.items()):
    with cols[i % 3]:
        st.subheader(name)

        # Sample mini line chart with unique key
        fig = go.Figure()
        fig.add_trace(go.Scatter(y=[1, 2, 1.5, 2.5, 3], mode="lines", line=dict(color="blue")))
        fig.update_layout(
            height=150,
            margin=dict(l=10, r=10, t=10, b=10),
            xaxis=dict(visible=False),
            yaxis=dict(visible=False),
        )
        st.plotly_chart(fig, use_container_width=True, key=f"chart-{i}")

        st.caption("An overview of recent trends in " + name.split('(')[0].strip())

        # Button with unique key
        if st.button(f"Go to {name}", key=f"button-{i}"):
            st.switch_page(f"pages/{page}.py")