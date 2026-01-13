from dash import dcc, html


def nav_link(link_id, href, label, icon):
    return dcc.Link(
        id=link_id,
        href=href,
        className="sidebar-link",
        children=[
            html.Img(src=f"/assets/{icon}", alt=label),
            html.Span(label),
        ],
    )


def sidebar():
    return html.Div(
        className="sidebar",
        children=[
            html.Img(src="/assets/logo.png", className="sidebar-logo", alt="Rocket Science"),
            nav_link("lnk-launch", "/launch", "Launch", "launch.png"),
            nav_link("lnk-analytics", "/analytics", "Analytics", "analytics.png"),
            nav_link("lnk-predictive", "/predictive", "Predictive", "settings.png"),
        ],
    )
