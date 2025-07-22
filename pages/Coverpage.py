import streamlit as st

st.set_page_config(layout="wide")

# Dummy data
data = {
    "Repo / Interest Rates": {
        "India": {"value": "5.50%", "date": "June-2025", "change": "▼ 50 bps", "color": "red"},
        "UK": {"value": "4.25%", "date": "June-2025", "change": "No change", "color": "grey"},
    },
    "Inflation": {
        "India": {"value": "6.1%", "date": "June-2025", "change": "▲ 20 bps", "color": "red"},
        "UK": {"value": "3.8%", "date": "June-2025", "change": "▼ 10 bps", "color": "green"},
    },
    "Unemployment": {
        "India": {"value": "7.2%", "date": "June-2025", "change": "▼ 15 bps", "color": "green"},
        "UK": {"value": "4.3%", "date": "June-2025", "change": "▲ 5 bps", "color": "red"},
    },
    "GDP Growth": {
        "India": {"value": "7.0%", "date": "2024-25", "change": "▲ 0.2%", "color": "green"},
        "UK": {"value": "1.2%", "date": "2024-25", "change": "▼ 0.1%", "color": "red"},
    }
}

flags = {
    "India": "https://flagcdn.com/in.svg",
    "UK": "https://flagcdn.com/gb.svg"
}

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