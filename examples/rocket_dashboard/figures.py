import numpy as np
import plotly.graph_objects as go


def radar_figure(rocket_offset=(0, 0), base=(64, 64)):
    base_x, base_y = base
    fig = go.Figure()
    for radius in (20, 40, 60):
        fig.add_shape(
            type="circle",
            x0=base_x - radius,
            y0=base_y - radius,
            x1=base_x + radius,
            y1=base_y + radius,
            line_color="#bbb",
        )
    fig.add_shape(type="line", x0=base_x, y0=base_y - 60, x1=base_x, y1=base_y + 60, line_color="#bbb")
    fig.add_shape(type="line", x0=base_x - 60, y0=base_y, x1=base_x + 60, y1=base_y, line_color="#bbb")
    fig.add_trace(go.Scatter(x=[base_x], y=[base_y], mode="markers", marker=dict(size=10, color="#0d6efd")))
    fig.add_trace(
        go.Scatter(
            x=[base_x + rocket_offset[0]],
            y=[base_y + rocket_offset[1]],
            mode="markers",
            marker=dict(size=8, color="#dc3545"),
        )
    )
    fig.update_layout(
        margin=dict(l=0, r=0, t=0, b=0),
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        xaxis=dict(visible=False, range=[0, 128]),
        yaxis=dict(visible=False, range=[0, 128]),
    )
    return fig


def sparkline(values, color):
    fig = go.Figure(go.Scatter(y=values, mode="lines", line=dict(color=color, width=2)))
    fig.update_layout(
        margin=dict(l=0, r=0, t=0, b=0),
        xaxis=dict(visible=False),
        yaxis=dict(visible=False),
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
    )
    return fig


def rocket_offset_from_time(t):
    return (np.cos(t) * 20, np.sin(t) * 20)
