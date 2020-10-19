import datetime, base64, os, io, time
import numpy as np
import pandas as pd
import plotly.graph_objs as go
from functools import reduce
import time

import flask
import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output, State
import dash_auth
import dash_table
from flask_caching import Cache
from dash.exceptions import PreventUpdate

import filter_data
VALID_USERNAME_PASSWORD_PAIRS = {
    'Jason': 'shell'
}

# external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']
external_stylesheets = ['https://unpkg.com/spectre.css/dist/spectre.min.css']

MARKERS = filter_data.MARKERS
COLORS = filter_data.COLORS
server = flask.Flask(__name__)
app = dash.Dash(__name__, 
                server=server, 
                url_base_pathname='/m2d/',
                external_stylesheets=external_stylesheets)
auth = dash_auth.BasicAuth(
    app,
    VALID_USERNAME_PASSWORD_PAIRS
)
CACHE_CONFIG = {
    # try 'filesystem' if you don't want to setup redis
    # 'CACHE_TYPE': 'redis',
    # 'CACHE_REDIS_URL': os.environ.get('REDIS_URL', 'localhost:6379')
    'CACHE_TYPE': 'filesystem',
    'CACHE_DIR': r'./tmp'
}
cache = Cache()
cache.init_app(app.server, config=CACHE_CONFIG)
server = app.server
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
                        id='scatter-mode1',
                        value='markers',
                        options=[{'label': i, 'value': j} for i, j in
                            zip(['Marker', 'Line', 'Marker+Line'], ['markers', 'lines', 'lines+markers'])],
                        style={'margin': '5px', 'display': 'inline-block', 'width': '22%', 'minWidth': '100px'}
                    ),
                    dcc.Input(
                        id='c1-title', value='', placeholder='Title of Chart 1', type='text',
                        style={'margin': '5px', 'display': 'inline-block', 'width': '22%', 'minWidth': '100px'}
                    ),
                    dcc.Input(
                        id='y1-title', value='', placeholder='y1-axis title', type='text',
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
                        type='text', value='', style={'margin': '5px'}
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
                        type='text', value='', style={'margin': '5px'}
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
                        id='scatter-mode3',
                        value='markers',
                        options=[{'label': i, 'value': j} for i, j in
                            zip(['Marker', 'Line', 'Marker+Line'], ['markers', 'lines', 'lines+markers'])],
                        style={'margin': '5px', 'display': 'inline-block', 'width': '22%', 'minWidth': '100px'}
                    ),
                    dcc.Input(
                        id='c3-title', value='', placeholder='Title of Chart 3', type='text',
                        style={'margin': '5px', 'display': 'inline-block', 'width': '22%', 'minWidth': '100px'}
                    ),
                    dcc.Input(
                        id='y3-title', value='', placeholder='y3-axis title', type='text',
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
                        type='text', value='', style={'margin': '5px'}
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
                        type='text', value='', style={'margin': '5px'}
                    ),
                ], style={'margin': '5px', 'display': 'inline-block'}),
                html.Div([html.Div(id='output-data-upload3')]),
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
                        id='scatter-mode2',
                        value='markers',
                        options=[{'label': i, 'value': j} for i, j in
                            zip(['Marker', 'Line', 'Marker+Line'], ['markers', 'lines', 'lines+markers'])],
                        style={'margin': '5px', 'display': 'inline-block', 'width': '22%', 'minWidth': '100px'}
                    ),
                    dcc.Input(
                        id='c2-title', value='', placeholder='Title of Chart 2', type='text',
                        style={'margin': '5px', 'display': 'inline-block', 'width': '22%', 'minWidth': '100px'}
                    ),
                    dcc.Input(
                        id='y2-title', value='', placeholder='y1-axis title', type='text',
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
                        type='text', value='', style={'margin': '5px'}
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
                        type='text', value='', style={'margin': '5px'}
                    ),
                ], style={'margin': '5px', 'display': 'inline-block'}),
                html.Div([html.Div(id='output-data-upload2')]),
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
                    id='scatter-mode4',
                    value='markers',
                    options=[{'label': i, 'value': j} for i, j in
                        zip(['Marker', 'Line', 'Marker+Line'], ['markers', 'lines', 'lines+markers'])],
                    style={'margin': '5px', 'display': 'inline-block', 'width': '22%', 'minWidth': '100px'}
                ),
                dcc.Input(
                    id='c4-title', value='', placeholder='Title of Chart 4', type='text',
                    style={'margin': '5px', 'display': 'inline-block', 'width': '22%', 'minWidth': '100px'}
                ),
                dcc.Input(
                    id='y4-title', value='', placeholder='y4-axis title', type='text',
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
                    type='text', value='', style={'margin': '5px'}
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
                    type='text', value='', style={'margin': '5px'}
                ),
            ], style={'margin': '5px', 'display': 'inline-block'}),
            html.Div([html.Div(id='output-data-upload4')]),
        ], style={'border': '2px dashed #999', 'borderRadius': '5px',
                    'padding': '10px', 'margin': '5px 5px'}),
        ], style={'display': 'inline-block', 'width': '48%'}),
    ]),

    html.Div(id='signal', style={'display': 'none'}),
    html.Div(id='maker_symbol', style={'display': 'none'}),

    # registration according to China Internet Policy
    html.Div([html.A('沪ICP备19043992号-1', href='http://beian.miit.gov.cn',
                        style={'font-size': 11, 'color': '#101010'}),
              html.P('      ',
                        style={'display': 'inline-block'}),
              html.A('沪公网备: 100012127306', href='http://www.zx110.org/picp?sn=:100012127306',
                        style={'display': 'inline-block', 'font-size': 11, 'color': '#101010'}),
             ], style={'textAlign': 'center', 'white-space': 'pre'})
])

# dataFrame cached
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
            # print(type(useful_df))
            return useful_df
        except:
            useful_df.dropna(how='all', inplace=True)
            # print(type(useful_df))
            return useful_df

# options for filters
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

# options in fileter1
@app.callback(Output('level1-value', 'options'),
              [Input('level1', 'value'), Input('upload-data', 'contents')],
              [State('upload-data', 'filename'), State('upload-data', 'last_modified')])
def filter_ops1(f1, contents, filename, status):
    if contents is None:
        raise PreventUpdate
    else:
        df_raw = global_store(contents, filename, status)
        if f1 == '':
            raise PreventUpdate
        else:
            f1_options = list(df_raw[f1].unique())
            f1_ops = [{'label': 'All', 'value': 'all'}] + [{'label': i, 'value': i} for i in f1_options]
            return f1_ops

# options in fileter2
@app.callback(Output('level2-value', 'options'),
              [Input('level1', 'value'), Input('level1-value', 'value'),
               Input('level2', 'value'), Input('upload-data', 'contents')],
              [State('upload-data', 'filename'), State('upload-data', 'last_modified')])
def filter_ops2(f1, f1v, f2, contents, filename, status):
    if contents is None:
        raise PreventUpdate
    else:
        df_raw = global_store(contents, filename, status)
        if (f2 == '') or (f1 == '') or (f1v == [] or None):
            raise PreventUpdate
        else:
            if 'all' in f1v:
                if bool(f2):
                    f2_options = list(df_raw[f2].unique())
                else:
                    raise PreventUpdate
            else:
                if bool(f2):
                    df_lv2 = df_raw.loc[df_raw[f1].isin(f1v)]
                    f2_options = list(df_lv2[f2].unique())
                else:
                    raise PreventUpdate
            f2_ops = [{'label': 'All', 'value': 'all'}] + [{'label': i, 'value': i} for i in f2_options]
            return f2_ops

# options in fileter3
@app.callback(Output('level3-value', 'options'),
              [Input('level1', 'value'), Input('level1-value', 'value'),
               Input('level2', 'value'), Input('level2-value', 'value'),
               Input('level3', 'value'), Input('upload-data', 'contents')],
              [State('upload-data', 'filename'), State('upload-data', 'last_modified')])
def filter_ops3(f1, f1v, f2, f2v, f3, contents, filename, status):
    if contents is None:
        raise PreventUpdate
    else:
        df_raw = global_store(contents, filename, status)
        if not (bool(f1) and bool(f2) and bool(f1v) and bool(f2v) and bool(f3)):
            raise PreventUpdate
        else:
            if 'all' in f1v:
                if 'all' in f2v:
                    f3_options = list(df_raw[f3].unique())
                else:
                    df_lv3 = df_raw.loc[df_raw[f2].isin(f2v)]
                    f3_options = list(df_lv3[f3].unique())
            else:
                if 'all' in f2v:
                    df_lv3 = df_raw.loc[df_raw[f1].isin(f1v)]
                    f3_options = list(df_lv3[f3].unique())
                else:
                    df_lv2 = df_raw.loc[df_raw[f1].isin(f1v)]
                    df_lv3 = df_lv2.loc[df_lv2[f2].isin(f2v)]
                    f3_options = list(df_lv3[f3].unique())
            f3_ops = [{'label': 'All', 'value': 'all'}] + [{'label': i, 'value': i} for i in f3_options]
            return f3_ops

# calculated cache
@app.callback(Output('signal', 'children'), [Input('upload-data', 'contents')],
             [State('upload-data', 'filename'), State('upload-data', 'last_modified')])
def compute_value(contents, filename, status):
    global_store(contents, filename, status)
    # print('cache successfully on: {}'.format(time.localtime()))
    return contents

# choose x-axis
@app.callback(Output('global-x', 'options'),
             [Input('upload-data', 'contents')],
             [State('upload-data', 'filename'), State('upload-data', 'last_modified')])
def x_ops(contents, filename, status):
    if contents is None:
        raise PreventUpdate
    else:
        df_raw = global_store(contents, filename, status)
        x_options = [{'label': i, 'value': i} for i in list(df_raw.columns)]
        return x_options

# choose y1-axis
@app.callback(Output('y1-axis', 'options'),
             [Input('upload-data', 'contents')],
             [State('upload-data', 'filename'), State('upload-data', 'last_modified')])
def y1_ops(contents, filename, status):
    if contents is None:
        raise PreventUpdate
    else:
        df_raw = global_store(contents, filename, status)
        y1_options = [{'label': i, 'value': i} for i in list(df_raw.columns)]
        return y1_options

@app.callback(Output('output-data-upload1', 'children'),
             [Input('level1', 'value'), Input('level1-value', 'value'), Input('level2', 'value'),
              Input('level2-value', 'value'), Input('level3', 'value'), Input('level3-value', 'value'),
              Input('global-x', 'value'), Input('y1-axis', 'value'), Input('scatter-mode1', 'value'),
              Input('min-lim-1', 'value'), Input('max-lim-1', 'value'),
              Input('min-lim-value1', 'value'), Input('max-lim-value1', 'value'),
              Input('c1-title', 'value'), Input('y1-title', 'value'),
              Input('upload-data', 'contents')],
             [State('upload-data', 'filename'), State('upload-data', 'last_modified')])
def get_df1(f1, f1v, f2, f2v, f3, f3v, xaxis, y1axis, marker_mode,
            minLim, maxLim, minLimVal, maxLimVal, charttitle, ytitle, contents, filename, status):
    global MARKERS
    global COLORS
    if contents is None:
        raise PreventUpdate
    else:
        a = bool(xaxis) and bool(y1axis) and (not(bool(f1v) ^ bool(f1))) and (not(bool(f2v) ^ bool(f2)))
        b = not(bool(f3v) ^ bool(f3))
        c = ((not(bool(f3))) & (f3v == 'all'))
        if ((a & b) or (a & c)):
            df = global_store(contents, filename, status)
            if bool(f2):
                color_dict = filter_data.get_color_dict(df, f2, COLORS)
            else:
                color_dict = None
            # print(color_dict)
            df_useful = filter_data.get_useful(df, f1, f1v, f2, f2v, f3, f3v, MARKERS)
            traces = filter_data.generate_scatter(df_useful, xaxis, y1axis, marker_mode, color_dict)
            layout = filter_data.layout_adjust(df, minLim, maxLim, minLimVal,
                                               maxLimVal, xaxis, ytitle, charttitle)
            return html.Div([
                dcc.Graph(
                    figure = {
                        'data': traces,
                        'layout': layout,
                    }
                )
            ])
        else:
            raise PreventUpdate

# choose y2-axis
@app.callback(Output('y2-axis', 'options'),
             [Input('upload-data', 'contents')],
             [State('upload-data', 'filename'), State('upload-data', 'last_modified')])
def y2_ops(contents, filename, status):
    if contents is None:
        raise PreventUpdate
    else:
        df_raw = global_store(contents, filename, status)
        y2_options = [{'label': i, 'value': i} for i in list(df_raw.columns)]
        return y2_options

@app.callback(Output('output-data-upload2', 'children'),
             [Input('level1', 'value'), Input('level1-value', 'value'), Input('level2', 'value'),
              Input('level2-value', 'value'), Input('level3', 'value'), Input('level3-value', 'value'),
              Input('global-x', 'value'), Input('y2-axis', 'value'), Input('scatter-mode2', 'value'),
              Input('min-lim-2', 'value'), Input('max-lim-2', 'value'),
              Input('min-lim-value2', 'value'), Input('max-lim-value2', 'value'),
              Input('c2-title', 'value'), Input('y2-title', 'value'),
              Input('upload-data', 'contents')],
             [State('upload-data', 'filename'), State('upload-data', 'last_modified')])
def get_df2(f1, f1v, f2, f2v, f3, f3v, xaxis, y2axis, marker_mode,
            minLim, maxLim, minLimVal, maxLimVal, charttitle, ytitle, contents, filename, status):
    global MARKERS
    global COLORS
    if contents is None:
        raise PreventUpdate
    else:
        a = bool(xaxis) and bool(y2axis) and (not(bool(f1v) ^ bool(f1))) and (not(bool(f2v) ^ bool(f2)))
        b = not(bool(f3v) ^ bool(f3))
        c = ((not(bool(f3))) & (f3v == 'all'))
        if ((a & b) or (a & c)):
            df = global_store(contents, filename, status)
            if bool(f2):
                color_dict = filter_data.get_color_dict(df, f2, COLORS)
            else:
                color_dict = None
            df_useful = filter_data.get_useful(df, f1, f1v, f2, f2v, f3, f3v, MARKERS)
            traces = filter_data.generate_scatter(df_useful, xaxis, y2axis, marker_mode, color_dict)
            layout = filter_data.layout_adjust(df, minLim, maxLim, minLimVal,
                                               maxLimVal, xaxis, ytitle, charttitle)
            return html.Div([
                dcc.Graph(
                    figure = {
                        'data': traces,
                        'layout': layout,
                    }
                )
            ])
        else:
            raise PreventUpdate

# choose y3-axis
@app.callback(Output('y3-axis', 'options'),
             [Input('upload-data', 'contents')],
             [State('upload-data', 'filename'), State('upload-data', 'last_modified')])
def y3_ops(contents, filename, status):
    if contents is None:
        raise PreventUpdate
    else:
        df_raw = global_store(contents, filename, status)
        y3_options = [{'label': i, 'value': i} for i in list(df_raw.columns)]
        return y3_options

@app.callback(Output('output-data-upload3', 'children'),
             [Input('level1', 'value'), Input('level1-value', 'value'), Input('level2', 'value'),
              Input('level2-value', 'value'), Input('level3', 'value'), Input('level3-value', 'value'),
              Input('global-x', 'value'), Input('y3-axis', 'value'), Input('scatter-mode3', 'value'),
              Input('min-lim-3', 'value'), Input('max-lim-3', 'value'),
              Input('min-lim-value3', 'value'), Input('max-lim-value3', 'value'),
              Input('c3-title', 'value'), Input('y3-title', 'value'),
              Input('upload-data', 'contents')],
             [State('upload-data', 'filename'), State('upload-data', 'last_modified')])
def get_df3(f1, f1v, f2, f2v, f3, f3v, xaxis, y3axis, marker_mode,
            minLim, maxLim, minLimVal, maxLimVal, charttitle, ytitle, contents, filename, status):
    global MARKERS
    global COLORS
    if contents is None:
        raise PreventUpdate
    else:
        a = bool(xaxis) and bool(y3axis) and (not(bool(f1v) ^ bool(f1))) and (not(bool(f2v) ^ bool(f2)))
        b = not(bool(f3v) ^ bool(f3))
        c = ((not(bool(f3))) & (f3v == 'all'))
        if ((a & b) or (a & c)):
            df = global_store(contents, filename, status)
            if bool(f2):
                color_dict = filter_data.get_color_dict(df, f2, COLORS)
            else:
                color_dict = None
            df_useful = filter_data.get_useful(df, f1, f1v, f2, f2v, f3, f3v, MARKERS)
            traces = filter_data.generate_scatter(df_useful, xaxis, y3axis, marker_mode, color_dict)
            layout = filter_data.layout_adjust(df, minLim, maxLim, minLimVal,
                                               maxLimVal, xaxis, ytitle, charttitle)
            return html.Div([
                dcc.Graph(
                    figure = {
                        'data': traces,
                        'layout': layout,
                    }
                )
            ])
        else:
            raise PreventUpdate

# choose y4-axis
@app.callback(Output('y4-axis', 'options'),
             [Input('upload-data', 'contents')],
             [State('upload-data', 'filename'), State('upload-data', 'last_modified')])
def y4_ops(contents, filename, status):
    if contents is None:
        raise PreventUpdate
    else:
        df_raw = global_store(contents, filename, status)
        y4_options = [{'label': i, 'value': i} for i in list(df_raw.columns)]
        return y4_options

@app.callback(Output('output-data-upload4', 'children'),
             [Input('level1', 'value'), Input('level1-value', 'value'), Input('level2', 'value'),
              Input('level2-value', 'value'), Input('level3', 'value'), Input('level3-value', 'value'),
              Input('global-x', 'value'), Input('y4-axis', 'value'), Input('scatter-mode4', 'value'),
              Input('min-lim-4', 'value'), Input('max-lim-4', 'value'),
              Input('min-lim-value4', 'value'), Input('max-lim-value4', 'value'),
              Input('c4-title', 'value'), Input('y4-title', 'value'),
              Input('upload-data', 'contents')],
             [State('upload-data', 'filename'), State('upload-data', 'last_modified')])
def get_df4(f1, f1v, f2, f2v, f3, f3v, xaxis, y4axis, marker_mode,
            minLim, maxLim, minLimVal, maxLimVal, charttitle, ytitle, contents, filename, status):
    global MARKERS
    global COLORS
    if contents is None:
        raise PreventUpdate
    else:
        a = bool(xaxis) and bool(y4axis) and (not(bool(f1v) ^ bool(f1))) and (not(bool(f2v) ^ bool(f2)))
        b = not(bool(f3v) ^ bool(f3))
        c = ((not(bool(f3))) & (f3v == 'all'))
        if ((a & b) or (a & c)):
            df = global_store(contents, filename, status)
            if bool(f2):
                color_dict = filter_data.get_color_dict(df, f2, COLORS)
            else:
                color_dict = None
            df_useful = filter_data.get_useful(df, f1, f1v, f2, f2v, f3, f3v, MARKERS)
            traces = filter_data.generate_scatter(df_useful, xaxis, y4axis, marker_mode, color_dict)
            layout = filter_data.layout_adjust(df, minLim, maxLim, minLimVal,
                                               maxLimVal, xaxis, ytitle, charttitle)
            return html.Div([
                dcc.Graph(
                    figure = {
                        'data': traces,
                        'layout': layout,
                    }
                )
            ])
        else:
            raise PreventUpdate

if __name__ == '__main__':
    app.run_server(debug=False)
