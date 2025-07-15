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

# Base directory for file paths
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Index Configuration
INDEX_CONFIG = {
    "Consumer Demand Index (CDI)": {
        "file": os.path.join(BASE_DIR, "data", "Consumer_Demand_Index.csv"),
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
        "file": os.path.join(BASE_DIR, "data", "Housing_Affordability.csv"),
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
        "file": os.path.join(BASE_DIR, "data", "IMP_Index.csv"),
        "scale": (-3, 3),
        "icon": "💰",
        "page": "6_IMP_Index",
        "description": "Measures India's overall economic well-being."
    }
}

# Helper functions
def percent_change(prev, curr, min_val, max_val):
    try:
        norm_prev = (prev - min_val) / (max_val - min_val)
        norm_curr = (curr - min_val) / (max_val - min_val)
        if norm_prev == 0:
            return None
        return ((norm_curr - norm_prev) / norm_prev) * 100
    except:
        return None

def load_cdi():
    try:
        filepath = INDEX_CONFIG["Consumer Demand Index (CDI)"]['file']
        if not os.path.exists(filepath):
            return None, None, "–"
        df = pd.read_csv(filepath)
        df['Date'] = pd.to_datetime(df['Date'], errors='coerce')
        df.dropna(subset=['Date'], inplace=True)
        features = INDEX_CONFIG["Consumer Demand Index (CDI)"]['features']
        df.dropna(subset=features, inplace=True)
        scaler = StandardScaler()
        scaled = scaler.fit_transform(df[features])
        pca = PCA(n_components=1)
        df['CDI_Real'] = pca.fit_transform(scaled)[:, 0]
        df = df.sort_values('Date')
        curr, prev = df['CDI_Real'].iloc[-1], df['CDI_Real'].iloc[-2]
        latest_month = df['Date'].iloc[-1].strftime('%b-%y')
        return prev, curr, latest_month
    except:
        return None, None, "–"

def load_imp():
    try:
        df = pd.read_csv(INDEX_CONFIG['IMP Index']['file'])
        df['Date'] = pd.to_datetime(df['Date'], format='%b-%y', errors='coerce')
        df.dropna(subset=['Date', 'Scale'], inplace=True)
        df = df.sort_values('Date')
        curr, prev = df['Scale'].iloc[-1], df['Scale'].iloc[-2]
        latest_month = df['Date'].iloc[-1].strftime('%b-%y')
        return prev, curr, latest_month
    except:
        return None, None, "–"

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

def load_ev_adoption():
    try:
        ev_data = get_latest_ev_adoption()
        curr = ev_data["rate"]
        latest_month = ev_data["month"]
        df_ev = pd.read_csv(os.path.join(BASE_DIR, "data", "EV_Adoption.csv"))
        df_ev.columns = df_ev.columns.str.strip()
        df_ev['Date'] = pd.to_datetime(df_ev['Date'], format='%m/%d/%Y', errors='coerce')
        df_ev = df_ev.dropna(subset=['Date'])
        ev_cols = ['EV Four-wheeler Sales', 'EV Two-wheeler Sales', 'EV Three-wheeler Sales']
        for col in ev_cols:
            df_ev[col] = pd.to_numeric(df_ev[col].astype(str).str.replace(',', ''), errors='coerce')
        df_ev['Total Vehicle Sales'] = pd.to_numeric(df_ev['Total Vehicle Sales'].astype(str).str.replace(',', ''), errors='coerce')
        df_ev['EV Total Sales'] = df_ev[ev_cols].sum(axis=1)
        df_ev['EV Adoption Rate'] = df_ev['EV Total Sales'] / df_ev['Total Vehicle Sales']
        df_ev = df_ev.sort_values("Date")
        prev = df_ev['EV Adoption Rate'].iloc[-2] if len(df_ev) >= 2 else None
        return prev, curr, latest_month
    except:
        return None, None, "–"

def load_renewable():
    try:
        df = pd.read_csv(os.path.join(BASE_DIR, "data", "Renewable_Energy.csv"))
        df.columns = df.columns.str.strip()
        df['Date'] = pd.to_datetime(df['Date'], errors='coerce')
        df.dropna(subset=['Date'], inplace=True)
        HOURS = 720
        df['Solar Gen (GWh)'] = df['Solar power plants Installed capacity'] * 0.2 * HOURS / 1000
        df['Wind Gen (GWh)'] = df['Wind power plants Installed capacity'] * 0.3 * HOURS / 1000
        df['Hydro Gen (GWh)'] = df['Hydro power plants Installed capacity'] * 0.4 * HOURS / 1000
        df['Total Gen (GWh)'] = df[['Solar Gen (GWh)', 'Wind Gen (GWh)', 'Hydro Gen (GWh)']].sum(axis=1)
        df['Power Consumption (GWh)'] = df['Power Consumption'] * 1000
        df['Renewable Share (%)'] = df['Total Gen (GWh)'] / df['Power Consumption (GWh)'] * 100
        df['Norm_Budget'] = (df['Budgetary allocation for MNRE sector'] - df['Budgetary allocation for MNRE sector'].min()) / (df['Budgetary allocation for MNRE sector'].max() - df['Budgetary allocation for MNRE sector'].min())
        df['Norm_Share'] = (df['Renewable Share (%)'] - df['Renewable Share (%)'].min()) / (df['Renewable Share (%)'].max() - df['Renewable Share (%)'].min())
        df['Readiness Score'] = 0.5 * df['Norm_Budget'] + 0.5 * df['Norm_Share']
        df = df.sort_values('Date')
        curr = df['Readiness Score'].iloc[-1]
        prev = df['Readiness Score'].iloc[-2] if len(df) > 1 else None
        latest_month = df['Date'].iloc[-1].strftime('%b-%y')
        return prev, curr, latest_month
    except:
        return None, None, "–"

# Load values
INDEX_CONFIG['Consumer Demand Index (CDI)']['prev'], INDEX_CONFIG['Consumer Demand Index (CDI)']['value'], INDEX_CONFIG['Consumer Demand Index (CDI)']['month'] = load_cdi()
INDEX_CONFIG['IMP Index']['prev'], INDEX_CONFIG['IMP Index']['value'], INDEX_CONFIG['IMP Index']['month'] = load_imp()
INDEX_CONFIG['Housing Affordability Stress Index']['prev'], INDEX_CONFIG['Housing Affordability Stress Index']['value'], INDEX_CONFIG['Housing Affordability Stress Index']['month'] = load_housing()
INDEX_CONFIG['EV Market Adoption Rate']['prev'], INDEX_CONFIG['EV Market Adoption Rate']['value'], INDEX_CONFIG['EV Market Adoption Rate']['month'] = load_ev_adoption()
INDEX_CONFIG['Renewable Transition Readiness Score']['prev'], INDEX_CONFIG['Renewable Transition Readiness Score']['value'], INDEX_CONFIG['Renewable Transition Readiness Score']['month'] = load_renewable()

# Build table
st.subheader("📈 Index Overview Table")
data = []
for name, cfg in INDEX_CONFIG.items():
    curr, prev = cfg.get('value'), cfg.get('prev')
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

# Show table
for i in range(len(df_display)):
    cols = st.columns([3, 2, 2, 2, 1])
    cols[0].markdown(f"**{df_display.iloc[i]['Index']}**")
    cols[1].markdown(df_display.iloc[i]['Latest Month'])
    cols[2].markdown(df_display.iloc[i]['Current Value'])
    cols[3].markdown(df_display.iloc[i]['MoM Change'])
    if df_display.iloc[i]['Action'] != "–":
        if cols[4].button("Open", key=f"btn-{i}"):
            st.switch_page(f"pages/{INDEX_CONFIG[list(INDEX_CONFIG.keys())[i]]['page']}.py")