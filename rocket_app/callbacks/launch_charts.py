import io

import pandas as pd
import plotly.graph_objects as go
from dash import Input, Output, State, html, no_update

from rocket_app.components.timeline import timeline_items
from rocket_app.data.dummy import INITIAL_HISTORY, INITIAL_TELEMETRY


def _format_clock(ms):
    total_ms = max(ms, 0)
    seconds = total_ms // 1000
    minutes = seconds // 60
    seconds = seconds % 60
    millis = total_ms % 1000
    return f"{minutes:02d}:{seconds:02d}.{millis:03d}"


def _y_title_for_key(key):
    units = {
        "velocity_mps": "Velocity (m/s)",
        "acceleration_mps2": "Acceleration (m/s^2)",
        "altitude_m": "Altitude (m)",
    }
    return units.get(key, key.replace("_", " ").title())


def _line_chart(df, x_key, y_key, color):
    if x_key not in df.columns or y_key not in df.columns:
        raise ValueError(f"Launch chart requires {x_key} and {y_key}.")
    time_array = df[x_key].tolist()
    value_array = df[y_key].tolist()
    if len(time_array) < 2 or len(value_array) < 2:
        fig = go.Figure()
        fig.update_layout(
            margin=dict(l=40, r=20, t=30, b=30),
            xaxis=dict(title="T+ (s)", showgrid=False, range=[0, 1]),
            yaxis=dict(
                showgrid=True,
                gridcolor="rgba(0,0,0,0.08)",
                title=_y_title_for_key(y_key),
                range=[-1, 1],
            ),
            plot_bgcolor="rgba(0,0,0,0)",
            paper_bgcolor="rgba(0,0,0,0)",
            height=200,
            autosize=False,
            annotations=[
                dict(
                    text="Waiting for data...",
                    x=0.5,
                    y=0.5,
                    xref="paper",
                    yref="paper",
                    showarrow=False,
                    font=dict(color="#6c757d"),
                )
            ],
        )
        return fig

    x_min = min(time_array)
    x_max = max(time_array)
    y_min = min(value_array) * 1.1
    y_max = max(value_array) * 1.1

    if x_min == x_max:
        x_min -= 1
        x_max += 1
    if y_min == y_max:
        y_min -= 1
        y_max += 1

    fig = go.Figure(
        go.Scatter(
            x=time_array,
            y=value_array,
            mode="lines",
            line=dict(color=color, width=2),
        )
    )
    fig.update_layout(
        margin=dict(l=40, r=20, t=30, b=30),
        xaxis=dict(title="T+ (s)", showgrid=False, range=[x_min, x_max]),
        yaxis=dict(
            showgrid=True,
            gridcolor="rgba(0,0,0,0.08)",
            title=_y_title_for_key(y_key),
            range=[y_min, y_max],
        ),
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        height=200,
        autosize=False,
    )
    return fig


def _history_to_df(history):
    history = history or INITIAL_HISTORY
    if not history:
        return pd.DataFrame(columns=["time_s", "altitude_m", "velocity_mps"])
    df = pd.DataFrame(history)
    if "time_s" not in df.columns and "time_tplus" in df.columns:
        df["time_s"] = df["time_tplus"] / 1000.0
    return df


def register(app):
    @app.callback(
        Output("metric-altitude", "children"),
        Output("metric-velocity", "children"),
        Output("metric-heading", "children"),
        Output("metric-distance", "children"),
        Output("metric-status", "children"),
        Output("countdown-display", "children"),
        Output("countdown-mode", "children"),
        Output("status-pill", "children"),
        Output("velocity-current", "children"),
        Output("accel-current", "children"),
        Output("altitude-current", "children"),
        Output("velocity-chart", "figure"),
        Output("accel-chart", "figure"),
        Output("altitude-chart", "figure"),
        Output("distance-total", "children"),
        Output("distance-x", "children"),
        Output("distance-y", "children"),
        Output("coords-current", "children"),
        Output("heading-current", "children"),
        Output("phase-current", "children"),
        Output("timeline", "children"),
        Input("telemetry_store", "data"),
        Input("telemetry_history_store", "data"),
    )
    def update_launch_panels(telemetry, history):
        telemetry = telemetry or INITIAL_TELEMETRY
        history_df = _history_to_df(history)

        altitude = f"{telemetry['altitude_m']:.1f}"
        velocity = f"{telemetry['velocity_mps']:.1f}"
        acceleration = f"{telemetry['acceleration_mps2']:.2f}"
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

        velocity_fig = _line_chart(history_df, "time_s", "velocity_mps", "#0d6efd")
        accel_fig = _line_chart(history_df, "time_s", "acceleration_mps2", "#dc3545")
        altitude_fig = _line_chart(history_df, "time_s", "altitude_m", "#198754")

        coords_text = (
            f"({telemetry['x_m']:.1f}, {telemetry['y_m']:.1f}, {telemetry['z_m']:.1f}) m"
        )

        return (
            f"{altitude} m",
            f"{velocity} m/s",
            f"{heading} deg",
            f"{distance} m",
            status_text,
            clock_value,
            clock_label,
            status_children,
            f"{velocity} m/s",
            f"{acceleration} m/s^2",
            f"{altitude} m",
            velocity_fig,
            accel_fig,
            altitude_fig,
            f"{telemetry['distance_m']:.1f} m",
            f"{telemetry['x_m']:.1f} m",
            f"{telemetry['y_m']:.1f} m",
            coords_text,
            f"{telemetry['heading_deg']:.0f} deg",
            telemetry.get("phase", status_text),
            timeline_items(status),
        )

    @app.callback(
        Output("download-telemetry", "data"),
        Input("download-btn", "n_clicks"),
        State("telemetry_history_store", "data"),
        prevent_initial_call=True,
    )
    def download_history(n_clicks, history):
        if not n_clicks:
            return no_update

        history_df = _history_to_df(history)
        if history_df.empty:
            return no_update

        export_cols = [
            "time_s",
            "altitude_m",
            "velocity_mps",
            "acceleration_mps2",
            "x_m",
            "y_m",
            "z_m",
            "heading_deg",
            "phase",
        ]
        for col in export_cols:
            if col not in history_df:
                history_df[col] = None

        csv_buffer = io.StringIO()
        history_df[export_cols].to_csv(csv_buffer, index=False)
        return dict(
            content=csv_buffer.getvalue(),
            filename="telemetry_history.csv",
            type="text/csv",
        )
