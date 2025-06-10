import streamlit as st
import pandas as pd
from sklearn.decomposition import PCA
from sklearn.preprocessing import StandardScaler
import plotly.graph_objects as go

st.set_page_config(layout="wide")
st.title("Consumer Demand Index")

DEFAULT_DATA_PATH = "data/Consumer_Demand_Index.csv"

# Load data
try:
    df = pd.read_csv(DEFAULT_DATA_PATH)
except Exception as e:
    st.error(f"Error loading data: {e}")
    st.stop()

df.columns = df.columns.str.strip()
df['Date'] = pd.to_datetime(df['Date'], errors='coerce')
df = df.dropna(subset=['Date'])

# Features
features = ['UPI Transactions', 'GST Revenue', 'Vehicle Sales', 'Housing Sales', 'Power Consumption']
missing_cols = [col for col in features if col not in df.columns]
if missing_cols:
    st.error(f"Missing columns: {missing_cols}")
    st.stop()

df = df.dropna(subset=features)

# Standardize & PCA
scaler_std = StandardScaler()
scaled_features = scaler_std.fit_transform(df[features])
pca = PCA(n_components=1)
pca_components = pca.fit_transform(scaled_features)

# Store CDI values
df['CDI_Real'] = pca_components[:, 0]
df['CDI_Scaled'] = df['CDI_Real'].clip(-5, 5)

# Time labels
df['Month'] = df['Date'].dt.strftime('%b-%Y')

def get_fiscal_quarter(date):
    m, y = date.month, date.year
    if m in [4, 5, 6]:
        q, fy = 'Q1', y
    elif m in [7, 8, 9]:
        q, fy = 'Q2', y
    elif m in [10, 11, 12]:
        q, fy = 'Q3', y
    else:
        q, fy = 'Q4', y - 1
    return f"{q} {fy}-{str(fy+1)[-2:]}"

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

# --- CDI SCALE ---
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

fig.add_shape(type="rect", x0=selected_value_scaled-0.5, x1=selected_value_scaled+0.5,
              y0=-0.35, y1=0.35, line=dict(color="crimson", width=3, dash="dot"),
              fillcolor="rgba(0,0,0,0)", layer="above")

fig.add_trace(go.Scatter(x=[selected_value_scaled], y=[0.45], mode='text',
                         text=[f"{selected_value_real:.2f}"], showlegend=False,
                         textfont=dict(size=16, color='crimson')))

fig.update_layout(title=f"Consumer Demand Index for {display_label} (Real: {selected_value_real:.2f})",
                  xaxis=dict(range=[-5.5, 5.5], title='CDI Scale (-5 to +5)',
                             showticklabels=False, showgrid=False),
                  yaxis=dict(visible=False), height=280,
                  margin=dict(l=30, r=30, t=60, b=30), showlegend=False)

st.plotly_chart(fig, use_container_width=True)
st.caption("Note: CDI scale is clipped to -5 to +5 for consistent visualization. Actual values shown in graphs and data.")

# --- 2-COLUMN LAYOUT ---
col1, col2 = st.columns(2)

# LEFT: Line chart
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

# RIGHT: Pie chart
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
            title=f"Contribution Breakdown: {display_label}",
            height=400, margin=dict(l=30, r=30, t=40, b=30)
        )
        st.plotly_chart(pie_fig, use_container_width=True)

# --- Raw Data ---
if st.checkbox("🔍 Show raw data with CDI"):
    st.dataframe(df[['Date', 'Month', 'Fiscal_Quarter', 'CDI_Real', 'CDI_Scaled'] + features])