import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from sklearn.decomposition import PCA
from sklearn.preprocessing import StandardScaler
import os
import streamlit.components.v1 as components

# ========== PAGE CONFIG ==========
st.set_page_config(layout="wide", page_title="Economic Indices Overview")
st.title("📊 Economic Indices Dashboard")
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

# ========== UTILITY ==========
def wrapped_chart(title, fig, overview, btn_key, page):
    chart_html = fig.to_html(include_plotlyjs="cdn", full_html=False)
    components.html(f"""
        <div style="
            background-color: #1e1e1e;
            padding: 1rem;
            border-radius: 12px;
            margin: 0.5rem;
            border: 1px solid #444444;
        ">
            <h4 style="color: white;">{title}</h4>
            {chart_html}
            <p style="color: #cccccc;">{overview}</p>
            <form action="?page={page}" style="margin-top: 0.5rem;">
                <button style="
                    background-color: #333333;
                    color: white;
                    border: none;
                    padding: 0.5rem 1rem;
                    border-radius: 6px;
                    cursor: pointer;
                " type="submit">View full index →</button>
            </form>
        </div>
    """, height=350)

# ========== CDI ==========
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
        components_ = pca.fit_transform(scaled)

        df['CDI_Real'] = components_[:, 0]
        df['CDI_Scaled'] = df['CDI_Real'].clip(-5, 5)

        latest = df.sort_values('Date').iloc[-1]
        return latest['CDI_Real'], latest['CDI_Scaled']
    except Exception as e:
        st.error(f"Error loading CDI: {e}")
        return 0.0, 0.0

# ========== IMP ==========
def get_latest_imp_values():
    try:
        df = pd.read_csv("data/IMP_Index.csv")
        df.columns = df.columns.str.strip()
        df['Date'] = pd.to_datetime(df['Date'], format='%b-%y', errors='coerce')
        df = df.dropna(subset=['Date', 'Scale'])

        df = df.sort_values('Date')
        latest = df.iloc[-1]
        val = latest['Scale']
        return val, max(min(round(val), 5), -5)
    except Exception as e:
        st.error(f"Error loading IMP Index: {e}")
        return 0.0, 0

# ========== EV Adoption Rate ==========
def get_latest_ev_values():
    try:
        reg_df = pd.read_csv("data/EV_Adoption.csv")
        reg_df['Date'] = pd.to_datetime(reg_df['Date'])
        merged = pd.merge(reg_df, veh_df, on='Date', how='inner')
        merged['EV Adoption Rate'] = 100 * merged['EV Registrations'] / merged['Vehicle Sales']
        merged = merged.dropna(subset=['EV Adoption Rate'])
        latest = merged.sort_values('Date').iloc[-1]
        real = latest['EV Adoption Rate']
        scaled = max(min(round((real - 1.5) / 1.0), 5), -5)
        return real, scaled
    except Exception as e:
        st.warning(f"Error loading EV data: {e}")
        return 1.7, 2  # fallback

# ========== MINI GAUGE ==========
def render_mini_gauge(real_val, scaled_val, name, scale_min, scale_max):
    fig = go.Figure()
    for val in range(scale_min, scale_max + 1):
        fill_color, label = color_map[val]
        fig.add_shape(type="rect", x0=val - 0.5, x1=val + 0.5, y0=-0.3, y1=0.3,
                      line=dict(color="black", width=1), fillcolor=fill_color, layer="below")
        fig.add_trace(go.Scatter(x=[val], y=[0], mode='text', text=[str(val)],
                                 hovertext=[f"{label} ({val})"], showlegend=False,
                                 textfont=dict(color='white', size=14)))
    fig.add_shape(type="rect", x0=scaled_val - 0.5, x1=scaled_val + 0.5,
                  y0=-0.35, y1=0.35, line=dict(color="crimson", width=3, dash="dot"),
                  fillcolor="rgba(0,0,0,0)", layer="above")
    fig.add_trace(go.Scatter(x=[scaled_val], y=[0.45], mode='text',
                             text=[f"{real_val:.2f}"], showlegend=False,
                             textfont=dict(size=14, color='crimson')))
    fig.update_layout(
        xaxis=dict(range=[scale_min - 0.5, scale_max + 0.5], showticklabels=False, showgrid=False),
        yaxis=dict(visible=False),
        height=200,
        margin=dict(l=10, r=10, t=10, b=10),
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        showlegend=False
    )
    return fig

# ========== LOAD VALUES ==========
latest_cdi_real, latest_cdi_scaled = get_latest_cdi_values()
latest_imp_real, latest_imp_scaled = get_latest_imp_values()
latest_ev_real, latest_ev_scaled = get_latest_ev_values()

# ========== INDEX DATA ==========
indices = [
    {
        "name": "Consumer Demand Index (CDI)",
        "icon": "🛍️",
        "real": latest_cdi_real,
        "scaled": latest_cdi_scaled,
        "overview": "Captures shifts in real-time consumer activity...",
        "page": "pages/1_CDI_Dashboard.py",
        "range": (-5, 5)
    },
    {
        "name": "EV Market Adoption Rate",
        "icon": "🚗",
        "real": latest_ev_real,
        "scaled": latest_ev_scaled,
        "overview": "Tracks how quickly India is transitioning to EVs...",
        "page": "pages/2_EV_Market_Adoption_Rate.py",
        "range": (-5, 5)
    },
    {
        "name": "Housing Affordability Stress Index",
        "icon": "🏠",
        "real": 1.5,
        "scaled": 2,
        "overview": "Measures how financially stretched households are in buying homes...",
        "page": "pages/3_Housing_Affordability_Stress_Index.py",
        "range": (-5, 5)
    },
    {
        "name": "Renewable Transition Readiness Score",
        "icon": "🌱",
        "real": 1.2,
        "scaled": 1,
        "overview": "How prepared India is to shift from fossil fuels to clean energy...",
        "page": "pages/4_Renewable_Transition_Readiness_Score.py",
        "range": (-5, 5)
    },
    {
        "name": "Infrastructure Activity Index (IAI)",
        "icon": "🏢",
        "real": 1.0,
        "scaled": 1,
        "overview": "Tracks and forecasts the pace of infrastructure development...",
        "page": "pages/5_Infrastructure_Activity_Index_(IAI).py",
        "range": (-5, 5)
    },
    {
        "name": "IMP Index",
        "icon": "💰",
        "real": latest_imp_real,
        "scaled": latest_imp_scaled,
        "overview": "India’s Macroeconomic Performance (IMP) Index...",
        "page": "pages/6_IMP_Index.py",
        "range": (-3, 3)
    }
]

# ========== DISPLAY ==========
left_col, right_col = st.columns(2)
for i, index in enumerate(indices):
    fig = render_mini_gauge(index["real"], index["scaled"], index["name"], *index["range"])
    col = left_col if i % 2 == 0 else right_col
    with col:
        wrapped_chart(f"{index['icon']} {index['name']}", fig, index["overview"], f"btn-{i}", index["page"])