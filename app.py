import dash
from dash.dependencies import Input, Output, State
import dash_table as dt
import dash_bootstrap_components as dbc
import dash_core_components as dcc
import dash_html_components as html
import pandas as pd
import base64


SUBMIT_BUTTON = [
    dbc.CardHeader(
        html.Div([
            dbc.Card([
                dcc.Upload(id='upload',
                    children=html.Div([
                        'Drag and Drop or ',html.A('Select Files')
                    ]),
                    style={
                        'textAlign': 'center',
                        'borderStyle': 'dashed',
                        'width': '100%',

                        'float':'center',
                        
                        'height': '40px',
                        'lineHeight': '40px',
                        'borderWidth': '1px',
                        
                        'borderRadius': '5px',
                        
                        'margin': '10px'
                    },
                    # Do not allow multiple files to be uploaded
                    multiple=False,
                ),

            ]),

            dbc.CardHeader(html.H5("Columns to be matched")),
            dbc.CardBody([
                dbc.Row([
                    dbc.Col([
                        dt.DataTable(
                            id='original_column',
                            style_table={'height': '300px', 'overflowY': 'auto'},
                            style_header={'backgroundColor': 'rgb(230, 230, 230)', 'fontWeight': 'bold'},
                            fixed_rows={'headers': True},
                            style_cell={'textAlign': 'center'},
                            style_data_conditional=[{'if': {'row_index': 'odd'}, 'backgroundColor': 'rgb(248, 248, 248)'}],
                            ),
                        ],
                        ),
                    dbc.Col([
                        dt.DataTable(
                            id='matching_column',

                            style_table={'height': '300px', 'overflowY': 'auto', 'width': '100%','minWidth': '100%',},

                            style_header={'backgroundColor': 'rgb(230, 230, 230)', 'fontWeight': 'bold'},
                            fixed_rows={'headers': True},
                            style_cell={'textAlign': 'center'},
                            style_data_conditional=[{'if': {'row_index': 'odd'}, 'backgroundColor': 'rgb(248, 248, 248)'}],
                            ),
                        ],),
                    ],),


                dbc.Row(id='row-excluded-words'),
                dbc.Row([
                    dbc.Col(dbc.Input(id="input-domain-specific-words", type="text")),
                    dbc.Col(dbc.Button("Add word", id = 'add-button', color="success", className="mr-1"),width=2),
                    dbc.Col(dbc.Button("Delete word", id = 'delete-button', color="danger", className="mr-1"),width=2),
                    dbc.Col(dbc.Button("Reset word", id = 'reset-button', color="secondary", className="mr-1"),width=2),
                    ]),
                ]),
            ],
            className="container")
        ),
]


WORDCLOUD_PLOTS = [
    dbc.CardHeader(html.H5("Common words used for matching")),
    dbc.Alert(
        "Not enough data to render these plots, please adjust the filters",
        id="no-data-alert",
        color="warning",
        style={"display": "none"},
    ),
    dbc.CardBody(
        [
            dbc.Row(
                [
                    dbc.Col(
                        dcc.Loading(
                            id="loading-frequencies",
                            children=[dcc.Graph(id="frequency_figure")],
                            type="default",
                        )
                    ),
                    dbc.Col(
                        [
                            dcc.Tabs(
                                id="tabs",
                                children=[
                                    dcc.Tab(
                                        label="Treemap",
                                        children=[
                                            dcc.Loading(
                                                id="loading-treemap",
                                                children=[dcc.Graph(id="bank-treemap")],
                                                type="default",
                                            )
                                        ],
                                    ),
                                    dcc.Tab(
                                        label="Wordcloud",
                                        children=[
                                            dcc.Loading(
                                                id="loading-wordcloud",
                                                children=[
                                                    dcc.Graph(id="bank-wordcloud")
                                                ],
                                                type="default",
                                            )
                                        ],
                                    ),
                                ],
                            )
                        ],
                        md=8,
                    ),
                ]
            )
        ]
    ),
]

HEADER = dbc.Container(
    [
        dbc.Card(SUBMIT_BUTTON),
    ],
    className="mt-12",
)


BODY = dbc.Container(
    [
        dbc.Card(WORDCLOUD_PLOTS),
    ],
    className="mt-12",
)

app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])
server = app.server  # for Heroku deployment

app.layout = html.Div(children=[HEADER,BODY])



"""
#  Callbacks
"""

@app.callback(
    [Output('original_column', 'columns'),
     Output('original_column', 'data'),
     Output('matching_column', 'columns'),
     Output('matching_column', 'data'),],

    [Input('upload', 'contents')],
    [State('upload', 'filename'),
     State('upload', 'last_modified')],
    )


def update_figure(content, name, date):

    if not content:
        return [],[], [], []

    content_type, content_string = content.split(',')
    decoded = base64.b64decode(content_string)

    df = pd.read_excel(decoded,sheet_name=None)

    sheets = list(df.keys())

    orig_df = df[sheets[0]].iloc[:,0:1]
    match_df = df[sheets[1]].iloc[:,0:1]

    return [{"name": i, "id": i} for i in orig_df.columns], orig_df.to_dict("rows"), [{"name": i, "id": i} for i in match_df.columns], match_df.to_dict("rows")



wordList = []

@app.callback(
    [Output('row-excluded-words','children')],
    [Input('input-domain-specific-words','value'),
     Input('add-button','n_clicks'),
     Input('delete-button','n_clicks')],
     )

def updateWordList(word,n_clicks_add,n_clicks_delete):

    ctx = dash.callback_context
    if not ctx.triggered:
        raise dash.exceptions.PreventUpdate
    else:
        button_id = ctx.triggered[0]['prop_id'].split('.')[0]

    if button_id not in ['add-button','delete-button']:
        raise dash.exceptions.PreventUpdate

    elif button_id == 'delete-button':
        if word in wordList:
            wordList.remove(word)
            
    elif button_id == 'add-button':
        if word not in wordList:
            wordList.append(word)

    childWordList = []
    for word in wordList:
        childWordList = childWordList + [dbc.ListGroupItem(word)]

    return [dbc.ListGroup(childWordList,horizontal=True, className="mb-2")]

@app.callback(Output('input-domain-specific-words','value'),
             [Input('reset-button','n_clicks')])
def update(reset):
    return ''

if __name__ == "__main__":
    app.run_server(debug=False)
