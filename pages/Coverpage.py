import streamlit as st

st.set_page_config(layout="wide")

# ---- HEADER ----
st.markdown("<h2 style='text-align: center;'>Macroeconomic Briefing: India and United Kingdom</h2>", unsafe_allow_html=True)
st.markdown("<h3 style='text-align: center; color: teal;'>June 2025</h3>", unsafe_allow_html=True)
st.markdown("<hr>", unsafe_allow_html=True)

# ---- CARD FUNCTION ----
def render_metric(title, india_value, india_date, india_change, uk_value, uk_date, uk_change):
    html = f"""
    <div style="display: flex; justify-content: space-around; align-items: flex-start; background-color: #111; padding: 20px; border-radius: 10px; margin-bottom: 15px;">
        <!-- India Column -->
        <div style="text-align: center; width: 30%;">
            <img src="https://flagcdn.com/in.svg" width="32"><br>
            <span style="font-size: 20px; font-weight: bold;">{india_value}</span><br>
            <span style="font-size: 13px; color: grey;">{india_date}</span><br>
            <span style="color:{'green' if '-' in india_change else 'red'}; font-size: 13px;">{india_change}</span>
        </div>

        <!-- Title Column -->
        <div style="text-align: center; width: 30%;">
            <span style="font-size: 15px; font-weight: 600; color: white;">{title}</span>
        </div>

        <!-- UK Column -->
        <div style="text-align: center; width: 30%;">
            <img src="https://flagcdn.com/gb.svg" width="32"><br>
            <span style="font-size: 20px; font-weight: bold;">{uk_value}</span><br>
            <span style="font-size: 13px; color: grey;">{uk_date}</span><br>
            <span style="color:{'green' if '-' in uk_change else 'red'}; font-size: 13px;">{uk_change}</span>
        </div>
    </div>
    """
    return html

# ---- METRICS ----
metrics = [
    {
        "title": "Repo / Interest Rates",
        "india_value": "5.50%",
        "india_date": "June-2025",
        "india_change": "▼ 50 bps",
        "uk_value": "4.25%",
        "uk_date": "June-2025",
        "uk_change": "No change"
    },
    {
        "title": "Inflation Rate",
        "india_value": "2.82%",
        "india_date": "May-2025",
        "india_change": "▼ 34 bps",
        "uk_value": "3.40%",
        "uk_date": "May-2025",
        "uk_change": "No change"
    },
    {
        "title": "Unemployment Rate",
        "india_value": "5.60%",
        "india_date": "May-2025",
        "india_change": "▲ 50 bps",
        "uk_value": "4.60%",
        "uk_date": "Apr-2025",
        "uk_change": "▼ 10 Q-o-Q"
    }
]

# ---- RENDER ALL ----
for metric in metrics:
    st.markdown(render_metric(**metric), unsafe_allow_html=True)