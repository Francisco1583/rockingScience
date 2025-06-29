import dash_chart_editor as dce
from dash import Dash, html, dcc, callback, Output, Input, State, no_update
import pandas as pd
import io
import base64
import datetime

# Crear app
app = Dash(__name__, external_scripts=["https://cdn.plot.ly/plotly-2.18.2.min.js"])

# Datos iniciales (ejemplo)
data_csv = """Día,Temperatura,Presión,Humedad
Lunes,22,1012,60
Martes,24,1010,55
Miércoles,23,1008,58
Jueves,25,1013,53
Viernes,26,1011,50
Sábado,27,1009,48
Domingo,28,1014,46"""
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
                dcc.Link(
                    href="/launch",
                    children=html.Div([
                        html.Div("🚀", style={"fontSize": "24px"}),
                        html.Div("Launch", style={"fontSize": "10px", "color": "white", "marginTop": "5px"})
                    ])
                ),
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
            # Componente para subir archivos
            dcc.Upload(
                id='upload-data',
                children=html.Div([
                    'Arrastra un CSV o ',
                    html.A('Selecciona un archivo')
                ]),
                style={
                    'width': '100%',
                    'height': '60px',
                    'lineHeight': '60px',
                    'borderWidth': '1px',
                    'borderStyle': 'dashed',
                    'borderRadius': '5px',
                    'textAlign': 'center',
                    'margin': '10px 0',
                    'backgroundColor': '#ffffff'
                },
                multiple=False  # Permitir solo un archivo
            ),
            # Mostrar nombre del archivo cargado
            html.Div(id='output-data-upload'),
            # Editor de gráficos
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

# Callback para procesar el archivo CSV subido
@callback(
    [Output('chartEditor', 'dataSources'),
     Output('output-data-upload', 'children')],
    Input('upload-data', 'contents'),
    State('upload-data', 'filename')
)
def update_output(contents, filename):
    if contents is not None:
        content_type, content_string = contents.split(',')
        decoded = base64.b64decode(content_string)
        try:
            if 'csv' in filename:
                # Leer CSV
                df = pd.read_csv(io.StringIO(decoded.decode('utf-8')))
            elif 'xls' in filename:
                # Leer Excel (opcional)
                df = pd.read_excel(io.BytesIO(decoded))
            else:
                return no_update, html.Div([
                    html.P("Formato no soportado. Sube un archivo CSV o Excel.")
                ], style={'color': 'red'})
            
            # Convertir a diccionario para el editor
            dataset = df.to_dict("list")
            return dataset, html.Div([
                html.P(f"Archivo cargado: {filename}"),
                html.P(f"Filas: {len(df)}, Columnas: {len(df.columns)}")
            ])
        except Exception as e:
            return no_update, html.Div([
                html.P("Error al procesar el archivo:"),
                html.P(str(e))
            ], style={'color': 'red'})
    return no_update, no_update

# Run app
if __name__ == "__main__":
    app.run(debug=True, port=1234)