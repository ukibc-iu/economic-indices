import streamlit as st
import pandas as pd
from sklearn.decomposition import PCA
from sklearn.preprocessing import MinMaxScaler, StandardScaler
import plotly.graph_objects as go

st.set_page_config(layout="wide")
st.title("Consumer Demand Index")

# Load data
DEFAULT_DATA_PATH = "data/Consumer_Demand_Index.csv"

try:
    df = pd.read_csv(DEFAULT_DATA_PATH)
except Exception as e:
    st.error(f"Error loading data file: {e}")
    st.stop()

df.columns = df.columns.str.strip()

# Parse date
df['Date'] = pd.to_datetime(df['Date'], errors='coerce')
df = df.dropna(subset=['Date'])

# Define features
features = ['UPI Transactions', 'GST Revenue', 'Vehicle Sales', 'Housing Sales', 'Power Consumption']
missing_cols = [col for col in features if col not in df.columns]
if missing_cols:
    st.error(f"Missing columns in data: {missing_cols}")
    st.stop()

df = df.dropna(subset=features)

# Standardize features for PCA
scaler_std = StandardScaler()
scaled_features = scaler_std.fit_transform(df[features])

# PCA to 1 component
pca = PCA(n_components=1)
pca_components = pca.fit_transform(scaled_features)

# Scale CDI to range -5 to +5
pca_shifted = pca_components - pca_components.min()
scaler_mm = MinMaxScaler(feature_range=(0, 1))
pca_normalized = scaler_mm.fit_transform(pca_shifted)
cdi_scaled = pca_normalized * 10 - 5

df['CDI'] = cdi_scaled.flatten()

# Create month label
df['Month'] = df['Date'].dt.strftime('%b-%Y')

# Fiscal quarter label helper
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

# User selects view mode
mode = st.radio("📅 View Mode", ['Monthly', 'Quarterly'], horizontal=True)

if mode == 'Monthly':
    selected_month = st.selectbox("Select a month", df['Month'].unique())
    selected_value = df.loc[df['Month'] == selected_month, 'CDI'].values[0]
    selected_idx = df[df['Month'] == selected_month].index[0]
    display_label = selected_month
    line_x = df['Date']
    line_y = df['CDI']
    line_title = "CDI Over Time (Monthly)"
    xaxis_type = "date"
    xaxis_title = "Date"
else:
    quarter_df = df.groupby('Fiscal_Quarter', sort=False)['CDI'].mean().reset_index()
    selected_quarter = st.selectbox("Select a fiscal quarter", quarter_df['Fiscal_Quarter'].unique())
    selected_value = quarter_df.loc[quarter_df['Fiscal_Quarter'] == selected_quarter, 'CDI'].values[0]
    # For selected_idx in quarterly mode, pick first index of that quarter in df for contributions
    selected_idx = df[df['Fiscal_Quarter'] == selected_quarter].index[0]
    display_label = selected_quarter
    line_x = quarter_df['Fiscal_Quarter']
    line_y = quarter_df['CDI']
    line_title = "CDI Over Time (Quarterly)"
    xaxis_type = "category"
    xaxis_title = "Fiscal Quarter"

# Colors and labels for scale
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

def hex_to_rgb(hex_color):
    hex_color = hex_color.lstrip('#')
    return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))

# --- CDI SCALE PLOT ---
# --- CDI SCALE PLOT ---
fig = go.Figure()

x_vals = []
texts = []
text_colors = []

for val in range(-5, 6):
    color, label = color_map[val]
    r, g, b = hex_to_rgb(color)
    brightness = (r*299 + g*587 + b*114) / 1000
    # Lower brightness means darker bg, use white text, else black
    text_color = 'white' if brightness < 150 else 'black'

    # Add the colored rectangle
    fig.add_shape(
        type="rect",
        x0=val - 0.5, x1=val + 0.5,
        y0=-0.3, y1=0.3,
        line=dict(color="black", width=1),
        fillcolor=color
    )
    # Save positions and text for a single Scatter trace
    x_vals.append(val)
    texts.append(str(val))
    text_colors.append(text_color)

# Highlight the selected CDI value with a border rectangle
fig.add_shape(
    type="rect",
    x0=selected_value - 0.5,
    x1=selected_value + 0.5,
    y0=-0.35, y1=0.35,
    line=dict(color="crimson", width=3, dash="dot"),
    fillcolor="rgba(0,0,0,0)"
)

# Add selected CDI numeric value just above the scale bar
fig.add_trace(go.Scatter(
    x=[selected_value],
    y=[0.5],
    mode='text',
    text=[f"{selected_value:.2f}"],
    textfont=dict(size=16, color='crimson', family="Arial"),
    showlegend=False
))

# Add the scale numbers as a single trace
fig.add_trace(go.Scatter(
    x=x_vals,
    y=[0]*len(x_vals),
    mode='text',
    text=texts,
    textfont=dict(
        color=text_colors,
        size=14,
        family="Arial"
    ),
    showlegend=False
))

fig.update_layout(
    title=f"Consumer Demand Index for {display_label}",
    xaxis=dict(range=[-5.5, 5.5], title='CDI Scale (-5 to +5)', showticklabels=False, showgrid=False),
    yaxis=dict(visible=False),
    height=280,
    margin=dict(l=30, r=30, t=60, b=30),
    plot_bgcolor='white',
    paper_bgcolor='white',
    showlegend=False
)

st.plotly_chart(fig, use_container_width=True)
# --- 2-COLUMN LAYOUT ---
col1, col2 = st.columns(2)

# LEFT: Line plot
with col1:
    line_fig = go.Figure()
    line_fig.add_trace(go.Scatter(
        x=line_x,
        y=line_y,
        mode='lines+markers',
        line=dict(color='#007381', width=3),
        marker=dict(size=6, color='#E85412'),
        name='CDI'
    ))
    line_fig.update_layout(
        title=line_title,
        xaxis_title=xaxis_title,
        yaxis_title="CDI (-5 to +5)",
        yaxis=dict(range=[-5.5, 5.5]),
        xaxis=dict(type=xaxis_type),
        height=400,
        margin=dict(l=40, r=40, t=50, b=40)
    )
    st.plotly_chart(line_fig, use_container_width=True)

# RIGHT: Pie chart feature contribution
with col2:
    st.markdown("### 🧠 Feature Contributions to CDI")
    pca_weights = pca.components_[0]
    scaled_row = scaled_features[selected_idx]
    contributions = scaled_row * pca_weights

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

# Show raw data toggle
if st.checkbox("🔍 Show raw data with CDI"):
    st.dataframe(df[['Date', 'Month', 'Fiscal_Quarter', 'CDI'] + features])