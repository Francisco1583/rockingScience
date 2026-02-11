import dash
from dash import Input, Output, State, no_update

from rocket_app.data.dummy import INITIAL_HISTORY, INITIAL_TELEMETRY, next_dummy, update_history

INTERVAL_MS = 100


def register(app):
    @app.callback(
        Output("telemetry_store", "data"),
        Output("telemetry_history_store", "data"),
        Input("telemetry-interval", "n_intervals"),
        Input("reset-btn", "n_clicks"),
        State("telemetry_store", "data"),
        State("telemetry_history_store", "data"),
        prevent_initial_call=True,
    )
    def update_telemetry(interval_ticks, reset_clicks, telemetry, history):
        ctx = dash.callback_context
        if not ctx.triggered:
            return no_update, no_update

        trigger = ctx.triggered[0]["prop_id"].split(".")[0]
        if trigger == "reset-btn":
            return INITIAL_TELEMETRY, INITIAL_HISTORY

        if interval_ticks is None:
            return no_update, no_update

        # Hardware integration point:
        # Replace next_dummy() with your hardware adapter when ready.
        updated = next_dummy(telemetry, INTERVAL_MS)
        updated_history = update_history(history, updated)
        return updated, updated_history

    @app.callback(
        Output("telemetry-interval", "disabled"),
        Input("start-btn", "n_clicks"),
        Input("stop-btn", "n_clicks"),
        Input("reset-btn", "n_clicks"),
        State("telemetry-interval", "disabled"),
        prevent_initial_call=True,
    )
    def toggle_interval(start, stop, reset, disabled):
        ctx = dash.callback_context
        if not ctx.triggered:
            return disabled
        trigger = ctx.triggered[0]["prop_id"].split(".")[0]
        if trigger == "start-btn":
            return False
        if trigger in {"stop-btn", "reset-btn"}:
            return True
        return disabled
