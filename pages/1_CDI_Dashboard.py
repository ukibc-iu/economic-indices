import streamlit as st
import pandas as pd
from sklearn.decomposition import PCA
from sklearn.preprocessing import StandardScaler
import plotly.graph_objects as go

st.set_page_config(layout="wide")
st.title("Consumer Demand Index (CDI)")

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
    border-radius: 12px;
    box-shadow: 0 2px 8px rgba(0,0,0,0.2);
    background: #1e1e1e;
    color: white;
    min-width: 200px;
}
.kpi-title {
    font-size: 1rem;
    font-weight: 600;
    margin-bottom: 0.3rem;
    color: #ccc;
}
.kpi-value {
    font-size: 1.8rem;
    font-weight: bold;
}
.kpi-delta {
    font-size: 1.2rem;
    margin-top: 0.2rem;
}
.bg-1 { background-color: rgba(57, 255, 20, 0.25); }     /* Neon Lime Green */
.bg-2 { background-color: rgba(255, 0, 144, 0.25); }     /* Bright Magenta */
.bg-3 { background-color: rgba(0, 255, 255, 0.25); }     /* Hot Cyan */
</style>
""", unsafe_allow_html=True)

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

mode = st.radio("Select View Mode", ['Monthly', 'Quarterly'], horizontal=True)

# === Mode-Specific Processing ===
if mode == 'Monthly':
    df_sorted = df.sort_values(by='Date')
    latest_row = df_sorted.iloc[-1]
    latest_real = latest_row['CDI_Real']
    latest_scaled = latest_row['CDI_Scaled']
    label_period = latest_row['Month']
    prev_row = df_sorted.iloc[-2] if len(df_sorted) > 1 else latest_row
    delta = latest_real - prev_row['CDI_Real']
    
    # For plots
    selected_idx = df_sorted.index[-1]
    line_x = df_sorted['Date']
    line_y = df_sorted['CDI_Real']
    line_title = f"CDI Trend - Monthly"
    xaxis_title = "Month"
    xaxis_type = "date"
    selected_quarter = None
else:
    quarter_df = df.groupby('Fiscal_Quarter', sort=False)['CDI_Real'].mean().reset_index()
    quarter_df['CDI_Scaled'] = df.groupby('Fiscal_Quarter', sort=False)['CDI_Scaled'].mean().values
    latest_quarter = quarter_df.iloc[-1]
    label_period = latest_quarter['Fiscal_Quarter']
    latest_real = latest_quarter['CDI_Real']
    latest_scaled = latest_quarter['CDI_Scaled']
    if len(quarter_df) > 1:
        prev_value = quarter_df.iloc[-2]['CDI_Real']
        delta = latest_real - prev_value
    else:
        delta = 0

    # For plots
    selected_idx = None
    selected_quarter = label_period
    line_x = quarter_df['Fiscal_Quarter']
    line_y = quarter_df['CDI_Real']
    line_title = f"CDI Trend - Quarterly"
    xaxis_title = "Fiscal Quarter"
    xaxis_type = "category"

# === DELTA STYLE ===
if delta > 0:
    delta_display = f"<div class='kpi-delta' style='color: green;'> {delta:+.2f}</div>"
elif delta < 0:
    delta_display = f"<div class='kpi-delta' style='color: red;'> {delta:+.2f}</div>"
else:
    delta_display = f"<div class='kpi-delta' style='color: gray;'> {delta:+.2f}</div>"

# === KPI CARDS ===
st.markdown(f"""
<div class="kpi-container">
    <div class="kpi-card bg-1">
        <div class="kpi-title">Actual CDI</div>
        <div class="kpi-value">{latest_real:.2f}</div>
        {delta_display}
    </div>
    <div class="kpi-card bg-2">
        <div class="kpi-title">{'Month' if mode == 'Monthly' else 'Fiscal Quarter'}</div>
        <div class="kpi-value">{label_period}</div>
    </div>
    <div class="kpi-card bg-3">
        <div class="kpi-title">Scaled CDI</div>
        <div class="kpi-value">{latest_scaled:.2f}</div>
    </div>
</div>
""", unsafe_allow_html=True)
st.markdown("---")

# === CDI SCALE PLOT ===
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

fig.add_shape(type="rect", x0=latest_scaled-0.5, x1=latest_scaled+0.5,
              y0=-0.35, y1=0.35, line=dict(color="crimson", width=3, dash="dot"),
              fillcolor="rgba(0,0,0,0)", layer="above")

fig.add_trace(go.Scatter(x=[latest_scaled], y=[0.45], mode='text',
                         text=[f"{latest_real:.2f}"], showlegend=False,
                         textfont=dict(size=16, color='crimson')))

fig.update_layout(title=f"Consumer Demand Index for {label_period} (Real: {latest_real:.2f})",
                  xaxis=dict(range=[-5.5, 5.5], title='CDI Scale (-5 to +5)',
                             showticklabels=False, showgrid=False),
                  yaxis=dict(visible=False), height=280,
                  margin=dict(l=30, r=30, t=60, b=30), showlegend=False)

st.plotly_chart(fig, use_container_width=True)
st.caption("Note: CDI scale is clipped to -5 to +5 for consistent visualization. Actual values shown in line graph and raw data.")

# --- 2-COLUMN LAYOUT ---
col1, col2 = st.columns(2)

# Line chart
with col1:
    line_fig = go.Figure()
    line_fig.add_trace(go.Scatter(
        x=line_x, y=line_y, mode='lines+markers',
        line=dict(color='#007381', width=3),
        marker=dict(size=6, color='#E85412'), name='CDI'
    ))
    line_fig.update_layout(title=line_title, xaxis_title=xaxis_title,
                           yaxis_title="CDI (Actual)", yaxis=dict(zeroline=True),
                           xaxis=dict(type=xaxis_type), height=400,
                           margin=dict(l=40, r=40, t=50, b=40))
    st.plotly_chart(line_fig, use_container_width=True)

# Pie chart
with col2:
    st.markdown("### Feature Contributions to CDI")
    pca_weights = pca.components_[0]

    if mode == 'Monthly':
        if 0 <= selected_idx < len(scaled_features):
            scaled_row = scaled_features[selected_idx]
            contrib_df = pd.DataFrame({
                'Feature': features,
                'Contribution': scaled_row * pca_weights
            })
            contrib_df['Abs_Contribution'] = contrib_df['Contribution'].abs()
        else:
            st.warning("Invalid index.")
            contrib_df = None
    else:
        quarter_indices = df[df['Fiscal_Quarter'] == selected_quarter].index
        if len(quarter_indices):
            avg_scaled = scaled_features[quarter_indices].mean(axis=0)
            contrib_df = pd.DataFrame({
                'Feature': features,
                'Contribution': avg_scaled * pca_weights
            })
            contrib_df['Abs_Contribution'] = contrib_df['Contribution'].abs()
        else:
            st.warning("No data for selected quarter.")
            contrib_df = None

    if contrib_df is not None:
        pie_fig = go.Figure(data=[go.Pie(
            labels=contrib_df['Feature'],
            values=contrib_df['Abs_Contribution'],
            hoverinfo='label+percent+value',
            textinfo='label+percent',
            marker=dict(colors=['#62C8CE', '#E85412', '#007381', '#002060', '#4B575F'],
                        line=dict(color='white', width=1.5))
        )])
        pie_fig.update_layout(
            title=f"Contribution Breakdown: {label_period}",
            height=400, margin=dict(l=30, r=30, t=40, b=30)
        )
        st.plotly_chart(pie_fig, use_container_width=True)

# --- RAW DATA ---
if st.checkbox("🔍 Show raw data with CDI"):
    st.dataframe(df[['Date', 'Month', 'Fiscal_Quarter', 'CDI_Real', 'CDI_Scaled'] + features])