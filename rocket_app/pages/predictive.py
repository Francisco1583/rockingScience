from dash import dcc, html
import dash_bootstrap_components as dbc

from rocket_app.components import upload_box, upload_status


def layout():
    return html.Div(
        className="predictive-page",
        children=[
            html.H2("Prediccion / Informe de Riesgo", className="page-title"),
            html.Div(
                className="predictive-disclaimer",
                children=(
                    "Demo basado en reglas/anomalias de telemetria. "
                    "No es un pronostico oficial ni reemplaza analisis meteorologicos."
                ),
            ),
            upload_box("predictive-upload", "Upload CSV for risk analysis."),
            upload_status("predictive-upload-status"),
            dcc.Store(id="predictive_store"),
            dcc.Download(id="predictive-download"),
            html.Div(
                className="predictive-top",
                children=[
                    html.Div(id="predictive-top-cards", className="predictive-card-grid"),
                    html.Div(
                        className="predictive-summary-card",
                        children=[
                            html.H4("Mission Risk Report", className="section-title"),
                            html.Div(id="predictive-summary", className="predictive-summary"),
                            dbc.Button(
                                "Download JSON",
                                id="predictive-download-btn",
                                color="secondary",
                                className="mt-2",
                            ),
                        ],
                    ),
                ],
            ),
            html.Div(
                className="predictive-grid",
                children=[
                    html.Div(
                        className="predictive-card",
                        children=[
                            html.H4("Risk Table", className="section-title"),
                            html.Div(id="predictive-risk-table"),
                        ],
                    ),
                    html.Div(
                        className="predictive-card",
                        children=[
                            html.H4("Evidence Charts", className="section-title"),
                            html.Div(
                                id="predictive-evidence",
                                className="overview-scroll",
                                style={"overflowY": "auto", "maxHeight": "75vh"},
                            ),
                        ],
                    ),
                ],
            ),
        ],
    )
