import streamlit as st
import pandas as pd
from sklearn.decomposition import PCA
from sklearn.preprocessing import MinMaxScaler

st.title("Consumer Demand Index Dashboard")

uploaded_file = st.file_uploader("Upload your monthly data CSV", type=["csv"])

if uploaded_file:
    df = pd.read_csv(uploaded_file)
    df.columns = df.columns.str.strip()
    st.write("Columns in uploaded CSV:", df.columns.tolist())

    # Custom function to parse dates like 'Jan-23' to proper datetime
    def parse_date_custom(date_str):
        try:
            month_str, year_str = date_str.split('-')
            month_num = pd.to_datetime(month_str, format='%b').month
            year_num = 2000 + int(year_str)  # Convert '23' to 2023 explicitly
            return pd.Timestamp(year=year_num, month=month_num, day=1)
        except:
            return pd.NaT

    df['Date'] = df['Date'].apply(parse_date_custom)

    if df['Date'].isnull().any():
        st.error("Some dates could not be parsed. Please check your CSV date format.")
        st.stop()

    features = ['UPI Transactions', 'GST Revenue', 'Vehicle Sales', 'Housing Sales', 'Power Consumption']
    missing_cols = [col for col in features if col not in df.columns]
    if missing_cols:
        st.error(f"Missing columns in CSV: {missing_cols}")
        st.stop()

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