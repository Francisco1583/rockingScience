from dash import dcc, html


def upload_box(upload_id, label, accept=".csv,.xls,.xlsx"):
    return dcc.Upload(
        id=upload_id,
        className="upload-area",
        multiple=False,
        accept=accept,
        children=html.Div(
            className="upload-content",
            children=[
                html.I(className="bi bi-cloud-arrow-up-fill", style={"fontSize": "30px"}),
                html.Span(label),
            ],
        ),
    )


def upload_status(status_id):
    return html.Div(id=status_id, className="upload-status")
