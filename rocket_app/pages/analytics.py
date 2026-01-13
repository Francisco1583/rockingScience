from dash import dcc, html
import dash_chart_editor as dce



def upload_box():
    return dcc.Upload(
        id="upload-data",
        className="upload-area",
        multiple=False,
        accept=".csv,.xls,.xlsx",
        children=html.Div(
            className="upload-content",
            children=[
                html.I(className="bi bi-cloud-arrow-up-fill", style={"fontSize": "30px"}),
                html.Span("Drag and drop your CSV or select a file."),
            ],
        ),
    )


def layout():
    return html.Div(
        className="analytics-page",
        children=[
            html.H2("Telemetry Analytics Studio", className="page-title"),
            upload_box(),
            html.Div(id="output-data-upload", className="upload-status"),
            html.Div(
                className="analytics-graph",
                children=[
                    dcc.Graph(
                        id="analytics-graph",
                        config={"displayModeBar": False},
                        figure={},
                    )
                ],
            ),
            html.Div(
                className="chart-editor-shell",
                children=[
                    dce.DashChartEditor(
                        id="chartEditor",
                        dataSources={},
                        style={"height": "650px", "width": "100%"},
                    )
                ],
            ),
        ],
    )
