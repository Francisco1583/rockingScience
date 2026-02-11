from dash import dcc, html
import dash_bootstrap_components as dbc
import dash_chart_editor as dce

from rocket_app.components import upload_box, upload_status


def layout():
    return html.Div(
        className="analytics-page",
        children=[
            html.H2("Telemetry Analytics Studio", className="page-title"),
            upload_box("upload-data", "Drag and drop your CSV or select a file."),
            upload_status("output-data-upload"),
            dcc.Tabs(
                id="analytics-tabs",
                value="overview",
                children=[
                    dcc.Tab(
                        label="Overview",
                        value="overview",
                        children=[
                            html.Div(
                                id="analytics-overview",
                                className="overview-scroll",
                                style={"overflowY": "auto", "maxHeight": "75vh"},
                                children=[],
                            )
                        ],
                    ),
                    dcc.Tab(
                        label="Editor",
                        value="editor",
                        children=[
                            html.Div(
                                className="chart-editor-shell",
                                children=[
                                    dce.DashChartEditor(
                                        id="chartEditor",
                                        dataSources={},
                                        style={"height": "620px", "width": "100%"},
                                    ),
                                    html.Div(
                                        className="editor-actions",
                                        children=dbc.Button(
                                            "Apply Changes",
                                            id="editor-apply-btn",
                                            color="primary",
                                        ),
                                    ),
                                ],
                            )
                        ],
                    ),
                ],
            ),
        ],
    )
