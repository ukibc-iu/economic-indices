import streamlit as st
import pandas as pd
import numpy as np
import os
from sklearn.decomposition import PCA
from sklearn.preprocessing import StandardScaler

# Page Config
st.set_page_config(layout="wide", page_title="Economic Indices Overview")
st.title("📊 Economic Indices Dashboard")
st.markdown("*Track key economic indicators and analyze their month-over-month changes.*")

# Index Configuration
INDEX_CONFIG = {
    "Consumer Demand Index (CDI)": {
        "file": "data/Consumer_Demand_Index.csv",
        "features": ['UPI Transactions', 'GST Revenue', 'Vehicle Sales', 'Housing Sales', 'Power Consumption'],
        "scale": (-5, 5),
        "icon": "🛍️",
        "page": "1_CDI_Dashboard",
        "description": "The Consumer Demand Index captures shifts in real-time consumer activity."
    },
    "EV Market Adoption Rate": {
        "value": 1.7,
        "prev": 1.6,
        "scale": (0, 10),
        "icon": "🚗",
        "page": "2_EV_Market_Adoption_Rate",
        "description": "Tracks how quickly India is transitioning to electric mobility.",
        "month": "Jul-25"
    },
    "Housing Affordability Stress Index": {
        "file": "data/Housing_Affordability.csv",
        "scale": (0, 2.5),
        "icon": "🏠",
        "page": "3_Housing_Affordability_Stress_Index",
        "description": "Measures how financially stretched households are in buying homes."
    },
    "Renewable Transition Readiness Score": {
        "value": 1.2,
        "prev": 1.1,
        "scale": (0, 5),
        "icon": "🌱",
        "page": "4_Renewable_Transition_Readiness_Score",
        "description": "Measures how prepared India is to shift from fossil fuels to clean energy.",
        "month": "Jul-25"
    },
    "Infrastructure Activity Index (IAI)": {
        "value": None,
        "prev": None,
        "scale": (0, 5),
        "icon": "🏢",
        "page": "5_Infrastructure_Activity_Index_(IAI)",
        "description": "Tracks and forecasts the pace of infrastructure development.",
        "month": "–"
    },
    "IMP Index": {
        "file": "data/IMP_Index.csv",
        "scale": (-3, 3),
        "icon": "💰",
        "page": "6_IMP_Index",
        "description": "Measures India's overall economic well-being."
    }
}

# Helper: Normalize and % Change
def percent_change(prev, curr, min_val, max_val):
    try:
        norm_prev = (prev - min_val) / (max_val - min_val)
        norm_curr = (curr - min_val) / (max_val - min_val)
        if norm_prev == 0:
            return None
        return ((norm_curr - norm_prev) / norm_prev) * 100
    except:
        return None

# Load CDI
def load_cdi():
    try:
        cfg = INDEX_CONFIG["Consumer Demand Index (CDI)"]
        df = pd.read_csv(cfg['file'])
        df['Date'] = pd.to_datetime(df['Date'], errors='coerce')
        df.dropna(subset=['Date'], inplace=True)
        df.dropna(subset=cfg['features'], inplace=True)

        scaler = StandardScaler()
        scaled = scaler.fit_transform(df[cfg['features']])
        pca = PCA(n_components=1)
        df['CDI_Real'] = pca.fit_transform(scaled)[:, 0]
        df = df.sort_values('Date')

        curr, prev = df['CDI_Real'].iloc[-1], df['CDI_Real'].iloc[-2]
        latest_month = df['Date'].iloc[-1].strftime('%b-%y')
        return prev, curr, latest_month
    except:
        return None, None, "–"

# Load IMP
def load_imp():
    try:
        df = pd.read_csv(INDEX_CONFIG['IMP Index']['file'])
        df['Date'] = pd.to_datetime(df['Date'], format='%b-%y', errors='coerce')
        df.dropna(subset=['Date', 'Scale'], inplace=True)
        df = df.sort_values('Date')
        if len(df) < 2:
            st.warning("⚠️ Not enough data to calculate change for IMP Index")
            return None, None, "–"
        curr, prev = df['Scale'].iloc[-1], df['Scale'].iloc[-2]
        latest_month = df['Date'].iloc[-1].strftime('%b-%y')
        return prev, curr, latest_month
    except Exception as e:
        st.error(f"❌ Error loading IMP Index: {e}")
        return None, None, "–"

# Load Housing Affordability
def load_housing():
    try:
        df = pd.read_csv(INDEX_CONFIG['Housing Affordability Stress Index']['file'])
        df['Date'] = pd.to_datetime(df['Date'], errors='coerce')
        df['Property Price Index'] = pd.to_numeric(df['Property Price Index'], errors='coerce')
        df['Per Capita NNI'] = pd.to_numeric(df['Per Capita NNI'], errors='coerce')
        df.dropna(inplace=True)
        df['Affordability Index'] = (df['Per Capita NNI'] / df['Property Price Index']) * 0.003
        df = df.sort_values('Date')
        curr, prev = df['Affordability Index'].iloc[-1], df['Affordability Index'].iloc[-2]
        latest_month = df['Date'].iloc[-1].strftime('%b-%y')
        return prev, curr, latest_month
    except:
        return None, None, "–"

# Attach values and month to config
INDEX_CONFIG['Consumer Demand Index (CDI)']['prev'], INDEX_CONFIG['Consumer Demand Index (CDI)']['value'], INDEX_CONFIG['Consumer Demand Index (CDI)']['month'] = load_cdi()
INDEX_CONFIG['IMP Index']['prev'], INDEX_CONFIG['IMP Index']['value'], INDEX_CONFIG['IMP Index']['month'] = load_imp()
INDEX_CONFIG['Housing Affordability Stress Index']['prev'], INDEX_CONFIG['Housing Affordability Stress Index']['value'], INDEX_CONFIG['Housing Affordability Stress Index']['month'] = load_housing()

# Build table data
st.subheader("📈 Index Overview Table")
table_data = []
for name, cfg in INDEX_CONFIG.items():
    curr, prev = cfg.get('value'), cfg.get('prev')
    min_val, max_val = cfg['scale']
    month = cfg.get("month", "–")

    if curr is not None and prev is not None:
        pct = percent_change(prev, curr, min_val, max_val)
        pct_display = f"{pct:+.2f}%" if pct is not None else "–"
        color = "green" if pct and pct > 0 else "red"
        pct_colored = f":{color}[{pct_display}]"
    else:
        pct_colored = "–"

    table_data.append({
        "📌 Index": f"{cfg['icon']} {name}",
        "🗓️ Latest Month": month,
        "📈 Current Value": f"{curr:.2f}" if curr is not None else "–",
        "🔁 MoM Change (%)": pct_colored,
        "🔗 Action": "Open"
    })

df_display = pd.DataFrame(table_data)

# Show dataframe (excluding button column)
st.dataframe(df_display.drop(columns=["🔗 Action"]), use_container_width=True)

# Optional download
csv = df_display.to_csv(index=False).encode('utf-8')
st.download_button("⬇️ Download Table as CSV", csv, "index_overview.csv", "text/csv", key="download-csv")

# Optional: Buttons section
st.markdown("### 🧭 Detailed View With Actions")
for i in range(len(df_display)):
    cols = st.columns([3, 2, 2, 2, 1])
    cols[0].markdown(f"**{df_display.iloc[i]['📌 Index']}**")
    cols[1].markdown(df_display.iloc[i]['🗓️ Latest Month'])
    cols[2].markdown(df_display.iloc[i]['📈 Current Value'])
    cols[3].markdown(df_display.iloc[i]['🔁 MoM Change (%)'])
    if cols[4].button("Open", key=f"btn-{i}"):
        st.switch_page(f"pages/{INDEX_CONFIG[list(INDEX_CONFIG.keys())[i]]['page']}.py")