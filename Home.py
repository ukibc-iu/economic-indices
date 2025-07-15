import streamlit as st
import pandas as pd
import numpy as np
import os
from sklearn.decomposition import PCA
from sklearn.preprocessing import StandardScaler
from shared.ev_index import get_latest_ev_adoption

st.set_page_config(layout="wide", page_title="Economic Indices Overview")
st.title("📊 Economic Indices Dashboard")

# Index config
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
    "IMP Index": {
        "file": os.path.join("data", "IMP_Index.csv"),
        "scale": (-3, 3),
        "icon": "💰",
        "page": "6_IMP_Index",
        "description": "Measures India's overall economic well-being."
    }
}

# ------------------- Percent Change -------------------
def percent_change(prev, curr, min_val, max_val):
    denominator = max_val - min_val
    norm_prev = (prev - min_val) / denominator
    norm_curr = (curr - min_val) / denominator
    if norm_prev == 0:
        return None
    return ((norm_curr - norm_prev) / norm_prev) * 100

# ------------------- Load CDI -------------------
def load_cdi():
    cfg = INDEX_CONFIG["Consumer Demand Index (CDI)"]
    df = pd.read_csv(cfg['file'])
    df['Date'] = pd.to_datetime(df['Date'], format="%m/%d/%Y")
    df.dropna(subset=cfg['features'], inplace=True)

    scaler = StandardScaler()
    scaled = scaler.fit_transform(df[cfg['features']])
    pca = PCA(n_components=1)
    df['CDI_Real'] = pca.fit_transform(scaled)[:, 0]

    df = df.sort_values('Date')
    prev, curr = df['CDI_Real'].iloc[-2], df['CDI_Real'].iloc[-1]
    latest_month = df['Date'].iloc[-1].strftime('%b-%y')
    return prev, curr, latest_month

# ------------------- Load CDI Values -------------------
INDEX_CONFIG['Consumer Demand Index (CDI)']['prev'], INDEX_CONFIG['Consumer Demand Index (CDI)']['value'], INDEX_CONFIG['Consumer Demand Index (CDI)']['month'] = load_cdi()

# ------------------- Build and Display Table -------------------
st.subheader("📈 Index Overview Table")
data = []

for name, cfg in INDEX_CONFIG.items():
    curr = cfg.get('value')
    prev = cfg.get('prev')
    min_val, max_val = cfg['scale']
    month = cfg.get("month", "–")

    if curr is not None and prev is not None:
        pct = percent_change(prev, curr, min_val, max_val)
        pct_display = f"{pct:+.2f}%" if pct is not None else "–"
        color = "green" if pct and pct > 0 else "red"
    else:
        pct_display = "–"
        color = "gray"

    data.append({
        "Index": f"{cfg['icon']} {name}",
        "Latest Month": month,
        "Current Value": f"{curr:.2f}" if curr is not None else "–",
        "MoM Change": f":{color}[{pct_display}]",
        "Action": "Go →"
    })

df_display = pd.DataFrame(data)

for i in range(len(df_display)):
    cols = st.columns([3, 2, 2, 2, 1])
    cols[0].markdown(f"**{df_display.iloc[i]['Index']}**")
    cols[1].markdown(df_display.iloc[i]['Latest Month'])
    cols[2].markdown(df_display.iloc[i]['Current Value'])
    cols[3].markdown(df_display.iloc[i]['MoM Change'])
    if cols[4].button("Open", key=f"btn-{i}"):
        st.switch_page(f"pages/{INDEX_CONFIG[list(INDEX_CONFIG.keys())[i]]['page']}.py")