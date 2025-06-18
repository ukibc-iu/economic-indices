import streamlit as st
import pandas as pd
from sklearn.decomposition import PCA
from sklearn.preprocessing import StandardScaler
import plotly.graph_objects as go

# === Streamlit Setup ===
st.set_page_config(layout="wide")
st.title("Consumer Demand Index (CDI)")

st.markdown('<p style="font-style: italic;">The Consumer Demand Index captures shifts in real-time consumer activity, helping forecast economic momentum through trends in spending, mobility, and energy use.</p>', unsafe_allow_html=True)

# === Custom CSS for KPI Cards ===
st.markdown("""
<style>
.kpi-container {
    display: flex;
    gap: 1rem;
    flex-wrap: wrap;
    margin-bottom: 1rem;
}
.kpi-card {
    flex: 1;
    padding: 1rem;
    border-radius: 16px;
    background: rgba(255, 255, 255, 0.08);
    backdrop-filter: blur(12px);
    -webkit-backdrop-filter: blur(12px);
    color: white;
    min-width: 200px;
    border: 1px solid rgba(255, 255, 255, 0.15);
    box-shadow: 0 4px 20px rgba(0, 0, 0, 0.3);
}
.kpi-title {
    font-size: 1rem;
    font-weight: 600;
    margin-bottom: 0.3rem;
    color: #ddd;
}
.kpi-value {
    font-size: 1.8rem;
    font-weight: bold;
}
.kpi-delta {
    font-size: 1.2rem;
    margin-top: 0.2rem;
    font-weight: bold;
}
.bg-1 {
    background: linear-gradient(135deg, rgba(160, 102, 255, 0.08), rgba(233, 102, 255, 0.6));
}
.bg-2 {
    background: linear-gradient(135deg, rgba(0, 198, 255, 0.08), rgba(0, 114, 255, 0.6));
}
.bg-3 {
    background: linear-gradient(135deg, rgba(0, 255, 231, 0.08), rgba(0, 195, 255, 0.6));
}
</style>
""", unsafe_allow_html=True)

# === Load Data ===
DEFAULT_DATA_PATH = "data/Consumer_Demand_Index.csv"
try:
    df = pd.read_csv(DEFAULT_DATA_PATH)
except Exception as e:
    st.error(f"Error loading data: {e}")
    st.stop()

df.columns = df.columns.str.strip()
df['Date'] = pd.to_datetime(df['Date'], errors='coerce')
df = df.dropna(subset=['Date'])

features = ['UPI Transactions', 'GST Revenue', 'Vehicle Sales', 'Housing Sales', 'Power Consumption']
if any(col not in df.columns for col in features):
    st.error("Missing required feature columns.")
    st.stop()

df = df.dropna(subset=features)

# === Compute PCA ===
scaler_std = StandardScaler()
scaled_features = scaler_std.fit_transform(df[features])
pca = PCA(n_components=1)
pca_components = pca.fit_transform(scaled_features)

df['CDI_Real'] = pca_components[:, 0]
df['CDI_Scaled'] = df['CDI_Real'].clip(-5, 5)
df['Month'] = df['Date'].dt.strftime('%b-%Y')

def get_fiscal_quarter(date):
    m, y = date.month, date.year
    if m in [4, 5, 6]: q, fy = 'Q1', y
    elif m in [7, 8, 9]: q, fy = 'Q2', y
    elif m in [10, 11, 12]: q, fy = 'Q3', y
    else: q, fy = 'Q4', y - 1
    return f"{q} {fy}-{str(fy+1)[-2:]}"

df['Fiscal_Quarter'] = df['Date'].apply(get_fiscal_quarter)

# === KPI-themed colors ===
kpi_theme_colors = [
    'rgba(160, 102, 255, 0.9)',
    'rgba(233, 102, 255, 0.9)',
    'rgba(0, 198, 255, 0.9)',
    'rgba(0, 114, 200, 0.9)',
    'rgba(0, 255, 150, 0.9)'
]

# === Mode Selection ===
mode = st.radio("Select View Mode", ['Monthly', 'Quarterly'], horizontal=True)

# Get latest row for KPI cards
latest_row = df.sort_values('Date').iloc[-1]
latest_real = latest_row['CDI_Real']
latest_scaled = latest_row['CDI_Scaled']
latest_month = latest_row['Month']
latest_quarter = latest_row['Fiscal_Quarter']

df_sorted = df.sort_values(by='Date')

# === KPI Cards ===
st.markdown(f"""
<div class="kpi-container">
    <div class="kpi-card bg-1">
        <div class="kpi-title">Actual CDI</div>
        <div class="kpi-value">{latest_real:.2f}</div>
    </div>
    <div class="kpi-card bg-2">
        <div class="kpi-title">{'Month' if mode == 'Monthly' else 'Fiscal Quarter'}</div>
        <div class="kpi-value">{latest_month if mode == 'Monthly' else latest_quarter}</div>
    </div>
    <div class="kpi-card bg-3">
        <div class="kpi-title">Scaled CDI</div>
        <div class="kpi-value">{latest_scaled:.2f}</div>
    </div>
</div>
""", unsafe_allow_html=True)

st.markdown("---")

# === Time Period Selection ===
if mode == 'Monthly':
    months = sorted(df['Month'].unique())
    selected_month = st.selectbox("Select Month", months, index=months.index(latest_month))
    df_filtered = df[df['Month'] == selected_month]
    selected_idx = df_filtered.index[0]

    label_period = selected_month
    line_x = df_sorted['Date']
    line_y = df_sorted['CDI_Real']
    line_title = "CDI Trend - Monthly"
    xaxis_title = "Month"
    xaxis_type = "date"
    selected_quarter = None

    # ✅ Add these two lines:
    selected_real = df_filtered['CDI_Real'].values[0]
    selected_scaled = df_filtered['CDI_Scaled'].values[0]

else:
    quarters = sorted(df['Fiscal_Quarter'].unique())
    selected_quarter = st.selectbox("Select Quarter", quarters, index=quarters.index(latest_quarter))

    quarter_df = df.groupby('Fiscal_Quarter', sort=False)['CDI_Real'].mean().reset_index()
    quarter_df['CDI_Scaled'] = df.groupby('Fiscal_Quarter', sort=False)['CDI_Scaled'].mean().values

    label_period = selected_quarter
    line_x = quarter_df['Fiscal_Quarter']
    line_y = quarter_df['CDI_Real']
    line_title = "CDI Trend - Quarterly"
    xaxis_title = "Fiscal Quarter"
    xaxis_type = "category"
    selected_idx = None

    # ✅ Add these two lines:
    selected_real = quarter_df[quarter_df['Fiscal_Quarter'] == selected_quarter]['CDI_Real'].values[0]
    selected_scaled = quarter_df[quarter_df['Fiscal_Quarter'] == selected_quarter]['CDI_Scaled'].values[0]

# === CDI Scale Bar ===
# === CDI Scale Bar ===
fig = go.Figure()
color_map = {
    -5: ("#800000", "Extremely Low"), -4: ("#bd0026", "Severely Low"),
    -3: ("#e31a1c", "Very Low"), -2: ("#fc4e2a", "Low"),
    -1: ("#fd8d3c", "Slightly Low"), 0: ("#fecc5c", "Neutral"),
    1: ("#c2e699", "Slightly High"), 2: ("#78c679", "High"),
    3: ("#31a354", "Very High"), 4: ("#006837", "Severely High"),
    5: ("#004529", "Extremely High")
}
for val in range(-5, 6):
    color, label = color_map[val]
    fig.add_shape(type="rect", x0=val-0.5, x1=val+0.5, y0=-0.3, y1=0.3,
                  line=dict(color="black", width=1), fillcolor=color, layer="below")
    fig.add_trace(go.Scatter(x=[val], y=[0], mode='text', text=[str(val)],
                             hovertext=[f"{label} ({val})"], showlegend=False,
                             textfont=dict(color='white', size=16)))

# ✅ USE selected_real & selected_scaled (NOT latest)
fig.add_shape(type="rect", x0=selected_scaled-0.5, x1=selected_scaled+0.5,
              y0=-0.35, y1=0.35, line=dict(color="crimson", width=3, dash="dot"),
              fillcolor="rgba(0,0,0,0)", layer="above")

fig.add_trace(go.Scatter(x=[selected_scaled], y=[0.45], mode='text',
                         text=[f"{selected_real:.2f}"], showlegend=False,
                         textfont=dict(size=16, color='crimson')))

fig.update_layout(title=f"Consumer Demand Index for {label_period} (Real: {selected_real:.2f})",
                  xaxis=dict(range=[-5.5, 5.5], title='CDI Scale (-5 to +5)',
                             showticklabels=False, showgrid=False),
                  yaxis=dict(visible=False), height=280,
                  margin=dict(l=30, r=30, t=60, b=30), showlegend=False)

st.plotly_chart(fig, use_container_width=True)

# === Charts ===
col1, col2 = st.columns(2)

with col1:
    line_fig = go.Figure()
    line_fig.add_trace(go.Scatter(
        x=line_x,
        y=line_y,
        mode='lines+markers',
        name='CDI',
        line=dict(color=kpi_theme_colors[0], width=3),
        marker=dict(size=6, color=kpi_theme_colors[1])
    ))
    line_fig.update_layout(
        title=line_title,
        xaxis_title=xaxis_title,
        yaxis_title="CDI (Actual)",
        yaxis=dict(zeroline=True),
        xaxis=dict(type=xaxis_type),
        height=400,
        margin=dict(l=40, r=40, t=50, b=40)
    )
    st.plotly_chart(line_fig, use_container_width=True)

with col2:
    st.markdown("### Contribution Breakdown")
    pca_weights = pca.components_[0]

    if mode == 'Monthly':
        scaled_row = scaled_features[selected_idx]
        contrib_df = pd.DataFrame({
            'Feature': features,
            'Contribution': scaled_row * pca_weights
        })
    else:
        indices = df[df['Fiscal_Quarter'] == selected_quarter].index
        avg_scaled = scaled_features[indices].mean(axis=0)
        contrib_df = pd.DataFrame({
            'Feature': features,
            'Contribution': avg_scaled * pca_weights
        })

    contrib_df['Abs_Contribution'] = contrib_df['Contribution'].abs()

    pie_fig = go.Figure()
    pie_fig.add_trace(go.Pie(
        labels=contrib_df['Feature'],
        values=contrib_df['Abs_Contribution'],
        hole=0.45,
        hoverinfo='label+percent+value',
        textinfo='label+percent',
        marker=dict(
            colors=kpi_theme_colors,
            line=dict(color='black', width=0.8)
        )
    ))

    pie_fig.update_traces(textposition='inside', textfont_size=14)
    pie_fig.update_layout(
        height=400,
        title_text=f"Contribution Breakdown: {label_period}",
        margin=dict(l=30, r=30, t=40, b=30),
        showlegend=True
    )

    st.plotly_chart(pie_fig, use_container_width=True)

# === Raw Data ===
if st.checkbox("\U0001F50D Show raw data with CDI"):
    st.dataframe(df[['Date', 'Month', 'Fiscal_Quarter', 'CDI_Real', 'CDI_Scaled'] + features])