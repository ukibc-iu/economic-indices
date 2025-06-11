import streamlit as st
import plotly.graph_objects as go

st.set_page_config(layout="wide", page_title="Economic Indices Overview")
st.title("📊 Economic Indices Dashboard")

st.markdown("Select an index below to explore its detailed trends and analysis.")

# Index info with color codes
indices = {
    "Consumer Demand Index (CDI)": ("1_CDI_Dashboard", "#62C8CE"),
    "EV Market Adoption Rate": ("2_EV Market Adoption Rate", "#E85412"),
    "Housing Affordability Stress Index": ("3_Housing Affordability Stress Index", "#007381"),
    "Renewable Transition Readiness Score": ("4_Renewable Transition Readiness Score", "#002060"),
    "Infrastructure Activity Index (IAI)": ("5_Infrastructure Activity Index (IAI)", "#4B575F"),
    "IMP Index": ("6_IMP Index", "#60AEB3"),
}

cols = st.columns(3)
for i, (name, (page, color)) in enumerate(indices.items()):
    with cols[i % 3]:
        st.subheader(name)

        # Mini line chart with custom color
        fig = go.Figure()
        fig.add_trace(go.Scatter(y=[1, 2, 1.5, 2.5, 3], mode="lines", line=dict(color=color)))
        fig.update_layout(
            height=150,
            margin=dict(l=10, r=10, t=10, b=10),
            xaxis=dict(visible=False),
            yaxis=dict(visible=False),
        )
        st.plotly_chart(fig, use_container_width=True, key=f"chart-{i}")

        st.caption("An overview of recent trends in " + name.split('(')[0].strip())

        # Stylized button
        button_html = f"""
            <a href="/pages/{page}.py" target="_self">
                <button style='background-color:{color};color:white;padding:0.5rem 1rem;border:none;border-radius:0.5rem;width:100%;margin-top:0.5rem;'>
                    Open detailed view of the index →
                </button>
            </a>
        """
        st.markdown(button_html, unsafe_allow_html=True)