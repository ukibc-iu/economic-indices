import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit.components.v1 as components
import os
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import MinMaxScaler

st.set_page_config(page_title="Infrastructure Activity Index (IAI)", layout="wide")
st.title("Infrastructure Activity Index (IAI)")

# --- Load Data ---
@st.cache_data

def load_data():
    file_path = os.path.join(os.path.dirname(__file__), '..', 'data', 'Infrastructure_Activity.csv')

    try:
        df = pd.read_csv(file_path)
    except FileNotFoundError:
        st.error("❌ Could not find the CSV file. Check the path: data/Infrastructure_Activity.csv")
        return None

    df.columns = df.columns.str.strip()

    expected_cols = [
        "Date",
        "Highway construction actual",
        "Railway line construction actual",
        "Power T&D line constr (220KV plus)",
        "Cement price",
        "GVA: construction (Basic Price)",
        "Budgetary allocation for infrastructure sector"
    ]

    for col in expected_cols:
        if col not in df.columns:
            st.error(f"❌ Missing column: `{col}`")
            return None

    df['Date'] = pd.to_datetime(df['Date'], errors='coerce')
    df.dropna(subset=['Date'], inplace=True)
    df['Month'] = df['Date'].dt.strftime('%b-%y')

    for col in expected_cols[1:]:
        df[col] = pd.to_numeric(df[col], errors='coerce')

    df.dropna(inplace=True)

    # --- Regression-Based Weights ---
    idv_cols = [
        "Highway construction actual",
        "Railway line construction actual",
        "Power T&D line constr (220KV plus)",
        "Cement price",
        "Budgetary allocation for infrastructure sector"
    ]
    target_col = "GVA: construction (Basic Price)"

    scaler = MinMaxScaler()
    X_scaled = scaler.fit_transform(df[idv_cols])
    X = pd.DataFrame(X_scaled, columns=idv_cols)
    y = df[target_col].values

    model = LinearRegression()
    model.fit(X, y)
    weights = model.coef_ / model.coef_.sum()

    df['IAI'] = X.dot(weights)

    df = df.sort_values('Date')
    return df

# Load and validate data
df = load_data()
if df is None or df.empty:
    st.warning("⚠️ No valid data available. Please check your CSV file.")
    st.stop()

# --- KPI Display ---
latest_row = df.iloc[-1]
latest_month = latest_row['Month']
latest_score = latest_row['IAI']
latest_gva = latest_row['GVA: construction (Basic Price)']

kpi_style = """
<style>
.card {
    padding: 1rem;
    border-radius: 16px;
    box-shadow: 0 4px 12px rgba(0,0,0,0.1);
    color: white;
    font-weight: bold;
    text-align: center;
}
.green-card { background: linear-gradient(#003366, #006699, #3399cc); }
.grey-card { background: linear-gradient(#666666, #999999, #cccccc); }
.red-card { background: linear-gradient(#990000, #cc0000, #ff3300); }
</style>
"""
st.markdown(kpi_style, unsafe_allow_html=True)

col1, col2, col3 = st.columns(3)

with col1:
    st.markdown(f"""
        <div class="card green-card">
            <div style="font-size: 1.2rem;">🗓 Latest Month</div>
            <div style="font-size: 2rem;">{latest_month}</div>
        </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown(f"""
        <div class="card grey-card">
            <div style="font-size: 1.2rem;">📊 IAI Score</div>
            <div style="font-size: 2rem;">{latest_score:.2f}</div>
        </div>
    """, unsafe_allow_html=True)

with col3:
    st.markdown(f"""
        <div class="card red-card">
            <div style="font-size: 1.2rem;">🏗️ GVA Construction</div>
            <div style="font-size: 2rem;">₹{latest_gva:,.0f} Cr</div>
        </div>
    """, unsafe_allow_html=True)

# --- Select Month ---
selected_month = st.selectbox("📅 Select Month", df['Month'].unique().tolist())
filtered = df[df['Month'] == selected_month]

if filtered.empty:
    st.warning("⚠️ No data found for selected month.")
    st.stop()

# === CHART WRAPPER ===
def wrapped_chart(title, fig, height=420):
    chart_html = fig.to_html(include_plotlyjs="cdn", full_html=False)
    components.html(f"""
    <div style="
        background-color: #1e1e1e;
        padding: 1rem;
        border-radius: 12px;
        margin-bottom: 1.5rem;
        box-shadow: 0 2px 5px rgba(0,0,0,0.2);
        color: white;
    ">
        <h4 style="margin-top: 0; margin-bottom: 10px;">{title}</h4>
        {chart_html}
    </div>
    """, height=height + 60)

# === Gauge ===
fig_gauge = go.Figure(go.Indicator(
    mode="gauge+number",
    value=filtered['IAI'].values[0],
    number={'font': {'color': 'white'}},
    gauge={
        'axis': {'range': [0, 1], 'tickcolor': 'white'},
        'bar': {'color': "black"},
        'steps': [
            {'range': [0, 0.2], 'color': "#ff0000"},
            {'range': [0.2, 0.4], 'color': "#ffa500"},
            {'range': [0.4, 0.6], 'color': "#ffff00"},
            {'range': [0.6, 0.8], 'color': "#90ee90"},
            {'range': [0.8, 1.0], 'color': "#008000"},
        ]
    }
))
fig_gauge.update_layout(height=400, paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font_color='white')
wrapped_chart(f"IAI Gauge – {selected_month}", fig_gauge)

# === Line Chart ===
st.subheader("📈 IAI Over Time")
fig_line = px.line(df, x='Month', y='IAI', markers=True, line_shape='linear', color_discrete_sequence=['#FF5733'])
fig_line.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font_color='white', height=450)
st.plotly_chart(fig_line, use_container_width=True)

# === Data Table ===
with st.expander("🔍 View Underlying Data Table"):
    st.dataframe(df[[
        'Month', 'Highway construction actual', 'Railway line construction actual',
        'Power T&D line constr (220KV plus)', 'Cement price',
        'GVA: construction (Basic Price)', 'Budgetary allocation for infrastructure sector', 'IAI'
    ]])