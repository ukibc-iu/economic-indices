import streamlit as st
import pandas as pd
from sklearn.decomposition import PCA
from sklearn.preprocessing import StandardScaler
import plotly.graph_objects as go
from streamlit.components.v1 import html

st.set_page_config(layout="wide", page_title="Economic Indices Overview")
st.title("📊 Economic Indices Dashboard")
st.markdown("*Select an index below to explore its detailed trends and analysis.*")

color_map = {
    -5: ("#800000", "Extremely Low"), -4: ("#bd0026", "Severely Low"),
    -3: ("#e31a1c", "Very Low"), -2: ("#fc4e2a", "Low"),
    -1: ("#fd8d3c", "Slightly Low"), 0: ("#fecc5c", "Neutral"),
    1: ("#c2e699", "Slightly High"), 2: ("#78c679", "High"),
    3: ("#31a354", "Very High"), 4: ("#006837", "Severely High"),
    5: ("#004529", "Extremely High")
}

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

latest_cdi_real, latest_cdi_scaled = get_latest_cdi_values()
latest_imp_real, latest_imp_scaled = get_latest_imp_values()

indices = {
    "Consumer Demand Index (CDI)": (
        "1_CDI_Dashboard", "#00FFF7", [latest_cdi_real], "🍭",
        "The Consumer Demand Index captures shifts in real-time consumer activity..."
    ),
    "EV Market Adoption Rate": (
        "2_EV_Market_Adoption_Rate", "#FF00D4", [1.7], "🚗",
        "The EV Market Adoption Rate tracks how quickly India is transitioning..."
    ),
    "Housing Affordability Stress Index": (
        "3_Housing_Affordability_Stress_Index", "#39FF14", [1.5], "🏠",
        "This index measures how financially stretched households are in buying homes..."
    ),
    "Renewable Transition Readiness Score": (
        "4_Renewable_Transition_Readiness_Score", "#FFD700", [1.2], "🌱",
        "Measures how prepared India is to shift from fossil fuels to clean energy..."
    ),
    "Infrastructure Activity Index (IAI)": (
        "5_Infrastructure_Activity_Index_(IAI)", "#FF3131", [1.0], "🏢",
        "Tracks and forecasts the pace of infrastructure development..."
    ),
    "IMP Index": (
        "6_IMP_Index", "#8A2BE2", [latest_imp_real], "💰",
        "India’s Macroeconomic Performance (IMP) Index measures India's overall economic well-being..."
    ),
}

def wrapped_card(title, icon, fig, overview_html, button_key, page_link, color="#1e1e1e", height=420):
    chart_html = fig.to_html(include_plotlyjs="cdn", full_html=False)
    html(f"""
    <div style="
        background-color: #1e1e1e;
        padding: 1.2rem;
        border-radius: 16px;
        box-shadow: 0 2px 10px rgba(0,0,0,0.25);
        margin-bottom: 20px;
    ">
        <h4 style="color: white; margin-bottom: 1rem;">{icon} {title}</h4>
        {chart_html}
        <p style="color: {color}; font-style: italic; margin-top: 1rem; font-size: 0.95rem;">{overview_html}</p>
        <form action="{page_link}">
            <button style="
                margin-top: 0.8rem;
                padding: 0.5rem 1rem;
                border: none;
                background-color: #444;
                color: white;
                border-radius: 8px;
                cursor: pointer;
            " type="submit">Open detailed view of the index →</button>
        </form>
    </div>
    """, height=height)

def render_index(col, name, data, key):
    page, color, trend, icon, overview = data
    latest_real = trend[-1]

    if name == "EV Market Adoption Rate":
        fig = go.Figure(go.Indicator(
            mode="gauge+number",
            value=latest_real,
            number={'suffix': "%", "font": {"color": color}},
            gauge={
                'axis': {'range': [0, 100]},
                'bar': {'color': color},
                'steps': [
                    {'range': [0, 20], 'color': "#ffe6f0"},
                    {'range': [20, 40], 'color': "#ffb3d9"},
                    {'range': [40, 60], 'color': "#ff66b3"},
                    {'range': [60, 80], 'color': "#ff1a8c"},
                    {'range': [80, 100], 'color': "#e60073"},
                ],
            },
            domain={'x': [0, 1], 'y': [0, 1]},
            title={'text': "EV Adoption Rate", 'font': {"size": 14}}
        ))
        fig.update_layout(margin=dict(l=10, r=10, t=40, b=10), height=220, paper_bgcolor="rgba(0,0,0,0)")
    else:
        scale_min, scale_max = -5, 5
        scaled = max(min(round(latest_real), scale_max), scale_min)
        fig = go.Figure()
        for val in range(scale_min, scale_max + 1):
            fill_color, label = color_map[val]
            fig.add_shape(type="rect", x0=val - 0.5, x1=val + 0.5, y0=-0.3, y1=0.3,
                          line=dict(color="black", width=1), fillcolor=fill_color, layer="below")
            fig.add_trace(go.Scatter(x=[val], y=[0], mode='text', text=[str(val)],
                                     hovertext=[f"{label} ({val})"], showlegend=False,
                                     textfont=dict(color='white', size=14)))
        fig.add_shape(type="rect", x0=scaled - 0.5, x1=scaled + 0.5,
                      y0=-0.35, y1=0.35, line=dict(color="crimson", width=3, dash="dot"),
                      fillcolor="rgba(0,0,0,0)", layer="above")
        fig.add_trace(go.Scatter(x=[scaled], y=[0.45], mode='text',
                                 text=[f"{latest_real:.2f}"], showlegend=False,
                                 textfont=dict(size=14, color='crimson')))
        fig.update_layout(
            xaxis=dict(range=[scale_min - 0.5, scale_max + 0.5], showticklabels=False, showgrid=False),
            yaxis=dict(visible=False),
            height=200, margin=dict(l=10, r=10, t=10, b=10),
            plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)", showlegend=False
        )

    with col:
        wrapped_card(title=name, icon=icon, fig=fig, overview_html=overview, button_key=f"btn-{key}", page_link=f"/{page}.py", color=color)

index_items = list(indices.items())
for i in range(0, len(index_items), 2):
    cols = st.columns(2)
    for j in range(2):
        if i + j < len(index_items):
            name, data = index_items[i + j]
            render_index(cols[j], name, data, f"{i+j}")