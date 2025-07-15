import streamlit as st
import pandas as pd
import numpy as np
import os
from sklearn.decomposition import PCA
from sklearn.preprocessing import StandardScaler
from shared.ev_index import get_latest_ev_adoption

# Debug working directory
cwd = os.getcwd()
st.write(f"📁 Current working directory: `{cwd}`")

data_dir = os.path.join(cwd, "data")
if not os.path.exists(data_dir):
    st.error("❌ 'data' folder not found in working directory.")
else:
    st.success(f"✅ 'data' folder found.")
    st.write("📄 Files in 'data':", os.listdir(data_dir))

# Page Config
st.set_page_config(layout="wide", page_title="Economic Indices Overview")
st.title("📊 Economic Indices Dashboard")
st.markdown("*Track key economic indicators and analyze their month-over-month changes.*")

# Index Configuration
INDEX_CONFIG = {
    "Consumer Demand Index (CDI)": {
        "file": os.path.join("data", "Consumer_Demand_Index.csv"),
        "features": ['UPI Transactions', 'GST Revenue', 'Vehicle Sales', 'Housing Sales', 'Power Consumption'],
        "scale": (-5, 5),
        "icon": "🏍️",
        "page": "1_CDI_Dashboard",
        "description": "The Consumer Demand Index captures shifts in real-time consumer activity."
    },
    "EV Market Adoption Rate": {
        "value": None,
        "prev": None,
        "scale": (0, 10),
        "icon": "🚗",
        "page": "2_EV_Market_Adoption_Rate",
        "description": "Tracks how quickly India is transitioning to electric mobility.",
        "month": "–"
    },
    "Housing Affordability Stress Index": {
        "file": os.path.join("data", "Housing_Affordability.csv"),
        "scale": (0, 2.5),
        "icon": "🏠",
        "page": "3_Housing_Affordability_Stress_Index",
        "description": "Measures how financially stretched households are in buying homes."
    },
    "Renewable Transition Readiness Score": {
        "value": None,
        "prev": None,
        "scale": (0, 5),
        "icon": "🌱",
        "page": "4_Renewable_Transition_Readiness_Score",
        "description": "Measures how prepared India is to shift from fossil fuels to clean energy.",
        "month": "–"
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
        "file": os.path.join("data", "IMP_Index.csv"),
        "scale": (-3, 3),
        "icon": "💰",
        "page": "6_IMP_Index",
        "description": "Measures India's overall economic well-being."
    }
}

# ✅ SAFE percent_change FUNCTION
def percent_change(prev, curr, min_val, max_val):
    try:
        if any(v is None for v in [prev, curr, min_val, max_val]):
            return None

        denominator = max_val - min_val
        if denominator == 0:
            return None

        norm_prev = (prev - min_val) / denominator
        norm_curr = (curr - min_val) / denominator

        if norm_prev == 0:
            return None

        pct = ((norm_curr - norm_prev) / norm_prev) * 100

        if not np.isfinite(pct):
            return None

        return pct
    except Exception:
        return None

def load_cdi():
    try:
        cfg = INDEX_CONFIG["Consumer Demand Index (CDI)"]
        filepath = cfg['file']

        if not os.path.exists(filepath):
            st.error(f"❌ File not found: {filepath}")
            return None, None, "–"

        df = pd.read_csv(filepath)

        if 'Date' not in df.columns:
            st.error("❌ 'Date' column not found in CDI CSV.")
            return None, None, "–"

        df['Date'] = pd.to_datetime(df['Date'], format="%m/%d/%Y", errors='coerce')
        df.dropna(subset=['Date'], inplace=True)

        missing = [f for f in cfg['features'] if f not in df.columns]
        if missing:
            st.error(f"❌ Missing required columns in CDI CSV: {missing}")
            return None, None, "–"

        df[cfg['features']] = df[cfg['features']].apply(pd.to_numeric, errors='coerce')
        df.dropna(subset=cfg['features'], inplace=True)

        scaler = StandardScaler()
        scaled = scaler.fit_transform(df[cfg['features']])
        pca = PCA(n_components=1)
        df['CDI_Real'] = pca.fit_transform(scaled)[:, 0]

        df = df.sort_values('Date')
        curr, prev = df['CDI_Real'].iloc[-1], df['CDI_Real'].iloc[-2]
        latest_month = df['Date'].iloc[-1].strftime('%b-%y')

        return prev, curr, latest_month

    except Exception as e:
        st.error(f"❌ Error loading CDI: {e}")
        return None, None, "–"

# Load CDI
INDEX_CONFIG['Consumer Demand Index (CDI)']['prev'], INDEX_CONFIG['Consumer Demand Index (CDI)']['value'], INDEX_CONFIG['Consumer Demand Index (CDI)']['month'] = load_cdi()

# Build Table
st.subheader("📈 Index Overview Table")
data = []
for name, cfg in INDEX_CONFIG.items():
    curr, prev = cfg.get('value'), cfg.get('prev')
    min_val, max_val = cfg['scale']
    month = cfg.get("month", "–")

    if curr is not None and prev is not None:
        pct = percent_change(prev, curr, min_val, max_val)
        pct_display = f"{pct:+.2f}%" if pct is not None else "–"
        color = "green" if isinstance(pct, (int, float)) and pct > 0 else "red"
    else:
        pct_display = "–"
        color = "gray"

    data.append({
        "Index": f"{cfg['icon']} {name}",
        "Latest Month": month,
        "Current Value": f"{curr:.2f}" if curr is not None else "–",
        "MoM Change": f":{color}[{pct_display}]",
        "Action": f"Go →"
    })

df_display = pd.DataFrame(data)

# Show Table
for i in range(len(df_display)):
    cols = st.columns([3, 2, 2, 2, 1])
    cols[0].markdown(f"**{df_display.iloc[i]['Index']}**")
    cols[1].markdown(df_display.iloc[i]['Latest Month'])
    cols[2].markdown(df_display.iloc[i]['Current Value'])
    cols[3].markdown(df_display.iloc[i]['MoM Change'])
    if df_display.iloc[i]['Action'] != "–":
        if cols[4].button("Open", key=f"btn-{i}"):
            st.switch_page(f"pages/{INDEX_CONFIG[list(INDEX_CONFIG.keys())[i]]['page']}.py")