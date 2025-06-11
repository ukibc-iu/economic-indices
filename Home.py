import streamlit as st
import plotly.graph_objects as go

# Set dark theme layout and page title
st.set_page_config(layout="wide", page_title="Economic Indices Overview")
st.title("📊 Economic Indices Dashboard")

st.markdown("Select an index below to explore its detailed trends and analysis.")

# Index info: filename, neon-style color, and mock trend data
indices = {
    "Consumer Demand Index (CDI)": (
        "1_CDI_Dashboard", "#00FFF7", [1.0, 0.2, 0.74, 1.6, 1.8]  # mild upward
    ),
    "EV Market Adoption Rate": (
        "2_EV_Market_Adoption_Rate", "#FF00D4", [2.5, 2.0, 1.1, 0.9, 1.7]  # gradual decline
    ),
    "Housing Affordability Stress Index": (
        "3_Housing_Affordability_Stress_Index", "#39FF14", [1.5, 1.3, 1.1, 1.4, 1.7]  # bounce back
    ),
    "Renewable Transition Readiness Score": (
        "4_Renewable_Transition_Readiness_Score", "#FFD700", [1.2, 1.8, 1.1, 1.9, 1.5]  # volatile
    ),
    "Infrastructure Activity Index (IAI)": (
        "5_Infrastructure_Activity_Index_(IAI)", "#FF3131", [1.0, 1.5, 1.2, 1.8, 2.5]  # strong growth
    ),
    "IMP Index": (
        "6_IMP_Index", "#8A2BE2", [2.0, 2.5, 1.8, 2.8, 2.3]  # dip and rise
    ),
}

# Create columns and render each index card
cols = st.columns(3)
for i, (name, (page, color, trend)) in enumerate(indices.items()):
    with cols[i % 3]:
        st.subheader(name)

        # Neon-style mini line chart with bold outline + hollow circle markers
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            y=trend,
            mode="lines+markers",
            line=dict(color=color, width=4),
            marker=dict(
                size=8,
                color=color,
                line=dict(width=2, color=color),
                symbol="circle-open"
            )
        ))
        fig.update_layout(
            height=150,
            margin=dict(l=10, r=10, t=10, b=10),
            xaxis=dict(visible=False),
            yaxis=dict(visible=False),
            plot_bgcolor="rgba(0,0,0,0)",
            paper_bgcolor="rgba(0,0,0,0)",
        )
        st.plotly_chart(fig, use_container_width=True, key=f"chart-{i}")

        # Colored caption text
        overview_text = f"<p style='color:{color}; margin-bottom: 0.5rem;'>An overview of recent trends in {name.split('(')[0].strip()}</p>"
        st.markdown(overview_text, unsafe_allow_html=True)

        # Default Streamlit button (to avoid loading issues)
        if st.button("Open detailed view of the index →", key=f"button-{i}"):
            st.switch_page(f"pages/{page}.py")