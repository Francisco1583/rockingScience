from dash import dcc, html
import dash_bootstrap_components as dbc


def sidebar_link(link_id, href, label, icon):
    return dcc.Link(
        id=link_id,
        href=href,
        className="sidebar-link",
        children=[
            html.Img(src=f"/assets/{icon}", alt=label),
            html.Span(label),
        ],
    )


def sidebar():
    return html.Div(
        className="sidebar",
        children=[
            html.Img(src="/assets/logo.png", className="sidebar-logo", alt="Rocket Science"),
            sidebar_link("lnk-launch", "/launch", "Launch", "launch.png"),
            sidebar_link("lnk-analytics", "/analytics", "Analytics", "analytics.png"),
        ],
    )


def metric_item(label, value_id):
    return html.Div(
        className="metric-item",
        children=[
            html.Div(label, className="metric-label"),
            html.Div(id=value_id, className="metric-value"),
        ],
    )


def metrics_strip(items):
    return html.Div(
        className="metrics-strip",
        children=[metric_item(label, value_id) for label, value_id in items],
    )


def launch_control_panel(base_coords):
    return dbc.Card(
        className="panel-card",
        children=[
            html.Div(
                className="panel-header",
                children=[
                    html.I(className="bi bi-rocket-fill"),
                    html.Span("Launch Control"),
                    html.Span(
                        className="status-pill",
                        children=[html.Span(className="status-dot"), "Connected"],
                    ),
                ],
            ),
            html.Div(
                className="panel-body",
                children=[
                    html.Div(
                        className="text-center",
                        children=[
                            html.Small("MISSION CLOCK", className="text-muted"),
                            html.Div(id="timer-display", className="clock"),
                        ],
                    ),
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
                            dcc.Graph(
                                id="radar-display",
                                config={"staticPlot": True},
                                style={"height": "220px"},
                            ),
                            html.Div(
                                children=[
                                    html.Div(
                                        children=[
                                            html.Small("Rocket", className="text-muted"),
                                            html.Div(id="rocket-coords", className="fw-bold"),
                                        ]
                                    ),
                                    html.Div(
                                        className="mt-2",
                                        children=[
                                            html.Small("Base", className="text-muted"),
                                            html.Div(
                                                f"{base_coords['latitude']:.4f} deg N, {base_coords['longitude']:.4f} deg W",
                                                className="fw-bold",
                                            ),
                                        ],
                                    ),
                                    html.Div(id="distance-display", className="text-muted mt-2"),
                                ],
                            ),
                        ],
                    ),
                ],
            ),
        ],
    )


def sparkline_card(title, graph_id, current_id, current_color):
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
                            html.Div(id=current_id, className="value-number", style={"color": current_color}),
                            html.Div("--", className="value-number text-end"),
                        ],
                    ),
                ],
            ),
        ],
    )


def upload_box():
    return dcc.Upload(
        id="upload-data",
        className="upload-area",
        multiple=False,
        accept=".csv,.xls,.xlsx",
        children=html.Div(
            className="upload-content",
            children=[
                html.I(className="bi bi-cloud-arrow-up-fill", style={"fontSize": "30px"}),
                html.Span("Drag and drop your CSV or select a file."),
            ],
        ),
    )
