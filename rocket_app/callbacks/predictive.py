import json

import dash_bootstrap_components as dbc
from dash import Input, Output, State, dcc, html, no_update
import numpy as np
import pandas as pd
import plotly.express as px

from rocket_app.data.csv_loader import load_dataframe_from_upload
from rocket_app.data.dummy import DEFAULT_ANALYTICS_DATA


def _df_from_state(state):
    if not state or not state.get("data_sources"):
        return DEFAULT_ANALYTICS_DATA.copy()
    return pd.DataFrame(state["data_sources"])


def _safe_col(df, name):
    if name and name in df.columns:
        return df[name]
    return pd.Series([np.nan] * len(df))


def _outlier_rate(series):
    series = series.dropna()
    if series.empty:
        return 0.0
    q1 = series.quantile(0.25)
    q3 = series.quantile(0.75)
    iqr = q3 - q1
    if iqr == 0:
        return 0.0
    lower = q1 - 1.5 * iqr
    upper = q3 + 1.5 * iqr
    return float(((series < lower) | (series > upper)).mean())


def _normalize(value, low, high):
    if high <= low:
        return 0.0
    return float(np.clip((value - low) / (high - low), 0.0, 1.0))


def _score_to_level(score):
    if score >= 0.66:
        return "High"
    if score >= 0.33:
        return "Medium"
    return "Low"


def _risk_report(df):
    time_col = df.columns[0] if len(df.columns) else None
    dt = _safe_col(df, time_col).diff().replace(0, np.nan)

    pressure = _safe_col(df, "pressure_hpa")
    temperature = _safe_col(df, "temperature_c")
    velocity = _safe_col(df, "velocity_mps")
    heading = _safe_col(df, "heading_deg")

    dPdt = pressure.diff() / dt
    dTdt = temperature.diff() / dt
    jerk = velocity.diff().diff() / dt
    heading_var = heading.rolling(window=10, min_periods=3).var()

    pressure_drop_rate = float((-dPdt.min(skipna=True) * 60) if not dPdt.isna().all() else 0.0)
    temp_spike = float((dTdt.abs().max(skipna=True) * 60) if not dTdt.isna().all() else 0.0)
    heading_variability = float(heading_var.mean(skipna=True) if not heading_var.isna().all() else 0.0)
    jerk_peak = float(jerk.abs().max(skipna=True) if not jerk.isna().all() else 0.0)
    velocity_osc = float(velocity.diff().abs().mean(skipna=True) if not velocity.isna().all() else 0.0)

    missing_rate = float(df.isna().mean().mean()) if not df.empty else 0.0
    outlier_rate = float(
        np.mean([_outlier_rate(df[col]) for col in df.select_dtypes(include="number").columns])
        if not df.empty
        else 0.0
    )

    storm_score = _normalize(pressure_drop_rate, 0.4, 2.5)
    wind_score = np.clip(_normalize(heading_variability, 5.0, 40.0) + _normalize(velocity_osc, 0.2, 2.0), 0, 1)
    turbulence_score = np.clip(_normalize(heading_variability, 8.0, 45.0) + _normalize(jerk_peak, 0.05, 0.5), 0, 1)
    thermal_score = _normalize(temp_spike, 0.2, 2.0)
    sensor_score = np.clip(_normalize(missing_rate, 0.02, 0.15) + _normalize(outlier_rate, 0.02, 0.2), 0, 1)

    risks = [
        {
            "event": "High Wind / Gust Risk",
            "score": float(wind_score),
            "evidence": f"heading variance: {heading_variability:.2f}, velocity oscillation: {velocity_osc:.2f}",
        },
        {
            "event": "Storm / Rapid pressure drop risk",
            "score": float(storm_score),
            "evidence": f"pressure drop rate: {pressure_drop_rate:.2f} hPa/min",
        },
        {
            "event": "Turbulence / Instability risk",
            "score": float(turbulence_score),
            "evidence": f"heading variance: {heading_variability:.2f}, jerk peak: {jerk_peak:.2f}",
        },
        {
            "event": "Thermal Stress risk",
            "score": float(thermal_score),
            "evidence": f"temperature spike rate: {temp_spike:.2f} C/min",
        },
        {
            "event": "Sensor Anomaly risk",
            "score": float(sensor_score),
            "evidence": f"missing rate: {missing_rate:.2%}, outlier rate: {outlier_rate:.2%}",
        },
        {
            "event": "Natural phenomena (earthquake/volcanic)",
            "score": 0.05,
            "evidence": "Insufficient evidence from telemetry-only data",
            "insufficient": True,
        },
    ]

    for item in risks:
        item["probability"] = int(round(item["score"] * 100))
        item["level"] = _score_to_level(item["score"])

    summary = (
        "Informe demo basado en reglas de anomalias. "
        "Use estos resultados solo como guia para pruebas de interfaz."
    )

    return {
        "risks": risks,
        "summary": summary,
        "time_col": time_col,
    }


def _risk_table(risks):
    header = html.Thead(
        html.Tr(
            [
                html.Th("Event"),
                html.Th("Probability"),
                html.Th("Level"),
                html.Th("Evidence"),
            ]
        )
    )
    body_rows = []
    for item in risks:
        badge_color = "danger" if item["level"] == "High" else "warning" if item["level"] == "Medium" else "success"
        badge_text = item["level"]
        if item.get("insufficient"):
            badge_color = "secondary"
            badge_text = "Insufficient data"
        body_rows.append(
            html.Tr(
                [
                    html.Td(item["event"]),
                    html.Td(f"{item['probability']}%"),
                    html.Td(dbc.Badge(badge_text, color=badge_color, className="me-1")),
                    html.Td(item["evidence"]),
                ]
            )
        )
    return dbc.Table([header, html.Tbody(body_rows)], bordered=False, hover=True, responsive=True)


def _top_cards(risks):
    top = sorted(risks, key=lambda item: item["probability"], reverse=True)[:3]
    cards = []
    for item in top:
        cards.append(
            html.Div(
                className="predictive-highlight-card",
                children=[
                    html.Div(item["event"], className="predictive-highlight-title"),
                    html.Div(f"{item['probability']}%", className="predictive-highlight-value"),
                    html.Div(item["evidence"], className="predictive-highlight-evidence"),
                ],
            )
        )
    return cards


def _evidence_chart(df, time_col, col_name):
    if not time_col or time_col not in df.columns:
        raise ValueError("Predictive charts require the first column as time.")
    if col_name not in df.columns:
        raise ValueError(f"Predictive chart requires column {col_name}.")
    fig = px.line(df, x=time_col, y=col_name)
    fig.update_layout(margin=dict(l=20, r=20, t=30, b=20), height=300)
    return fig


def _evidence_rows(df, time_col):
    numeric_cols = df.select_dtypes(include="number").columns.tolist()
    if time_col not in numeric_cols:
        raise ValueError("Predictive evidence requires numeric time column.")
    y_cols = [col for col in numeric_cols if col != time_col]
    if not y_cols:
        raise ValueError("Predictive evidence requires numeric columns to plot.")

    rows = []
    for col in y_cols:
        fig = _evidence_chart(df, time_col, col)
        rows.append(
            html.Div(
                className="overview-row",
                children=[
                    html.Div(col.replace("_", " ").title(), className="overview-title"),
                    dcc.Graph(figure=fig, config={"displayModeBar": False}),
                ],
            )
        )
    return rows


def register(app):
    @app.callback(
        Output("predictive_store", "data"),
        Input("predictive-upload", "contents"),
        State("predictive-upload", "filename"),
        prevent_initial_call=True,
    )
    def update_predictive_store(contents, filename):
        if not contents or not filename:
            return no_update
        try:
            df, message = load_dataframe_from_upload(contents, filename)
            if df is None:
                return no_update
            report = _risk_report(df)
            return {
                "data_sources": df.to_dict("list"),
                "message": message,
                "message_level": "success",
                "report": report,
            }
        except Exception as exc:
            return {
                "data_sources": DEFAULT_ANALYTICS_DATA.to_dict("list"),
                "message": f"Upload error: {exc}",
                "message_level": "danger",
                "report": _risk_report(DEFAULT_ANALYTICS_DATA.copy()),
            }

    @app.callback(
        Output("predictive-top-cards", "children"),
        Output("predictive-risk-table", "children"),
        Output("predictive-summary", "children"),
        Output("predictive-evidence", "children"),
        Output("predictive-upload-status", "children"),
        Input("predictive_store", "data"),
    )
    def build_predictive_report(state):
        df = _df_from_state(state)
        report = state.get("report") if state else _risk_report(df)
        risks = report.get("risks", [])
        time_col = report.get("time_col")
        return (
            _top_cards(risks),
            _risk_table(risks),
            report.get("summary"),
            _evidence_rows(df, time_col),
            dbc.Alert(state.get("message"), color=state.get("message_level", "info"), className="upload-status")
            if state and state.get("message")
            else None,
        )

    @app.callback(
        Output("predictive-download", "data"),
        Input("predictive-download-btn", "n_clicks"),
        State("predictive_store", "data"),
        prevent_initial_call=True,
    )
    def download_report(n_clicks, state):
        if not n_clicks:
            return no_update
        report = (state or {}).get("report")
        if not report:
            return no_update
        return dict(
            content=json.dumps(report, indent=2),
            filename="risk_report.json",
            type="application/json",
        )
