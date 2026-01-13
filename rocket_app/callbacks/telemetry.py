import dash
from dash import Input, Output, State, no_update, html
import plotly.graph_objects as go

from rocket_app.components.timeline import timeline_items
from rocket_app.data.dummy import INITIAL_HISTORY, INITIAL_TELEMETRY, next_dummy, update_history

INTERVAL_MS = 200


def _format_clock(ms):
    total_ms = max(ms, 0)
    seconds = total_ms // 1000
    minutes = seconds // 60
    seconds = seconds % 60
    millis = total_ms % 1000
    return f"{minutes:02d}:{seconds:02d}.{millis:03d}"


def _sparkline(values, color):
    fig = go.Figure(go.Scatter(y=values, mode="lines", line=dict(color=color, width=2)))
    fig.update_layout(
        margin=dict(l=0, r=0, t=0, b=0),
        xaxis=dict(visible=False),
        yaxis=dict(visible=False),
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
    )
    return fig


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
        # Replace next_dummy() with a call to your hardware adapter.
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

    @app.callback(
        Output("metric-altitude", "children"),
        Output("metric-velocity", "children"),
        Output("metric-heading", "children"),
        Output("metric-distance", "children"),
        Output("metric-status", "children"),
        Output("countdown-display", "children"),
        Output("countdown-mode", "children"),
        Output("status-pill", "children"),
        Output("rocket-position", "children"),
        Output("distance-display", "children"),
        Output("velocity-current", "children"),
        Output("altitude-current", "children"),
        Output("velocity-graph", "figure"),
        Output("altitude-graph", "figure"),
        Output("timeline", "children"),
        Input("telemetry_store", "data"),
        Input("telemetry_history_store", "data"),
    )
    def update_display(telemetry, history):
        telemetry = telemetry or INITIAL_TELEMETRY
        history = history or INITIAL_HISTORY

        altitude = f"{telemetry['altitude_m']:.1f}"
        velocity = f"{telemetry['velocity_mps']:.1f}"
        heading = f"{telemetry['heading_deg']:.0f}"
        distance = f"{telemetry['distance_m']:.0f}"
        status = telemetry.get("status", "COUNTDOWN")

        if telemetry["time_ms"] > 0:
            clock_label = "T-"
            clock_value = _format_clock(telemetry["time_ms"])
        else:
            clock_label = "T+"
            clock_value = _format_clock(telemetry["time_tplus"])

        status_text = status.replace("_", " ")
        status_children = [html.Span(className="status-dot"), status_text]

        radar_text = f"Heading {telemetry['heading_deg']:.0f} deg"
        distance_text = f"Range {telemetry['distance_m']:.0f} m"

        velocity_fig = _sparkline(history.get("velocity_mps", []), "#0d6efd")
        altitude_fig = _sparkline(history.get("altitude_m", []), "#198754")

        return (
            f"{altitude} m",
            f"{velocity} m/s",
            f"{heading} deg",
            f"{distance} m",
            status_text,
            clock_value,
            clock_label,
            status_children,
            radar_text,
            distance_text,
            f"{velocity} m/s",
            f"{altitude} m",
            velocity_fig,
            altitude_fig,
            timeline_items(status),
        )
