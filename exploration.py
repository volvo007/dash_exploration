import datetime
import base64
import os, io
import time
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
    # title 1
    html.H2([
        'Step 1. Drag a Excel or CSV table to the box below.'
    ]),
	# Upload component
    dcc.Upload(
        id='upload-data',
        children=html.Div([
            'Drag and Drop or ',
            html.A('Select Files')
        ]),
        style={
            'width': '90%', 'height': '60px', 'lineHeight': '60px',
            'borderWidth': '2px', 'borderStyle': 'dashed', 'borderRadius': '5px',
            'textAlign': 'center', 'margin': '20px'
        },
        # Allow multiple files to be uploaded
        multiple=False,
    ),

    html.Div(id='graph-area1'),
    html.Div(id='graph-area2'),
    html.Div(id='signal', style={'display': 'none'})
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
            return (useful_df, content_type, filename, status)
        except:
            return (useful_df, content_type, filename, status)

@app.callback(Output('signal', 'children'), 
              [Input('upload-data', 'contents')],
              [State('upload-data', 'filename'),
               State('upload-data', 'last_modified')])
def send_signal(contents, filename, status):
    global_store(contents, filename, status)
    return filename

def generate_figure(useful_df):
    data = [go.Scatter(x=useful_df["OIL KM's"], y=useful_df['Iron ppm FE'],
                       mode='markers', marker={'size': 12, 'opacity': 0.5})]
    layout = go.Layout(xaxis={'title': 'Oil KM'}, title='Demo', hovermode='closest',
                       margin={'l': 20, 'r': 20, 't': 20, 'b': 20})
    return dcc.Graph(figure={'data': data, 'layout': layout})

@app.callback(Output('graph-area1', 'children'),
              [Input('upload-data', 'contents')],
              [State('upload-data', 'filename'),
               State('upload-data', 'last_modified')])
def update_graph_1(useful_df, filename, status):
    cached_data = global_store(useful_df, filename, status)
    if cached_data is not None:
        return html.Div([
                        html.H5('Filename: {}'.format(cached_data[2])),
                        html.H5('Modified: {}'.format(datetime.datetime.fromtimestamp(cached_data[3]))),
                        generate_figure(global_store(useful_df, filename, status)[0])
        ])

@app.callback(Output('graph-area2', 'children'),
              [Input('upload-data', 'contents')],
              [State('upload-data', 'filename'),
               State('upload-data', 'last_modified')])
def update_graph_2(useful_df, filename, status):
    cached_data = global_store(useful_df, filename, status)
    if cached_data is not None:
        return html.Div([
                        html.H5('Filename: {}'.format(cached_data[2])),
                        html.H5('Modified: {}'.format(datetime.datetime.fromtimestamp(cached_data[3]))),
                        generate_figure(global_store(useful_df, filename, status)[0])
        ])

if __name__ == '__main__':
    app.run_server(debug=True)