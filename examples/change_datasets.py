import dash_chart_editor as dce
from dash import Dash, html
import pandas as pd
import io

app = Dash(__name__, external_scripts=["https://cdn.plot.ly/plotly-2.18.2.min.js"])

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

app.layout = html.Div(
    [
        html.H4("Dash Chart Editor Demo con datos personalizados"),
        dce.DashChartEditor(
            dataSources=dataset, id="chartEditor"
        ),
    ]
)

if __name__ == "__main__":
    app.run(debug=True, port=1234)

