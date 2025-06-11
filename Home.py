import streamlit as st
import plotly.graph_objects as go

st.set_page_config(layout="wide", page_title="Economic Indices Overview")
st.title("📊 Economic Indices Dashboard")
st.markdown("Select an index below to explore its detailed trends and analysis.")

# Index data
indices = {
    "Consumer Demand Index (CDI)": ("1_CDI_Dashboard", "#00FFD1", [1.0, 0.2, 0.74, 1.6, 1.8]),
    "EV Market Adoption Rate": ("2_EV_Market_Adoption_Rate", "#FF5C00", [2.5, 2.0, 1.1, 0.9, 1.7]),
    "Housing Affordability Stress Index": ("3_Housing_Affordability_Stress_Index", "#00A6A6", [1.5, 1.3, 1.1, 1.4, 1.7]),
    "Renewable Transition Readiness Score": ("4_Renewable_Transition_Readiness_Score", "#7DF9FF", [1.2, 1.8, 1.1, 1.9, 1.5]),
    "Infrastructure Activity Index (IAI)": ("5_Infrastructure_Activity_Index_(IAI)", "#66FF66", [1.0, 1.5, 1.2, 1.8, 2.5]),
    "IMP Index": ("6_IMP_Index", "#FF44CC", [2.0, 2.5, 1.8, 2.8, 2.3]),
}

# Layout: 3 columns per row
cols = st.columns(3)

for i, (name, (page, color, trend)) in enumerate(indices.items()):
    with cols[i % 3]:
        with st.container():
            # Create a box using markdown with native Streamlit padding
            st.markdown(
                f"""
                <div style="border:2px solid {color}; border-radius:12px; padding: 1.5rem; margin-bottom: 1.5rem;">
                """,
                unsafe_allow_html=True,
            )

            # Title
            st.markdown(f"<h5 style='color:white'>{name}</h5>", unsafe_allow_html=True)

            # Chart
            fig = go.Figure()
            fig.add_trace(go.Scatter(
                y=trend,
                mode="lines",
                line=dict(color=color, width=4),
            ))
            fig.update_layout(
                height=150,
                margin=dict(l=10, r=10, t=10, b=10),
                xaxis=dict(visible=False),
                yaxis=dict(visible=False),
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0)',
            )
            st.plotly_chart(fig, use_container_width=True)

            # Overview
            st.markdown(f"<p style='color:{color}'>An overview of recent trends in {name.split('(')[0].strip()}</p>", unsafe_allow_html=True)

            # Button
            if st.button("Open detailed view of the index →", key=f"btn-{i}"):
                st.switch_page(f"pages/{page}.py")

            st.markdown("</div>", unsafe_allow_html=True)