import streamlit as st
import pandas as pd

st.set_page_config(layout="wide")

# Load data from Excel
df = pd.read_excel("data/Macro_MoM_Comparison.xlsx")

# Convert column names to standard format
df.columns = df.columns.str.strip()

# Create mapping from Parameter to display names (optional)
display_names = {
    "Repo Rate": "Repo / Interest Rates",
    "Inflation Rate": "Inflation",
    "Unemployment Rate": "Unemployment",
    "GDP Growth": "GDP Growth",
    "Manufacturing PMI": "Manufacturing PMI",
    "Merchandise Imports": "Merchandise Imports",
    "Merchandise Exports": "Merchandise Exports"
}

# Flag URLs
flags = {
    "India": "https://flagcdn.com/in.svg",
    "UK": "https://flagcdn.com/gb.svg"
}

# Convert dataframe into structured dictionary
data = {}
for _, row in df.iterrows():
    param = row["Parameter"].strip()
    display_label = display_names.get(param, param)
    
    india_color = "green" if "+" in str(row["India MoM Change"]) else "red" if "-" in str(row["India MoM Change"]) else "grey"
    uk_color = "green" if "+" in str(row["UK MoM Change"]) else "red" if "-" in str(row["UK MoM Change"]) else "grey"

    data[display_label] = {
        "India": {
            "value": str(row["India"]),
            "date": row["India Date"].strftime("%b-%y"),
            "change": str(row["India MoM Change"]),
            "color": india_color
        },
        "UK": {
            "value": str(row["UK"]),
            "date": row["UK Date"].strftime("%b-%y"),
            "change": str(row["UK MoM Change"]),
            "color": uk_color
        }
    }

# Card rendering function
def card(country, details):
    return f"""
    <div style="text-align: center; background-color: #111; padding: 15px; border-radius: 10px; border: 1px solid #333;">
        <img src='{flags[country]}' width='32'><br>
        <span style='font-size: 20px; font-weight: bold;'>{details["value"]}</span><br>
        <span style='font-size: 13px; color: grey;'>{details["date"]}</span><br>
        <span style='color: {details["color"]}; font-size: 13px;'>{details["change"]}</span>
    </div>
    """

# Group parameters in pairs (2 per row)
param_names = list(data.keys())
param_pairs = [param_names[i:i+2] for i in range(0, len(param_names), 2)]

# Render layout
for pair in param_pairs:
    col_block = st.columns(2)
    
    for i, param in enumerate(pair):
        with col_block[i]:
            st.markdown(f"<h3 style='text-align: center; color: white;'>{param}</h3>", unsafe_allow_html=True)
            subcols = st.columns(2)
            with subcols[0]:
                st.markdown(card("India", data[param]["India"]), unsafe_allow_html=True)
            with subcols[1]:
                st.markdown(card("UK", data[param]["UK"]), unsafe_allow_html=True)