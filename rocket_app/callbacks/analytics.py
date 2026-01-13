import base64
import io

import dash_bootstrap_components as dbc
from dash import Input, Output, State, no_update
import pandas as pd
import plotly.express as px

from rocket_app.data.dummy import DEFAULT_ANALYTICS_DATA, DEFAULT_ANALYTICS_STATE


def _build_figure(df):
    if df.empty:
        return px.line(title="No data")

    numeric_cols = df.select_dtypes(include="number").columns.tolist()
    if len(numeric_cols) >= 2:
        x_col, y_col = numeric_cols[0], numeric_cols[1]
        fig = px.line(df, x=x_col, y=y_col, markers=True)
    elif len(df.columns) >= 2:
        x_col, y_col = df.columns[0], df.columns[1]
        fig = px.line(df, x=x_col, y=y_col, markers=True)
    else:
        x_col = df.columns[0]
        fig = px.line(df, y=x_col, markers=True)

    fig.update_layout(margin=dict(l=20, r=20, t=40, b=20))
    return fig


def _state_from_dataframe(df, message=None, level=None):
    return {
        "data_sources": df.to_dict("list"),
        "message": message,
        "message_level": level,
    }


def _state_from_upload(contents, filename, current_state):
    if not contents or not filename:
        return no_update

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
        return _state_from_dataframe(df, message=message, level="success")
    except Exception as exc:
        fallback = current_state or DEFAULT_ANALYTICS_STATE
        return {
            "data_sources": fallback.get("data_sources"),
            "message": f"Upload error: {exc}",
            "message_level": "danger",
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


def register(app):
    @app.callback(
        Output("analytics_store", "data"),
        Input("upload-data", "contents"),
        State("upload-data", "filename"),
        State("analytics_store", "data"),
        prevent_initial_call=True,
    )
    def update_store(contents, filename, current_state):
        return _state_from_upload(contents, filename, current_state)

    @app.callback(
        Output("analytics-graph", "figure"),
        Output("chartEditor", "dataSources"),
        Output("output-data-upload", "children"),
        Input("analytics_store", "data"),
    )
    def sync_outputs(state):
        df = _df_from_state(state)
        fig = _build_figure(df)
        data_sources = df.to_dict("list")
        alert = _alert_from_state(state)
        return fig, data_sources, alert
