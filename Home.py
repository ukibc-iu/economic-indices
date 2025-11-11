import streamlit as st
import pandas as pd
import numpy as np
import os
from sklearn.decomposition import PCA
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import MinMaxScaler
from shared.ev_index import get_latest_ev_adoption
from shared.retail_index import compute_retail_index

st.set_page_config(layout="wide", page_title="Economic Indices Overview")
st.title("Economic Indices Dashboard")
st.markdown("*Track key economic indicators and analyze their month-over-month changes.*")

# Index Configuration (with images)
INDEX_CONFIG = {
    "Consumer Demand Index (CDI)": {
        "file": "data/Consumer_Demand_Index.csv",
        "features": ['UPI Transactions', 'GST Revenue', 'Vehicle Sales', 'Housing Sales', 'Power Consumption'],
        "scale": (-5, 5),
        "image": "images/CDI.jpg",
        "page": "1_CDI_Dashboard",
        "description": "The Consumer Demand Index captures shifts in real-time consumer activity."
    },
    "EV Market Adoption Rate": {
        "value": None, "prev": None, "scale": (0, 10),
        "image": "images/EV.jpg", "page": "2_EV_Market_Adoption_Rate",
        "description": "Tracks how quickly India is transitioning to electric mobility.",
        "month": "–"
    },
    "Housing Affordability Stress Index": {
        "file": "data/Housing_Affordability.csv",
        "scale": (0, 2.5),
        "image": "images/Housing.jpg",
        "page": "3_Housing_Affordability_Stress_Index",
        "description": "Measures how financially stretched households are in buying homes."
    },
    "Renewable Transition Readiness Score": {
        "value": None, "prev": None, "scale": (0, 5),
        "image": "images/Renewable.jpg", "page": "4_Renewable_Transition_Readiness_Score",
        "description": "Measures how prepared India is to shift from fossil fuels to clean energy.",
        "month": "–"
    },
    "Infrastructure Activity Index (IAI)": {
        "value": None, "prev": None, "scale": (0, 5),
        "image": "images/Infra.jpg", "page": "5_Infrastructure_Activity_Index_(IAI)",
        "description": "Tracks and forecasts the pace of infrastructure development.",
        "month": "–"
    },
    "IMP Index": {
        "file": "data/IMP_Index.csv",
        "scale": (-3, 3),
        "image": "images/IMP.jpg", "page": "6_IMP_Index",
        "description": "Measures India's overall economic well-being."
    },
    "Retail Health Index": {
        "file": "data/Retail_Health.csv",
        "scale": (0, 1),
        "image": "images/Retail.jpg", "page": "7_Retail_Health",
        "description": "Reflects the overall economic environment influencing retail activity."
    }
}

def percent_change(prev, curr, min_val, max_val):
    try:
        norm_prev = (prev - min_val) / (max_val - min_val)
        norm_curr = (curr - min_val) / (max_val - min_val)
        if norm_prev == 0:
            return None
        return ((norm_curr - norm_prev) / norm_prev) * 100
    except:
        return None

# Individual Loaders
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

def load_imp():
    try:
        df = pd.read_csv(INDEX_CONFIG['IMP Index']['file'])

        # --- FIX DATE PARSING ---
        # Convert "18-May" → "2018-May"
        df['Date'] = df['Date'].astype(str).str.strip()
        df['Date'] = df['Date'].apply(lambda x: f"20{x[:2]}-{x[3:]}" if "-" in x else x)

        # Now parse properly
        df['Date'] = pd.to_datetime(df['Date'], format="%Y-%b", errors="coerce")

        df.dropna(subset=["Date", "Scale"], inplace=True)
        df = df.sort_values("Date")

        # Compute values normally
        curr = df['Scale'].iloc[-1]
        prev = df['Scale'].iloc[-2] if len(df) > 1 else None
        latest_month = df['Date'].iloc[-1].strftime("%b-%y")

        return prev, curr, latest_month

    except Exception as e:
        print("IMP Index load error:", e)
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
        df_ev = pd.read_csv("data/EV_Adoption.csv")
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
        df = pd.read_csv("data/Renewable_Energy.csv")
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
        df['Norm_Budget'] = (df['Budgetary allocation for MNRE sector'] - df['Budgetary allocation for MNRE sector'].min()) / \
                            (df['Budgetary allocation for MNRE sector'].max() - df['Budgetary allocation for MNRE sector'].min())
        df['Norm_Share'] = (df['Renewable Share (%)'] - df['Renewable Share (%)'].min()) / \
                           (df['Renewable Share (%)'].max() - df['Renewable Share (%)'].min())
        df['Readiness Score'] = 0.5 * df['Norm_Budget'] + 0.5 * df['Norm_Share']
        df = df.sort_values('Date')
        curr = df['Readiness Score'].iloc[-1]
        prev = df['Readiness Score'].iloc[-2] if len(df) > 1 else None
        latest_month = df['Date'].iloc[-1].strftime('%b-%y')
        return prev, curr, latest_month
    except:
        return None, None, "–"

def load_iai():
    try:
        df = pd.read_csv("data/Infrastructure_Activity.csv")
        df.columns = df.columns.str.strip()
        df['Date'] = pd.to_datetime(df['Date'], errors='coerce')
        df.dropna(subset=['Date'], inplace=True)
        idv_cols = [
            "Highway construction actual", "Railway line construction actual",
            "Power T&D line constr (220KV plus)", "Cement price",
            "Budgetary allocation for infrastructure sector"
        ]
        target_col = "GVA: construction (Basic Price)"
        for col in idv_cols + [target_col]:
            df[col] = pd.to_numeric(df[col], errors='coerce')
        df.dropna(inplace=True)
        scaler = MinMaxScaler()
        X_scaled = scaler.fit_transform(df[idv_cols])
        model = LinearRegression()
        model.fit(X_scaled, df[target_col])
        weights = model.coef_ / model.coef_.sum()
        df['IAI'] = pd.DataFrame(X_scaled, columns=idv_cols).dot(weights)
        df = df.sort_values('Date')
        curr = df['IAI'].iloc[-1]
        prev = df['IAI'].iloc[-2] if len(df) > 1 else None
        latest_month = df['Date'].iloc[-1].strftime('%b-%y')
        return prev, curr, latest_month
    except:
        return None, None, "–"

def load_retail_health():
    try:
        df = pd.read_csv("data/Retail_Health.csv")
        df.columns = df.columns.str.strip()
        df['Date'] = pd.to_datetime(df['Date'], errors='coerce')
        df = df.dropna(subset=['Date'])

        # --- Clean numeric columns
        numeric_cols = ['CCI', 'Inflation', 'Private Consumption', 'UPI Transactions', 'Repo Rate', 'Per Capita NNI']
        for col in numeric_cols:
            df[col] = pd.to_numeric(df[col], errors='coerce')

        # --- Adjust directionality (negative indicators)
        df['Inflation'] = -df['Inflation']
        df['Repo Rate'] = -df['Repo Rate']

        df_clean = df.dropna(subset=numeric_cols).copy()

        # --- Perform PCA with training cutoff
        training_end = pd.to_datetime("2024-03-01")
        df_train = df_clean[df_clean['Date'] <= training_end].copy()

        scaler = StandardScaler()
        X_train_scaled = scaler.fit_transform(df_train[numeric_cols])
        pca = PCA(n_components=1)
        train_index = pca.fit_transform(X_train_scaled)

        X_all_scaled = scaler.transform(df_clean[numeric_cols])
        df_clean['Retail Index Raw'] = pca.transform(X_all_scaled)
        min_val, max_val = train_index.min(), train_index.max()
        df_clean['Retail Index'] = (df_clean['Retail Index Raw'] - min_val) / (max_val - min_val)
        df_clean['Retail Index'] = df_clean['Retail Index'].clip(0, 1)

        df_clean = df_clean.sort_values("Date")
        curr = df_clean['Retail Index'].iloc[-1]
        prev = df_clean['Retail Index'].iloc[-2]
        latest_month = df_clean['Date'].iloc[-1].strftime('%b-%y')
        return prev, curr, latest_month
    except:
        return None, None, "–"
# Load All Values
INDEX_CONFIG['Consumer Demand Index (CDI)']['prev'], INDEX_CONFIG['Consumer Demand Index (CDI)']['value'], INDEX_CONFIG['Consumer Demand Index (CDI)']['month'] = load_cdi()
INDEX_CONFIG['IMP Index']['prev'], INDEX_CONFIG['IMP Index']['value'], INDEX_CONFIG['IMP Index']['month'] = load_imp()
INDEX_CONFIG['Housing Affordability Stress Index']['prev'], INDEX_CONFIG['Housing Affordability Stress Index']['value'], INDEX_CONFIG['Housing Affordability Stress Index']['month'] = load_housing()
INDEX_CONFIG['EV Market Adoption Rate']['prev'], INDEX_CONFIG['EV Market Adoption Rate']['value'], INDEX_CONFIG['EV Market Adoption Rate']['month'] = load_ev_adoption()
INDEX_CONFIG['Renewable Transition Readiness Score']['prev'], INDEX_CONFIG['Renewable Transition Readiness Score']['value'], INDEX_CONFIG['Renewable Transition Readiness Score']['month'] = load_renewable()
INDEX_CONFIG['Infrastructure Activity Index (IAI)']['prev'], INDEX_CONFIG['Infrastructure Activity Index (IAI)']['value'], INDEX_CONFIG['Infrastructure Activity Index (IAI)']['month'] = load_iai()
INDEX_CONFIG['Retail Health Index']['prev'], INDEX_CONFIG['Retail Health Index']['value'], INDEX_CONFIG['Retail Health Index']['month'] = load_retail_health()

# === Render Table ===
data = []
for name, cfg in INDEX_CONFIG.items():
    curr, prev = cfg.get('value'), cfg.get('prev')
    min_val, max_val = cfg['scale']
    month = cfg.get("month", "–")

    if curr is not None and prev is not None:
        pct = percent_change(prev, curr, min_val, max_val)
        if pct is not None and abs(pct) < 0.01:
            pct_display = "–"
        elif pct is not None:
            arrow = "▲" if pct > 0 else "▼"
            color = "green" if pct > 0 else "red"
            pct_display = f'<span style="color:{color};">{arrow} {abs(pct):.2f}%</span>'
        else:
            pct_display = "–"
    else:
        pct_display = "–"

    data.append({
        "Index": name,
        "Image": cfg.get("image"),
        "Latest Month": month,
        "Current Value": f"{curr:.2f}" if curr is not None else "–",
        "MoM Change": pct_display,
        "Action": "Go →" if cfg.get("page") else "–"
    })

df_display = pd.DataFrame(data)

# Render rows
for i in range(len(df_display)):
    cols = st.columns([1, 3, 2, 2, 2, 1])
    img_path = df_display.iloc[i]['Image']
    if img_path and os.path.exists(img_path):
        cols[0].image(img_path, width=50)
    else:
        cols[0].markdown("📄")

    cols[1].markdown(f"**{df_display.iloc[i]['Index']}**")
    cols[2].markdown(df_display.iloc[i]['Latest Month'])
    cols[3].markdown(df_display.iloc[i]['Current Value'])
    cols[4].markdown(df_display.iloc[i]['MoM Change'], unsafe_allow_html=True)

    if df_display.iloc[i]['Action'] != "–":
        if cols[5].button("Open", key=f"btn-{i}"):
            st.switch_page(f"pages/{INDEX_CONFIG[df_display.iloc[i]['Index']]['page']}.py")

import streamlit as st
import pandas as pd
import streamlit.components.v1 as components

st.markdown("---")
st.subheader("UK-India Macroeconomic Comparison")

try:
    # Load data
    macro_df = pd.read_excel("data/Macro_MoM_Comparison.xlsx", sheet_name="June")
    display_params = ["Repo Rate", "Inflation Rate", "Unemployment Rate"]
    macro_df = macro_df[macro_df["Parameter"].isin(display_params)]

    def styled_change(change_str, param):
        if not isinstance(change_str, str):
            return "–"
        text = change_str.strip().lower()
        if text in ["no change", "0 bps", "0.0%", "0%", "+0 bps", "+0%", "0", "–", "-", "", "na", "n/a"]:
            return "<span style='color:grey;'>No Change</span>"
        up = "+" in text
        if param.lower() in ["inflation rate", "unemployment rate"]:
            color = "red" if up else "green"
        else:
            color = "green" if up else "red"
        arrow = "▲" if up else "▼"
        return f"<span style='color:{color}; font-weight: 600;'>{arrow} {change_str.strip()}</span>"

    # Flags
    uk_flag = "<img src='https://flagcdn.com/gb.svg' width='32' style='vertical-align: middle;'>"
    in_flag = "<img src='https://flagcdn.com/in.svg' width='32' style='vertical-align: middle;'>"

    # HTML content
    html = f"""
    <style>
        body {{
            margin: 0;
            padding: 0;
            font-family: 'Segoe UI', sans-serif;
            background-color: transparent;
        }}

        .wrapper {{
            display: flex;
            justify-content: center;
            align-items: center;
            width: 100%;
        }}

        .macro-table {{
            width: 100%;
            max-width: 800px;
            border-collapse: collapse;
            background-color: #1e1e1e;
            color: white;
            border: 1px solid #333;
            border-radius: 10px;
            overflow: hidden;
        }}

        .macro-table th, .macro-table td {{
            text-align: center;
            padding: 16px;
            font-size: 17px;
        }}

        .macro-table th {{
            background-color: #2e2e2e;
            font-weight: bold;
        }}

        .macro-table td:first-child {{
            text-align: left;
            font-weight: 600;
            color: #ccc;
            padding-left: 20px;
        }}
    </style>

    <div class='wrapper'>
        <table class='macro-table'>
            <tr>
                <th>Parameter</th>
                <th>{uk_flag}</th>
                <th>{in_flag}</th>
            </tr>
    """

    for _, row in macro_df.iterrows():
        param = row["Parameter"]
        uk_change = styled_change(str(row["UK MoM Change"]), param)
        in_change = styled_change(str(row["India MoM Change"]), param)
        html += f"""
            <tr>
                <td>{param}</td>
                <td>{uk_change}</td>
                <td>{in_change}</td>
            </tr>
        """
    html += "</table></div>"

    # Force full width of iframe and disable scroll
    components.html(html, height=220, width=1000, scrolling=False)

    # CTA Button
    st.markdown(
        """
        <div style='margin-top: 16px; display: flex; align-items: center; gap: 16px;'>
            <span style='font-weight: 500; font-size: 16px;'><em>For an in-depth look at other economic parameters</em></span>
            <a href='/Coverpage' target='_self'>
                <button style='padding:8px 16px; font-size:15px; border-radius:8px; background-color:#444; color:white; border:none; cursor:pointer;'>
                    Click
                </button>
            </a>
        </div>
        """,
        unsafe_allow_html=True
    )

except Exception as e:
    st.error(f"Could not load macroeconomic comparison data: {e}")

st.markdown("---")
import streamlit as st
import pandas as pd

# --- Fertiliser Demand Data ---
fert_df = pd.read_excel("data/Agri_Model.xlsx")
fert_df = fert_df.dropna(subset=["Predicted"])
fert_latest = fert_df.tail(1)

fert_quarter = fert_latest["Quarter"].values[0]
fert_actual = fert_latest["Actual"].values[0] if pd.notna(fert_latest["Actual"].values[0]) else "NA"
fert_predicted = fert_latest["Predicted"].values[0]

fert_actual_str = f"{fert_actual:.2f}" if fert_actual != "NA" else "NA"
fert_predicted_str = f"{fert_predicted:.2f}"


# --- Houses Construction Data ---
house_df = pd.read_excel("data/Housing_Model.xlsx")
house_df = house_df.dropna(subset=["Predicted"])
house_latest = house_df.tail(1)

house_quarter = house_latest["Quarter"].values[0]
house_actual = house_latest["Actual"].values[0] if pd.notna(house_latest["Actual"].values[0]) else "NA"
house_predicted = house_latest["Predicted"].values[0]

house_actual_str = f"{house_actual:.2f}" if house_actual != "NA" else "NA"
house_predicted_str = f"{house_predicted:.2f}"


# --- Vehicle Production Data (from 6 sheets) ---
vehicle_sheets = [
    "Passenger Vehicles",
    "Light Commercial Vehicles",
    "Medium Commercial Vehicles",
    "Heavy Commercial Vehicles",
    "Three Wheelers and Quadricycles",
    "Two Wheelers"
]

vehicle_df_dict = pd.read_excel("data/Auto_Model.xlsx", sheet_name=None)

latest_quarters = []
vehicle_actual_total = 0
vehicle_predicted_total = 0

for sheet in vehicle_sheets:
    df = vehicle_df_dict[sheet]
    df.columns = [col.strip() for col in df.columns]
    df = df.dropna(subset=["Predicted"])
    df["Actual"] = pd.to_numeric(df["Actual"], errors="coerce")
    df["Predicted"] = pd.to_numeric(df["Predicted"], errors="coerce")

    if df.empty:
        continue

    latest_row = df.tail(1)
    latest_quarters.append(latest_row["Quarter"].values[0])

    actual_val = latest_row["Actual"].values[0]
    predicted_val = latest_row["Predicted"].values[0]

    if pd.notna(actual_val):
        vehicle_actual_total += actual_val
    if pd.notna(predicted_val):
        vehicle_predicted_total += predicted_val

vehicle_quarter = latest_quarters[0] if latest_quarters else "—"
vehicle_actual_str = f"{vehicle_actual_total:,.0f}" if vehicle_actual_total else "NA"
vehicle_predicted_str = f"{vehicle_predicted_total:,.0f}" if vehicle_predicted_total else "NA"


# --- Renewable Capacity Addition (Solar + Wind) ---
re_sheets = ["Solar", "Wind"]
re_path = "data/Solar&Wind_Model.xlsx"

re_actual_total = 0
re_predicted_total = 0
re_quarter = "—"
actual_missing = True
predicted_missing = True

re_df_dict = pd.read_excel(re_path, sheet_name=None)

for sheet in re_sheets:
    df = re_df_dict[sheet]
    df.columns = [col.strip() for col in df.columns]
    df = df.dropna(subset=["Predicted"])
    df["Actual"] = pd.to_numeric(df["Actual"], errors="coerce")
    df["Predicted"] = pd.to_numeric(df["Predicted"], errors="coerce")

    if df.empty:
        continue

    latest_row = df.tail(1)
    re_quarter = latest_row["Quarter"].values[0]

    actual_val = latest_row["Actual"].values[0]
    predicted_val = latest_row["Predicted"].values[0]

    if pd.notna(actual_val):
        re_actual_total += actual_val
        actual_missing = False
    if pd.notna(predicted_val):
        re_predicted_total += predicted_val
        predicted_missing = False

re_actual_str = f"{re_actual_total:,.0f}" if not actual_missing else "NA"
re_predicted_str = f"{re_predicted_total:,.0f}" if not predicted_missing else "NA"


# --- Header ---
st.markdown("### Sectoral Forecasts")


# --- Card Renderer ---
def render_card(title, link, quarter="—", actual="—", predicted="—", unit=""):
    st.markdown(f"""
    <a href='/{link}' target='_self' style='text-decoration: none;'>
        <div style='
            width: 100%;
            border-radius: 12px;
            padding: 16px;
            background-color: #111;
            border: 1px solid #333;
            box-shadow: 1px 2px 6px rgba(0,0,0,0.15);
            transition: 0.2s ease-in-out;
        ' onmouseover="this.style.backgroundColor='#1e1e1e'" onmouseout="this.style.backgroundColor='#111'">
            <div style='font-size: 15px; font-weight: 600; color: #fff;'>
                {title} ({unit}) →
            </div>
            <div style='font-size: 13px; color: #ccc; padding-top: 4px;'>Quarter: {quarter}</div>
            <div style='font-size: 13px; color: #ccc;'>
                <span style='color: #007381;'>Actual: {actual}</span> &nbsp;|&nbsp;
                <span style='color: #E85412;'>Predicted: {predicted}</span>
            </div>
        </div>
    </a>
    """, unsafe_allow_html=True)


# --- First row ---
col1, col2 = st.columns(2)
with col1:
    render_card("Fertiliser Demand Forecast", "fertiliser_demand", fert_quarter, fert_actual_str, fert_predicted_str, unit="MMT")
with col2:
    render_card("Vehicle Production Forecast", "vehicle_production", vehicle_quarter, vehicle_actual_str, vehicle_predicted_str, unit="Units")

# --- Spacer ---
st.markdown("<div style='margin: 20px 0;'></div>", unsafe_allow_html=True)

# --- Second row ---
col3, col4 = st.columns(2)
with col3:
    render_card("Houses Construction Forecast", "houses_constructed", house_quarter, house_actual_str, house_predicted_str, unit="Units")
with col4:
    render_card("Renewable Capacity Addition Forecast", "RE_addition", re_quarter, re_actual_str, re_predicted_str, unit="MW")