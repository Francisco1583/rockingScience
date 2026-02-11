import dash_bootstrap_components as dbc
from dash import Input, Output, State, dcc, html, no_update
import pandas as pd
import plotly.graph_objects as go

from rocket_app.data.csv_loader import load_dataframe_from_upload
from rocket_app.data.dummy import DEFAULT_ANALYTICS_DATA, DEFAULT_ANALYTICS_STATE


def _state_from_dataframe(df, message=None, level=None):
    numeric_cols = df.select_dtypes(include="number").columns.tolist()
    time_col = df.columns[0] if len(df.columns) else None
    return {
        "data_sources": df.to_dict("list"),
        "message": message,
        "message_level": level,
        "time_col": time_col,
        "numeric_cols": numeric_cols,
    }


def _df_from_state(state):
    if not state or not state.get("data_sources"):
        return DEFAULT_ANALYTICS_DATA.copy()
    return pd.DataFrame(state["data_sources"])


def _alert_from_state(state):
    if not state:
        return None
    message = state.get("message")
    if not message:
        return None
    level = state.get("message_level") or "info"
    return dbc.Alert(message, color=level, is_open=True, className="upload-status")


def _label_from_column(column):
    units = {
        "_mps": "m/s",
        "_m": "m",
        "_c": "C",
        "_hpa": "hPa",
        "_deg": "deg",
    }
    for suffix, unit in units.items():
        if column.lower().endswith(suffix):
            return f"{column.replace('_', ' ').title()} ({unit})"
    return column.replace("_", " ").title()


def _overview_cards(df, time_col):
    if df.empty:
        raise ValueError("Analytics Overview requires a non-empty dataframe.")
    if not time_col or time_col not in df.columns:
        raise ValueError("Analytics Overview requires the first column as time.")
    if len(df.columns) < 2:
        raise ValueError("Analytics Overview requires at least two columns.")

    time_values = pd.to_numeric(df[time_col], errors="coerce")
    if time_values.dropna().empty:
        raise ValueError("Analytics Overview requires numeric time column.")

    cards = []
    for col in df.columns[1:]:
        values = pd.to_numeric(df[col], errors="coerce")
        plot_df = pd.DataFrame({time_col: time_values, col: values}).dropna()
        if len(plot_df) < 2:
            continue

        time_array = plot_df[time_col].tolist()
        value_array = plot_df[col].tolist()

        fig = go.Figure(
            go.Scatter(
                x=time_array,
                y=value_array,
                mode="lines",
                line=dict(width=2),
            )
        )
        fig.update_layout(
            margin=dict(l=50, r=20, t=30, b=40),
            xaxis=dict(title=_label_from_column(time_col), autorange=True),
            yaxis=dict(title=_label_from_column(col), autorange=True),
            height=300,
            autosize=False,
            dragmode="pan",
        )

        cards.append(
            html.Div(
                className="overview-row",
                children=[
                    html.Div(_label_from_column(col), className="overview-title"),
                    html.Div(
                        dcc.Graph(
                            figure=fig,
                            config={
                                "scrollZoom": True,
                                "displayModeBar": True,
                                "displaylogo": False,
                                "modeBarButtonsToRemove": [],
                            },
                            className="overview-graph",
                        ),
                        style={
                            "overflowX": "auto",
                            "overflowY": "auto",
                            "maxHeight": "320px",
                            "maxWidth": "100%",
                            "border": "1px solid #2a2a2a",
                            "borderRadius": "6px",
                        },
                    ),
                ],
            )
        )
    return cards


def register(app):
    @app.callback(
        Output("analytics_store", "data"),
        Input("upload-data", "contents"),
        State("upload-data", "filename"),
        State("analytics_store", "data"),
        prevent_initial_call=True,
    )
    def update_store(contents, filename, current_state):
        if not contents or not filename:
            return no_update
        try:
            df, message = load_dataframe_from_upload(contents, filename)
            if df is None:
                return no_update
            return _state_from_dataframe(df, message=message, level="success")
        except Exception as exc:
            fallback = current_state or DEFAULT_ANALYTICS_STATE
            return {
                "data_sources": fallback.get("data_sources"),
                "message": f"Upload error: {exc}",
                "message_level": "danger",
                "time_col": fallback.get("time_col"),
                "numeric_cols": fallback.get("numeric_cols"),
            }

    @app.callback(
        Output("analytics-overview", "children"),
        Output("output-data-upload", "children"),
        Input("analytics_store", "data"),
    )
    def build_overview(state):
        df = _df_from_state(state)
        time_col = state.get("time_col") if state else (df.columns[0] if len(df.columns) else None)
        return _overview_cards(df, time_col), _alert_from_state(state)
