import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# Page title
st.title("🏘️ Housing Affordability Stress Index")

# Load local data
@st.cache_data
def load_data():
    df = pd.read_csv("data/Housing_Affordability.csv")  # local CSV path

    # Clean column names
    df.columns = df.columns.str.strip()

    # Parse dates
    df['Date'] = pd.to_datetime(df['Date'])

    # Clean Per Capita NNI
    df['Per Capita NNI'] = (
        df['Per Capita NNI']
        .astype(str)
        .str.replace(',', '', regex=False)
        .str.replace('₹', '', regex=False)
        .str.strip()
    )
    df['Per Capita NNI'] = pd.to_numeric(df['Per Capita NNI'], errors='coerce')

    # Clean Housing Loan Interest Rate
    df['Housing Loan Interest Rate'] = (
        df['Housing Loan Interest Rate']
        .astype(str)
        .str.replace('%', '', regex=False)
        .str.strip()
    )
    df['Housing Loan Interest Rate'] = pd.to_numeric(df['Housing Loan Interest Rate'], errors='coerce')

    # Clean Urbanization Rate
    df['Urbanization Rate'] = (
        df['Urbanization Rate']
        .astype(str)
        .str.replace('%', '', regex=False)
        .str.strip()
    )
    df['Urbanization Rate'] = pd.to_numeric(df['Urbanization Rate'], errors='coerce')

    return df.dropna()

# Load the dataset
df = load_data()

# Loan eligibility assumption
LOAN_ELIGIBILITY_FACTOR = 5  # i.e., you can get loan up to 5× your annual income

# Calculate Affordability Ratio using Property Price Index
df['Affordability Ratio'] = df['Property Price Index'] / (df['Per Capita NNI'] * LOAN_ELIGIBILITY_FACTOR)

# Normalize Affordability Score (0 to 1)
df['Affordability Score'] = (
    df['Affordability Ratio'] - df['Affordability Ratio'].min()
) / (df['Affordability Ratio'].max() - df['Affordability Ratio'].min())

# Show latest data point
st.subheader("📊 Latest Housing Affordability Snapshot")
latest = df.iloc[-1]
st.metric("Affordability Ratio", f"{latest['Affordability Ratio']:.2f}×")
st.metric("Affordability Score (normalized)", f"{latest['Affordability Score']:.2f}")
st.metric("PPI", f"{latest['Property Price Index']:.2f}")
st.metric("Per Capita NNI", f"₹{latest['Per Capita NNI']:.0f}")
st.metric("Loan Rate", f"{latest['Housing Loan Interest Rate']:.2f}%")

# Plot trends
st.subheader("📈 Affordability Trend Over Time")
selected_metric = st.selectbox(
    "Choose metric to plot:",
    ['Affordability Ratio', 'Affordability Score', 'Property Price Index', 'Per Capita NNI']
)

fig, ax = plt.subplots()
ax.plot(df['Date'], df[selected_metric], marker='o', linewidth=2)
ax.set_xlabel("Date")
ax.set_ylabel(selected_metric)
ax.grid(True)
st.pyplot(fig)

# Raw data expander
with st.expander("🗂️ Show raw data"):
    st.dataframe(df)