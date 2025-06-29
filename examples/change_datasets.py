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
import dash_chart_editor as dce

# ---------- CSS que queremos inyectar ----------
SIDEBAR_CSS = """
.sidebar-link{
    color:#fff;
    text-decoration:none;
    display:flex;
    flex-direction:column;
    align-items:center;
    gap:4px;
    font-size:18px;
    font-weight:700;
    padding:6px 0;
    transition:transform .2s ease,background .2s ease;
}
.sidebar-link:hover{
    transform:scale(1.10);
    background:rgba(255,255,255,.15);
    cursor:pointer;
}
.sidebar-link.active{
    background:rgba(255,255,255,.30);
}
"""


# ────────────────────────────────────────────────────────────────────────────────
#  DASH APP (tema claro)
# ────────────────────────────────────────────────────────────────────────────────
app = dash.Dash(
    __name__,
    external_scripts=["https://cdn.plot.ly/plotly-2.18.2.min.js"],
    suppress_callback_exceptions=True,
    external_stylesheets=[dbc.themes.FLATLY],   #  ← tema claro
)
# ------  inyectamos el <style>  ------
app.index_string = f"""
<!DOCTYPE html>
<html>
  <head>
    {{%metas%}}
    <title>Rocket Dashboard</title>
    {{%favicon%}}
    {{%css%}}
    <style>{SIDEBAR_CSS}</style>   <!-- aquí va tu hoja -->
  </head>
  <body>
    {{%app_entry%}}
    <footer>
      {{%config%}}
      {{%scripts%}}
      {{%renderer%}}
    </footer>
  </body>
</html>
"""

server = app.server

# ────────────────────────────────────────────────────────────────────────────────
#  DATASETS
# ────────────────────────────────────────────────────────────────────────────────
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

INITIAL_TELEMETRY = dict(
    altitude=0.0,
    velocity=0.0,
    latitude=19.4567,
    longitude=-103.5678,
    distanceFromBase=0.0,
    acceleration=0.0,
)
GRAPH_WINDOW = 50

# ───  BLOQUE CSS QUE VAMOS A INYECTAR ──────────────────────────────
SIDEBAR_CSS = """
.sidebar-link{
    color:#fff;
    text-decoration:none;
    display:flex;
    flex-direction:column;
    align-items:center;
    gap:4px;
    font-size:18px;
    font-weight:700;
    transition:all .2s ease;
}
.sidebar-link:hover{
    transform:scale(1.1);
    opacity:.9;
}
/* enlace activo (página actual) */
.sidebar-link.active{
    background:rgba(255,255,255,.18);
    border-radius:8px;
}
"""

app.index_string = app.index_string.replace(
    "</style>",
    """
.upload-area:hover{
    background:#e9f2ff;
}
</style>
"""
)


# ────────────────────────────────────────────────────────────────────────────────
#  LAYOUT GENERAL
# ────────────────────────────────────────────────────────────────────────────────
app.layout = html.Div(
    style={
        "display": "flex",
        "height": "100vh",
        "margin": 0,
        "fontFamily": "Arial, sans-serif",
        "backgroundColor": "#fafafa",
        "color": "#000",
    },
    children=[
        # ---------- NAVBAR LATERAL ----------
        html.Div(
            style={
                "width": "130px",
                "backgroundColor": "#2B44A0",
                "color": "#fff",
                "borderRight": "1px solid #ddd",
                "display": "flex",
                "flexDirection": "column",
                "alignItems": "center",
                "paddingTop": "20px",
                "gap": "30px",
            },
           children=[
    html.Img(src="assets/logo.png", style={"width": "80px", "borderRadius": "50%"}),

    # --- Launch ----------------------------------------------------
    dcc.Link(
        id="lnk-launch", 
        href="/launch",
        style={
            "color": "#fff",
            "textDecoration": "none",
            "display": "flex",           # ← contenedor flex
            "flexDirection": "column",   # ← columna
            "alignItems": "center",      # ← centrado
            "gap": "4px",    
            "fontSize": "18px",
            "fontWeight": "bold",

        },
        children=[
            html.Img(src="assets/launch.png", style={"width": "40px"}),
            html.Small("Launch"),
        ],
    ),

    # --- Analytics -------------------------------------------------
    dcc.Link(
        id="lnk-analytics", 
        href="/analytics",
        style={
            "color": "#fff",
            "textDecoration": "none",
            "display": "flex",
            "flexDirection": "column",
            "alignItems": "center",
            "gap": "4px",
            "fontSize": "18px",
            "fontWeight": "bold",
        },
        children=[
            html.Img(src="assets/analytics.png", style={"width": "40px"}),
            html.Small("Analytics"),
        ],
    ),
],
        ),
        # ---------- CONTENEDOR DINÁMICO ----------
        html.Div(
            style={"flex": 1, "padding": "20px"},
            children=[
                dcc.Location(id="url", refresh=False),
                html.Div(id="page-content"),
                dcc.Interval(id="interval-update", interval=200, disabled=True),
                dcc.Store(id="telemetry-store", data=INITIAL_TELEMETRY),
                dcc.Store(
                    id="graph-data-store",
                    data=dict(velocity=[0] * GRAPH_WINDOW, acceleration=[0] * GRAPH_WINDOW, altitude=[0] * GRAPH_WINDOW),
                ),
               dcc.Store(
                    id="time-store",
                    data=dict(seconds=10, ms=0, mode="down"),   # ← nuevo campo «mode»
                ),

            ],
        ),
    ],
)

# ────────────────────────────────────────────────────────────────────────────────
#  COMPONENTES REUTILIZABLES
# ────────────────────────────────────────────────────────────────────────────────
def metric_card(title, metric_id):
    return html.Div(
        className="text-center",
        children=[html.Small(title, style={"color": "#666"}), html.Div(id=f"{metric_id}-display", className="fw-bold")],
    )


def metric_display(label, value_id):
    return html.Div([html.Small(label, style={"color": "#666"}), html.Div(id=value_id, className="fw-bold")])


def radar_figure(base_x=64, base_y=64, rocket_offset=(0, 0)):
    fig = go.Figure()
    for r in [20, 40, 60]:
        fig.add_shape(type="circle", x0=base_x - r, y0=base_y - r, x1=base_x + r, y1=base_y + r, line_color="#bbb")
    fig.add_shape(type="line", x0=base_x, y0=base_y - 60, x1=base_x, y1=base_y + 60, line_color="#bbb")
    fig.add_shape(type="line", x0=base_x - 60, y0=base_y, x1=base_x + 60, y1=base_y, line_color="#bbb")
    fig.add_trace(go.Scatter(x=[base_x], y=[base_y], mode="markers", marker=dict(size=10, color="#0d6efd")))
    fig.add_trace(
        go.Scatter(
            x=[base_x + rocket_offset[0]], y=[base_y + rocket_offset[1]], mode="markers", marker=dict(size=8, color="#dc3545")
        )
    )
    fig.update_layout(
        margin=dict(l=0, r=0, t=0, b=0),
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        xaxis=dict(visible=False, range=[0, 128]),
        yaxis=dict(visible=False, range=[0, 128]),
    )
    return fig

# ────────────────────────────────────────────────────────────────────────────────
#  PÁGINA: LAUNCH
# ────────────────────────────────────────────────────────────────────────────────
def launch_page():
    
    return html.Div(
        children=[
            # --- Métricas superiores ---
            html.H2("Rocket Launch Center", className="mb-4"),
            html.Div(
                style={
                    "display": "grid", "gridTemplateColumns": "repeat(5, 1fr)", "gap": "1rem",
                    "backgroundColor": "#ffffff", "border": "1px solid #ddd", "padding": "1rem",
                    "borderRadius": "8px", "marginBottom": "1.5rem",
                },
                children=[
                    metric_card("Altitude", "altitude"),
                    metric_card("Velocity", "velocity"),
                    metric_card("Latitude", "latitude"),
                    metric_card("Longitude", "longitude"),
                    metric_card("Distance", "distanceFromBase"),
                ],
            ),
            # --- Layout principal ---
            html.Div(
                style={"display": "grid", "gridTemplateColumns": "1fr 1fr", "gap": "1.5rem"},
                children=[left_panel(), right_panel()],
            ),
        ]
    )

def left_panel():
    return dbc.Card(
        style={"border": 0, "boxShadow": "0 0 12px rgba(0,0,0,.08)"},
        children=[
            # ---------- CABECERA ----------
            dbc.CardHeader(
                html.Div(
                    [
                        html.I(className="bi bi-rocket-fill me-2"),   # icono (necesita bootstrap-icons)
                        "Launch Control",
                        html.Span("● Connected", className="badge bg-success ms-auto"),
                    ],
                    className="d-flex align-items-center text-white h5 mb-0",
                ),
                className="bg-primary py-2",
            ),

            # ---------- CUERPO ----------
            dbc.CardBody(
                [
                    # Reloj / temporizador
                    html.Div(
                        [
                            html.Small("MISSION CLOCK", className="text-muted"),
                            html.Div(
                                id="timer-display",
                                className="display-4 fw-bold text-primary",
                                style={"fontFamily": "monospace"},
                            ),
                        ],
                        className="text-center mb-4",
                    ),

                    # Botones de control
                    html.Div(
                        [
                            dbc.Button("Start", id="start-btn", color="success", className="px-4"),
                            dbc.Button("Stop", id="stop-btn", color="danger", className="px-4 ms-2"),
                            dbc.Button("Reset", id="reset-btn", color="secondary", className="px-4 ms-2"),
                        ],
                        className="d-flex justify-content-center mb-4",
                    ),

                    # Radar + coordenadas (en fila)
                    dbc.Row(
                        [
                            dbc.Col(
                                dcc.Graph(
                                    id="radar-display",
                                    config={"staticPlot": True},
                                    style={"height": "200px", "margin": 0},
                                ),
                                width=6,
                            ),
                            dbc.Col(
                                [
                                    html.Div(
                                        [
                                            html.Small("Rocket", className="text-muted"),
                                            html.Div(id="rocket-coords", className="fw-bold mb-2"),
                                        ]
                                    ),
                                    html.Div(
                                        [
                                            html.Small("Base", className="text-muted"),
                                            html.Div("19.4567° N, -103.5678° W", className="fw-bold mb-2"),
                                        ]
                                    ),
                                    html.Div(id="distance-display", className="text-muted"),
                                ],
                                width=6,
                                className="d-flex flex-column justify-content-center",
                            ),
                        ],
                        className="g-3",  # espacio entre columnas
                    ),
                ]
            ),
        ],
    )

def mini_graph(data_type: str, title: str) -> dbc.Card:
    """Pequeña tarjeta con sparkline y métricas."""
    color_map = {          # paleta por tipo (opcional)
        "velocity":  "#0d6efd",
        "acceleration": "#6610f2",
        "altitude": "#198754",
    }
    line_color = color_map.get(data_type, "#0d6efd")

    return dbc.Card(
        style={"border": 0, "boxShadow": "0 0 10px rgba(0,0,0,.06)"},
        children=[
            # ---------- encabezado ----------
            dbc.CardHeader(
                html.Div(
                    [
                        html.I(className="bi bi-graph-up-arrow me-2"),  # necesita bootstrap-icons
                        title,
                    ],
                    className="d-flex align-items-center fw-semibold",
                ),
                className="bg-light py-2",
            ),

            # ---------- cuerpo ----------
            dbc.CardBody(
                style={"padding": "1rem 1.25rem"},
                children=[
                    # Sparkline centrado
                    dcc.Graph(
                        id=f"{data_type}-graph",
                        config={"displayModeBar": False},
                        style={"height": "80px"},   # un poco más alto
                    ),

                    # Grid 2×2  (label / value) -----------------------
                    html.Div(
                        style={
                            "display": "grid",
                            "gridTemplateColumns": "1fr 1fr",
                            "gap": "0.5rem 1rem",
                            "marginTop": "8px",
                        },
                        children=[
                            html.Small("Current", className="text-muted"),
                            html.Small("Marked",  className="text-muted text-end"),

                            html.Div(id=f"{data_type}-current-value",
                                     className="fw-bold", style={"color": line_color}),
                            html.Div(id=f"{data_type}-marked-value",
                                     className="fw-bold text-end"),
                        ],
                    ),
                ],
            ),
        ],
    )


def right_panel():
    return html.Div(children=[mini_graph("velocity", "Velocity"), mini_graph("acceleration", "Acceleration")])

# ────────────────────────────────────────────────────────────────────────────────
#  PÁGINA: ANALYTICS
# ────────────────────────────────────────────────────────────────────────────────
def analytics_page():
    return html.Div(
        style={"maxWidth": "1300px", "margin": "0 auto"},
        children=[
            html.H2("Telemetry Analytics Studio", className="mb-4"),
            # ---------- selector de archivo bonito ----------
dcc.Upload(
    id="upload-data",
    children=html.Div(
        [
            html.I(className="bi bi-cloud-arrow-up-fill", style={"fontSize": "34px"}),
            html.Span(" Drag & drop your CSV or select a file.", style={"fontWeight": 600}),
        ],
        style={
            "display": "flex",
            "flexDirection": "column",
            "justifyContent": "center",
            "alignItems": "center",
            "gap": "6px",                 # espacio entre icono y texto
            "height": "100%",             # ocupar todo el contenedor
        },
    ),
    style={
        "width": "100%",
        "height": "70px",
        "border": "2px dashed #0d6efd",
        "borderRadius": "8px",
        "backgroundColor": "#f8faff",
        "color": "#0d6efd",
        "fontSize": "17px",
        "fontWeight": "500",
        "cursor": "pointer",
        "transition": "background .2s ease, transform .2s ease",
        "marginBottom": "16px",
    },
    className="upload-area",   # para el hover
    multiple=False,
)

,
            html.Div(id="output-data-upload", className="mb-3"),
            dce.DashChartEditor(
                id="chartEditor",
                dataSources=DEFAULT_DATASET,
                style={"border": "1px solid #ddd", "borderRadius": "8px", "padding": "20px", "backgroundColor": "#fff"},
            ),
        ],
    )

# ────────────────────────────────────────────────────────────────────────────────
#  PÁGINAS EXTRAS
# ────────────────────────────────────────────────────────────────────────────────
def welcome_page():
    return html.Div([html.H2("Welcome"), html.P("Elige una opción en la barra lateral.")])

# ────────────────────────────────────────────────────────────────────────────────
#  NAVEGACIÓN
# ────────────────────────────────────────────────────────────────────────────────
@callback(Output("page-content", "children"), Input("url", "pathname"))

def display_page(path):
    if path == "/launch":
        return launch_page()
    if path == "/analytics":
        return analytics_page()
    return welcome_page()

@callback(
    Output("lnk-launch",    "className"),
    Output("lnk-analytics", "className"),
    Input("url", "pathname"),
)
def highlight_active(path):
    base = "sidebar-link"
    return (
        f"{base} active" if path == "/launch"    else base,
        f"{base} active" if path == "/analytics" else base,
    )

# ────────────────────────────────────────────────────────────────────────────────
#  SIMULACIÓN TELEMETRÍA (idéntico a antes)
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
    timer = timer.copy()

    # --- tiempo ---
    if timer["mode"] == "down":
        # restamos 200 ms
        total_ms = timer["seconds"] * 1000 + timer["ms"] - 200
        if total_ms <= 0:
            # llegamos a cero: saltar a cuenta ascendente
            timer.update(seconds=0, ms=0, mode="up")
        else:
            timer.update(seconds=total_ms // 1000,
                        ms=total_ms % 1000)
    else:  # mode == "up"
        timer["ms"] += 200
        if timer["ms"] >= 1000:
            timer["seconds"] += 1
            timer["ms"] -= 1000

    new_telemetry = dict(
        altitude=max(0, telemetry["altitude"] + (random.random() - 0.3) * 8),
        velocity=max(0, telemetry["velocity"] + (random.random() - 0.4) * 12),
        acceleration=(random.random() - 0.5) * 18,
        latitude=telemetry["latitude"] + (random.random() - 0.5) * 0.0001,
        longitude=telemetry["longitude"] + (random.random() - 0.5) * 0.0001,
        distanceFromBase=np.sqrt(telemetry["altitude"] ** 2 + 15**2),
    )
    for k in ["velocity", "acceleration", "altitude"]:
        graph_data[k] = graph_data[k][1:] + [new_telemetry[k]]
    return new_telemetry, graph_data, timer

# ---- START / STOP / RESET ----
@callback(Output("interval-update", "disabled"),
          Input("start-btn", "n_clicks"), Input("stop-btn", "n_clicks"), Input("reset-btn", "n_clicks"),
          State("interval-update", "disabled"), prevent_initial_call=True)
def toggle_interval(start, stop, reset, disabled):
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
    Input("reset-btn", "n_clicks"), prevent_initial_call=True)
def reset_data(_):
    if _ is None:
        return no_update, no_update, no_update
    return INITIAL_TELEMETRY, \
    dict(velocity=[0]*GRAPH_WINDOW,
                acceleration=[0]*GRAPH_WINDOW,
                altitude=[0]*GRAPH_WINDOW), \
        dict(seconds=10, ms=0, mode="down")      # ← modo reiniciado

# ---- ACTUALIZACIÓN VISUAL ----
@callback(
    # --- métricas superiores ---
    Output("altitude-display", "children"),
    Output("velocity-display", "children"),
    Output("latitude-display", "children"),
    Output("longitude-display", "children"),
    Output("distanceFromBase-display", "children"),
    # --- reloj / coords ---
    Output("timer-display", "children"),
    Output("rocket-coords", "children"),
    Output("distance-display", "children"),
    # --- valores actuales  (YA SIN altitude-current-value) ---
    Output("velocity-current-value", "children"),
    Output("acceleration-current-value", "children"),
    # --- figuras (YA SIN altitude-graph) ---
    Output("velocity-graph", "figure"),
    Output("acceleration-graph", "figure"),
    Output("radar-display", "figure"),
    Input("telemetry-store", "data"),
    Input("graph-data-store", "data"),
    Input("time-store", "data"),
)

def update_display(tlm, gdata, tmr):
    metrics = (f"{tlm['altitude']:.0f} m", f"{tlm['velocity']:.0f} km/h",
               f"{tlm['latitude']:.4f}° N", f"{tlm['longitude']:.4f}° W",
               f"{tlm['distanceFromBase']:.0f} m")
    clock = f"{tmr['seconds']:02d} s {tmr['ms']:03d} ms"
    coords = f"{tlm['latitude']:.4f}° N, {tlm['longitude']:.4f}° W"
    dist_lbl = f"Distance: {tlm['distanceFromBase']:.0f} m"
    currents = (f"{tlm['velocity']:.0f} km/h", f"{tlm['acceleration']:.2f} m/s²")

    def line(values):
        fig = go.Figure(go.Scatter(y=values, mode="lines", line=dict(color="#0d6efd", width=2)))
        fig.update_layout(margin=dict(l=0, r=0, t=0, b=0), xaxis=dict(visible=False), yaxis=dict(visible=False),
                          plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)")
        return fig
    velocity_fig, acc_fig = line(gdata["velocity"]), line(gdata["acceleration"])
    t = time.time()
    radar_fig = radar_figure(rocket_offset=(np.cos(t)*20, np.sin(t)*20))
    return (*metrics, clock, coords, dist_lbl, *currents, velocity_fig, acc_fig,  radar_fig)

# ---- SUBIDA CSV ----
@callback([Output("chartEditor", "dataSources"), Output("output-data-upload", "children")],
          Input("upload-data", "contents"), State("upload-data", "filename"), prevent_initial_call=True)
def upload_csv(contents, filename):
    if not contents: return no_update, no_update
    _, data = contents.split(","); decoded = base64.b64decode(data)
    try:
        if filename.lower().endswith(".csv"):
            df = pd.read_csv(io.StringIO(decoded.decode("utf-8")))
        elif filename.lower().endswith((".xls", ".xlsx")):
            df = pd.read_excel(io.BytesIO(decoded))
        else:
            raise ValueError("Formato no soportado.")
        return df.to_dict("list"), dbc.Alert(f"{filename} cargado ({df.shape[0]} filas × {df.shape[1]} columnas)",
                                             color="success", is_open=True)
    except Exception as e:
        return no_update, dbc.Alert(f"Error: {e}", color="danger", is_open=True)

# ────────────────────────────────────────────────────────────────────────────────
#  MAIN
# ────────────────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    app.run(debug=True, port=1234)
