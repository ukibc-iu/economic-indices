import streamlit as st
import pandas as pd
from sklearn.decomposition import PCA
from sklearn.preprocessing import StandardScaler
import plotly.graph_objects as go

# ========== PAGE CONFIG ==========
st.set_page_config(layout="wide", page_title="Economic Indices Overview")
st.title("\U0001F4CA Economic Indices Dashboard")
st.markdown("*Select an index below to explore its detailed trends and analysis.*")

# ========== COLOR MAP ==========
color_map = {
    -5: ("#800000", "Extremely Low"), -4: ("#bd0026", "Severely Low"),
    -3: ("#e31a1c", "Very Low"), -2: ("#fc4e2a", "Low"),
    -1: ("#fd8d3c", "Slightly Low"), 0: ("#fecc5c", "Neutral"),
    1: ("#c2e699", "Slightly High"), 2: ("#78c679", "High"),
    3: ("#31a354", "Very High"), 4: ("#006837", "Severely High"),
    5: ("#004529", "Extremely High")
}

# ========== CDI VALUE ==========
def get_latest_cdi_values():
    try:
        df = pd.read_csv("data/Consumer_Demand_Index.csv")
        df.columns = df.columns.str.strip()
        df['Date'] = pd.to_datetime(df['Date'], errors='coerce')
        df = df.dropna(subset=['Date'])

        features = ['UPI Transactions', 'GST Revenue', 'Vehicle Sales', 'Housing Sales', 'Power Consumption']
        df = df.dropna(subset=features)

        scaler = StandardScaler()
        scaled = scaler.fit_transform(df[features])
        pca = PCA(n_components=1)
        components = pca.fit_transform(scaled)

        df['CDI_Real'] = components[:, 0]
        df['CDI_Scaled'] = df['CDI_Real'].clip(-5, 5)

        latest_row = df.sort_values('Date').iloc[-1]
        return latest_row['CDI_Real'], latest_row['CDI_Scaled']
    except Exception as e:
        st.error(f"Error loading CDI: {e}")
        return 0.0, 0.0

# ========== IMP INDEX VALUE ==========
def get_latest_imp_values():
    try:
        df = pd.read_csv("data/IMP_Index.csv")
        df.columns = df.columns.str.strip()
        df['Date'] = pd.to_datetime(df['Date'], format='%b-%y', errors='coerce')
        df = df.dropna(subset=['Date', 'Scale'])

        df = df.sort_values('Date')
        latest_row = df.iloc[-1]

        latest_real = latest_row['Scale']
        latest_scaled = max(min(round(latest_real), 5), -5)

        return latest_real, latest_scaled
    except Exception as e:
        st.error(f"Error loading IMP Index: {e}")
        return 0.0, 0.0

# ========== GET LATEST VALUES ==========
latest_cdi_real, latest_cdi_scaled = get_latest_cdi_values()
latest_imp_real, latest_imp_scaled = get_latest_imp_values()

# ========== INDEX DATA ==========
indices = {
    "Consumer Demand Index (CDI)": (
        "1_CDI_Dashboard", "#00FFF7", [latest_cdi_real], "\U0001F6CD️",
        "The Consumer Demand Index captures shifts in real-time consumer activity..."
    ),
    "EV Market Adoption Rate": (
        "2_EV_Market_Adoption_Rate", "#FF00D4", [1.7], "\U0001F697",
        "The EV Market Adoption Rate tracks how quickly India is transitioning..."
    ),
    "Housing Affordability Stress Index": (
        "3_Housing_Affordability_Stress_Index", "#39FF14", [1.5], "\U0001F3E0",
        "This index measures how financially stretched households are in buying homes..."
    ),
    "Renewable Transition Readiness Score": (
        "4_Renewable_Transition_Readiness_Score", "#FFD700", [1.2], "\U0001F331",
        "Measures how prepared India is to shift from fossil fuels to clean energy..."
    ),
    "Infrastructure Activity Index (IAI)": (
        "5_Infrastructure_Activity_Index_(IAI)", "#FF3131", [1.0], "\U0001F3E2",
        "Tracks and forecasts the pace of infrastructure development..."
    ),
    "IMP Index": (
        "6_IMP_Index", "#8A2BE2", [latest_imp_real], "\U0001F4B0",
        "India’s Macroeconomic Performance (IMP) Index measures India's overall economic well-being..."
    ),
}

# ========== RENDER CARD FUNCTION ==========
def render_card(name, data, key):
    page, color, trend, icon, overview = data
    latest_real = trend[-1]

    scale_min, scale_max = (-3, 3) if name == "IMP Index" else (-5, 5)
    latest_scaled = max(min(round(latest_real), scale_max), scale_min)

    with st.container():
        st.markdown(f"""
        <div style='border: 1px solid #ccc; border-radius: 12px; padding: 20px; margin-bottom: 20px; background-color: #f9f9f9;'>
            <h4 style='margin-top:0'>{icon} {name}</h4>
        """, unsafe_allow_html=True)

        fig = go.Figure()
        for val in range(scale_min, scale_max + 1):
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
            xaxis=dict(range=[scale_min - 0.5, scale_max + 0.5], showticklabels=False, showgrid=False),
            yaxis=dict(visible=False),
            height=160, margin=dict(l=10, r=10, t=10, b=10),
            plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)", showlegend=False
        )
        st.plotly_chart(fig, use_container_width=True, key=f"scale-{key}")

        st.markdown(f"<p style='color:{color}; margin-bottom: 0.5rem;'><em>{overview}</em></p>", unsafe_allow_html=True)

        if st.button("Open detailed view →", key=f"btn-{key}"):
            st.switch_page(f"pages/{page}.py")

        st.markdown("</div>", unsafe_allow_html=True)

# ========== GRID RENDERING ==========
rows = list(zip(*(iter(indices.items()),) * 3))  # group in threes for 2 rows of 3 columns
for row in rows:
    cols = st.columns(3)
    for col, (name, data) in zip(cols, row):
        with col:
            render_card(name, data, name)

# If odd number, render remaining last
remaining = len(indices) % 3
if remaining:
    cols = st.columns(remaining)
    for col, (name, data) in zip(cols, list(indices.items())[-remaining:]):
        with col:
            render_card(name, data, name)