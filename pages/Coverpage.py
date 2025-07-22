import streamlit as st

st.set_page_config(layout="wide")

# Header
st.markdown("<h2 style='text-align: center;'>Macroeconomic Briefing: India and United Kingdom</h2>", unsafe_allow_html=True)
st.markdown("<h3 style='text-align: center; color: teal;'>June 2025</h3><hr>", unsafe_allow_html=True)

# Aligned block: India | Title | UK
html_block = """
<div style="display: flex; justify-content: space-around; align-items: flex-start; background-color: #111; padding: 20px; border-radius: 10px;">

    <!-- India Column -->
    <div style="text-align: center; width: 30%;">
        <img src="https://flagcdn.com/in.svg" width="32"><br>
        <span style="font-size: 20px; font-weight: bold;">5.50%</span><br>
        <span style="font-size: 13px; color: grey;">June-2025</span><br>
        <span style="color: red; font-size: 13px;">▼ 50 bps</span>
    </div>

    <!-- Title Column -->
    <div style="text-align: center; width: 30%;">
        <span style="font-size: 15px; font-weight: 600; color: white;">Repo / Interest Rates</span>
    </div>

    <!-- UK Column -->
    <div style="text-align: center; width: 30%;">
        <img src="https://flagcdn.com/gb.svg" width="32"><br>
        <span style="font-size: 20px; font-weight: bold;">4.25%</span><br>
        <span style="font-size: 13px; color: grey;">June-2025</span><br>
        <span style="color: grey; font-size: 13px;">No change</span>
    </div>

</div>
"""

# Render it
st.markdown(html_block, unsafe_allow_html=True)