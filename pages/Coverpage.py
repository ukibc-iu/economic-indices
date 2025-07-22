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
    }
}

def country_box(flag_url, value, date, change, color):
    return f"""
    <div style='text-align: center; background-color: #111; padding: 15px; border-radius: 10px;'>
        <img src='{flag_url}' width='32'><br>
        <span style='font-size: 20px; font-weight: bold;'>{value}</span><br>
        <span style='font-size: 13px; color: grey;'>{date}</span><br>
        <span style='color: {color}; font-size: 13px;'>{change}</span>
    </div>
    """

flags = {
    "India": "https://flagcdn.com/in.svg",
    "UK": "https://flagcdn.com/gb.svg"
}

# Loop through each parameter section
for parameter, values in data.items():
    st.markdown(f"### {parameter}")

    col1, col2 = st.columns([1, 1])

    with col1:
        india = values["India"]
        st.markdown(country_box(flags["India"], india["value"], india["date"], india["change"], india["color"]), unsafe_allow_html=True)

    with col2:
        uk = values["UK"]
        st.markdown(country_box(flags["UK"], uk["value"], uk["date"], uk["change"], uk["color"]), unsafe_allow_html=True)

    st.markdown("---")