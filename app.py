import streamlit as st
import pandas as pd
from sklearn.decomposition import PCA
from sklearn.preprocessing import MinMaxScaler
import plotly.graph_objects as go

st.set_page_config(layout="wide")
st.title("📊 Consumer Demand Index Dashboard (Scale: -5 to +5)")

uploaded_file = st.file_uploader("📁 Upload your monthly data CSV", type=["csv"])

if uploaded_file:
    df = pd.read_csv(uploaded_file)
    df.columns = df.columns.str.strip()

    # Parse date column
    df['Date'] = pd.to_datetime(df['Date'], dayfirst=False, errors='coerce')
    df = df.dropna(subset=['Date'])

    # Features to be used for PCA
    features = ['UPI Transactions', 'GST Revenue', 'Vehicle Sales', 'Housing Sales', 'Power Consumption']
    missing_cols = [col for col in features if col not in df.columns]
    if missing_cols:
        st.error(f"❌ Missing columns in CSV: {missing_cols}")
        st.stop()

    df = df.dropna(subset=features)

    # PCA
    pca = PCA(n_components=1)
    pca_components = pca.fit_transform(df[features])

    # Min-Max Scaling between -5 to +5
    scaler = MinMaxScaler(feature_range=(-5, 5))
    df['CDI'] = scaler.fit_transform(pca_components)

    # Monthly labels
    df['Month'] = df['Date'].dt.strftime('%b-%Y')

    # Custom Fiscal Quarter Function
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
        else:  # Jan to Mar
            quarter = "Q4"
            fy_start = year - 1
        fy_label = f"{fy_start}-{str(fy_start + 1)[-2:]}"
        return f"{quarter} {fy_label}"

    df['Fiscal_Quarter'] = df['Date'].apply(get_fiscal_quarter)

    # Mode toggle
    mode = st.radio("📅 View Mode", ['Monthly', 'Quarterly'], horizontal=True)

    if mode == 'Monthly':
        selected_month = st.selectbox("Select a month", df['Month'].unique())
        selected_value = df.loc[df['Month'] == selected_month, 'CDI'].values[0]
        display_label = selected_month
    else:
        quarter_df = df.groupby('Fiscal_Quarter')['CDI'].mean().reset_index()
        selected_quarter = st.selectbox("Select a fiscal quarter", quarter_df['Fiscal_Quarter'].unique())
        selected_value = quarter_df.loc[quarter_df['Fiscal_Quarter'] == selected_quarter, 'CDI'].values[0]
        display_label = selected_quarter

    # Draw the CDI Scale
    fig = go.Figure()

    # CDI Marker
    fig.add_trace(go.Scatter(
        x=[selected_value],
        y=[0],
        mode='markers+text',
        marker=dict(size=20, color='crimson'),
        text=[f"{selected_value:.2f}"],
        textposition="top center",
        name="CDI"
    ))

    # Dotted line for selected CDI
    fig.add_shape(
        type='line',
        x0=selected_value, x1=selected_value,
        y0=-0.3, y1=0.3,
        line=dict(color='crimson', dash='dot')
    )

    fig.update_layout(
        title=f"Consumer Demand Index for {display_label}",
        xaxis=dict(
            range=[-5.5, 5.5],
            tickmode='linear',
            tick0=-5,
            dtick=1,
            title='CDI Scale (-5 to +5)',
            showgrid=False
        ),
        yaxis=dict(visible=False),
        height=220,
        margin=dict(l=30, r=30, t=50, b=30)
    )

    st.plotly_chart(fig, use_container_width=True)

    # Optional: Show full CDI table
    if st.checkbox("🔍 Show raw data with CDI"):
        st.dataframe(df[['Date', 'Month', 'Fiscal_Quarter', 'CDI'] + features])

else:
    st.info("Please upload your monthly data CSV to begin.")