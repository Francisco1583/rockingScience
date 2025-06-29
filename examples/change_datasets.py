import dash_chart_editor as dce
from dash import Dash, html, dcc, callback, Output, Input
import pandas as pd
import io

app = Dash(__name__, external_scripts=["https://cdn.plot.ly/plotly-2.18.2.min.js"])

# CSV de ejemplo
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

# Función para generar ítem del menú
def menu_item(icon, label, path, current_path):
    is_active = path == current_path
    base_style = {
        "width": "100%",
        "display": "flex",
        "flexDirection": "column",
        "alignItems": "center",
        "padding": "10px 0",
        "cursor": "pointer",
        "transition": "0.3s"
    }
    if is_active:
        base_style["backgroundColor"] = "#1d263b"
    return dcc.Link(
        href=path,
        children=html.Div(
            style=base_style,
            children=[
                html.Div(icon, style={"fontSize": "24px"}),
                html.Div(label, style={"fontSize": "10px", "color": "#ccc", "marginTop": "5px"})
            ],
            className="menu-item"
        )
    )

# Layout principal
app.layout = html.Div(
    style={"display": "flex", "height": "100vh", "margin": 0, "fontFamily": "Arial, sans-serif"},
    children=[
        # Contenedor de navegación + contenido
        dcc.Location(id="url", refresh=False),
        html.Div(id="main-layout")
    ]
)

# Render layout completo según URL
@callback(Output("main-layout", "children"), Input("url", "pathname"))
def display_layout(pathname):
    sidebar = html.Div(
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
            menu_item("🚀", "Launch", "/launch", pathname),
            menu_item("📈", "Analytics", "/analytics", pathname),
            menu_item("⚙️", "Settings", "/settings", pathname)
        ]
    )

    if pathname == "/launch":
        content = html.Div([
            html.H2("Página de Lanzamiento 🚀", style={"color": "#124158"}),
            html.P("Aquí puedes comenzar a desarrollar tu vista de lanzamiento.")
        ])
    elif pathname == "/analytics":
        content = html.Div([
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
        content = html.Div([
            html.H2("Configuración ⚙️", style={"color": "#124158"}),
            html.P("Aquí puedes poner los ajustes de tu aplicación.")
        ])
    else:
        content = html.Div([
            html.H2("Bienvenida", style={"color": "#124158"}),
            html.P("Selecciona una opción del menú lateral.")
        ])

    return html.Div(
        style={"display": "flex", "width": "100%"},
        children=[
            sidebar,
            html.Div(
                style={"flex": 1, "backgroundColor": "#f7f9fc", "padding": "30px"},
                children=content
            )
        ]
    )

# CSS personalizado (lo puedes guardar en `assets/style.css`)
app.index_string = '''
<!DOCTYPE html>
<html>
    <head>
        {%metas%}
        <title>Dash App</title>
        {%favicon%}
        {%css%}
        <style>
            .menu-item:hover {
                background-color: #2a3f5f !important;
            }
        </style>
    </head>
    <body>
        {%app_entry%}
        <footer>
            {%config%}
            {%scripts%}
            {%renderer%}
        </footer>
    </body>
</html>
'''

# Ejecutar
if __name__ == "__main__":
    app.run(debug=True, port=1234)
