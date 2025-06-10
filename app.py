import streamlit as st
import pandas as pd
from sklearn.decomposition import PCA
from sklearn.preprocessing import StandardScaler
import plotly.graph_objects as go

st.set_page_config(layout="wide")
st.title("Consumer Demand Index")

# Path to your default data file
DEFAULT_DATA_PATH = "data/Consumer_Demand_Index.csv"

# Load the data
try:
    df = pd.read_csv(DEFAULT_DATA_PATH)
except Exception as e:
    st.error(f"Error loading data file: {e}")
    st.stop()

df.columns = df.columns.str.strip()

# Parse date column
df['Date'] = pd.to_datetime(df['Date'], dayfirst=False, errors='coerce')
df = df.dropna(subset=['Date'])

# Features for PCA
features = ['UPI Transactions', 'GST Revenue', 'Vehicle Sales', 'Housing Sales', 'Power Consumption']
missing_cols = [col for col in features if col not in df.columns]
if missing_cols:
    st.error(f"Missing columns in data: {missing_cols}")
    st.stop()

df = df.dropna(subset=features)

# Standardize features
scaler_std = StandardScaler()
scaled_features = scaler_std.fit_transform(df[features])

# PCA
pca = PCA(n_components=1)
pca_components = pca.fit_transform(scaled_features)

# Store real and scaled CDI
df['CDI_Real'] = pca_components[:, 0]
df['CDI_Scaled'] = df['CDI_Real'].clip(lower=-5, upper=5)  # only for scale plot

# Month and Quarter labels
df['Month'] = df['Date'].dt.strftime('%b-%Y')

def get_fiscal_quarter(date):
    month = date.month
    year = date.year
    if month in [4, 5, 6]:
        quarter = "Q1"
        fy_start = year
    elif month in [7, 8, 9]:
        quarter = "Q2"
        fy_start = year
    elif month in [10, 11, 12]:
        quarter = "Q3"
        fy_start = year
    else:
        quarter = "Q4"
        fy_start = year - 1
    fy_label = f"{fy_start}-{str(fy_start + 1)[-2:]}"
    return f"{quarter} {fy_label}"

df['Fiscal_Quarter'] = df['Date'].apply(get_fiscal_quarter)

# View mode
mode = st.radio("📅 View Mode", ['Monthly', 'Quarterly'], horizontal=True)

if mode == 'Monthly':
    selected_month = st.selectbox("Select a month", df['Month'].unique())
    selected_row = df[df['Month'] == selected_month].iloc[0]
    selected_value_real = selected_row['CDI_Real']
    selected_value_scaled = selected_row['CDI_Scaled']
    selected_idx = selected_row.name
    display_label = selected_month
    line_x = df['Date']
    line_y = df['CDI_Real']
    line_title = "CDI Over Time (Monthly)"
    xaxis_type = "date"
    xaxis_title = "Date"
else:
    quarter_df = df.groupby('Fiscal_Quarter', sort=False)['CDI_Real'].mean().reset_index()
    selected_quarter = st.selectbox("Select a fiscal quarter", quarter_df['Fiscal_Quarter'].unique())
    selected_value_real = quarter_df.loc[quarter_df['Fiscal_Quarter'] == selected_quarter, 'CDI_Real'].values[0]
    quarter_indices = df[df['Fiscal_Quarter'] == selected_quarter].index
    selected_idx = quarter_indices[0]
    display_label = selected_quarter
    line_x = quarter_df['Fiscal_Quarter']
    line_y = quarter_df['CDI_Real']
    line_title = "CDI Over Time (Quarterly)"
    xaxis_type = "category"
    xaxis_title = "Fiscal Quarter"
    selected_value_scaled = df.loc[quarter_indices, 'CDI_Scaled'].mean()

# --- CDI SCALE PLOT ---
fig = go.Figure()
color_map = {
    -5: ("#800000", "Extremely Low"),
    -4: ("#bd0026", "Severely Low"),
    -3: ("#e31a1c", "Very Low"),
    -2: ("#fc4e2a", "Low"),
    -1: ("#fd8d3c", "Slightly Low"),
     0: ("#fecc5c", "Neutral"),
     1: ("#c2e699", "Slightly High"),
     2: ("#78c679", "High"),
     3: ("#31a354", "Very High"),
     4: ("#006837", "Severely High"),
     5: ("#004529", "Extremely High")
}

for val in range(-5, 6):
    color, label = color_map[val]
    fig.add_shape(
        type="rect",
        x0=val - 0.5, x1=val + 0.5,
        y0=-0.3, y1=0.3,
        line=dict(color="black", width=1),
        fillcolor=color,
        layer="below"
    )
    fig.add_trace(go.Scatter(
        x=[val],
        y=[0],
        mode='text',
        text=[str(val)],
        textposition="middle center",
        hoverinfo="text",
        hovertext=[f"{label} ({val})"],
        textfont=dict(color='white', size=16, family="Arial Black", weight='bold'),
        showlegend=False
    ))

fig.add_shape(
    type="rect",
    x0=selected_value_scaled - 0.5,
    x1=selected_value_scaled + 0.5,
    y0=-0.35, y1=0.35,
    line=dict(color="crimson", width=3, dash="dot"),
    fillcolor="rgba(0,0,0,0)",
    layer="above"
)

fig.add_trace(go.Scatter(
    x=[selected_value_scaled],
    y=[0.45],
    mode='text',
    text=[f"{selected_value_real:.2f}"],
    textfont=dict(size=16, color='crimson', family="Arial Black", weight='bold'),
    showlegend=False
))

fig.update_layout(
    title=f"Consumer Demand Index for {display_label} (Real CDI: {selected_value_real:.2f})",
    xaxis=dict(range=[-5.5, 5.5], title='CDI Scale (-5 to +5)', showticklabels=False, showgrid=False),
    yaxis=dict(visible=False),
    height=280,
    margin=dict(l=30, r=30, t=60, b=30),
    showlegend=False
)

st.plotly_chart(fig, use_container_width=True)
st.caption("Note: Scale bar clips CDI between -5 to +5 for visual comparison. Real values used elsewhere.")

# --- 2-COLUMN LAYOUT ---
col1, col2 = st.columns(2)

# LEFT: Line Graph
with col1:
    line_fig = go.Figure()
    line_fig.add_trace(go.Scatter(
        x=line_x,
        y=line_y,
        mode='lines+markers',
        line=dict(color='#007381', width=3),
        marker=dict(size=6, color='#E85412'),
        name='CDI (Real)'
    ))

    line_fig.update_layout(
        title=line_title,
        xaxis_title=xaxis_title,
        yaxis_title="CDI (Real Value)",
        xaxis=dict(type=xaxis_type),
        height=400,
        margin=dict(l=40, r=40, t=50, b=40)
    )
    st.plotly_chart(line_fig, use_container_width=True)

# RIGHT: Pie chart
with col2:
    st.markdown("### Feature Contributions to CDI")

    pca_weights = pca.components_[0]

    if mode == 'Monthly':
        if 0 <= selected_idx < len(scaled_features):
            scaled_row = scaled_features[selected_idx]
            contributions = scaled_row * pca_weights
        else:
            contributions = [0] * len(features)
    else:
        quarter_indices = df[df['Fiscal_Quarter'] == selected_quarter].index
        avg_scaled_features = scaled_features[quarter_indices].mean(axis=0)
        contributions = avg_scaled_features * pca_weights

    contrib_df = pd.DataFrame({
        'Feature': features,
        'Contribution': contributions
    })
    contrib_df['Abs_Contribution'] = contrib_df['Contribution'].abs()

    color_palette = ['#62C8CE', '#E85412', '#007381', '#002060', '#4B575F']

    pie_fig = go.Figure(data=[
        go.Pie(
            labels=contrib_df['Feature'],
            values=contrib_df['Abs_Contribution'],
            hoverinfo='label+percent+value',
            textinfo='label+percent',
            marker=dict(
                colors=color_palette[:len(contrib_df)],
                line=dict(color='white', width=1.5)
            )
        )
    ])
    pie_fig.update_layout(
        title=f"Contribution Breakdown: {display_label}",
        height=400,
        margin=dict(l=30, r=30, t=40, b=30)
    )
    st.plotly_chart(pie_fig, use_container_width=True)

# --- Raw Data ---
if st.checkbox("🔍 Show raw data with CDI"):
    st.dataframe(df[['Date', 'Month', 'Fiscal_Quarter', 'CDI_Real', 'CDI_Scaled'] + features])