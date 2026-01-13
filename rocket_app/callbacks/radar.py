from dash import Input, Output

from rocket_app.components.radar import radar_figure
from rocket_app.data.dummy import INITIAL_TELEMETRY


def register(app):
    @app.callback(Output("radar-graph", "figure"), Input("telemetry_store", "data"))
    def update_radar(telemetry):
        telemetry = telemetry or INITIAL_TELEMETRY
        return radar_figure(telemetry["distance_m"], telemetry["heading_deg"])
