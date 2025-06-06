import streamlit as st
import pandas as pd
from sklearn.decomposition import PCA
from sklearn.preprocessing import MinMaxScaler

st.title("Consumer Demand Index Dashboard")

uploaded_file = st.file_uploader("Upload your monthly data CSV", type=["csv"])

if uploaded_file:
    # Read CSV with default header (first row as header)
    df = pd.read_csv(uploaded_file)
    
    # Strip any whitespace from column names
    df.columns = df.columns.str.strip()
    
    # Show columns for debugging
    st.write("Columns in uploaded CSV:", df.columns.tolist())
    
    # Convert 'Date' column to datetime with format '%b-%y' (e.g., Jan-23)
    try:
        df['Date'] = pd.to_datetime(df['Date'], format='%b-%y', errors='coerce')
        # Fix any years parsed as 1900s to 2000s
        df.loc[df['Date'].dt.year < 2000, 'Date'] += pd.DateOffset(years=100)
    except Exception as e:
        st.error(f"Date parsing error: {e}")
        st.stop()
    
    # Define the features you want to use for PCA — make sure these exactly match your CSV headers
    features = ['UPI Transactions', 'GST Revenue', 'Vehicle Sales', 'Housing Sales', 'Power Consumption']
    
    # Check if all features exist in the data
    missing_cols = [col for col in features if col not in df.columns]
    if missing_cols:
        st.error(f"Missing columns in CSV: {missing_cols}")
        st.stop()
    
    # Drop rows with missing values in features (or handle differently)
    df = df.dropna(subset=features)
    
    # Perform PCA with 1 component
    pca = PCA(n_components=1)
    pca_components = pca.fit_transform(df[features])
    
    # Scale PCA output to 0-100
    scaler = MinMaxScaler(feature_range=(0, 100))
    cdi_scaled = scaler.fit_transform(pca_components)
    df['Consumer Demand Index'] = cdi_scaled
    
    # Plot Consumer Demand Index over time
    st.line_chart(df.set_index('Date')['Consumer Demand Index'])
    
    # Optionally show raw data
    if st.checkbox("Show raw data"):
        st.dataframe(df)

else:
    st.info("Upload your monthly data CSV file to begin.")