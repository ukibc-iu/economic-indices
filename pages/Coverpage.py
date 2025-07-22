import streamlit as st

st.set_page_config(layout="wide")

# Header
st.markdown("<h2 style='text-align:center;'>Macroeconomic Briefing: India and United Kingdom</h2>", unsafe_allow_html=True)
st.markdown("<h3 style='text-align:center; color: teal;'>June 2025</h3>", unsafe_allow_html=True)

# Data for each metric box (manually for now, can be from a CSV later)
metrics = [
    {
        "title": "Repo / Interest Rates",
        "in_value": "5.50%",
        "uk_value": "4.25%",
        "in_date": "June-2025",
        "uk_date": "June-2025",
        "in_change": "▼ 50 bps",
        "uk_change": "No change",
        "in_color": "#e6fff2",
        "uk_color": "#fff8e6",
        "in_change_color": "red",
        "uk_change_color": "grey",
    },
    # Repeat for other metrics...
]

# Helper to render a metric box
def render_metric_box(metric):
    col1, col2, col3 = st.columns([1, 0.2, 1])

    with col1:
        st.image("https://flagcdn.com/in.svg", width=32)
        st.markdown(f"<div style='font-size:22px; font-weight:bold;'>{metric['in_value']}</div>", unsafe_allow_html=True)
        st.markdown(f"<div style='color:grey; font-size:14px;'>{metric['in_date']}</div>", unsafe_allow_html=True)
        st.markdown(f"<div style='color:{metric['in_change_color']}; font-size:14px;'>{metric['in_change']}</div>", unsafe_allow_html=True)

    with col2:
        st.markdown(f"<div style='text-align:center; font-weight:600; font-size:16px;'>{metric['title']}</div>", unsafe_allow_html=True)

    with col3:
        st.image("https://flagcdn.com/gb.svg", width=32)
        st.markdown(f"<div style='font-size:22px; font-weight:bold;'>{metric['uk_value']}</div>", unsafe_allow_html=True)
        st.markdown(f"<div style='color:grey; font-size:14px;'>{metric['uk_date']}</div>", unsafe_allow_html=True)
        st.markdown(f"<div style='color:{metric['uk_change_color']}; font-size:14px;'>{metric['uk_change']}</div>", unsafe_allow_html=True)

st.divider()

# Render cards (2 rows, 3 columns layout)
row1 = metrics[:3]
row2 = metrics[3:]  # Add later

for row in [row1, row2]:
    cols = st.columns(3)
    for idx, metric in enumerate(row):
        with cols[idx]:
            render_metric_box(metric)