import streamlit as st
import pandas as pd
from sklearn.decomposition import PCA
from sklearn.preprocessing import MinMaxScaler

st.title("Consumer Demand Index Dashboard")

uploaded_file = st.file_uploader("Upload your monthly data CSV", type=["csv"])

if uploaded_file:
    # Step 1: Read the CSV file
    df = pd.read_csv(uploaded_file, skiprows=1)

    # Step 2: Clean column names (removes extra spaces, etc.)
    df.columns = df.columns.str.strip()

    # Step 3: Show column names to debug
    st.write("Uploaded columns:", df.columns.tolist())

    # Step 4: Check if 'Date' column exists
    if 'Date' not in df.columns:
        st.error("❌ No column named 'Date' found in the uploaded CSV.")
        st.stop()

    # Step 5: Convert Date column
    df['Date'] = pd.to_datetime(df['Date'], format='%b-%y')

    # Step 6: Continue with the rest of your logic
    features = ['UPI Transactions', 'GST Revenue', 'Vehicle Sales', 'Housing Sales', 'Power Consumption']

    if df[features].isnull().any().any():
        df = df.dropna(subset=features)

    pca = PCA(n_components=1)
    pca_components = pca.fit_transform(df[features])

    scaler = MinMaxScaler(feature_range=(0, 100))
    cdi_scaled = scaler.fit_transform(pca_components)
    df['Consumer Demand Index'] = cdi_scaled

    st.line_chart(df.set_index('Date')['Consumer Demand Index'])

    if st.checkbox("Show raw data"):
        st.dataframe(df)

else:
    st.info("Upload your monthly data CSV file to begin.")