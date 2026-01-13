from dash import dcc, html
import dash_chart_editor as dce

from .components import (
    launch_control_panel,
    metrics_strip,
    sidebar,
    sparkline_card,
    upload_box,
)
from .data import (
    BASE_COORDS,
    DEFAULT_DATASET,
    INITIAL_GRAPH_DATA,
    INITIAL_TELEMETRY,
    INITIAL_TIMER,
    UPDATE_INTERVAL_MS,
)


def root_layout():
    return html.Div(
        className="app-shell",
        children=[
            sidebar(),
            html.Div(
                className="page-container",
                children=[
                    dcc.Location(id="url", refresh=False),
                    html.Div(id="page-content"),
                ],
            ),
        ],
    )


def launch_page():
    return html.Div(
        className="launch-page",
        children=[
            dcc.Interval(id="interval-update", interval=UPDATE_INTERVAL_MS, disabled=False),
            dcc.Store(id="telemetry-store", data=INITIAL_TELEMETRY),
            dcc.Store(id="graph-data-store", data=INITIAL_GRAPH_DATA),
            dcc.Store(id="timer-store", data=INITIAL_TIMER),
            html.H2("Rocket Launch Center", className="page-title"),
            metrics_strip(
                [
                    ("Altitude", "metric-altitude"),
                    ("Velocity", "metric-velocity"),
                    ("Latitude", "metric-latitude"),
                    ("Longitude", "metric-longitude"),
                    ("Distance", "metric-distance"),
                ]
            ),
            html.Div(
                className="launch-grid",
                children=[
                    launch_control_panel(BASE_COORDS),
                    html.Div(
                        children=[
                            sparkline_card("Velocity", "velocity-graph", "velocity-current", "#0d6efd"),
                            html.Div(style={"height": "12px"}),
                            sparkline_card("Acceleration", "acceleration-graph", "acceleration-current", "#6f42c1"),
                        ]
                    ),
                ],
            ),
        ],
    )


def analytics_page():
    return html.Div(
        className="analytics-page",
        children=[
            html.H2("Telemetry Analytics Studio", className="page-title"),
            upload_box(),
            html.Div(id="output-data-upload", className="upload-status"),
            html.Div(
                className="chart-editor-shell",
                children=[
                    dce.DashChartEditor(
                        id="chartEditor",
                        dataSources=DEFAULT_DATASET,
                        style={"height": "650px", "width": "100%"},
                    )
                ],
            ),
        ],
    )


def welcome_page():
    return html.Div(
        children=[
            html.H2("Welcome", className="page-title"),
            html.P("Select a page from the sidebar."),
        ]
    )


PAGE_BUILDERS = {
    "/launch": launch_page,
    "/analytics": analytics_page,
}


def resolve_page(pathname):
    if pathname in (None, "/", ""):
        return launch_page()
    builder = PAGE_BUILDERS.get(pathname)
    return builder() if builder else welcome_page()
