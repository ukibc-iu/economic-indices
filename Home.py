import streamlit as st
import plotly.graph_objects as go

st.set_page_config(layout="wide", page_title="Economic Indices Overview")
st.title("📊 Economic Indices Dashboard")

st.markdown("Select an index below to explore its detailed trends and analysis.")

# Index info: filename, color, and mock trend data
indices = {
    "Consumer Demand Index (CDI)": (
        "1_CDI_Dashboard", "#62C8CE", [1.0, 0.2, 0.74, 1.6, 1.8]  # mild upward
    ),
    "EV Market Adoption Rate": (
        "2_EV_Market_Adoption_Rate", "#E85412", [2.5, 2.0, 1.1, 0.9, 1.7]  # gradual decline
    ),
    "Housing Affordability Stress Index": (
        "3_Housing_Affordability_Stress_Index", "#007381", [1.5, 1.3, 1.1, 1.4, 1.7]  # bounce back
    ),
    "Renewable Transition Readiness Score": (
        "4_Renewable_Transition_Readiness_Score", "#002060", [1.2, 1.8, 1.1, 1.9, 1.5]  # volatile
    ),
    "Infrastructure Activity Index (IAI)": (
        "5_Infrastructure_Activity_Index_(IAI)", "#4B575F", [1.0, 1.5, 1.2, 1.8, 2.5]  # strong growth
    ),
    "IMP Index": (
        "6_IMP_Index", "#60AEB3", [2.0, 2.5, 1.8, 2.8, 2.3]  # dip and rise
    ),
}

cols = st.columns(3)
for i, (name, (page, color, trend)) in enumerate(indices.items()):
    with cols[i % 3]:
        st.subheader(name)

        # Mini chart with unique trend and color
        fig = go.Figure()
        fig.add_trace(go.Scatter(y=trend, mode="lines", line=dict(color=color)))
        fig.update_layout(
            height=150,
            margin=dict(l=10, r=10, t=10, b=10),
            xaxis=dict(visible=False),
            yaxis=dict(visible=False),
        )
        st.plotly_chart(fig, use_container_width=True, key=f"chart-{i}")

        st.caption("An overview of recent trends in " + name.split('(')[0].strip())

        # Stylized button linking to the index dashboard
        button_html = f"""
            <a href="/pages/{page}.py" target="_self">
                <button style='background-color:{color};color:white;padding:0.5rem 1rem;border:none;border-radius:0.5rem;width:100%;margin-top:0.5rem;'>
                    Open detailed view of the index →
                </button>
            </a>
        """
        st.markdown(button_html, unsafe_allow_html=True)