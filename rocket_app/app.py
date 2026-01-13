from pathlib import Path

import dash
import dash_bootstrap_components as dbc
from dash import dcc, html

from rocket_app.callbacks import register_callbacks
from rocket_app.components import sidebar
from rocket_app.data.dummy import (
    DEFAULT_ANALYTICS_STATE,
    INITIAL_HISTORY,
    INITIAL_TELEMETRY,
)
from rocket_app.routes import register_routes

BOOTSTRAP_ICONS = "https://cdn.jsdelivr.net/npm/bootstrap-icons@1.11.3/font/bootstrap-icons.css"
PLOTLY_CDN = "https://cdn.plot.ly/plotly-2.18.2.min.js"


def build_layout():
    return html.Div(
        className="app-shell",
        children=[
            sidebar(),
            html.Div(
                className="page-container",
                children=[
                    dcc.Location(id="url", refresh=False),
                    dcc.Store(id="telemetry_store", data=INITIAL_TELEMETRY),
                    dcc.Store(id="telemetry_history_store", data=INITIAL_HISTORY),
                    dcc.Store(id="analytics_store", data=DEFAULT_ANALYTICS_STATE),
                    html.Div(id="page-content"),
                ],
            ),
        ],
    )


def create_app():
    assets_path = Path(__file__).resolve().parent / "assets"
    app = dash.Dash(
        __name__,
        assets_folder=str(assets_path),
        suppress_callback_exceptions=True,
        external_scripts=[PLOTLY_CDN],
        external_stylesheets=[dbc.themes.FLATLY, BOOTSTRAP_ICONS],
    )
    app.title = "Rocket Dashboard"
    app.layout = build_layout()

    register_callbacks(app)
    register_routes(app)
    return app


app = create_app()
server = app.server

if __name__ == "__main__":
    app.run(debug=True, port=1234)
