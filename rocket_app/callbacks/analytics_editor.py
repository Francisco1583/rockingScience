from dash import Input, Output
import pandas as pd
import plotly.express as px

from rocket_app.data.dummy import DEFAULT_ANALYTICS_DATA


def _df_from_state(state):
    if not state or not state.get("data_sources"):
        return DEFAULT_ANALYTICS_DATA.copy()
    return pd.DataFrame(state["data_sources"])


def _editor_figure(df, time_col, y_col):
    if df.empty:
        raise ValueError("Analytics Editor requires a non-empty dataframe.")
    if not time_col or time_col not in df.columns:
        raise ValueError("Analytics Editor requires the first column as time.")
    if not y_col or y_col not in df.columns:
        raise ValueError("Analytics Editor requires a valid Y column.")
    fig = px.line(df, x=time_col, y=y_col)
    fig.update_layout(margin=dict(l=20, r=20, t=30, b=20))
    return fig


def register(app):
    @app.callback(
        Output("chartEditor", "dataSources"),
        Input("analytics_store", "data"),
    )
    def sync_editor(state):
        df = _df_from_state(state)
        time_col = state.get("time_col") if state else (df.columns[0] if len(df.columns) else None)
        if len(df.columns) < 2:
            raise ValueError("Analytics Editor requires at least two columns.")
        _editor_figure(df, time_col, df.columns[1])
        return df.to_dict("list")
