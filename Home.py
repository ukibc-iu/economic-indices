def render_index_card(name, data, key):
    page, color, trend, icon, overview = data
    latest_real = trend[-1]
    scale_min, scale_max = (-3, 3) if name == "IMP Index" else (-5, 5)
    latest_scaled = max(min(round(latest_real), scale_max), scale_min)

    # Streamlit-native box styling using columns and empty text
    with st.container():
        with st.container():
            # Card background using Streamlit columns trick
            col_bg, col_main, col_bg2 = st.columns([0.05, 0.9, 0.05])
            with col_main:
                st.markdown("### " + icon + " " + name)

                # Plot
                fig = go.Figure()

                for val in range(scale_min, scale_max + 1):
                    fill_color, label = color_map[val]
                    fig.add_shape(type="rect", x0=val - 0.5, x1=val + 0.5, y0=-0.3, y1=0.3,
                                  line=dict(color="black", width=1), fillcolor=fill_color, layer="below")
                    fig.add_trace(go.Scatter(x=[val], y=[0], mode='text', text=[str(val)],
                                             hovertext=[f"{label} ({val})"], showlegend=False,
                                             textfont=dict(color='white', size=14)))

                # Highlight
                fig.add_shape(type="rect", x0=latest_scaled - 0.5, x1=latest_scaled + 0.5,
                              y0=-0.35, y1=0.35, line=dict(color="crimson", width=3, dash="dot"),
                              fillcolor="rgba(0,0,0,0)", layer="above")

                fig.add_trace(go.Scatter(x=[latest_scaled], y=[0.45], mode='text',
                                         text=[f"{latest_real:.2f}"], showlegend=False,
                                         textfont=dict(size=14, color='crimson')))

                fig.update_layout(
                    xaxis=dict(range=[scale_min - 0.5, scale_max + 0.5], showticklabels=False, showgrid=False),
                    yaxis=dict(visible=False),
                    height=180, margin=dict(l=10, r=10, t=10, b=10),
                    plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)", showlegend=False
                )

                st.plotly_chart(fig, use_container_width=True, key=f"plot-{key}")
                st.markdown(f"**Overview:** {overview}")
                if st.button("Open detailed view →", key=f"btn-{key}"):
                    st.switch_page(f"pages/{page}.py")