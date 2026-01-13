from dash import Input, Output, html

from rocket_app.pages import analytics_layout, launch_layout, predictive_layout

ROUTE_MAP = {
    "/launch": launch_layout,
    "/analytics": analytics_layout,
    "/predictive": predictive_layout,
}


def resolve_page(pathname):
    if pathname in (None, "", "/"):
        return launch_layout()
    layout_fn = ROUTE_MAP.get(pathname)
    if layout_fn:
        return layout_fn()
    return html.Div([html.H2("Page not found")])


def register_routes(app):
    @app.callback(Output("page-content", "children"), Input("url", "pathname"))
    def route_page(pathname):
        return resolve_page(pathname)

    @app.callback(
        Output("lnk-launch", "className"),
        Output("lnk-analytics", "className"),
        Output("lnk-predictive", "className"),
        Input("url", "pathname"),
    )
    def highlight_nav(pathname):
        base = "sidebar-link"
        launch_active = pathname in (None, "", "/", "/launch")
        return (
            f"{base} active" if launch_active else base,
            f"{base} active" if pathname == "/analytics" else base,
            f"{base} active" if pathname == "/predictive" else base,
        )
