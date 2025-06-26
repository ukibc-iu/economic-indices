import streamlit as st
import pandas as pd
from sklearn.decomposition import PCA
from sklearn.preprocessing import StandardScaler
import plotly.graph_objects as go

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

# ========== EV ADOPTION RATE VALUE ==========
def get_latest_ev_adoption_value():
    try:
        df = pd.read_csv("data/EV_Adoption.csv")
        df.columns = df.columns.str.strip()
        df['Date'] = pd.to_datetime(df['Date'], errors='coerce')
        df = df.dropna(subset=['Date'])

        ev_cols = ['EV Four-wheeler Sales', 'EV Two-wheeler Sales', 'EV Three-wheeler Sales']
        total_sales_col = 'Total Vehicle Sales'

        for col in ev_cols + [total_sales_col]:
            df[col] = pd.to_numeric(df[col].astype(str).str.replace(',', ''), errors='coerce')

        df['EV Total Sales'] = df[ev_cols].sum(axis=1)
        df['EV Adoption Rate'] = df['EV Total Sales'] / df[total_sales_col]

        latest_row = df.sort_values('Date').iloc[-1]
        latest_rate = latest_row['EV Adoption Rate'] * 100  # %
        return latest_rate
    except Exception as e:
        st.error(f"Error loading EV data: {e}")
        return 0.0

# ========== GET LATEST VALUES ==========
latest_cdi_real, _ = get_latest_cdi_values()
latest_imp_real, _ = get_latest_imp_values()
latest_ev_rate = get_latest_ev_adoption_value()

# ========== INDEX DATA ==========
indices = {
    "Consumer Demand Index (CDI)": (
        "1_CDI_Dashboard", "#00FFF7", [latest_cdi_real], "🛍️",
        "The Consumer Demand Index captures shifts in real-time consumer activity..."
    ),
    "EV Market Adoption Rate": (
        "2_EV_Market_Adoption_Rate", "#FF00D4", [latest_ev_rate], "🚗",
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

# ========== LAYOUT COLUMNS ==========
col1, col_mid, col2 = st.columns([1, 0.02, 1])
with col_mid:
    st.markdown("""<div style="height: 1000px; width: 1px; background-color: lightgray; margin: auto;"></div>""",
                unsafe_allow_html=True)

# ========== RENDER INDEX ==========
def render_index(col, name, data, key):
    page, color, trend, icon, overview = data
    latest_real = trend[-1]
    with col:
        st.subheader(f"{icon} {name}")

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
            fig.update_layout(
                margin=dict(l=10, r=10, t=40, b=10),
                height=220,
                paper_bgcolor="rgba(0,0,0,0)"
            )
            st.plotly_chart(fig, use_container_width=True, key=f"gauge-{key}")
        else:
            # Horizontal scale bar
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
            st.plotly_chart(fig, use_container_width=True, key=f"scale-{key}")

        st.markdown(f"<p style='color:{color}; margin-bottom: 0.5rem;'><em>{overview}</em></p>", unsafe_allow_html=True)
        if st.button("Open detailed view of the index →", key=f"btn-{key}"):
            st.switch_page(f"pages/{page}.py")

# ========== DISPLAY ALL INDEX CARDS ==========
index_items = list(indices.items())
mid = len(index_items) // 2
for i, (name, data) in enumerate(index_items[:mid]):
    render_index(col1, name, data, f"left-{i}")
for i, (name, data) in enumerate(index_items[mid:]):
    render_index(col2, name, data, f"right-{i}")