from dash import dcc, html
import plotly.graph_objects as go


def rocket_3d_component(graph_id="rocket-3d-graph", class_name="rocket-3d-panel"):
    return html.Div(
        className=class_name,
        children=[
            dcc.Graph(
                id=graph_id,
                config={"displayModeBar": False},
                style={"height": "600px", "width": "100%"},
            )
        ],
    )


def rocket_3d_figure(points, max_trail=600):
    if not points:
        raise ValueError("Rocket 3D requires telemetry history.")

    latest = points[-1]
    if latest.get("distance_m") is None or latest.get("heading_deg") is None or latest.get("altitude_m") is None:
        raise ValueError("Rocket 3D requires distance_m, heading_deg, and altitude_m.")

    x = float(latest.get("x_m", 0.0))
    y = float(latest.get("y_m", 0.0))
    z = max(0.0, float(latest.get("z_m", latest.get("altitude_m", 0.0))))

    path = points[-max_trail:]
    path_x = [float(item.get("x_m", 0.0)) for item in path]
    path_y = [float(item.get("y_m", 0.0)) for item in path]
    path_z = [max(0.0, float(item.get("z_m", item.get("altitude_m", 0.0)))) for item in path]

    fig = go.Figure()
    fig.add_trace(
        go.Scatter3d(
            x=path_x,
            y=path_y,
            z=path_z,
            mode="lines",
            line=dict(color="black", width=4),
            name="Path",
        )
    )
    fig.add_trace(
        go.Scatter3d(
            x=[x],
            y=[y],
            z=[z],
            mode="markers",
            marker=dict(size=6, color="blue"),
            name="Rocket",
        )
    )
    fig.add_trace(
        go.Scatter3d(
            x=[0, x],
            y=[0, y],
            z=[0, z],
            mode="lines",
            line=dict(color="red", width=4),
            name="Vector",
        )
    )
    fig.update_layout(
        scene=dict(
            xaxis=dict(range=[-200, 200], title="X (m)"),
            yaxis=dict(range=[-200, 200], title="Y (m)"),
            zaxis=dict(range=[0, 1200], title="Z (m)"),
            aspectmode="cube",
        ),
        autosize=False,
        height=600,
        dragmode="orbit",
    )
    return fig
