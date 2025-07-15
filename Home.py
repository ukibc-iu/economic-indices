import streamlit as st
import pandas as pd
import numpy as np
import os
from sklearn.decomposition import PCA
from sklearn.preprocessing import StandardScaler
from shared.ev_index import get_latest_ev_adoption

# Set page config
st.set_page_config(layout="wide", page_title="Economic Indices Overview")
st.title("📊 Economic Indices Dashboard")
st.markdown("*Track key economic indicators with latest available values.*")

# Index Configuration
INDEX_CONFIG = {
    "Consumer Demand Index (CDI)": {
        "file": os.path.join("data", "Consumer_Demand_Index.csv"),
        "features": ['UPI Transactions', 'GST Revenue', 'Vehicle Sales', 'Housing Sales', 'Power Consumption'],
        "icon": "🏍️",
        "page": "1_CDI_Dashboard",
        "description": "Captures real-time consumer activity trends.",
        "value": None,
        "month": "–"
    },
    "EV Market Adoption Rate": {
        "value": None,
        "icon": "🚗",
        "page": "2_EV_Market_Adoption_Rate",
        "description": "Tracks India's transition to electric mobility.",
        "month": "–"
    },
    "Housing Affordability Stress Index": {
        "file": os.path.join("data", "Housing_Affordability.csv"),
        "icon": "🏠",
        "page": "3_Housing_Affordability_Stress_Index",
        "description": "Measures housing affordability stress.",
        "value": None,
        "month": "–"
    },
    "Renewable Transition Readiness Score": {
        "value": None,
        "icon": "🌱",
        "page": "4_Renewable_Transition_Readiness_Score",
        "description": "Readiness to switch to renewable energy.",
        "month": "–"
    },
    "Infrastructure Activity Index (IAI)": {
        "value": None,
        "icon": "🏢",
        "page": "5_Infrastructure_Activity_Index_(IAI)",
        "description": "Pace of infrastructure development.",
        "month": "–"
    },
    "IMP Index": {
        "file": os.path.join("data", "IMP_Index.csv"),
        "icon": "💰",
        "page": "6_IMP_Index",
        "description": "India's macroeconomic performance.",
        "value": None,
        "month": "–"
    }
}


def load_cdi():
    try:
        cfg = INDEX_CONFIG["Consumer Demand Index (CDI)"]
        filepath = cfg['file']
        df = pd.read_csv(filepath)

        df['Date'] = pd.to_datetime(df['Date'], format="%m/%d/%Y", errors='coerce')
        df.dropna(subset=['Date'], inplace=True)

        scaler = StandardScaler()
        features = cfg['features']
        scaled = scaler.fit_transform(df[features])
        pca = PCA(n_components=1)
        df['CDI_Real'] = pca.fit_transform(scaled)[:, 0]

        df = df.sort_values('Date')
        latest_value = df['CDI_Real'].iloc[-1]
        latest_month = df['Date'].iloc[-1].strftime('%b-%Y')

        return latest_value, latest_month
    except Exception as e:
        st.error(f"❌ Error loading CDI: {e}")
        return None, "–"


# Load CDI Index
INDEX_CONFIG['Consumer Demand Index (CDI)']['value'], INDEX_CONFIG['Consumer Demand Index (CDI)']['month'] = load_cdi()


# Build display table
st.subheader("📈 Latest Index Values")
data = []

for name, cfg in INDEX_CONFIG.items():
    index_label = f"{cfg.get('icon', '')} {name}"
    value = cfg.get('value')
    month = cfg.get('month', '–')
    try:
        value_str = f"{value:.2f}" if isinstance(value, (int, float)) else "–"
    except:
        value_str = "–"

    data.append({
        "Index": index_label,
        "Latest Month": month,
        "Latest Value": value_str,
        "Action": "Go →"
    })

df_display = pd.DataFrame(data)

# Render layout
for i in range(len(df_display)):
    cols = st.columns([3, 2, 2, 1])
    cols[0].markdown(f"**{df_display.iloc[i]['Index']}**")
    cols[1].markdown(df_display.iloc[i]['Latest Month'])
    cols[2].markdown(df_display.iloc[i]['Latest Value'])
    if cols[3].button("Open", key=f"btn-{i}"):
        st.switch_page(f"pages/{INDEX_CONFIG[list(INDEX_CONFIG.keys())[i]]['page']}.py")