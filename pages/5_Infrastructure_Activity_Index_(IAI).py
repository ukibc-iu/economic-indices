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
st.markdown("*The Infrastructure Activity Index (IAI) tracks the pace of India’s infrastructure development by synthesizing key construction and investment trends.*")
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

    # Regression-Based Weights
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

    def get_fiscal_quarter_label(date):
        month = date.month
        year = date.year
        if month >= 4:
            fy_start = year
            fy_end = year + 1
        else:
            fy_start = year - 1
            fy_end = year
        if month in [4, 5, 6]:
            q = "Q1"
        elif month in [7, 8, 9]:
            q = "Q2"
        elif month in [10, 11, 12]:
            q = "Q3"
        else:
            q = "Q4"
        return f"{q} {fy_start}-{str(fy_end)[-2:]}"
    
    df['Fiscal Quarter'] = df['Date'].apply(get_fiscal_quarter_label)
    df = df.sort_values('Date')
    return df

# --- Load Data ---
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
.green-card { background: linear-gradient(#453717, #624E20, #82672A); }
.grey-card { background: linear-gradient(#A78437, #C49E4D, #D4AF37); }
.red-card { background: linear-gradient(#DD9E4B, #D9B84F, #E0C56E); }
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
            <div style="font-size: 1.2rem;">IAI Score</div>
            <div style="font-size: 2rem;">{latest_score:.2f}</div>
        </div>
    """, unsafe_allow_html=True)
with col3:
    st.markdown(f"""
        <div class="card red-card">
            <div style="font-size: 1.2rem;">GVA Construction</div>
            <div style="font-size: 2rem;">₹{latest_gva:,.0f} Cr</div>
        </div>
    """, unsafe_allow_html=True)

# --- View Selector ---
st.markdown("---")
st.subheader("📅 View Mode")
view_type = st.radio("Select data preview:", ["Monthly", "Quarterly"], horizontal=True)

# --- Period Selection ---
if view_type == "Monthly":
    month_options = df['Month'].unique().tolist()
    default_month = df['Month'].iloc[-1]
    selected_month = st.selectbox("🗓 Select Month", month_options, index=month_options.index(default_month))
    filtered = df[df['Month'] == selected_month]
    display_label = selected_month
else:
    quarter_options = df['Fiscal Quarter'].unique().tolist()
    default_quarter = df['Fiscal Quarter'].iloc[-1]
    selected_quarter = st.selectbox("📆 Select Quarter", quarter_options, index=quarter_options.index(default_quarter))
    filtered = df[df['Fiscal Quarter'] == selected_quarter]
    filtered = filtered.mean(numeric_only=True).to_frame().T
    display_label = selected_quarter

if filtered.empty:
    st.warning("⚠️ No data found for selected time period.")
    st.stop()

# === CHART WRAPPER ===
def wrapped_chart(title, figure):
    with st.container(border=True):
        st.markdown(f"**{title}**")
        st.plotly_chart(figure, use_container_width=True)

# === SIDE-BY-SIDE GAUGE AND SCATTER ===
col1, col2 = st.columns(2)

# Gauge Chart
with col1:
    fig_gauge = go.Figure(go.Indicator(
        mode="gauge+number",
        value=filtered['IAI'].values[0],
        number={'font': {'color': 'white'}},
        gauge={
            'axis': {'range': [0, 1], 'tickcolor': 'white'},
            'bar': {'color': "black"},
            'steps': [
                {'range': [0, 0.2], 'color': "#C49E4D"},
                {'range': [0.2, 0.4], 'color': "#A78437"},
                {'range': [0.4, 0.6], 'color': "#82672A"},
                {'range': [0.6, 0.8], 'color': "#624E20"},
                {'range': [0.8, 1.0], 'color': "#453717"},
            ]
        }
    ))
    fig_gauge.update_layout(height=400, paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font_color='white')
    wrapped_chart(f"IAI Gauge – {display_label}", fig_gauge)

# Chart #3 – Scatter: IAI vs GVA
with col2:
    fig_scatter = px.scatter(
        df,
        x="IAI",
        y="GVA: construction (Basic Price)",
        trendline="ols",
        color_discrete_sequence=["#A78437"],
        labels={
            "IAI": "Infrastructure Activity Index",
            "GVA: construction (Basic Price)": "GVA: Construction (₹ Cr)"
        }
    )
    fig_scatter.update_traces(marker=dict(size=8, opacity=0.85))
    fig_scatter.update_layout(
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font_color='white',
        height=400
    )
    wrapped_chart("IAI vs GVA Construction (All Periods)", fig_scatter)
st.markdown("### 💡 Expert Opinion")

# Expert opinion (static for now)
expert_opinion = "Infrastructure Activity Index is currently..."

# Styled display box
st.markdown(f"""
<div style="
    background-color: rgba(100, 100, 100, 0.3);
    padding: 1rem;
    border-radius: 10px;
    border: 1px solid rgba(255, 255, 255, 0.2);
    color: white;
    font-style: italic;
    font-size: 1rem;
">
    {expert_opinion}
</div>
""", unsafe_allow_html=True)
# --- Line Chart ---
st.subheader("📈 IAI Over Time")
if view_type == "Monthly":
    fig_line = px.line(df, x='Month', y='IAI', markers=False, line_shape='linear', color_discrete_sequence=['#A78437'])
else:
    df_q = df.groupby('Fiscal Quarter').mean(numeric_only=True).reset_index()
    fig_line = px.line(df_q, x='Fiscal Quarter', y='IAI', markers=True, line_shape='linear', color_discrete_sequence=['#A78437'])

fig_line.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font_color='white', height=450)
st.plotly_chart(fig_line, use_container_width=True)

# --- Data Table ---
with st.expander("🔍 View Underlying Data Table"):
    st.dataframe(df[[ 
        'Month', 'Highway construction actual', 'Railway line construction actual',
        'Power T&D line constr (220KV plus)', 'Cement price',
        'GVA: construction (Basic Price)', 'Budgetary allocation for infrastructure sector', 'IAI'
    ]])