import streamlit as st
import pandas as pd

st.set_page_config(layout="wide")
st.markdown("<h2 style='text-align:center;'>Macroeconomic Briefing: India and United Kingdom</h2>", unsafe_allow_html=True)
st.markdown("<h3 style='text-align:center; color: teal;'>September 2025</h3>", unsafe_allow_html=True)
# Load data
df = pd.read_excel("data/Macro_MoM_Comparison.xlsx")
df.columns = df.columns.str.strip()

# Define reverse logic parameters
reverse_logic_params = ["Unemployment Rate", "Inflation Rate", "Merchandise Imports"]

# % fields to format
percent_params = ["Repo Rate", "Inflation Rate", "Unemployment Rate"]

# Parameter display mapping
display_names = {
    "Repo Rate": "Repo / Interest Rates",
    "Inflation Rate": "Inflation",
    "Unemployment Rate": "Unemployment",
    "GDP Growth": "GDP Growth",
    "Manufacturing PMI": "Manufacturing PMI",
    "Merchandise Imports": "Merchandise Imports",
    "Merchandise Exports": "Merchandise Exports"
}

# Flags
flags = {
    "India": "https://flagcdn.com/in.svg",
    "UK": "https://flagcdn.com/gb.svg"
}

# Function to assign color based on logic
def get_color(change, is_reverse=False):
    change_str = str(change)
    if "+" in change_str:
        return "red" if is_reverse else "green"
    elif "-" in change_str:
        return "green" if is_reverse else "red"
    else:
        return "grey"

# Build data
data = {}
for _, row in df.iterrows():
    param = row["Parameter"].strip()
    display_label = display_names.get(param, param)
    is_reverse = param in reverse_logic_params

    # Format values
    value_india = str(row["India"]).strip()
    value_uk = str(row["UK"]).strip()

    if param in percent_params:
        if isinstance(row["India"], (int, float)):
            value_india = f"{row['India'] * 100:.2f}%"
        elif not value_india.endswith("%"):
            value_india += "%"
        
        if isinstance(row["UK"], (int, float)):
            value_uk = f"{row['UK'] * 100:.2f}%"
        elif not value_uk.endswith("%"):
            value_uk += "%"

    # Format dates
    india_date = row["India Date"].strftime("%b-%y") if pd.notnull(row["India Date"]) else ""
    uk_date = row["UK Date"].strftime("%b-%y") if pd.notnull(row["UK Date"]) else ""

    # Format color using logic
    india_color = get_color(row["India MoM Change"], is_reverse)
    uk_color = get_color(row["UK MoM Change"], is_reverse)

    data[display_label] = {
        "India": {
            "value": value_india,
            "date": india_date,
            "change": str(row["India MoM Change"]),
            "color": india_color
        },
        "UK": {
            "value": value_uk,
            "date": uk_date,
            "change": str(row["UK MoM Change"]),
            "color": uk_color
        }
    }

# Card rendering
def card(country, details):
    return f"""
    <div style="text-align: center; background-color: #111; padding: 15px; border-radius: 10px; border: 1px solid #333;">
        <img src='{flags[country]}' width='32'><br>
        <span style='font-size: 20px; font-weight: bold;'>{details["value"]}</span><br>
        <span style='font-size: 13px; color: grey;'>{details["date"]}</span><br>
        <span style='color: {details["color"]}; font-size: 13px;'>{details["change"]}</span>
    </div>
    """

# Render layout
param_names = list(data.keys())
param_pairs = [param_names[i:i+2] for i in range(0, len(param_names), 2)]

for pair in param_pairs:
    col_block = st.columns(2)
    for i, param in enumerate(pair):
        with col_block[i]:
            st.markdown(f"<h3 style='text-align: center;'>{param}</h3>", unsafe_allow_html=True)
            subcols = st.columns(2)
            with subcols[0]:
                st.markdown(card("India", data[param]["India"]), unsafe_allow_html=True)
            with subcols[1]:
                st.markdown(card("UK", data[param]["UK"]), unsafe_allow_html=True)

st.markdown("""
<div style='font-size: 12px; font-style: italic; color: grey; margin-top: 30px;'>
    <strong>Note:</strong> 
    1. bps refers to basis points; 
    2. PMI refers to Purchasing Managers' Index; 
    3. Unit for merchandise imports and exports is US$; 
    4. 1$ = 86.60 INR; 
    5. 1£ = 1.35$.
</div>
""", unsafe_allow_html=True)