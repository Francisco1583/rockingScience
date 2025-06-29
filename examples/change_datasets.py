# ────────────────────────────────────────────────────────────────────────────────
#  IMPORTS
# ────────────────────────────────────────────────────────────────────────────────
import base64
import io
import time
import random

import numpy as np
import pandas as pd
import plotly.graph_objects as go

import dash
from dash import dcc, html, Input, Output, State, callback, no_update
import dash_bootstrap_components as dbc
import dash_chart_editor as dce   # ← editor de gráficas interactivo

# ────────────────────────────────────────────────────────────────────────────────
#  DASH APP
# ────────────────────────────────────────────────────────────────────────────────
app = dash.Dash(
    __name__,
    external_scripts=["https://cdn.plot.ly/plotly-2.18.2.min.js"],
    suppress_callback_exceptions=True,
    external_stylesheets=[dbc.themes.DARKLY],
)

server = app.server  # para despliegues (Heroku, Render, etc.)

# ────────────────────────────────────────────────────────────────────────────────
#  DATASETS
# ────────────────────────────────────────────────────────────────────────────────
# - Ejemplo por defecto en el editor Analytics
DATA_CSV = """Día,Temperatura,Presión,Humedad
Lunes,22,1012,60
Martes,24,1010,55
Miércoles,23,1008,58
Jueves,25,1013,53
Viernes,26,1011,50
Sábado,27,1009,48
Domingo,28,1014,46"""
df_example = pd.read_csv(io.StringIO(DATA_CSV))
DEFAULT_DATASET = df_example.to_dict("list")

# - Estado inicial para la simulación
INITIAL_TELEMETRY = dict(
    altitude=0.0,
    velocity=0.0,
    latitude=19.4567,
    longitude=-103.5678,
    distanceFromBase=0.0,
    acceleration=0.0,
)
GRAPH_WINDOW = 50  # puntos a mostrar por gráfica

# ────────────────────────────────────────────────────────────────────────────────
#  LAYOUT GENERAL
# ────────────────────────────────────────────────────────────────────────────────
app.layout = html.Div(
    style={
        "display": "flex",
        "height": "100vh",
        "margin": 0,
        "fontFamily": "Arial, sans-serif",
        "backgroundColor": "#1a1a1a",
        "color": "white",
    },
    children=[
        # ---------- NAVBAR LATERAL ----------
        html.Div(
            style={
                "width": "80px",
                "backgroundColor": "#000",
                "display": "flex",
                "flexDirection": "column",
                "alignItems": "center",
                "paddingTop": "20px",
                "gap": "30px",
            },
            children=[
                html.Img(
                    src="https://raw.githubusercontent.com/plotly/datasets/master/logo-plotly.png",
                    style={"width": "60px", "borderRadius": "50%"},
                ),
                dcc.Link(
                    href="/launch",
                    children=[html.Div("🚀", style={"fontSize": "24px"}), html.Div("Launch", className="nav-label")],
                ),
                dcc.Link(
                    href="/analytics",
                    children=[html.Div("📈", style={"fontSize": "24px"}), html.Div("Analytics", className="nav-label")],
                ),
            ],
        ),
        # ---------- CONTENEDOR DINÁMICO ----------
        html.Div(
            style={"flex": 1, "backgroundColor": "#1a1a1a", "padding": "20px"},
            children=[
                dcc.Location(id="url", refresh=False),
                html.Div(id="page-content"),
                # Stores e intervalos para la simulación
                dcc.Interval(id="interval-update", interval=200, disabled=True),  # 200 ms por paso
                dcc.Store(id="telemetry-store", data=INITIAL_TELEMETRY),
                dcc.Store(
                    id="graph-data-store",
                    data=dict(
                        velocity=[0] * GRAPH_WINDOW,
                        acceleration=[0] * GRAPH_WINDOW,
                        altitude=[0] * GRAPH_WINDOW,
                    ),
                ),
                dcc.Store(id="time-store", data=dict(seconds=10, ms=0)),
            ],
        ),
    ],
)

# ────────────────────────────────────────────────────────────────────────────────
#  UTILIDADES DE UI
# ────────────────────────────────────────────────────────────────────────────────
def metric_card(title, metric_id):
    return html.Div(
        className="text-center",
        children=[
            html.Div(title, className="text-sm text-gray-400"),
            html.Div(id=f"{metric_id}-display", className="text-lg font-bold"),
        ],
    )


def metric_display(label, value_id):
    return html.Div(
        className="text-center",
        children=[html.Div(label, className="text-xs text-gray-400"), html.Div(id=value_id, className="text-lg font-bold")],
    )


def radar_figure(base_x=64, base_y=64, rocket_offset=(0, 0)):
    """Devuelve una figura con cuadrícula de radar y puntos base/cohete."""
    rad_fig = go.Figure()

    # círculos
    for r in [20, 40, 60]:
        rad_fig.add_shape(
            type="circle", x0=base_x - r, y0=base_y - r, x1=base_x + r, y1=base_y + r, line_color="#444"
        )

    # ejes principales
    rad_fig.add_shape(type="line", x0=base_x, y0=base_y - 60, x1=base_x, y1=base_y + 60, line_color="#444")
    rad_fig.add_shape(type="line", x0=base_x - 60, y0=base_y, x1=base_x + 60, y1=base_y, line_color="#444")

    # base
    rad_fig.add_trace(go.Scatter(x=[base_x], y=[base_y], mode="markers", marker=dict(size=10, color="#10b981")))

    # rocket
    rad_fig.add_trace(
        go.Scatter(
            x=[base_x + rocket_offset[0]],
            y=[base_y + rocket_offset[1]],
            mode="markers",
            marker=dict(size=8, color="#ef4444"),
        )
    )

    rad_fig.update_layout(
        margin=dict(l=0, r=0, t=0, b=0),
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        xaxis=dict(visible=False, range=[0, 128]),
        yaxis=dict(visible=False, range=[0, 128]),
    )

    return rad_fig


# ────────────────────────────────────────────────────────────────────────────────
#  PÁGINA: LAUNCH
# ────────────────────────────────────────────────────────────────────────────────
def launch_page():
    return html.Div(
        children=[
            # -------- Barra de métricas superior --------
            html.Div(
                style={
                    "display": "grid",
                    "gridTemplateColumns": "repeat(5, 1fr)",
                    "gap": "1rem",
                    "backgroundColor": "#2d2d2d",
                    "border": "1px solid #444",
                    "padding": "1rem",
                    "borderRadius": "0.5rem",
                    "marginBottom": "1.5rem",
                },
                children=[
                    metric_card("Altitude", "altitude"),
                    metric_card("Velocity", "velocity"),
                    metric_card("Latitude", "latitude"),
                    metric_card("Longitude", "longitude"),
                    metric_card("Distance from base", "distanceFromBase"),
                ],
            ),
            # -------- Contenido principal --------
            html.Div(
                style={"display": "grid", "gridTemplateColumns": "1fr 1fr", "gap": "1.5rem"},
                children=[left_panel(), right_panel()],
            ),
        ]
    )


def left_panel():
    return dbc.Card(
        className="bg-gray-800 border-gray-700",
        children=[
            dbc.CardBody(
                children=[
                    html.H2("Rocket Status", className="text-xl font-bold text-center mb-3"),
                    html.Div(
                        className="flex justify-center items-center mb-4",
                        children=[
                            html.I(className="fas fa-check-circle text-success me-2"),
                            html.Span("Successful connection", className="text-success"),
                        ],
                    ),
                    html.Div(
                        className="text-center mb-4",
                        children=[
                            html.Div("Update Time", className="text-gray-400 mb-1"),
                            html.Div(id="timer-display", className="text-4xl font-bold"),
                        ],
                    ),
                    html.Div(
                        className="flex justify-center gap-3 mb-4",
                        children=[
                            dbc.Button("START", id="start-btn", color="success"),
                            dbc.Button("STOP", id="stop-btn", color="danger"),
                            dbc.Button("RESET", id="reset-btn", color="secondary"),
                        ],
                    ),
                    dcc.Graph(id="radar-display", config={"staticPlot": True}, style={"height": "200px"}),
                    html.Div(
                        className="text-center mt-3",
                        children=[
                            html.Div("Coordinates of rocket", className="text-sm text-gray-400"),
                            html.Div(id="rocket-coords", className="font-bold"),
                            html.Div("Coordinates of base", className="text-sm text-gray-400 mt-2"),
                            html.Div("19.4567° N, -103.5678° W", className="font-bold"),
                            html.Div(id="distance-display", className="text-sm text-gray-300 mt-2"),
                        ],
                    ),
                ]
            )
        ],
    )


def mini_graph(data_type, title):
    return dbc.Card(
        className="bg-gray-800 border-gray-700",
        children=[
            dbc.CardBody(
                children=[
                    html.Div(title, className="text-xs text-gray-400 mb-2"),
                    dcc.Graph(id=f"{data_type}-graph", config={"displayModeBar": False}, style={"height": "200px"}),
                    html.Div(
                        className="flex justify-between mt-2",
                        children=[
                            metric_display("Current", f"{data_type}-current-value"),
                            metric_display("Marked Point", f"{data_type}-marked-value"),
                        ],
                    ),
                ]
            )
        ],
    )


def right_panel():
    return html.Div(
        className="space-y-6",
        children=[
            mini_graph("velocity", "Velocity vs Time"),
            mini_graph("acceleration", "Acceleration vs Time"),
            mini_graph("altitude", "Altitude vs Time"),
        ],
    )


# ────────────────────────────────────────────────────────────────────────────────
#  PÁGINA: ANALYTICS (editor de gráficas)
# ────────────────────────────────────────────────────────────────────────────────
def analytics_page():
    return html.Div(
        style={"maxWidth": "1300px", "margin": "0 auto"},
        children=[
            html.H2("Editor de gráficas meteorológicas", className="mb-4"),
            dcc.Upload(
                id="upload-data",
                children=html.Div(["Arrastra un CSV o ", html.A("selecciona un archivo")], style={"cursor": "pointer"}),
                style={
                    "width": "100%",
                    "height": "60px",
                    "lineHeight": "60px",
                    "borderWidth": "1px",
                    "borderStyle": "dashed",
                    "borderRadius": "5px",
                    "textAlign": "center",
                    "marginBottom": "10px",
                    "backgroundColor": "#2d2d2d",
                },
                multiple=False,
            ),
            html.Div(id="output-data-upload", className="mb-3"),
            dce.DashChartEditor(
                id="chartEditor",
                dataSources=DEFAULT_DATASET,
                style={
                    "border": "1px solid #444",
                    "borderRadius": "10px",
                    "padding": "20px",
                    "backgroundColor": "#060606",
                },
            ),
        ],
    )


# ────────────────────────────────────────────────────────────────────────────────
#  PÁGINAS EXTRA
# ────────────────────────────────────────────────────────────────────────────────
def settings_page():
    return html.Div([html.H2("Configuración ⚙️"), html.P("Ajustes de la aplicación.")])

def welcome_page():
    return html.Div([html.H2("Bienvenida"), html.P("Selecciona una opción del menú lateral.")])

# ────────────────────────────────────────────────────────────────────────────────
#  NAVEGACIÓN POR URL
# ────────────────────────────────────────────────────────────────────────────────
@callback(Output("page-content", "children"), Input("url", "pathname"))
def display_page(pathname):
    if pathname == "/launch":
        return launch_page()
    if pathname == "/analytics":
        return analytics_page()
    if pathname == "/settings":
        return settings_page()
    return welcome_page()

# ────────────────────────────────────────────────────────────────────────────────
#  CALLBACK: SIMULACIÓN DE TELEMETRÍA
# ────────────────────────────────────────────────────────────────────────────────
@callback(
    [Output("telemetry-store", "data"), Output("graph-data-store", "data"), Output("time-store", "data")],
    Input("interval-update", "n_intervals"),
    State("telemetry-store", "data"),
    State("graph-data-store", "data"),
    State("time-store", "data"),
)
def update_telemetry(_, telemetry, graph_data, timer):
    if _ is None:
        return no_update, no_update, no_update

    # ---- tiempo
    timer = timer.copy()
    timer["ms"] += 200
    if timer["ms"] >= 1000:
        timer["seconds"] += 1
        timer["ms"] -= 1000

    # ---- nueva telemetría simulada
    new_telemetry = dict(
        altitude=max(0, telemetry["altitude"] + (random.random() - 0.3) * 8),
        velocity=max(0, telemetry["velocity"] + (random.random() - 0.4) * 12),
        acceleration=(random.random() - 0.5) * 18,
        latitude=telemetry["latitude"] + (random.random() - 0.5) * 0.0001,
        longitude=telemetry["longitude"] + (random.random() - 0.5) * 0.0001,
        distanceFromBase=np.sqrt(telemetry["altitude"] ** 2 + 15**2),
    )

    # ---- historial para gráficas
    for k in ["velocity", "acceleration", "altitude"]:
        graph_data[k] = graph_data[k][1:] + [new_telemetry[k]]

    return new_telemetry, graph_data, timer

# ────────────────────────────────────────────────────────────────────────────────
#  CALLBACK: START / STOP / RESET
# ────────────────────────────────────────────────────────────────────────────────
@callback(
    Output("interval-update", "disabled"),
    Input("start-btn", "n_clicks"),
    Input("stop-btn", "n_clicks"),
    Input("reset-btn", "n_clicks"),
    State("interval-update", "disabled"),
    prevent_initial_call=True,
)
def control_simulation(start, stop, reset, disabled):
    ctx = dash.callback_context.triggered_id
    if ctx == "start-btn":
        return False
    if ctx == "stop-btn":
        return True
    if ctx == "reset-btn":
        return True
    return disabled

@callback(
    [Output("telemetry-store", "data", allow_duplicate=True),
     Output("graph-data-store", "data", allow_duplicate=True),
     Output("time-store", "data", allow_duplicate=True)],
    Input("reset-btn", "n_clicks"),
    prevent_initial_call=True,
)
def reset_simulation(_):
    if _ is None:
        return no_update, no_update, no_update
    return (
        INITIAL_TELEMETRY,
        dict(velocity=[0] * GRAPH_WINDOW, acceleration=[0] * GRAPH_WINDOW, altitude=[0] * GRAPH_WINDOW),
        dict(seconds=10, ms=0),
    )

# ────────────────────────────────────────────────────────────────────────────────
#  CALLBACK: VISUALIZACIÓN EN /launch
# ────────────────────────────────────────────────────────────────────────────────
@callback(
    #  ---- métricas superiores (5) ----
    Output("altitude-display", "children"),
    Output("velocity-display", "children"),
    Output("latitude-display", "children"),
    Output("longitude-display", "children"),
    Output("distanceFromBase-display", "children"),
    #  ---- reloj, coords, distancia ----
    Output("timer-display", "children"),
    Output("rocket-coords", "children"),
    Output("distance-display", "children"),
    #  ---- valores actuales ----
    Output("velocity-current-value", "children"),
    Output("acceleration-current-value", "children"),
    Output("altitude-current-value", "children"),
    #  ---- gráficas (3) ----
    Output("velocity-graph", "figure"),
    Output("acceleration-graph", "figure"),
    Output("altitude-graph", "figure"),
    #  ---- radar ----
    Output("radar-display", "figure"),
    Input("telemetry-store", "data"),
    Input("graph-data-store", "data"),
    Input("time-store", "data"),
)
def update_displays(telemetry, graph_data, timer):
    # ----- métricas -----
    metrics = (
        f"{telemetry['altitude']:.0f} m",
        f"{telemetry['velocity']:.0f} km/h",
        f"{telemetry['latitude']:.4f}° N",
        f"{telemetry['longitude']:.4f}° W",
        f"{telemetry['distanceFromBase']:.0f} m",
    )

    # ----- reloj / coords -----
    clock = f"{timer['seconds']:02d} s  {timer['ms']:03d} ms"
    coords = f"{telemetry['latitude']:.4f}° N, {telemetry['longitude']:.4f}° W"
    distance_label = f"Distance: {telemetry['distanceFromBase']:.0f} m"

    # ----- valores actuales -----
    current_vals = (
        f"{telemetry['velocity']:.0f} km/h",
        f"{telemetry['acceleration']:.2f} m/s²",
        f"{telemetry['altitude']:.0f} m",
    )

    # ----- gráficas de líneas -----
    def line_fig(values):
        fig = go.Figure(go.Scatter(y=values, mode="lines", line=dict(color="#10b981", width=2)))
        fig.update_layout(
            margin=dict(l=0, r=0, t=0, b=0),
            plot_bgcolor="rgba(0,0,0,0)",
            paper_bgcolor="rgba(0,0,0,0)",
            xaxis=dict(visible=False),
            yaxis=dict(visible=False),
        )
        return fig

    velocity_fig = line_fig(graph_data["velocity"])
    acceleration_fig = line_fig(graph_data["acceleration"])
    altitude_fig = line_fig(graph_data["altitude"])

    # ----- radar -----
    # posición del cohete: pequeña órbita estética para animar
    t = time.time()
    rocket_offset = (np.cos(t) * 20, np.sin(t) * 20)
    radar_fig = radar_figure(rocket_offset=rocket_offset)

    return (
        *metrics,
        clock,
        coords,
        distance_label,
        *current_vals,
        velocity_fig,
        acceleration_fig,
        altitude_fig,
        radar_fig,
    )

# ────────────────────────────────────────────────────────────────────────────────
#  CALLBACK: SUBIDA DE CSV EN /analytics
# ────────────────────────────────────────────────────────────────────────────────
@callback(
    [Output("chartEditor", "dataSources"), Output("output-data-upload", "children")],
    Input("upload-data", "contents"),
    State("upload-data", "filename"),
    prevent_initial_call=True,
)
def upload_dataset(contents, filename):
    if not contents:
        return no_update, no_update

    header, content = contents.split(",")
    decoded = base64.b64decode(content)

    try:
        if filename.lower().endswith(".csv"):
            df = pd.read_csv(io.StringIO(decoded.decode("utf-8")))
        elif filename.lower().endswith((".xls", ".xlsx")):
            df = pd.read_excel(io.BytesIO(decoded))
        else:
            raise ValueError("Formato no soportado (usa CSV, XLS o XLSX).")

        return (
            df.to_dict("list"),
            dbc.Alert(f"Cargado: {filename} – {df.shape[0]} filas × {df.shape[1]} columnas", color="success", is_open=True),
        )

    except Exception as e:
        return no_update, dbc.Alert(f"Error: {e}", color="danger", is_open=True)

# ────────────────────────────────────────────────────────────────────────────────
#  MAIN
# ────────────────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    app.run(debug=True, port=1234)
