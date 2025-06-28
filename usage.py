from dash import Dash, dcc, html, Input, Output, State, MATCH, ALL, ctx, no_update, Patch
import plotly.express as px
import plotly.graph_objs as go
import dash_bootstrap_components as dbc
import dash_chart_editor as dce

df = px.data.iris()

app = Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])

app.layout = dbc.Container(
    [
        dcc.Store(id='oldSum', data=0),
        dbc.Modal([
            dbc.ModalTitle('Customizing Charts'),
            dbc.ModalBody([dcc.Input(id="chartId"),dce.DashChartEditor(dataSources=df.to_dict('list'), id='editor',
                                                                       style={'height': '60vh'})]),
            dbc.ModalFooter([dbc.Button('Save Chart', id='saveEditor'),
                            dbc.Button('Save & Close', id='saveCloseEditor', color='secondary')])
        ], id='editorMenu', size='xl'),
        dbc.Row(
            dbc.Col(
                [
                    html.H3("Pattern Matching Callbacks Demo"),
                    dbc.Button(
                        "Add Chart", id="pattern-match-add-chart", n_clicks=0
                    ),
                    html.Div(id="pattern-match-container", children=[], className="mt-4"),
                ]
            )
        ),
     ],
    fluid=True,
)

def make_card(n_clicks):
    return dbc.Card(
        [
            dbc.CardHeader(
                [
                    f"Figure {n_clicks + 1} ",
                    dbc.Button(
                        "Edit",
                        id={"type": "dynamic-edit", "index": n_clicks},
                        n_clicks=0,
                        color="info",
                    ),
                    dbc.Button(
                        "X",
                        id={"type": "dynamic-delete", "index": n_clicks},
                        n_clicks=0,
                        color="secondary",
                    ),
                ],
                className="text-end",
            ),
            dcc.Graph(
                id={"type": "dynamic-output", "index": n_clicks},
                style={"height": 400},
                figure=go.Figure()
            ),
        ],
        style={
            "width": 400,
            "display": "inline-block",
        },
        className="m-1",
        id={"type": "dynamic-card", "index": n_clicks},
    )

@app.callback(
    Output("pattern-match-container", "children"),
    Input("pattern-match-add-chart", "n_clicks"),
)
def add_card(n_clicks):
    patched_children = Patch()
    new_card = make_card(n_clicks)
    patched_children.append(new_card)
    return patched_children

@app.callback(
    Output("pattern-match-container", "children", allow_duplicate=True),
    Input({"type": "dynamic-delete", "index": ALL}, "n_clicks"),
    State({"type": "dynamic-card", "index": ALL}, 'id'),
    prevent_initial_call=True,
)
def remove_card(_, ids):
    rem = Patch()
    if ctx.triggered[0]['value'] > 0:
        for i in range(len(ids)):
            if ids[i]['index'] == ctx.triggered_id['index']:
                del rem[i]
                return rem
    return no_update

@app.callback(
    Output("editorMenu", "is_open"), Output("editor", "loadFigure"), Output('chartId', 'value'),
    Output('oldSum', 'data'),
    Input({"type": "dynamic-edit", "index": ALL}, "n_clicks"),
    State({"type": "dynamic-output", "index": ALL}, "figure"),
    State('oldSum', 'data'),
    State({"type": "dynamic-card", "index": ALL}, 'id'),
    prevent_initial_call=True,
)
def remove_card(edit, figs, oldSum, ids):
    if sum(edit) > 0 and sum(edit) != oldSum:
        oldSum = sum(edit)
        if ctx.triggered[0]['value'] > 0:
            for i in range(len(ids)):
                if ids[i]['index'] == ctx.triggered_id['index']:
                    if figs[i]['data']:
                        return True, figs[i], ctx.triggered_id['index'], oldSum
                    return True, {'data': [], 'layout': {}}, ctx.triggered_id['index'], oldSum
    return no_update, no_update, no_update, oldSum

@app.callback(
    Output('editor', 'saveState'),
    Input('saveEditor', 'n_clicks'),
    Input('saveCloseEditor', 'n_clicks'),
)
def saveChart(n, n1):
    if n or n1:
        return True

@app.callback(
    Output("editorMenu", "is_open", allow_duplicate=True),
    Input('saveCloseEditor', 'n_clicks'),
    prevent_initial_call=True
)
def saveChart(n):
    if n:
        return False
    return no_update

@app.callback(
    Output("pattern-match-container", "children", allow_duplicate=True),
    Input('editor', 'figure'), State('chartId', 'value'),
    State({"type": "dynamic-card", "index": ALL}, 'id'),
    prevent_initial_call=True
)
def saveToFig(f, v, ids):
    if f:
        figs = Patch()
        for i in range(len(ids)):
            if ids[i]['index'] == v:
                figs[i]['props']['children'][1]['props']['figure'] = dce.chartToPython(f, df)
                return figs
    return no_update

if __name__ == "__main__":
    app.run(debug=True)
