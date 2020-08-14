import dash
from dash.dependencies import Input, Output, State
import dash_table as dt
import dash_bootstrap_components as dbc
import dash_core_components as dcc
import dash_html_components as html
import pandas as pd
from fuzzywuzzy import fuzz, process
import base64
from rq import Queue
from worker import conn
import time
import os

# redis connection to execute tasks in the background
q = Queue(connection=conn,job_timeout='3m')

app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])
server = app.server

# initialise global vars
#pd.Series([]).to_csv('wordList.csv',index=None)
if os.path.exists('matched_data.csv'): os.remove('matched_data.csv')

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
                    ],),

                    dbc.Col([
                        dt.DataTable(
                            id='matching_column',

                            style_table={'height': '300px', 'overflowY': 'auto', 'width': '100%','minWidth': '100%',},

                            style_header={'backgroundColor': 'rgb(230, 230, 230)', 'fontWeight': 'bold'},
                            fixed_rows={'headers': True},
                            style_cell={'textAlign': 'center'},
                            style_data_conditional=[{'if': {'row_index': 'odd'}, 'backgroundColor': 'rgb(248, 248, 248)'}],
                        ),
                    ]),
                ]),
            ],
            className="container"),

            dbc.CardFooter([
                dbc.Row([dbc.Button("Start Matching", id = 'launch-matching-button', color="success")],align="center",),
                dbc.Progress(id='progress-bar',striped=True),
                dcc.Interval(id='trigger_background_job')
            ]),

            dbc.CardHeader(html.H5("Matching Results")),
            dbc.CardBody([

                dbc.Row([
                    dbc.Col([
                        dt.DataTable(
                            id='table-matched-columns',
                            style_table={'height': '300px', 'overflowY': 'auto'},
                            style_header={'backgroundColor': 'rgb(230, 230, 230)', 'fontWeight': 'bold'},
                            #fixed_rows={'headers': True},
                            style_cell={'textAlign': 'center'},
                            style_data_conditional=[{'if': {'row_index': 'odd'}, 'backgroundColor': 'rgb(248, 248, 248)'}],
                        ),
                    ]),
                ]),
            ],
            className="container"),
                

                
            dbc.CardBody([
                dbc.Row(dbc.ListGroup(id='row-excluded-words',horizontal=True, className="mb-2")),
                dbc.Row([
                    dbc.Col(dbc.Input(id="input-domain-specific-words", type="text")),
                    dbc.Col(dbc.Button("Add word", id = 'add-button', color="success", className="mr-1"),width=2),
                    dbc.Col(dbc.Button("Delete word", id = 'delete-button', color="danger", className="mr-1"),width=2),
                    dbc.Col(dbc.Button("Reset word list", id = 'reset-button', color="secondary", className="mr-1"),width=2),
                    ]),
                ]),
            ],
            className="container"),
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


app.layout = html.Div(children=[HEADER])



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


def update_table(content, name, date):

    if not content:
        raise dash.exceptions.PreventUpdate

    content_type, content_string = content.split(',')
    decoded = base64.b64decode(content_string)

    df = pd.read_excel(decoded,sheet_name=None)

    sheets = list(df.keys())

    orig_df = df[sheets[0]].iloc[:,0:1]
    match_df = df[sheets[1]].iloc[:,0:1]

    return [{"name": i, "id": i} for i in orig_df.columns], orig_df.to_dict("rows"), [{"name": i, "id": i} for i in match_df.columns], match_df.to_dict("rows")



@app.callback(
    [Output('progress-bar','value')],
    [Input('upload', 'contents'),
     Input('launch-matching-button', 'n_clicks')],
    [State('row-excluded-words','children')],
     )

def launch_matching_table(content, n_clicks_launch,children_GroupList_words):

    if not content:
        raise dash.exceptions.PreventUpdate
    else:
        ctx = dash.callback_context
        if not ctx.triggered:
            raise dash.exceptions.PreventUpdate
        else:
            button_id = ctx.triggered[0]['prop_id'].split('.')[0]
            if button_id != 'launch-matching-button':
                raise dash.exceptions.PreventUpdate

    content_type, content_string = content.split(',')
    decoded = base64.b64decode(content_string)

    df = pd.read_excel(decoded,sheet_name=None)

    sheets = list(df.keys())

    orig_series = df[sheets[0]].iloc[:,0]
    match_series = df[sheets[1]].iloc[:,0]

    from utils import matchStrings
    
    # retrieve word list
    wordList = []
    if children_GroupList_words:
        for item in children_GroupList_words:
            wordList.append(item['props']['children'])

    df = q.enqueue(matchStrings, [wordList,orig_series,match_series]).result

    return [50]


@app.callback(
    [Output('table-matched-columns', 'columns'),
     Output('table-matched-columns', 'data')],
    [Input('trigger_background_job','n_intervals'),]
    )
def poll_update(n_intervals):

    if os.path.exists('matched_data.csv'):
        df = pd.read_csv('matched_data.csv')
        if not df.empty:
            return [{"name": i, "id": i} for i in df.columns], df.to_dict("rows")
    else:
        return [],[]


@app.callback(
    [Output('row-excluded-words','children')],
    [Input('input-domain-specific-words','value'),
     Input('add-button','n_clicks'),
     Input('delete-button','n_clicks'),
     Input('reset-button','n_clicks')],
     [State('row-excluded-words','children')],
     )

def updateWordList(word,n_clicks_add,n_clicks_delete,n_clicks_reset,children_GroupList_words):

    ctx = dash.callback_context
    if not ctx.triggered:
        raise dash.exceptions.PreventUpdate
    else:
        button_id = ctx.triggered[0]['prop_id'].split('.')[0]

    if button_id not in ['add-button','delete-button','reset-button']:
        raise dash.exceptions.PreventUpdate
    else:
        if not children_GroupList_words:
            children_GroupList_words = []


        if button_id == 'delete-button':
            for item in children_GroupList_words:
                if item['props']['children'] == word:
                    children_GroupList_words.remove(item)
                
        elif button_id == 'add-button':
            children_GroupList_words.append(dbc.ListGroupItem(word))

        elif button_id == 'reset-button':
            print('pressed reset')
            return [[]]
    print(children_GroupList_words)

    return [children_GroupList_words]



if __name__ == "__main__":
    app.run_server(debug=True,dev_tools_silence_routes_logging = False)
