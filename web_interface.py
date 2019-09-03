import datetime, base64, os, io, time
import numpy as np
import pandas as pd
import plotly.graph_objs as go
from functools import reduce
import time

import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output, State
import dash_auth
import dash_table
from flask_caching import Cache
from dash.exceptions import PreventUpdate

import filter_data

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

    html.H2('Step 3. Choose x-axis and y-axis for each chart'),
    # x-axis option
    html.Div([
        dcc.Dropdown(
            id='global-x', value='', placeholder='Select a feature as public x-axis...'
        ),
    ], style={'width': '96%', 'margin': '10px'}),

    html.Div([
        # chart 1,3
        html.Div([
            # chart 1 options
            html.Div([
                html.Div([
                    dcc.Dropdown(
                        id='y1-axis', value='', placeholder='y1-axis of Chart 1',
                        style={'margin': '5px', 'display': 'inline-block', 'width': '22%', 'minWidth': '100px'}
                    ),
                    dcc.Dropdown(
                        id='c1-title', value='', placeholder='Title of Chart 1',
                        style={'margin': '5px', 'display': 'inline-block', 'width': '22%', 'minWidth': '100px'}
                    ),
                    dcc.Dropdown(
                        id='y1-title', value='', placeholder='y1-axis title',
                        style={'margin': '5px', 'display': 'inline-block', 'width': '22%', 'minWidth': '100px'}
                    ),
                    dcc.Dropdown(
                        id='scatter-mode1',
                        value='markers',
                        options=[{'label': i, 'value': j} for i, j in
                            zip(['Marker', 'Line', 'Marker+Line'], ['markers', 'lines', 'lines+markers'])],
                        style={'margin': '5px', 'display': 'inline-block', 'width': '22%', 'minWidth': '100px'}
                    ),
                ]),
                html.Div([
                    dcc.RadioItems(
                        id='min-lim-1',
                        options=[{'label': i, 'value': i} for i in ['Lower-Limit', 'No Need']],
                        value='No Need', labelStyle={'display': 'inline-block'},
                        style={'margin': '5px'}
                    ),
                    dcc.Input(
                        id='min-lim-value1', placeholder='Enter a value...',
                        type='number', value='', style={'margin': '5px'}
                    ),
                ], style={'margin': '5px', 'display': 'inline-block'}),
                html.Div([
                    dcc.RadioItems(
                        id='max-lim-1',
                        options=[{'label': i, 'value': i} for i in ['Upper-Limit', 'No Need']],
                        value='No Need', labelStyle={'display': 'inline-block'},
                        style={'margin': '5px'}
                    ),
                    dcc.Input(
                        id='max-lim-value1', placeholder='Enter a value...',
                        type='number', value='', style={'margin': '5px'}
                    ),
                ], style={'margin': '5px', 'display': 'inline-block'}),
                html.Div([html.Div(id='output-data-upload1')]),
            ], style={'border': '2px dashed #999', 'borderRadius': '5px',
                        'padding': '10px', 'margin': '5px 5px'}),

            # chart 3 options
            html.Div([
                html.Div([
                    dcc.Dropdown(
                        id='y3-axis', value='', placeholder='y3-axis of Chart 3',
                        style={'margin': '5px', 'display': 'inline-block', 'width': '22%', 'minWidth': '100px'}
                    ),
                    dcc.Dropdown(
                        id='c3-title', value='', placeholder='Title of Chart 3',
                        style={'margin': '5px', 'display': 'inline-block', 'width': '22%', 'minWidth': '100px'}
                    ),
                    dcc.Dropdown(
                        id='y3-title', value='', placeholder='y3-axis title',
                        style={'margin': '5px', 'display': 'inline-block', 'width': '22%', 'minWidth': '100px'}
                    ),
                    dcc.Dropdown(
                        id='scatter-mode3',
                        value='markers',
                        options=[{'label': i, 'value': j} for i, j in
                            zip(['Marker', 'Line', 'Marker+Line'], ['markers', 'lines', 'lines+markers'])],
                        style={'margin': '5px', 'display': 'inline-block', 'width': '22%', 'minWidth': '100px'}
                    ),
                ]),
                html.Div([
                    dcc.RadioItems(
                        id='min-lim-3',
                        options=[{'label': i, 'value': i} for i in ['Lower-Limit', 'No Need']],
                        value='No Need', labelStyle={'display': 'inline-block'},
                        style={'margin': '5px'}
                    ),
                    dcc.Input(
                        id='min-lim-value3', placeholder='Enter a value...',
                        type='number', value='', style={'margin': '5px'}
                    ),
                ], style={'margin': '5px', 'display': 'inline-block'}),
                html.Div([
                    dcc.RadioItems(
                        id='max-lim-3',
                        options=[{'label': i, 'value': i} for i in ['Upper-Limit', 'No Need']],
                        value='No Need', labelStyle={'display': 'inline-block'},
                        style={'margin': '5px'}
                    ),
                    dcc.Input(
                        id='max-lim-value3', placeholder='Enter a value...',
                        type='number', value='', style={'margin': '5px'}
                    ),
                ], style={'margin': '5px', 'display': 'inline-block'}),
                html.Div([html.Div(id='output-data-upload2')]),
            ], style={'border': '2px dashed #999', 'borderRadius': '5px',
                        'padding': '10px', 'margin': '5px 5px'}),
            ], style={'display': 'inline-block', 'width': '48%'}),

        # chart 2.4
        html.Div([
            # chart 2 options
            html.Div([
                html.Div([
                    dcc.Dropdown(
                        id='y2-axis', value='', placeholder='y2-axis of Chart 2',
                        style={'margin': '5px', 'display': 'inline-block', 'width': '22%', 'minWidth': '100px'}
                    ),
                    dcc.Dropdown(
                        id='c2-title', value='', placeholder='Title of Chart 2',
                        style={'margin': '5px', 'display': 'inline-block', 'width': '22%', 'minWidth': '100px'}
                    ),
                    dcc.Dropdown(
                        id='y2-title', value='', placeholder='y1-axis title',
                        style={'margin': '5px', 'display': 'inline-block', 'width': '22%', 'minWidth': '100px'}
                    ),
                    dcc.Dropdown(
                        id='scatter-mode2',
                        value='markers',
                        options=[{'label': i, 'value': j} for i, j in
                            zip(['Marker', 'Line', 'Marker+Line'], ['markers', 'lines', 'lines+markers'])],
                        style={'margin': '5px', 'display': 'inline-block', 'width': '22%', 'minWidth': '100px'}
                    ),
                ]),
                html.Div([
                    dcc.RadioItems(
                        id='min-lim-2',
                        options=[{'label': i, 'value': i} for i in ['Lower-Limit', 'No Need']],
                        value='No Need', labelStyle={'display': 'inline-block'},
                        style={'margin': '5px'}
                    ),
                    dcc.Input(
                        id='min-lim-value2', placeholder='Enter a value...',
                        type='number', value='', style={'margin': '5px'}
                    ),
                ], style={'margin': '5px', 'display': 'inline-block'}),
                html.Div([
                    dcc.RadioItems(
                        id='max-lim-2',
                        options=[{'label': i, 'value': i} for i in ['Upper-Limit', 'No Need']],
                        value='No Need', labelStyle={'display': 'inline-block'},
                        style={'margin': '5px'}
                    ),
                    dcc.Input(
                        id='max-lim-value2', placeholder='Enter a value...',
                        type='number', value='', style={'margin': '5px'}
                    ),
                ], style={'margin': '5px', 'display': 'inline-block'}),
                html.Div([html.Div(id='output-data-upload3')]),
            ], style={'border': '2px dashed #999', 'borderRadius': '5px',
                        'padding': '10px', 'margin': '5px 5px'}),

        # chart 4 options
        html.Div([
            html.Div([
                dcc.Dropdown(
                    id='y4-axis', value='', placeholder='y4-axis of Chart 4',
                    style={'margin': '5px', 'display': 'inline-block', 'width': '22%', 'minWidth': '100px'}
                ),
                dcc.Dropdown(
                    id='c4-title', value='', placeholder='Title of Chart 4',
                    style={'margin': '5px', 'display': 'inline-block', 'width': '22%', 'minWidth': '100px'}
                ),
                dcc.Dropdown(
                    id='y4-title', value='', placeholder='y4-axis title',
                    style={'margin': '5px', 'display': 'inline-block', 'width': '22%', 'minWidth': '100px'}
                ),
                dcc.Dropdown(
                    id='scatter-mode4',
                    value='markers',
                    options=[{'label': i, 'value': j} for i, j in
                        zip(['Marker', 'Line', 'Marker+Line'], ['markers', 'lines', 'lines+markers'])],
                    style={'margin': '5px', 'display': 'inline-block', 'width': '22%', 'minWidth': '100px'}
                ),
            ]),
            html.Div([
                dcc.RadioItems(
                    id='min-lim-4',
                    options=[{'label': i, 'value': i} for i in ['Lower-Limit', 'No Need']],
                    value='No Need', labelStyle={'display': 'inline-block'},
                    style={'margin': '5px'}
                ),
                dcc.Input(
                    id='min-lim-value4', placeholder='Enter a value...',
                    type='number', value='', style={'margin': '5px'}
                ),
            ], style={'margin': '5px', 'display': 'inline-block'}),
            html.Div([
                dcc.RadioItems(
                    id='max-lim-4',
                    options=[{'label': i, 'value': i} for i in ['Upper-Limit', 'No Need']],
                    value='No Need', labelStyle={'display': 'inline-block'},
                    style={'margin': '5px'}
                ),
                dcc.Input(
                    id='max-lim-value4', placeholder='Enter a value...',
                    type='number', value='', style={'margin': '5px'}
                ),
            ], style={'margin': '5px', 'display': 'inline-block'}),
            html.Div([html.Div(id='output-data-upload4')]),
        ], style={'border': '2px dashed #999', 'borderRadius': '5px',
                    'padding': '10px', 'margin': '5px 5px'}),
        ], style={'display': 'inline-block', 'width': '48%'}),
    ]),

    html.Div(id='signal', style={'display': 'none'}),
])

@cache.memoize(timeout=60)
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
            print(type(useful_df))
            return useful_df
        except:
            useful_df.dropna(how='all', inplace=True)
            print(type(useful_df))
            return useful_df

@app.callback([Output('level1', 'options'), Output('level2', 'options'), Output('level3', 'options')], [Input('upload-data', 'contents')],
             [State('upload-data', 'filename'), State('upload-data', 'last_modified')])
def filter_choose(contents, filename, status):
    if contents is None:
        raise PreventUpdate
    else:
        df_raw = global_store(contents, filename, status)
        col_names = list(df_raw.columns)
        valid_ops1 = [{'label': i, 'value': i} for i in col_names]
        valid_ops2 = [{'label': i, 'value': i} for i in col_names]
        valid_ops3 = [{'label': i, 'value': i} for i in col_names]
        return valid_ops1, valid_ops2, valid_ops3

@app.callback(Output('level1-value', 'options'),
              [Input('level1', 'value'), Input('upload-data', 'contents')],
              [State('upload-data', 'filename'), State('upload-data', 'last_modified')])
def filter_ops1(f, contents, filename, status):
    if contents is None:
        raise PreventUpdate
    else:
        df_raw = global_store(contents, filename, status)
        if f is None:
            raise PreventUpdate
        else:
            f_options = list(df_raw[f].unique())
            print(f_options)
            f_ops = [{'label': 'All', 'value': 'all'}] + [{'label': i, 'value': i} for i in f_options]
            return f_ops

@app.callback(Output('level2-value', 'options'),
              [Input('level2', 'value'), Input('upload-data', 'contents')],
              [State('upload-data', 'filename'), State('upload-data', 'last_modified')])
def filter_ops2(f, contents, filename, status):
    if contents is None:
        raise PreventUpdate
    else:
        df_raw = global_store(contents, filename, status)
        if f is None:
            raise PreventUpdate
        else:
            f_options = list(df_raw[f].unique())
            print(f_options)
            f_ops = [{'label': 'All', 'value': 'all'}] + [{'label': i, 'value': i} for i in f_options]
            return f_ops

@app.callback(Output('level3-value', 'options'),
              [Input('level3', 'value'), Input('upload-data', 'contents')],
              [State('upload-data', 'filename'), State('upload-data', 'last_modified')])
def filter_ops3(f, contents, filename, status):
    if contents is None:
        raise PreventUpdate
    else:
        df_raw = global_store(contents, filename, status)
        if f is None:
            raise PreventUpdate
        else:
            f_options = list(df_raw[f].unique())
            print(f_options)
            f_ops = [{'label': 'All', 'value': 'all'}] + [{'label': i, 'value': i} for i in f_options]
            return f_ops

@app.callback(Output('signal', 'children'), [Input('upload-data', 'contents')],
             [State('upload-data', 'filename'), State('upload-data', 'last_modified')])
def compute_value(contents, filename, status):
    global_store(contents, filename, status)
    # print('cache successfully on: {}'.format(time.localtime()))
    return contents

MARKERS = filter_data.MARKERS
COLORS = filter_data.COLORS

# @app.callback()

if __name__ == '__main__':
    app.run_server(debug=True)