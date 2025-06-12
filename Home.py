import streamlit as st
import plotly.graph_objects as go

# Set dark theme layout and page title
st.set_page_config(layout="wide", page_title="Economic Indices Overview")
st.title("📊 Economic Indices Dashboard")

st.markdown("*Select an index below to explore its detailed trends and analysis.*")

# Index info: filename, neon-style color, mock trend data, icon, and new overview text
indices = {
    "Consumer Demand Index (CDI)": (
        "1_CDI_Dashboard", "#00FFF7", [1.0, 0.2, 0.74, 1.6, 1.8], "🛍️",
        "The Consumer Demand Index captures shifts in real-time consumer activity, helping forecast economic momentum through trends in spending, mobility, and energy use."
    ),
    "EV Market Adoption Rate": (
        "2_EV_Market_Adoption_Rate", "#FF00D4", [2.5, 2.0, 1.1, 0.9, 1.7], "🚗",
        "The EV Market Adoption Rate tracks how quickly India is transitioning to electric vehicles, revealing the impact of crude prices, government policies, and market trends on EV uptake."
    ),
    "Housing Affordability Stress Index": (
        "3_Housing_Affordability_Stress_Index", "#39FF14", [1.5, 1.3, 1.1, 1.4, 1.7], "🏠",
        "The Housing Affordability Stress Index measures how financially stretched urban households are in buying homes, combining income, loan limits, and property prices to guide policy and planning."
    ),
    "Renewable Transition Readiness Score": (
        "4_Renewable_Transition_Readiness_Score", "#FFD700", [1.2, 1.8, 1.1, 1.9, 1.5], "🌱",
        "The Renewable Transition Readiness Score measures how prepared India is to shift from fossil fuels to clean energy, reflecting progress in capacity and investment to support a sustainable future."
    ),
    "Infrastructure Activity Index (IAI)": (
        "5_Infrastructure_Activity_Index_(IAI)", "#FF3131", [1.0, 1.5, 1.2, 1.8, 2.5], "🏢",
        "The Infrastructure Activity Index tracks and forecasts the pace of India’s infrastructure development by combining key construction and investment trends to inform industry and policy decisions."
    ),
    "IMP Index": (
        "6_IMP_Index", "#8A2BE2", [2.0, 2.5, 1.8, 2.8, 2.3], "💰",
        "India’s Macroeconomic Performance (IMP) Index provides a comprehensive snapshot of the nation’s economic health by combining inflation, employment, credit, and industrial output into one robust indicator."
    ),
}

# Create columns and render each index card with 2 per row
cols = st.columns(2)
for i, (name, (page, color, trend, icon, overview)) in enumerate(indices.items()):
    with cols[i % 2]:
        st.subheader(f"{icon} {name}")

        # Neon-style mini line chart
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

        # Updated: Italic + colored overview text
        overview_text = f"<p style='color:{color}; margin-bottom: 0.5rem;'><em>{overview}</em></p>"
        st.markdown(overview_text, unsafe_allow_html=True)

        if st.button("Open detailed view of the index →", key=f"button-{i}"):
            st.switch_page(f"pages/{page}.py")