import datetime, base64, os, io, time
import numpy as np
import pandas as pd
import plotly.graph_objs as go

import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output, State
import dash_auth
import dash_table
from flask_caching import Cache

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)
CACHE_CONFIG = {
    # try 'filesystem' if you don't want to setup redis
    # 'CACHE_TYPE': 'redis',
    # 'CACHE_REDIS_URL': os.environ.get('REDIS_URL', 'localhost:6379')
    'CACHE_TYPE': 'filesystem',
    'CACHE_DIR': r'./tmp'
}
cache = Cache()
cache.init_app(app.server, config=CACHE_CONFIG)
# app.config.suppress_callback_exceptions = True

app.layout = html.Div([
    html.H2('Step 1. Upload an excel or csv file.'),
	# Upload component
    dcc.Upload(
        id='upload-data',
        children=html.Div([
            'Drag and Drop or ',
            html.A('Select Files')
        ]),
        style={
            'width': '95%', 'height': '60px', 'lineHeight': '60px',
            'borderWidth': '2px', 'borderStyle': 'dashed', 'borderRadius': '5px',
            'textAlign': 'center', 'margin': '20px'
        },
        multiple=False,
    ),

    # level 1, level 2, level 3 filters
    html.Div([
        html.H2('Step 2. Select Level 1/2/3 filters'),
        html.Div('''If you select any classes under Level 1 filter, say, A and B; 
                    then Level 2 filter will only leave those elements belonging to classes A and B.'''),
        html.Div('The default value is All which means all classes will be chosen defaultly.', 
                    style={'margin': '20px 0px 20px'}),
        html.Div([
            dcc.Dropdown(
                id='level1', value='', placeholder='Level 1 filter name like Project Code', style={'margin': '5px'}
            ),
            dcc.Dropdown(
                id='level1-value', value='all', placeholder='Level 1 options...', multi=True, style={'margin': '5px'}
            )
        ], style={'width': '32%', 'display': 'inline-block'}),
        html.Div([
            dcc.Dropdown(
                id='level2', value='', placeholder='Level 2 filter name like REG No.', style={'margin': '5px'}
            ),
            dcc.Dropdown(
                id='level2-value', value='all', placeholder='Level 2 options...', multi=True, style={'margin': '5px'}
            )
        ], style={'width': '32%', 'display': 'inline-block'}),
        html.Div([
            dcc.Dropdown(
                id='level3', value='', placeholder='Level 3 filter name like Oil Code', style={'margin': '5px'}
            ),
            dcc.Dropdown(
                id='level3-value', value='all', placeholder='Level 3 options...', multi=True, style={'margin': '5px'}
            )
        ], style={'width': '32%', 'display': 'inline-block'}),
    ], style={'margin': '10px'}),

    html.H2('Step 3. Choose x-axis and y-axis for different charts'),
    html.Div([
        dcc.Dropdown(
            id='global-x', value='', placeholder='Select a feature as public x-axis...'
        ),
    ], style={'width': '96%', 'margin': '10px'}),
    html.Div([
        html.Div([
            dcc.Dropdown(
                id='axis-y1', value='', placeholder='y1-axis of 1st chart',
                style={'margin': '5px'}
            ),
            dcc.Dropdown(
                id='axis-y2', value='', placeholder='y3-axis of 2nd chart',
                style={'margin': '5px'}
            ),
        ], style={'margin': '5px', 'width': '48%', 'display': 'inline-block'}),
        html.Div([
            dcc.Dropdown(
                id='axis-y3', value='', placeholder='y2-axis of 3rd chart',
                style={'margin': '5px'}
            ),
            dcc.Dropdown(
                id='axis-y4', value='', placeholder='y4-axis of 4th chart',
                style={'margin': '5px'}
            ),
        ], style={'margin': '5px', 'width': '48%', 'display': 'inline-block'}),
    ], style={'width': '96%'}),

    # xaxis, need lower limitation or not, limitation value
    html.Div([
        html.H2('Step 3. Choose the x-axis and y-axis'),
        html.Div([
            dcc.Dropdown(
                id='xaxis-column', value='', placeholder='Select a feature as xaxis...'
            ),
            html.Div([
                html.H5('Need Lower-limitation?'),
                dcc.RadioItems(
                    id='min-limit-value',
                    options=[{'label': i, 'value': i} for i in ['Lower-Limit', 'No Need']],
                    value='No Need',
                    labelStyle={'display': 'inline-block'}
            ),
                dcc.Input(
                    id='min-lim-value', placeholder='Enter a value...', type='text', value=''
            ),
            ],
                style={'border': '2px dashed #999', 'borderRadius': '5px', 
                        'padding': '10px', 'margin': '5px 10px'}
            )
        ], style={'width': '48%', 'display': 'inline-block'}),

        # yaxis, need upper limitation or not, limitation value
        html.Div([
            dcc.Dropdown(
                id='yaxis-column', value='', placeholder='Select features as yaxis...'
            ),
            html.Div([
                html.H5('Need Upper-limitation?'),
                dcc.RadioItems(
                    id='upper-limit-value',
                    options=[{'label': i, 'value': i} for i in ['Upper-Limit', 'No Need']],
                    value='No Need',
                    labelStyle={'display': 'inline-block'}
                ),
                dcc.Input(
                    id='max-lim-value', placeholder='Enter a value...', type='text', value=''
                )],
                style={
                    'border': '2px dashed #999', 'borderRadius': '5px', 
                    'padding': '10px', 'margin': '5px 10px'}),
                ],
        style={'width': '48%', 'display': 'inline-block'}),

        html.Div([
            html.H5('Choose the type of the chart: scatter or line?'),
            dcc.Dropdown(
                id='scatter-mode', value='markers',
                options=[{'label': i, 'value': j} for i, j in 
                            zip(['Marker', 'Line', 'Marker+Line'], ['markers', 'lines', 'lines+markers'])]
            )
        ],
            style={'width': '48%'}),
    ], style={'margin': '20px'}),

    html.Div(id='output-data-upload'),
])

@cache.memoize(timeout=20)
def global_store(contents, filename, status):
    # simulate expensive query
    if contents is not None:
        content_type, content_string = contents.split(',')
        decoded = base64.b64decode(content_string)
        try:
            if 'csv' in filename:
                df = pd.read_csv(io.StringIO(decoded.decode('utf-8')))
            elif 'xls' in filename:
                df = pd.read_excel(io.BytesIO(decoded))
        except Exception as e:
            print(e)
            return html.Div([
                'There was an error processing this file.'
            ])
        useful_df = df.replace(r'<(.*)', r'\1', regex=True)
        try:
            useful_df["OIL KM's"] = pd.to_numeric(df["OIL KM's"], 'coerce')
            useful_df = useful_df[~useful_df["OIL KM's"].isnull()]
            useful_df.dropna(how='all', inplace=True)
            return (useful_df, content_type, filename, status)
        except:
            useful_df.dropna(how='all', inplace=True)
            return (useful_df, content_type, filename, status)

if __name__ == '__main__':
    app.run_server(debug=True)