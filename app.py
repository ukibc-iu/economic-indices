import streamlit as st
import pandas as pd
from sklearn.decomposition import PCA
from sklearn.preprocessing import MinMaxScaler

st.title("Consumer Demand Index Dashboard")

uploaded_file = st.file_uploader("Upload your monthly data CSV", type=["csv"])

if uploaded_file:
    # Read CSV, skip first row if needed (adjust as per your file)
    df = pd.read_csv(uploaded_file, skiprows=1)

    # Drop unnamed index columns if present
    if df.columns[0].startswith("Unnamed"):
        df = df.drop(df.columns[0], axis=1)

    # Clean column names
    df.columns = df.columns.str.strip()

    # Convert 'Date' to datetime - adjust format if needed
    df['Date'] = pd.to_datetime(df['Date'], format='%b-%y')

    # Features for PCA
    features = ['UPI Transactions', 'GST Revenue', 'Vehicle Sales', 'Housing Sales', 'Power Consumption']

    # Drop rows with missing data in features
    df = df.dropna(subset=features)

    # Apply PCA with 1 component
    pca = PCA(n_components=1)
    pca_components = pca.fit_transform(df[features])

    # Scale PCA output to 0-100
    scaler = MinMaxScaler(feature_range=(0, 100))
    cdi_scaled = scaler.fit_transform(pca_components)

    # Add CDI column to dataframe
    df['Consumer Demand Index'] = cdi_scaled

    # Show line chart using Streamlit
    st.line_chart(df.set_index('Date')['Consumer Demand Index'])

    # Optional: show raw data
    if st.checkbox("Show raw data"):
        st.dataframe(df)
else:
    st.info("Upload your monthly data CSV file to begin.")