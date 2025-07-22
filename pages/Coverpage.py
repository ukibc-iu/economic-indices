import streamlit as st

st.set_page_config(layout="wide")

st.markdown("""
    <h2 style='text-align: center;'>Macroeconomic Briefing: India and United Kingdom</h2>
    <h3 style='text-align: center; color: teal;'>June 2025</h3>
    <hr>
""", unsafe_allow_html=True)

# ✅ WORKING HTML
st.markdown("""
<div style="display: flex; justify-content: space-between; align-items: center; padding: 20px 60px;">

    <!-- India -->
    <div style="width: 30%; text-align: center; background-color: #111; padding: 10px; border-radius: 10px;">
        <img src="https://flagcdn.com/in.svg" width="32"><br>
        <span style="font-size: 20px; font-weight: bold;">5.50%</span><br>
        <span style="font-size: 13px; color: grey;">June-2025</span><br>
        <span style="color: red; font-size: 13px;">▼ 50 bps</span>
    </div>

    <!-- Title (center block, no data, just the label) -->
    <div style="width: 30%; text-align: center;">
        <div style="font-size: 15px; font-weight: 600; color: white;">Repo / Interest Rates</div>
    </div>

    <!-- UK -->
    <div style="width: 30%; text-align: center; background-color: #111; padding: 10px; border-radius: 10px;">
        <img src="https://flagcdn.com/gb.svg" width="32"><br>
        <span style="font-size: 20px; font-weight: bold;">4.25%</span><br>
        <span style="font-size: 13px; color: grey;">June-2025</span><br>
        <span style="color: grey; font-size: 13px;">No change</span>
    </div>

</div>
""", unsafe_allow_html=True)