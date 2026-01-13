from dash import html


def metric_card(label, value_id):
    return html.Div(
        className="metric-card",
        children=[
            html.Div(label, className="metric-label"),
            html.Div(id=value_id, className="metric-value"),
        ],
    )


def telemetry_strip():
    items = [
        ("Altitude (m)", "metric-altitude"),
        ("Velocity (m/s)", "metric-velocity"),
        ("Heading (deg)", "metric-heading"),
        ("Distance (m)", "metric-distance"),
        ("Status", "metric-status"),
    ]
    return html.Div(
        className="metrics-strip",
        children=[metric_card(label, value_id) for label, value_id in items],
    )
