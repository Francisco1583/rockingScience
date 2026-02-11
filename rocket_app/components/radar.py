from dash import dcc, html
import plotly.graph_objects as go


def radar_component(graph_id="radar-graph", class_name="radar-panel"):
    return html.Div(
        className=class_name,
        children=[
            dcc.Graph(
                id=graph_id,
                config={"displayModeBar": False},
                style={"height": "400px", "width": "100%"},
            )
        ]
    )


def radar_figure(distance_m, heading_deg):
    if distance_m is None or heading_deg is None:
        raise ValueError("Radar requires distance_m and heading_deg.")

    max_radius = max(float(distance_m), 10.0)
    fig = go.Figure()
    fig.add_trace(
        go.Scatterpolar(
            r=[float(distance_m)],
            theta=[float(heading_deg)],
            mode="markers",
            marker=dict(size=12, color="red"),
        )
    )
    fig.update_layout(
        polar=dict(
            domain={"x": [0, 1], "y": [0, 1]},
            radialaxis=dict(range=[0, max_radius], showline=True, gridcolor="lightgray"),
            angularaxis=dict(direction="clockwise", rotation=90, tickvals=[0, 90, 180, 270]),
        ),
        showlegend=False,
        height=400,
    )
    return fig
