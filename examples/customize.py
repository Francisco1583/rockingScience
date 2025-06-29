import dash_chart_editor as dce
from dash import Dash, html
import plotly.express as px

app = Dash(
    __name__,
    external_scripts=["https://cdn.plot.ly/plotly-2.35.2.min.js"],
    suppress_callback_exceptions=True
)

df = px.data.gapminder()

# Estilos en modo oscuro
DARK_STYLE = {
    "backgroundColor": "#1e1e24",
    "color": "#f0f0f0",
    "padding": "2rem",
    "fontFamily": "Segoe UI, sans-serif",
    "minHeight": "100vh",
}

CONTAINER_STYLE = {
    "border": "1px solid #333",
    "borderRadius": "12px",
    "padding": "1.5rem",
    "backgroundColor": "#2b2d33",
    "boxShadow": "0 4px 12px rgba(0, 0, 0, 0.3)",
}

app.layout = html.Div(
    style=DARK_STYLE,
    children=[
        html.H2(
            "🌍 Dash Chart Editor - Gapminder Dataset",
            style={"textAlign": "center", "marginBottom": "1.5rem"}
        ),
        html.Div(
            style=CONTAINER_STYLE,
            children=[
                dce.DashChartEditor(
                    dataSources=df.to_dict("list"),
                    logoSrc="https://busybee.alliancebee.com/static/logo.png",
                    config={
                        "editable": True,
                        "modeBarButtonsToAdd": [
                            "drawline",
                            "drawopenpath",
                            "drawclosedpath",
                            "drawcircle",
                            "drawrect",
                            "eraseshape",
                        ],
                    },
                ),
            ],
        ),
        html.Footer(
            "📊 Interfaz construida con Plotly + Dash Chart Editor",
            style={"textAlign": "center", "marginTop": "2rem", "fontSize": "0.9rem", "opacity": 0.7}
        ),
    ],
)

if __name__ == "__main__":
    app.run(debug=True)
