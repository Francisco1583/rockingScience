from pathlib import Path

import dash
import dash_bootstrap_components as dbc

from .callbacks import register_callbacks
from .pages import root_layout

BOOTSTRAP_ICONS = "https://cdn.jsdelivr.net/npm/bootstrap-icons@1.11.3/font/bootstrap-icons.css"
PLOTLY_CDN = "https://cdn.plot.ly/plotly-2.18.2.min.js"


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
    app.layout = root_layout()
    register_callbacks(app)
    return app


app = create_app()
server = app.server

if __name__ == "__main__":
    app.run(debug=True, port=1234)
