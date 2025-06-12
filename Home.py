import streamlit as st
import plotly.graph_objects as go

st.set_page_config(layout="wide", page_title="Economic Indices Overview")
st.title("📊 Economic Indices Dashboard")
st.markdown("*Select an index below to explore its detailed trends and analysis.*")

# Inject CSS for center dividing line
st.markdown("""
    <style>
    .reportview-container .main .block-container {
        display: flex;
        flex-direction: row;
        gap: 3rem;
    }
    .divider-column {
        border-left: 2px solid #888;
        padding-left: 1.5rem;
    }
    .card-box {
        background-color: #111111;
        border: 1px solid #444444;
        padding: 1.2rem;
        border-radius: 10px;
        margin-bottom: 2rem;
    }
    </style>
""", unsafe_allow_html=True)

# Color map for the scale bars
color_map = {
    -5: ("#800000", "Extremely Low"), -4: ("#bd0026", "Severely Low"),
    -3: ("#e31a1c", "Very Low"), -2: ("#fc4e2a", "Low"),
    -1: ("#fd8d3c", "Slightly Low"), 0: ("#fecc5c", "Neutral"),
    1: ("#c2e699", "Slightly High"), 2: ("#78c679", "High"),
    3: ("#31a354", "Very High"), 4: ("#006837", "Severely High"),
    5: ("#004529", "Extremely High")
}

# Index info
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
        "India’s Macroeconomic Performance (IMP) Index measures India's overall economic well-being, taking into consideration significant economic parameters such as inflation rate, unemployment rate, etc."
    ),
}

# Render two columns: second one gets the divider style
left_col, right_col = st.columns([1, 1])
col_refs = [left_col, right_col]

for i, (name, (page, color, trend, icon, overview)) in enumerate(indices.items()):
    col = col_refs[i % 2]

    # Add class for right column to enable divider
    with col:
        container_style = "class='card-box'"
        st.markdown(f"<div {container_style}>", unsafe_allow_html=True)

        st.subheader(f"{icon} {name}")

        # === Scale bar ===
        latest_real = trend[-1]
        latest_scaled = max(min(round(latest_real), 5), -5)

        fig = go.Figure()
        for val in range(-5, 6):
            fill_color, label = color_map[val]
            fig.add_shape(type="rect", x0=val - 0.5, x1=val + 0.5, y0=-0.3, y1=0.3,
                          line=dict(color="black", width=1), fillcolor=fill_color, layer="below")
            fig.add_trace(go.Scatter(x=[val], y=[0], mode='text', text=[str(val)],
                                     hovertext=[f"{label} ({val})"], showlegend=False,
                                     textfont=dict(color='white', size=14)))

        fig.add_shape(type="rect", x0=latest_scaled - 0.5, x1=latest_scaled + 0.5,
                      y0=-0.35, y1=0.35, line=dict(color="crimson", width=3, dash="dot"),
                      fillcolor="rgba(0,0,0,0)", layer="above")

        fig.add_trace(go.Scatter(x=[latest_scaled], y=[0.45], mode='text',
                                 text=[f"{latest_real:.2f}"], showlegend=False,
                                 textfont=dict(size=14, color='crimson')))

        fig.update_layout(
            xaxis=dict(range=[-5.5, 5.5], title='Scale (-5 to +5)',
                       showticklabels=False, showgrid=False),
            yaxis=dict(visible=False),
            height=200, margin=dict(l=10, r=10, t=10, b=10),
            plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)", showlegend=False
        )

        st.plotly_chart(fig, use_container_width=True, key=f"scale-{i}")

        # Overview paragraph
        st.markdown(f"<p style='color:{color};'><em>{overview}</em></p>", unsafe_allow_html=True)

        # Navigation button
        if st.button("Open detailed view of the index →", key=f"button-{i}"):
            st.switch_page(f"pages/{page}.py")

        st.markdown("</div>", unsafe_allow_html=True)