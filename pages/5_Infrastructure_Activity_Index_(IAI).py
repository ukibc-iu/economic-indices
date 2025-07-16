import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit.components.v1 as components

st.set_page_config(page_title="Infrastructure Activity Index", layout="wide")
st.title("🏗️ Infrastructure Activity Index (IAI)")
st.markdown("*The Infrastructure Activity Index (IAI) tracks national infrastructure build-out across sectors such as highways, railways, power transmission, and more.*")

# --- Load Data ---
@st.cache_data
def load_data():
    try:
        df = pd.read_csv("data/Infrastructure_Activity.csv")
    except FileNotFoundError:
        st.error("❌ Could not find 'data/Infrastructure_Activity.csv'. Make sure it's in the correct folder.")
        return None
    df.columns = df.columns.str.strip()

    df['Date'] = pd.to_datetime(df['Date'], format='%m/%d/%Y', errors='coerce')
    df.dropna(subset=['Date'], inplace=True)
    df['Month'] = df['Date'].dt.strftime('%b-%y')

    def format_quarter(row):
        q = f"Q{((row['Date'].month - 1) // 3 + 1)}"
        fy = row['Date'].year if row['Date'].month >= 4 else row['Date'].year - 1
        return f"{q} {fy}-{str(fy + 1)[-2:]}"
    df['QuarterFormatted'] = df.apply(format_quarter, axis=1)

    df.dropna(inplace=True)

    # Normalize indicators
    for col in [
        'Highway construction actual',
        'Railway line construction actual',
        'Power T&D line constr (220KV plus)',
        'Cement price',
        'GVA: construction (Basic Price)',
        'Budgetary allocation for infrastructure sector '
    ]:
        df[col] = pd.to_numeric(df[col], errors='coerce')

    df.dropna(inplace=True)

    # Min-max normalization
    df['Norm_Highway'] = (df['Highway construction actual'] - df['Highway construction actual'].min()) / (df['Highway construction actual'].max() - df['Highway construction actual'].min())
    df['Norm_Rail'] = (df['Railway line construction actual'] - df['Railway line construction actual'].min()) / (df['Railway line construction actual'].max() - df['Railway line construction actual'].min())
    df['Norm_Power'] = (df['Power T&D line constr (220KV plus)'] - df['Power T&D line constr (220KV plus)'].min()) / (df['Power T&D line constr (220KV plus)'].max() - df['Power T&D line constr (220KV plus)'].min())
    df['Norm_Cement'] = 1 - ((df['Cement price'] - df['Cement price'].min()) / (df['Cement price'].max() - df['Cement price'].min()))  # negative indicator
    df['Norm_GVA'] = (df['GVA: construction (Basic Price)'] - df['GVA: construction (Basic Price)'].min()) / (df['GVA: construction (Basic Price)'].max() - df['GVA: construction (Basic Price)'].min())
    df['Norm_Budget'] = (df['Budgetary allocation for infrastructure sector '] - df['Budgetary allocation for infrastructure sector '].min()) / (df['Budgetary allocation for infrastructure sector '].max() - df['Budgetary allocation for infrastructure sector '].min())

    # IAI Score (weights can be adjusted)
    df['IAI Score'] = (
        0.2 * df['Norm_Highway'] +
        0.2 * df['Norm_Rail'] +
        0.2 * df['Norm_Power'] +
        0.1 * df['Norm_Cement'] +
        0.2 * df['Norm_GVA'] +
        0.1 * df['Norm_Budget']
    )

    df = df.sort_values('Date')
    return df


df = load_data()
if df is None or df.empty:
    st.warning("⚠️ No valid data available. Please check your CSV.")
    st.stop()

latest_row = df.iloc[-1]
latest_month = latest_row['Month']
latest_quarter = latest_row['QuarterFormatted']
latest_score = latest_row['IAI Score']
latest_gva = latest_row['GVA: construction (Basic Price)']

# --- KPI Cards ---
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
.grey-card { background: linear-gradient(#003300, #336600, #66cc66); }
.red-card { background: linear-gradient(#660000, #993333, #cc6666); }
</style>
"""
st.markdown(kpi_style, unsafe_allow_html=True)
col1, col2, col3 = st.columns(3)

with col1:
    st.markdown(f"""
        <div class="card green-card">
            <div style="font-size: 1.2rem;">🗓 Latest Period</div>
            <div style="font-size: 2rem;">{latest_month} / {latest_quarter}</div>
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
            <div style="font-size: 1.2rem;">🏗 GVA from Construction</div>
            <div style="font-size: 2rem;">{latest_gva:,.0f}</div>
        </div>
    """, unsafe_allow_html=True)

# --- Preview Selection ---
preview_type = st.selectbox("📅 Preview Type", ["Monthly", "Quarterly"])
period_list = df['Month'].unique().tolist() if preview_type == "Monthly" else df['QuarterFormatted'].unique().tolist()
selected_period = st.selectbox("📆 Select Month or Quarter", period_list)

filtered = df[df['Month'] == selected_period] if preview_type == "Monthly" else df[df['QuarterFormatted'] == selected_period]
if filtered.empty:
    st.warning("⚠️ No data found for selected period.")
    st.stop()

# === Charts ===
left_col, right_col = st.columns(2)

with left_col:
    donut_data = {
        "Category": ["Highway", "Railway", "Power T&D"],
        "Value": [
            filtered['Highway construction actual'].values[0],
            filtered['Railway line construction actual'].values[0],
            filtered['Power T&D line constr (220KV plus)'].values[0]
        ]
    }
    fig_donut = px.pie(donut_data, values='Value', names='Category', hole=0.5,
                       color_discrete_sequence=['#1f77b4', '#2ca02c', '#ff7f0e'])
    fig_donut.update_traces(textposition='inside', textinfo='percent+label')
    fig_donut.update_layout(height=400, paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font_color='white')
    components.html(fig_donut.to_html(include_plotlyjs="cdn", full_html=False), height=460)

with right_col:
    fig_gauge = go.Figure(go.Indicator(
        mode="gauge+number",
        value=filtered['IAI Score'].values[0],
        number={'font': {'color': 'white'}},
        domain={'x': [0, 1], 'y': [0, 1]},
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
    components.html(fig_gauge.to_html(include_plotlyjs="cdn", full_html=False), height=460)

# === Line Chart ===
st.subheader("📈 IAI Score Over Time")
fig_line = px.line(df, x='Month', y='IAI Score', markers=True, color_discrete_sequence=['#FF5733'])
fig_line.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font_color='white', height=450)
st.plotly_chart(fig_line, use_container_width=True)

# === Data Table ===
with st.expander("🔍 View Underlying Data Table"):
    st.dataframe(df[[
        'Month', 'QuarterFormatted', 'IAI Score',
        'Highway construction actual', 'Railway line construction actual', 'Power T&D line constr (220KV plus)',
        'Cement price', 'GVA: construction (Basic Price)', 'Budgetary allocation for infrastructure sector '
    ]])