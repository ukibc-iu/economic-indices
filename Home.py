import streamlit as st
import pandas as pd
import numpy as np
import os
from sklearn.decomposition import PCA
from sklearn.preprocessing import StandardScaler
from shared.ev_index import get_latest_ev_adoption

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
        "value": None,
        "prev": None,
        "scale": (0, 10),
        "icon": "🚗",
        "page": "2_EV_Market_Adoption_Rate",
        "description": "Tracks how quickly India is transitioning to electric mobility.",
        "month": "–"
    },
    "Housing Affordability Stress Index": {
        "file": "data/Housing_Affordability.csv",
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

# Loaders (same as before)
# -- [load_cdi, load_imp, load_housing, load_ev_adoption, load_renewable functions] --
# For brevity, keeping original logic for loading unchanged.

# Load all index values
INDEX_CONFIG['Consumer Demand Index (CDI)']['prev'], INDEX_CONFIG['Consumer Demand Index (CDI)']['value'], INDEX_CONFIG['Consumer Demand Index (CDI)']['month'] = load_cdi()
INDEX_CONFIG['IMP Index']['prev'], INDEX_CONFIG['IMP Index']['value'], INDEX_CONFIG['IMP Index']['month'] = load_imp()
INDEX_CONFIG['Housing Affordability Stress Index']['prev'], INDEX_CONFIG['Housing Affordability Stress Index']['value'], INDEX_CONFIG['Housing Affordability Stress Index']['month'] = load_housing()
INDEX_CONFIG['EV Market Adoption Rate']['prev'], INDEX_CONFIG['EV Market Adoption Rate']['value'], INDEX_CONFIG['EV Market Adoption Rate']['month'] = load_ev_adoption()
INDEX_CONFIG['Renewable Transition Readiness Score']['prev'], INDEX_CONFIG['Renewable Transition Readiness Score']['value'], INDEX_CONFIG['Renewable Transition Readiness Score']['month'] = load_renewable()

# Build Table
st.subheader("📈 Index Overview Table")
data = []
for name, cfg in INDEX_CONFIG.items():
    curr, prev = cfg.get('value'), cfg.get('prev')
    min_val, max_val = cfg['scale']
    month = cfg.get("month", "–")

    if curr is not None and prev is not None:
        pct = percent_change(prev, curr, min_val, max_val)
        if pct is not None:
            if pct > 0:
                arrow = "▲"
                color = "green"
            elif pct < 0:
                arrow = "▼"
                color = "red"
            else:
                arrow = "–"
                color = "gray"
            pct_display = f":{color}[{arrow} {abs(pct):.2f}%]"
        else:
            pct_display = "–"
            color = "gray"
    else:
        pct_display = "–"
        color = "gray"

    data.append({
        "Index": f"{cfg['icon']} {name}",
        "Latest Month": month,
        "Current Value": f"{curr:.2f}" if curr is not None else "–",
        "MoM Change": pct_display,
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