import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit.components.v1 as components

st.set_page_config(page_title="Housing Affordability Index", layout="wide")
st.title("🏠 Housing Affordability Stress Index")
st.markdown("*This index reflects housing stress by comparing property prices to income levels and housing loan burden across time.*")

# --- Load Data ---
@st.cache_data
def load_data():
    try:
        df = pd.read_csv("data/Housing_Affordability.csv")
    except FileNotFoundError:
        st.error("❌ Could not find 'data/Housing_Affordability.csv'. Make sure it's in the correct folder.")
        return None

    df.columns = df.columns.str.strip()
    df['Date'] = pd.to_datetime(df['Date'], errors='coerce')
    df.dropna(subset=['Date'], inplace=True)

    df['Month'] = df['Date'].dt.strftime('%b-%y')

    def format_quarter(row):
        q = f"Q{((row['Date'].month - 1) // 3 + 1)}"
        fy = row['Date'].year if row['Date'].month >= 4 else row['Date'].year - 1
        return f"{q} {fy}-{str(fy + 1)[-2:]}"
    df['QuarterFormatted'] = df.apply(format_quarter, axis=1)

    # Clean and convert numerics
    df['Per Capita NNI'] = (
        df['Per Capita NNI'].astype(str)
        .str.replace(',', '')
        .str.replace('₹', '')
        .str.strip()
    )
    df['Per Capita NNI'] = pd.to_numeric(df['Per Capita NNI'], errors='coerce')

    df['Housing Loan Interest Rate'] = (
        df['Housing Loan Interest Rate'].astype(str)
        .str.replace('%', '')
        .str.strip()
    )
    df['Housing Loan Interest Rate'] = pd.to_numeric(df['Housing Loan Interest Rate'], errors='coerce')

    df['Urbanization Rate'] = (
        df['Urbanization Rate'].astype(str)
        .str.replace('%', '')
        .str.strip()
    )
    df['Urbanization Rate'] = pd.to_numeric(df['Urbanization Rate'], errors='coerce')

    df['Property Price Index'] = pd.to_numeric(df['Property Price Index'], errors='coerce')

    df.dropna(inplace=True)

    # Affordability metrics
    LOAN_ELIGIBILITY_FACTOR = 5
    df['Affordability Ratio'] = df['Property Price Index'] / (df['Per Capita NNI'] * LOAN_ELIGIBILITY_FACTOR)
    df['Affordability Score'] = (
        df['Affordability Ratio'] - df['Affordability Ratio'].min()
    ) / (df['Affordability Ratio'].max() - df['Affordability Ratio'].min())

    return df.sort_values('Date')

df = load_data()
if df is None or df.empty:
    st.stop()

# --- Latest KPIs ---
latest = df.iloc[-1]
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
.green-card { background: linear-gradient(#004d00, #00cc44); }
.grey-card { background: linear-gradient(#333333, #666666); }
.red-card { background: linear-gradient(#990000, #cc3300); }
</style>
"""
st.markdown(kpi_style, unsafe_allow_html=True)

col1, col2, col3 = st.columns(3)

with col1:
    st.markdown(f"""
        <div class="card green-card">
            <div style="font-size: 1.2rem;">🗓 Latest Period</div>
            <div style="font-size: 2rem;">{latest['Month']} / {latest['QuarterFormatted']}</div>
        </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown(f"""
        <div class="card grey-card">
            <div style="font-size: 1.2rem;">🏠 Affordability Ratio</div>
            <div style="font-size: 2rem;">{latest['Affordability Ratio']:.2f}×</div>
        </div>
    """, unsafe_allow_html=True)

with col3:
    st.markdown(f"""
        <div class="card red-card">
            <div style="font-size: 1.2rem;">📉 Affordability Score</div>
            <div style="font-size: 2rem;">{latest['Affordability Score']:.2f}</div>
        </div>
    """, unsafe_allow_html=True)

# --- Filter Preview ---
preview_type = st.selectbox("📅 Preview Type", ["Monthly", "Quarterly"])
period_list = df['Month'].unique() if preview_type == "Monthly" else df['QuarterFormatted'].unique()
selected_period = st.selectbox("📆 Select Period", period_list)

if preview_type == "Monthly":
    filtered = df[df['Month'] == selected_period]
else:
    filtered = df[df['QuarterFormatted'] == selected_period]

if filtered.empty:
    st.warning("⚠️ No data found for selected period.")
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

# === Donut - Housing Loan Factors ===
left_col, right_col = st.columns(2)

with left_col:
    loan_data = {
        "Component": ["Loan Interest Rate", "Urbanization Rate"],
        "Value": [
            filtered['Housing Loan Interest Rate'].values[0],
            filtered['Urbanization Rate'].values[0]
        ]
    }
    fig_donut = px.pie(loan_data, names="Component", values="Value", hole=0.5,
                       color_discrete_sequence=['#ff9999', '#66b3ff'])
    fig_donut.update_traces(textposition='inside', textinfo='percent+label')
    fig_donut.update_layout(height=400,
                            paper_bgcolor='rgba(0,0,0,0)',
                            plot_bgcolor='rgba(0,0,0,0)',
                            font_color='white')
    wrapped_chart(f"Loan & Urbanization Mix – {selected_period}", fig_donut)

with right_col:
    score_val = filtered['Affordability Score'].values[0]
    fig_gauge = go.Figure(go.Indicator(
        mode="gauge+number",
        value=score_val,
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
    fig_gauge.update_layout(height=400,
                            paper_bgcolor='rgba(0,0,0,0)',
                            plot_bgcolor='rgba(0,0,0,0)',
                            font_color='white')
    wrapped_chart(f"Affordability Score – {selected_period}", fig_gauge)

# === Line Chart ===
st.subheader("📈 Affordability Trend Over Time")
fig_line = px.line(df, x='Month', y='Affordability Score', markers=True,
                   line_shape='linear', color_discrete_sequence=['#33ccff'])
fig_line.update_layout(
    paper_bgcolor='rgba(0,0,0,0)',
    plot_bgcolor='rgba(0,0,0,0)',
    font_color='white',
    height=450
)
st.plotly_chart(fig_line, use_container_width=True)

# === Raw Data Table ===
with st.expander("🔍 View Full Dataset"):
    st.dataframe(df[[
        'Month', 'QuarterFormatted', 'Affordability Score', 'Affordability Ratio',
        'Property Price Index', 'Per Capita NNI', 'Housing Loan Interest Rate', 'Urbanization Rate'
    ]])