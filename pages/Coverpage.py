import streamlit as st

st.set_page_config(layout="wide")

st.markdown("<h2 style='text-align:center;'>Macroeconomic Briefing: India and United Kingdom</h2>", unsafe_allow_html=True)
st.markdown("<h3 style='text-align:center; color: teal;'>June 2025</h3>", unsafe_allow_html=True)
st.markdown("<hr>", unsafe_allow_html=True)

# Sample data: Add 6 dicts like this
metrics = [
    {
        "title": "Repo / Interest Rates",
        "in_value": "5.50%",
        "uk_value": "4.25%",
        "in_date": "June-2025",
        "uk_date": "June-2025",
        "in_change": "▼ 50 bps",
        "uk_change": "No change",
        "in_change_color": "red",
        "uk_change_color": "grey"
    },
    {
        "title": "Inflation Rate",
        "in_value": "2.82%",
        "uk_value": "3.40%",
        "in_date": "May-2025",
        "uk_date": "May-2025",
        "in_change": "▼ 34 bps",
        "uk_change": "No change",
        "in_change_color": "green",
        "uk_change_color": "grey"
    },
    # Add 4 more metric boxes...
]

def render_metric(metric):
    box_style = """
        border: 1px solid #444; 
        border-radius: 10px; 
        padding: 12px 10px; 
        background-color: #111111;
    """
    
    html = f"""
    <div style="{box_style}">
        <div style="display: flex; justify-content: space-between; align-items: center;">
            <!-- India Column -->
            <div style="text-align: center; width: 30%;">
                <img src="https://flagcdn.com/in.svg" width="32"><br>
                <span style="font-size: 20px; font-weight: bold;">{metric['in_value']}</span><br>
                <span style="font-size: 13px; color: grey;">{metric['in_date']}</span><br>
                <span style="color:{metric['in_change_color']}; font-size: 13px;">{metric['in_change']}</span>
            </div>

            <!-- Title Center -->
            <div style="text-align: center; width: 40%;">
                <div style="font-size: 15px; font-weight: 600; color: white;">{metric['title']}</div>
            </div>

            <!-- UK Column -->
            <div style="text-align: center; width: 30%;">
                <img src="https://flagcdn.com/gb.svg" width="32"><br>
                <span style="font-size: 20px; font-weight: bold;">{metric['uk_value']}</span><br>
                <span style="font-size: 13px; color: grey;">{metric['uk_date']}</span><br>
                <span style="color:{metric['uk_change_color']}; font-size: 13px;">{metric['uk_change']}</span>
            </div>
        </div>
    </div>
    """
    return html

# Render 2 rows of 3 columns each
rows = [metrics[:3], metrics[3:]]

for row in rows:
    cols = st.columns(3)
    for i, metric in enumerate(row):
        with cols[i]:
            st.markdown(render_metric(metric), unsafe_allow_html=True)