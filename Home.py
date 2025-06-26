import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import streamlit.components.v1 as components
from sklearn.decomposition import PCA
from sklearn.preprocessing import StandardScaler

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

# ========== FUNCTIONS TO LOAD VALUES ==========
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

def get_latest_ev_value():
    try:
        df = pd.read_csv("data/EV_Market_Adoption.csv")
        df.columns = df.columns.str.strip()
        df['Date'] = pd.to_datetime(df['Date'], errors='coerce')
        df = df.dropna(subset=['Date', 'Adoption Rate'])
        df = df.sort_values('Date')
        latest_value = df.iloc[-1]['Adoption Rate']
        return latest_value
    except Exception as e:
        st.error(f"Error loading EV data: {e}")
        return 0.0

# ========== GET LATEST VALUES ==========
latest_cdi_real, latest_cdi_scaled = get_latest_cdi_values()
latest_imp_real, latest_imp_scaled = get_latest_imp_values()
latest_ev_real = get_latest_ev_value()

# ========== INDEX METADATA ==========
indices = {
    "Consumer Demand Index (CDI)": (
        "1_CDI_Dashboard", "#00FFF7", [latest_cdi_real], "\U0001F6CD",
        "Captures shifts in real-time consumer activity based on digital transactions and utilities."
    ),
    "EV Market Adoption Rate": (
        "2_EV_Market_Adoption_Rate", "#FF00D4", [latest_ev_real], "\U0001F697",
        "Tracks how quickly India is transitioning to EVs based on adoption rates."
    ),
    "Housing Affordability Stress Index": (
        "3_Housing_Affordability_Stress_Index", "#39FF14", [1.5], "\U0001F3E0",
        "Measures how financially stretched households are in buying homes."
    ),
    "Renewable Transition Readiness Score": (
        "4_Renewable_Transition_Readiness_Score", "#FFD700", [1.2], "\U0001F331",
        "Evaluates India's preparedness to shift from fossil fuels to clean energy."
    ),
    "Infrastructure Activity Index (IAI)": (
        "5_Infrastructure_Activity_Index_(IAI)", "#FF3131", [1.0], "\U0001F3E2",
        "Tracks and forecasts the pace of infrastructure development."
    ),
    "IMP Index": (
        "6_IMP_Index", "#8A2BE2", [latest_imp_real], "\U0001F4B0",
        "Measures India's overall macroeconomic performance."
    ),
}

# ========== CHART WRAPPER ==========
def wrapped_chart(title, fig, overview, color, page_key):
    chart_html = fig.to_html(include_plotlyjs="cdn", full_html=False)
    components.html(f"""
    <div style="
        background-color: #1e1e1e;
        padding: 1rem;
        border-radius: 12px;
        margin-bottom: 1.5rem;
        box-shadow: 0 0 10px rgba(255, 255, 255, 0.1);
    ">
        <h4 style="color: {color}; margin-bottom: 0.75rem;">{title}</h4>
        {chart_html}
        <p style='color: {color}; margin-top: 1rem; font-style: italic;'>{overview}</p>
        <a href="./{page_key}" style="color: #00f0ff; text-decoration: none; font-weight: bold;">Explore full index →</a>
    </div>
    """, height=400)

# ========== SCALE BAR OR GAUGE ==========
def render_chart(name, value_list):
    val = value_list[-1]
    if name == "EV Market Adoption Rate":
        return go.Figure(go.Indicator(
            mode="gauge+number",
            value=val,
            gauge={
                'axis': {'range': [0, 10]},
                'bar': {'color': "#FF00D4"},
            },
            number={'suffix': "%"}
        ))
    else:
        scaled_val = max(min(round(val), 5), -5)
        fig = go.Figure()
        for v in range(-5, 6):
            fill_color, label = color_map[v]
            fig.add_shape(type="rect", x0=v - 0.5, x1=v + 0.5, y0=-0.3, y1=0.3,
                          line=dict(color="black", width=1), fillcolor=fill_color, layer="below")
            fig.add_trace(go.Scatter(x=[v], y=[0], mode='text', text=[str(v)],
                                     hovertext=[f"{label} ({v})"], showlegend=False,
                                     textfont=dict(color='white', size=14)))

        fig.add_shape(type="rect", x0=scaled_val - 0.5, x1=scaled_val + 0.5,
                      y0=-0.35, y1=0.35, line=dict(color="crimson", width=3, dash="dot"),
                      fillcolor="rgba(0,0,0,0)", layer="above")

        fig.add_trace(go.Scatter(x=[scaled_val], y=[0.45], mode='text',
                                 text=[f"{val:.2f}"], showlegend=False,
                                 textfont=dict(size=14, color='crimson')))

        fig.update_layout(
            xaxis=dict(range=[-5.5, 5.5], showticklabels=False, showgrid=False),
            yaxis=dict(visible=False),
            height=200, margin=dict(l=10, r=10, t=10, b=10),
            plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)", showlegend=False
        )
        return fig

# ========== DISPLAY ALL WRAPPED INDEX CARDS ==========
col_left, col_right = st.columns(2)
index_items = list(indices.items())

for i, (name, (page_key, color, val_list, icon, overview)) in enumerate(index_items):
    fig = render_chart(name, val_list)
    col = col_left if i % 2 == 0 else col_right
    with col:
        wrapped_chart(f"{icon} {name}", fig, overview, color, f"pages/{page_key}.py")