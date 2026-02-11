from dash import Input, Output

from rocket_app.components.rocket_3d import rocket_3d_figure
from rocket_app.data.dummy import INITIAL_HISTORY


def register(app):
    @app.callback(Output("rocket-3d-graph", "figure"), Input("telemetry_history_store", "data"))
    def update_rocket_3d(history):
        history = history or INITIAL_HISTORY
        return rocket_3d_figure(history)
