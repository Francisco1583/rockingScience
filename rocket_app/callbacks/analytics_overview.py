import dash_bootstrap_components as dbc
from dash import Input, Output, State, dcc, html, no_update
import pandas as pd
import plotly.express as px

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

    numeric_cols = df.select_dtypes(include="number").columns.tolist()
    time_col_name = df.columns[0]
    if time_col_name not in numeric_cols:
        raise ValueError("Analytics Overview requires numeric time column.")
    y_cols = [col for col in numeric_cols if col != time_col_name]
    if not y_cols:
        raise ValueError("Analytics Overview requires numeric columns to plot.")

    cards = []
    for col in y_cols:
        fig = px.line(df, x=df.columns[0], y=col)
        fig.update_layout(
            margin=dict(l=20, r=20, t=30, b=20),
            xaxis=dict(title=_label_from_column(df.columns[0])),
            yaxis=dict(title=_label_from_column(col)),
            height=300,
        )
        cards.append(
            html.Div(
                className="overview-row",
                children=[
                    html.Div(_label_from_column(col), className="overview-title"),
                    dcc.Graph(
                        figure=fig,
                        config={"displayModeBar": False},
                        className="overview-graph",
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
