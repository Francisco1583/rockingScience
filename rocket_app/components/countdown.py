from dash import html


def countdown_panel():
    return html.Div(
        className="countdown-panel",
        children=[
            html.Div("Mission Clock", className="countdown-label"),
            html.Div(id="countdown-display", className="countdown-time"),
            html.Div(id="countdown-mode", className="countdown-mode"),
        ],
    )
