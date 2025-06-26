import streamlit as st
import plotly.graph_objects as go
from itertools import islice

# Configure page
st.set_page_config(page_title="ESG India Index", layout="wide")

# Inject custom CSS
st.markdown("""
<style>
.card-box {
    background-color: #1e1e1e;
    border-radius: 20px;
    padding: 1.2rem;
    margin-bottom: 1.5rem;
    box-shadow: 0 4px 15px rgba(0,0,0,0.2);
    color: white;
    height: 400px;
    display: flex;
    flex-direction: column;
    justify-content: space-between;
}
.card-box h3 {
    margin: 0 0 0.5rem 0;
    font-size: 1.2rem;
    color: #00FFFF;
}
.card-box p {
    font-size: 0.92rem;
    line-height: 1.4;
}
.card-box button {
    margin-top: auto;
}
</style>
""", unsafe_allow_html=True)

# Define color scale map for the mini-graph
color_map = {
    -5: ("#5c0216", "Very Poor"),
    -4: ("#7a061c", "Poor"),
    -3: ("#8f1a21", "Weak"),
    -2: ("#ab332d", "Below Avg"),
    -1: ("#d6553b", "Slightly Below Avg"),
     0: ("#e8b449", "Neutral"),
     1: ("#b4bf38", "Slightly Above Avg"),
     2: ("#8dbf2d", "Above Avg"),
     3: ("#3aa539", "Good"),
     4: ("#1a9e2f", "Very Good"),
     5: ("#007e2f", "Excellent"),
}

# Dummy index data for demonstration
indices = {
    "EV Adoption Rate": ["ev_adoption", "#1f77b4", [1.5, 2.3, 2.8, 3.6, 4.5, 5.0], "⚡", "EVs are increasingly adopted across India, reflecting strong policy push."],
    "Carbon Intensity": ["carbon_intensity", "#ff7f0e", [-2.1, -2.3, -1.9, -1.5, -1.1, -0.8], "🌿", "Declining carbon intensity signals cleaner energy mix."],
    "Green Energy Use": ["green_energy", "#2ca02c", [1.0, 1.5, 1.8, 2.1, 2.4, 2.7], "🔋", "Renewables are growing steadily in national grid usage."],
    "Water Stress Index": ["water_stress", "#d62728", [-3.0, -3.1, -3.3, -3.5, -3.7, -3.9], "💧", "Rising water stress requires urgent mitigation efforts."],
    "Waste Recycling Rate": ["recycling_rate", "#9467bd", [0.5, 0.7, 1.1, 1.3, 1.8, 2.0], "♻️", "Improved recycling rates hint at better waste handling."],
    "Public Transit Share": ["transit_share", "#8c564b", [0.2, 0.5, 0.7, 1.0, 1.4, 1.9], "🚆", "Urban mobility is shifting toward sustainable public transit."],
}

# Function to render a single card
def render_card(col, name, data, key):
    page, color, trend, icon, overview = data
    latest_real = trend[-1]
    scaled = max(min(round(latest_real), 5), -5)

    # Build mini scale bar chart
    fig = go.Figure()
    for val in range(-5, 6):
        fill_color, _ = color_map[val]
        fig.add_shape(
            type="rect", x0=val - 0.5, x1=val + 0.5, y0=0, y1=1,
            line=dict(color="black", width=1),
            fillcolor=fill_color, layer="below"
        )
    fig.add_shape(
        type="rect", x0=scaled - 0.5, x1=scaled + 0.5, y0=0, y1=1,
        line=dict(color="crimson", width=3, dash="dot"),
        fillcolor="rgba(0,0,0,0)", layer="above"
    )
    fig.add_trace(go.Scatter(
        x=[scaled], y=[1.1], mode='text',
        text=[f"{latest_real:.2f}"],
        textfont=dict(size=13, color="crimson"),
        showlegend=False
    ))
    fig.update_layout(
        xaxis=dict(range=[-5.5, 5.5], visible=False),
        yaxis=dict(visible=False),
        margin=dict(l=0, r=0, t=0, b=0),
        height=100,
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)'
    )
    mini_graph_html = fig.to_html(full_html=False, include_plotlyjs="cdn")

    # Render card in column
    with col:
        st.markdown(f"""
        <div class="card-box">
            <h3>{icon} {name}</h3>
            {mini_graph_html}
            <p style="color:{color};">{overview}</p>
            <form action="/{page}" method="get">
                <button type="submit" style="background-color:#444; color:white; border:none; padding:0.5rem 1rem; border-radius:8px; cursor:pointer;">Open detailed view →</button>
            </form>
        </div>
        """, unsafe_allow_html=True)

# Render in 2 rows of 3 columns
index_list = list(indices.items())
for row in range(2):
    cols = st.columns(3)
    for i, (name, data) in enumerate(islice(index_list, row * 3, (row + 1) * 3)):
        render_card(cols[i], name, data, f"{row}-{i}")