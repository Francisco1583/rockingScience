from dash import dcc, html
import dash_bootstrap_components as dbc

from rocket_app.components import (
    countdown_panel,
    rocket_3d_component,
    telemetry_strip,
    timeline_container,
)


def line_chart_card(title, graph_id, current_id, color):
    return dbc.Card(
        className="sparkline-card",
        children=[
            html.Div(
                className="sparkline-header",
                children=[html.I(className="bi bi-graph-up-arrow me-2"), title],
            ),
            html.Div(
                className="sparkline-body",
                children=[
                    dcc.Graph(
                        id=graph_id,
                        config={"displayModeBar": False},
                        style={"height": "210px"},
                    ),
                    html.Div(
                        style={
                            "display": "grid",
                            "gridTemplateColumns": "1fr",
                            "gap": "0.5rem 1rem",
                            "marginTop": "8px",
                        },
                        children=[
                            html.Small("Current", className="value-label"),
                            html.Div(id=current_id, className="value-number", style={"color": color}),
                        ],
                    ),
                ],
            ),
        ],
    )


def layout():
    return html.Div(
        children=[
            dcc.Interval(id="telemetry-interval", interval=100, disabled=False),
            html.H2("Rocket Launch Center", className="page-title"),
            telemetry_strip(),
            dcc.Download(id="download-telemetry"),
            html.Div(
                className="launch-grid",
                children=[
                    dbc.Card(
                        className="panel-card",
                        children=[
                            html.Div(
                                className="panel-header",
                                children=[
                                    html.I(className="bi bi-rocket-fill"),
                                    html.Span("Launch Control"),
                                    html.Span(
                                        id="status-pill",
                                        className="status-pill",
                                        children=[html.Span(className="status-dot"), "Connected"],
                                    ),
                                ],
                            ),
                            html.Div(
                                className="panel-body",
                                children=[
                                    countdown_panel(),
                                    html.Div(
                                        className="control-buttons",
                                        children=[
                                            dbc.Button("Start", id="start-btn", color="success"),
                                            dbc.Button("Stop", id="stop-btn", color="danger"),
                                            dbc.Button("Reset", id="reset-btn", color="secondary"),
                                        ],
                                    ),
                                    html.Div(
                                        className="launch-3d-row",
                                        children=[
                                            html.Div(
                                                className="rocket-3d-panel",
                                                children=[
                                                    rocket_3d_component(class_name="rocket-3d-panel-inner"),
                                                    html.Div(
                                                        className="flight-metrics",
                                                        children=[
                                                            html.Div(
                                                                className="flight-metric",
                                                                children=[
                                                                    html.Small("Distance (total)", className="value-label"),
                                                                    html.Div(
                                                                        id="distance-total",
                                                                        className="value-number",
                                                                    ),
                                                                ],
                                                            ),
                                                            html.Div(
                                                                className="flight-metric",
                                                                children=[
                                                                    html.Small("Distance X", className="value-label"),
                                                                    html.Div(id="distance-x", className="value-number"),
                                                                ],
                                                            ),
                                                            html.Div(
                                                                className="flight-metric",
                                                                children=[
                                                                    html.Small("Distance Y", className="value-label"),
                                                                    html.Div(id="distance-y", className="value-number"),
                                                                ],
                                                            ),
                                                            html.Div(
                                                                className="flight-metric",
                                                                children=[
                                                                    html.Small(
                                                                        "Coordinates (x,y,z)",
                                                                        className="value-label",
                                                                    ),
                                                                    html.Div(
                                                                        id="coords-current",
                                                                        className="value-number",
                                                                    ),
                                                                ],
                                                            ),
                                                            html.Div(
                                                                className="flight-metric",
                                                                children=[
                                                                    html.Small("Heading", className="value-label"),
                                                                    html.Div(
                                                                        id="heading-current",
                                                                        className="value-number",
                                                                    ),
                                                                ],
                                                            ),
                                                            html.Div(
                                                                className="flight-metric",
                                                                children=[
                                                                    html.Small("Phase", className="value-label"),
                                                                    html.Div(
                                                                        id="phase-current",
                                                                        className="value-number",
                                                                    ),
                                                                ],
                                                            ),
                                                        ],
                                                    ),
                                                ],
                                            ),
                                        ],
                                    ),
                                    timeline_container(),
                                ],
                            ),
                        ],
                    ),
                    html.Div(
                        children=[
                            html.Div(
                                className="telemetry-panel",
                                children=[
                                    html.Div(
                                        className="telemetry-header",
                                        children="Telemetry History",
                                    ),
                                    line_chart_card(
                                        "Velocity vs T+",
                                        "velocity-chart",
                                        "velocity-current",
                                        "#0d6efd",
                                    ),
                                    html.Div(style={"height": "12px"}),
                                    line_chart_card(
                                        "Acceleration vs T+",
                                        "accel-chart",
                                        "accel-current",
                                        "#dc3545",
                                    ),
                                    html.Div(style={"height": "12px"}),
                                    line_chart_card(
                                        "Altitude vs T+",
                                        "altitude-chart",
                                        "altitude-current",
                                        "#198754",
                                    ),
                                ],
                            ),
                            html.Div(
                                className="download-row",
                                children=[
                                    html.Div(className="download-label", children="Telemetry History"),
                                    dbc.Button(
                                        "Download CSV",
                                        id="download-btn",
                                        color="primary",
                                        className="download-button",
                                    ),
                                ],
                            ),
                            html.Div(
                                className="text-muted small",
                                children="Use the button to export the full flight history.",
                            ),
                        ]
                    ),
                ],
            ),
        ]
    )
