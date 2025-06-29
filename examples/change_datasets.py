import dash_chart_editor as dce
from dash import Dash, html, dcc, callback, Output, Input
import pandas as pd
import io

# Crear app
app = Dash(__name__, external_scripts=["https://cdn.plot.ly/plotly-2.18.2.min.js"])

# Leer datos CSV
data_csv = """
Día,Temperatura,Presión,Humedad
Lunes,22,1012,60
Martes,24,1010,55
Miércoles,23,1008,58
Jueves,25,1013,53
Viernes,26,1011,50
Sábado,27,1009,48
Domingo,28,1014,46
"""
df = pd.read_csv(io.StringIO(data_csv))
dataset = df.to_dict("list")

# Layout
app.layout = html.Div(
    style={
        "display": "flex",
        "height": "100vh",
        "margin": 0,
        "fontFamily": "Arial, sans-serif",
        "backgroundColor": "#000000"
    },
    children=[
        # Navbar lateral
        html.Div(
            style={
                "width": "80px",
                "backgroundColor": "#000000",
                "display": "flex",
                "flexDirection": "column",
                "alignItems": "center",
                "paddingTop": "20px",
                "gap": "30px"
            },
            children=[
                html.Img(src="/assets/logo.png", style={"width": "60px", "borderRadius": "50%"}),

                # Botón Launch
                dcc.Link(
                    href="/launch",
                    children=html.Div([
                        html.Div("🚀", style={"fontSize": "24px"}),
                        html.Div("Launch", style={"fontSize": "10px", "color": "white", "marginTop": "5px"})
                    ])
                ),

                # Botón Analytics (seleccionado)
                dcc.Link(
                    href="/analytics",
                    children=html.Div(
                        style={
                            "backgroundColor": "#1d263b",
                            "width": "100%",
                            "display": "flex",
                            "flexDirection": "column",
                            "alignItems": "center",
                            "padding": "10px 0"
                        },
                        children=[
                            html.Div("📈", style={"fontSize": "24px"}),
                            html.Div("Analytics", style={"fontSize": "10px", "color": "#cccccc", "marginTop": "5px"})
                        ]
                    )
                ),

                # Botón Settings
                dcc.Link(
                    href="/settings",
                    children=html.Div([
                        html.Div("⚙️", style={"fontSize": "24px"}),
                        html.Div("Settings", style={"fontSize": "10px", "color": "white", "marginTop": "5px"})
                    ])
                ),
            ]
        ),

        # Contenedor de página dinámica
        html.Div(
            style={"flex": 1, "backgroundColor": "#f7f9fc"},
            children=[
                dcc.Location(id="url", refresh=False),
                html.Div(id="page-content", style={"padding": "30px"})
            ]
        )
    ]
)

# Callback de navegación por URL
@callback(Output("page-content", "children"), Input("url", "pathname"))
def render_page(pathname):
    if pathname == "/launch":
        return html.Div([
            html.H2("Página de Lanzamiento 🚀", style={"color": "#124158"}),
            html.P("Aquí puedes comenzar a desarrollar tu vista de lanzamiento.")
        ])
    elif pathname == "/analytics":
        return html.Div([
            html.H2("Editor de gráficas meteorológicas", style={"color": "#124158"}),
            dce.DashChartEditor(
                id="chartEditor",
                dataSources=dataset,
                style={
                    "border": "1px solid #ccc",
                    "borderRadius": "10px",
                    "padding": "20px",
                    "marginTop": "20px",
                    "backgroundColor": "white"
                }
            )
        ])
    elif pathname == "/settings":
        return html.Div([
            html.H2("Configuración ⚙️", style={"color": "#124158"}),
            html.P("Aquí puedes poner los ajustes de tu aplicación.")
        ])
    else:
        return html.Div([
            html.H2("Bienvenida", style={"color": "#124158"}),
            html.P("Selecciona una opción del menú lateral.")
        ])

# Run app
if __name__ == "__main__":
    app.run(debug=True, port=1234)
