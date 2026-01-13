import base64
import io
import time

import dash
from dash import Input, Output, State, no_update
import dash_bootstrap_components as dbc
import pandas as pd

from .data import (
    DATA_SOURCE,
    GRAPH_WINDOW,
    INITIAL_GRAPH_DATA,
    INITIAL_TELEMETRY,
    INITIAL_TIMER,
    UPDATE_INTERVAL_MS,
)
from .figures import radar_figure, rocket_offset_from_time, sparkline
from .hardware import get_telemetry
from .pages import resolve_page

LINE_COLORS = {
    "velocity": "#0d6efd",
    "acceleration": "#6f42c1",
}


def register_callbacks(app):
    @app.callback(Output("page-content", "children"), Input("url", "pathname"))
    def display_page(pathname):
        return resolve_page(pathname)

    @app.callback(
        Output("lnk-launch", "className"),
        Output("lnk-analytics", "className"),
        Input("url", "pathname"),
    )
    def highlight_active(path):
        base = "sidebar-link"
        launch_active = path in (None, "", "/", "/launch")
        return (
            f"{base} active" if launch_active else base,
            f"{base} active" if path == "/analytics" else base,
        )

    @app.callback(
        Output("telemetry-store", "data"),
        Output("graph-data-store", "data"),
        Output("timer-store", "data"),
        Input("interval-update", "n_intervals"),
        State("telemetry-store", "data"),
        State("graph-data-store", "data"),
        State("timer-store", "data"),
    )
    def update_telemetry(_, telemetry, graph_data, timer):
        if _ is None:
            return no_update, no_update, no_update

        telemetry = telemetry or INITIAL_TELEMETRY.copy()
        graph_data = graph_data or INITIAL_GRAPH_DATA.copy()
        timer = (timer or INITIAL_TIMER).copy()

        if timer["mode"] == "down":
            total_ms = timer["seconds"] * 1000 + timer["ms"] - UPDATE_INTERVAL_MS
            if total_ms <= 0:
                timer.update(seconds=0, ms=0, mode="up")
            else:
                timer.update(seconds=total_ms // 1000, ms=total_ms % 1000)
        else:
            timer["ms"] += UPDATE_INTERVAL_MS
            if timer["ms"] >= 1000:
                timer["seconds"] += 1
                timer["ms"] -= 1000

        new_telemetry = get_telemetry(telemetry, DATA_SOURCE)

        updated_graph_data = {}
        for key, values in graph_data.items():
            series = list(values) + [new_telemetry.get(key, 0.0)]
            updated_graph_data[key] = series[-GRAPH_WINDOW:]

        return new_telemetry, updated_graph_data, timer

    @app.callback(
        Output("interval-update", "disabled"),
        Input("start-btn", "n_clicks"),
        Input("stop-btn", "n_clicks"),
        Input("reset-btn", "n_clicks"),
        State("interval-update", "disabled"),
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
        Output("telemetry-store", "data", allow_duplicate=True),
        Output("graph-data-store", "data", allow_duplicate=True),
        Output("timer-store", "data", allow_duplicate=True),
        Input("reset-btn", "n_clicks"),
        prevent_initial_call=True,
    )
    def reset_data(_):
        if _ is None:
            return no_update, no_update, no_update
        return INITIAL_TELEMETRY, INITIAL_GRAPH_DATA, INITIAL_TIMER

    @app.callback(
        Output("metric-altitude", "children"),
        Output("metric-velocity", "children"),
        Output("metric-latitude", "children"),
        Output("metric-longitude", "children"),
        Output("metric-distance", "children"),
        Output("timer-display", "children"),
        Output("rocket-coords", "children"),
        Output("distance-display", "children"),
        Output("velocity-current", "children"),
        Output("acceleration-current", "children"),
        Output("velocity-graph", "figure"),
        Output("acceleration-graph", "figure"),
        Output("radar-display", "figure"),
        Input("telemetry-store", "data"),
        Input("graph-data-store", "data"),
        Input("timer-store", "data"),
    )
    def update_display(tlm, gdata, tmr):
        tlm = tlm or INITIAL_TELEMETRY
        gdata = gdata or INITIAL_GRAPH_DATA
        tmr = tmr or INITIAL_TIMER

        metrics = (
            f"{tlm['altitude']:.0f} m",
            f"{tlm['velocity']:.0f} km/h",
            f"{tlm['latitude']:.4f} deg N",
            f"{tlm['longitude']:.4f} deg W",
            f"{tlm['distanceFromBase']:.0f} m",
        )
        clock = f"{tmr['seconds']:02d} s {tmr['ms']:03d} ms"
        coords = f"{tlm['latitude']:.4f} deg N, {tlm['longitude']:.4f} deg W"
        dist_lbl = f"Distance: {tlm['distanceFromBase']:.0f} m"
        currents = (
            f"{tlm['velocity']:.0f} km/h",
            f"{tlm['acceleration']:.2f} m/s^2",
        )

        velocity_fig = sparkline(gdata.get("velocity", []), LINE_COLORS["velocity"])
        acceleration_fig = sparkline(
            gdata.get("acceleration", []), LINE_COLORS["acceleration"]
        )
        radar_fig = radar_figure(rocket_offset=rocket_offset_from_time(time.time()), base=(64, 64))

        return (*metrics, clock, coords, dist_lbl, *currents, velocity_fig, acceleration_fig, radar_fig)

    @app.callback(
        Output("chartEditor", "dataSources"),
        Output("output-data-upload", "children"),
        Input("upload-data", "contents"),
        State("upload-data", "filename"),
        prevent_initial_call=True,
    )
    def upload_csv(contents, filename):
        if not contents or not filename:
            return no_update, no_update

        _, data = contents.split(",", 1)
        decoded = base64.b64decode(data)

        try:
            if filename.lower().endswith(".csv"):
                try:
                    text = decoded.decode("utf-8")
                except UnicodeDecodeError:
                    text = decoded.decode("latin-1")
                df = pd.read_csv(io.StringIO(text))
            elif filename.lower().endswith((".xls", ".xlsx")):
                df = pd.read_excel(io.BytesIO(decoded))
            else:
                raise ValueError("Unsupported file format.")

            message = f"{filename} loaded ({df.shape[0]} rows x {df.shape[1]} columns)"
            return df.to_dict("list"), dbc.Alert(
                message,
                color="success",
                is_open=True,
                className="upload-status",
            )
        except Exception as exc:
            return no_update, dbc.Alert(
                f"Upload error: {exc}",
                color="danger",
                is_open=True,
                className="upload-status",
            )
