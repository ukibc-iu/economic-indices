import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

st.set_page_config(page_title="Housing Affordability Index", layout="wide")
st.title("🏡 Housing Affordability Index Dashboard")
st.markdown("*The Housing Affordability Index reflects how affordable residential property is for an average individual, using per capita income and property prices.*")

# --- Load Data ---
@st.cache_data
def load_data():
    df = pd.read_csv("data/Housing_Affordability.csv")
    df.columns = df.columns.str.strip()

    # Explicit date parsing fix
    df['Date'] = pd.to_datetime(df['Date'], format='%m/%d/%Y', errors='coerce')
    df.dropna(subset=['Date'], inplace=True)

    df['Month'] = df['Date'].dt.strftime('%b-%y')

    def format_quarter(row):
        q = f"Q{((row['Date'].month - 1) // 3 + 1)}"
        fy = row['Date'].year if row['Date'].month >= 4 else row['Date'].year - 1
        return f"{q} {fy}-{str(fy + 1)[-2:]}"
    df['QuarterFormatted'] = df.apply(format_quarter, axis=1)

    df['Property Price Index'] = pd.to_numeric(df['Property Price Index'], errors='coerce')
    df['Per Capita NNI'] = pd.to_numeric(df['Per Capita NNI'], errors='coerce')

    # Affordability Index calculation
    LOAN_FACTOR = 0.003
    df['Affordability Index'] = (df['Per Capita NNI'] / df['Property Price Index']) * LOAN_FACTOR

    df.dropna(inplace=True)
    df = df.sort_values('Date')

    return df

df = load_data()

if df is None or df.empty:
    st.warning("⚠️ No valid data available. Please check your CSV.")
    st.stop()

# Debug: Check date range
# st.write("Earliest date:", df['Date'].min())
# st.write("Latest date:", df['Date'].max())

# --- Latest KPIs ---
latest_row = df.iloc[-1]
latest_month = latest_row['Month']
latest_quarter = latest_row['QuarterFormatted']
latest_index = latest_row['Affordability Index']
latest_price = latest_row['Property Price Index']

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
.green-card { background: linear-gradient(#004466, #006699, #3399cc); }
.grey-card { background: linear-gradient(#336699, #6699cc, #99ccff); }
.red-card { background: linear-gradient(#cccccc, #999999, #666666); }
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
            <div style="font-size: 1.2rem;">📊 Affordability Index</div>
            <div style="font-size: 2rem;">{latest_index:.2f}</div>
        </div>
    """, unsafe_allow_html=True)

with col3:
    st.markdown(f"""
        <div class="card red-card">
            <div style="font-size: 1.2rem;">📈 Property Price Index</div>
            <div style="font-size: 2rem;">{latest_price:.2f}</div>
        </div>
    """, unsafe_allow_html=True)

# --- Preview Type ---
preview_type = st.selectbox("🗓 Preview Type", ["Monthly", "Quarterly"])
period_list = df['Month'].unique().tolist() if preview_type == "Monthly" else df['QuarterFormatted'].unique().tolist()
selected_period = st.selectbox("📆 Select Month or Quarter", period_list)

filtered = df[df['Month'] == selected_period] if preview_type == "Monthly" else df[df['QuarterFormatted'] == selected_period]
if filtered.empty:
    st.warning("⚠️ No data found for selected period.")
    st.stop()

# --- Gauge Chart ---
score_val = filtered['Affordability Index'].values[0]
fig_gauge = go.Figure(go.Indicator(
    mode="gauge+number",
    value=score_val,
    number={'font': {'color': 'white'}},
    domain={'x': [0, 1], 'y': [0, 1]},
    gauge={
        'axis': {'range': [0, 1], 'tickcolor': 'white'},
        'bar': {'color': "black"},
        'steps': [
            {'range': [0, 0.2], 'color': "#ff0000"},
            {'range': [0.2, 0.3], 'color': "#ffa500"},
            {'range': [0.3, 0.4], 'color': "#ffff00"},
            {'range': [0.4, 0.6], 'color': "#90ee90"},
            {'range': [0.6, 1], 'color': "#008000"},
        ]
    }
))
fig_gauge.update_layout(height=400, paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font_color='white')
st.plotly_chart(fig_gauge, use_container_width=True)

# --- Line Chart ---
st.subheader("📈 Affordability Index Over Time")
fig_line = px.line(df, x='Date', y='Affordability Index', markers=True,
                   line_shape='linear', color_discrete_sequence=['#FF5733'])
fig_line.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
                       font_color='white', height=450)
st.plotly_chart(fig_line, use_container_width=True)

# --- Data Table ---
with st.expander("🔍 View Underlying Data Table"):
    st.dataframe(df[['Date', 'Month', 'QuarterFormatted', 'Affordability Index', 'Property Price Index', 'Per Capita NNI']])