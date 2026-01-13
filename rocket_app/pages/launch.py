from dash import dcc, html
import dash_bootstrap_components as dbc

from rocket_app.components import countdown_panel, radar_component, telemetry_strip, timeline_container


def sparkline_card(title, graph_id, current_id, color):
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
                        style={"height": "90px"},
                    ),
                    html.Div(
                        style={
                            "display": "grid",
                            "gridTemplateColumns": "1fr 1fr",
                            "gap": "0.5rem 1rem",
                            "marginTop": "8px",
                        },
                        children=[
                            html.Small("Current", className="value-label"),
                            html.Small("Marked", className="value-label text-end"),
                            html.Div(id=current_id, className="value-number", style={"color": color}),
                            html.Div("--", className="value-number text-end"),
                        ],
                    ),
                ],
            ),
        ],
    )


def layout():
    return html.Div(
        children=[
            dcc.Interval(id="telemetry-interval", interval=200, disabled=False),
            html.H2("Rocket Launch Center", className="page-title"),
            telemetry_strip(),
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
                                        className="radar-grid",
                                        children=[
                                            radar_component(),
                                            html.Div(
                                                children=[
                                                    html.Div(
                                                        children=[
                                                            html.Small("Rocket", className="text-muted"),
                                                            html.Div(id="rocket-position", className="fw-bold"),
                                                        ]
                                                    ),
                                                    html.Div(
                                                        className="mt-2",
                                                        children=[
                                                            html.Small("Base", className="text-muted"),
                                                            html.Div("Base 0", className="fw-bold"),
                                                        ],
                                                    ),
                                                    html.Div(id="distance-display", className="text-muted mt-2"),
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
                            sparkline_card("Velocity", "velocity-graph", "velocity-current", "#0d6efd"),
                            html.Div(style={"height": "12px"}),
                            sparkline_card("Altitude", "altitude-graph", "altitude-current", "#198754"),
                        ]
                    ),
                ],
            ),
        ]
    )
