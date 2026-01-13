from dash import dcc, html
import plotly.graph_objects as go


def radar_component(graph_id="radar-graph"):
    return html.Div(
        children=[
            dcc.Graph(
                id=graph_id,
                config={"displayModeBar": False},
                style={"height": "220px"},
            )
        ]
    )


def radar_figure(distance_m, heading_deg):
    max_radius = max(distance_m * 1.2, 100.0)
    fig = go.Figure()
    fig.add_trace(
        go.Scatterpolar(
            r=[0],
            theta=[0],
            mode="markers",
            marker=dict(size=10, color="#0d6efd"),
            name="Base",
        )
    )
    fig.add_trace(
        go.Scatterpolar(
            r=[distance_m],
            theta=[heading_deg],
            mode="markers",
            marker=dict(size=8, color="#dc3545"),
            name="Rocket",
        )
    )
    fig.update_layout(
        showlegend=False,
        margin=dict(l=10, r=10, t=10, b=10),
        paper_bgcolor="rgba(0,0,0,0)",
        polar=dict(
            bgcolor="rgba(0,0,0,0)",
            radialaxis=dict(range=[0, max_radius], showticklabels=False, ticks=""),
            angularaxis=dict(showticklabels=False, ticks=""),
        ),
    )
    return fig
