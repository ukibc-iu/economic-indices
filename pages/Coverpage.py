import streamlit as st

st.set_page_config(layout="wide")

# Title
st.markdown("<h2 style='text-align: center;'>Macroeconomic Briefing: India and United Kingdom</h2>", unsafe_allow_html=True)
st.markdown("<h3 style='text-align: center; color: teal;'>June 2025</h3>", unsafe_allow_html=True)
st.markdown("---")

# Create 3 side-by-side columns
col1, col2, col3 = st.columns([1, 1, 1])

# India Column
with col1:
    st.markdown("<div style='text-align: center; background-color: #111; padding: 15px; border-radius: 10px;'>"
                "<img src='https://flagcdn.com/in.svg' width='32'><br>"
                "<span style='font-size: 20px; font-weight: bold;'>5.50%</span><br>"
                "<span style='font-size: 13px; color: grey;'>June-2025</span><br>"
                "<span style='color: red; font-size: 13px;'>▼ 50 bps</span>"
                "</div>", unsafe_allow_html=True)

# Center Label Column
with col2:
    st.markdown("<div style='text-align: center; padding-top: 25px;'>"
                "<span style='font-size: 16px; font-weight: 600;'>Repo / Interest Rates</span>"
                "</div>", unsafe_allow_html=True)

# UK Column
with col3:
    st.markdown("<div style='text-align: center; background-color: #111; padding: 15px; border-radius: 10px;'>"
                "<img src='https://flagcdn.com/gb.svg' width='32'><br>"
                "<span style='font-size: 20px; font-weight: bold;'>4.25%</span><br>"
                "<span style='font-size: 13px; color: grey;'>June-2025</span><br>"
                "<span style='color: grey; font-size: 13px;'>No change</span>"
                "</div>", unsafe_allow_html=True)