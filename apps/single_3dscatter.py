import base64
import datetime
import io

import dash
import dash_auth
from dash.dependencies import Input, Output, State
import dash_core_components as dcc
import dash_html_components as html
from dash.exceptions import PreventUpdate
import dash_table
from flask_caching import Cache
import flask

import pandas as pd
import plotly.express as px
import plotly.graph_objs as go

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']
# Keep this out of source code repository - save in a file or a database
VALID_USERNAME_PASSWORD_PAIRS = {
    'Jason': 'shell'
}
server = flask.Flask(__name__)
app = dash.Dash(__name__,
                server=server,
                url_base_pathname='/s3d/',
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
# available_indicators = df['Indicator Name'].unique()

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
        # Allow multiple files to be uploaded
        multiple=False,
    ),

    # xaxis
    html.Div([
        html.Div([
            html.H2('Step 2. Choose x-axis, y-axis, z-axis and if you need classification'),
            html.P(['x-axis:']),
            html.Div([
                dcc.Dropdown(
                    id='xaxis-column', value='',
                    placeholder='Select a feature as x-axis...', options=[]
                ),
                html.P(['y-axis:']),
                dcc.Dropdown(
                    id='yaxis-column', value='',
                    placeholder='Select features as y-axis...', options=[]
                ),
                html.P(['z-axis:']),
                dcc.Dropdown(
                    id='zaxis-column', value='',
                    placeholder='Select features as z-axis...', options=[]
                ),
                html.P(['classes:']),
                dcc.Dropdown(
                    id='class-column', value='',
                    placeholder='Select features as class...', options=[]
                ),
            ]),
        ]),
       html.Div([
            html.H2('Step 3. Adjust chart properties if you need'),
            html.Div(['Adjust chart properties such as chart type or add y-axis title, chart title, etc.']),
            dcc.Input(
                id='chart-title', placeholder='customize chart title', type='text', value='',
                style={'width': '45%', 'display': 'inline-block', 'margin': '5px 5px'}
            ),
            dcc.Input(
                id='y-axis-title', placeholder='customize y-axis title', type='text', value='',
                style={'width': '45%', 'display': 'inline-block', 'margin': '5px 5px'}
            ),
            html.H5('Choose the type of the chart: scatter or line?'),
            dcc.Dropdown(
                id='scatter-mode',
                value='markers',
                options=[{'label': i, 'value': j} for i, j in
                            zip(['Marker', 'Line', 'Marker+Line'], ['markers', 'lines', 'lines+markers'])]
            ),
        ])
    ], style={'width': '25%', 'float': 'left', 'margin': '5px 5px'}),
    html.Div([
        html.Div(id='output-data-upload'),
    ], style={'width': '70%', 'display': 'inline-block', 'margin': '5px 5px'}),
])

# dataFrame cached
@cache.memoize(timeout=60)
def global_store(contents, filename, status):
    # simulate expensive query
    if contents is not None:
        _, content_string = contents.split(',')
        decoded = base64.b64decode(content_string)
        # print(filename)
        try:
            if 'csv' in filename:
                df = pd.read_csv(io.StringIO(decoded.decode('utf-8')))
            elif 'xls' in filename:
                df = pd.read_excel(io.BytesIO(decoded))
        except Exception as e:
            print(e)
            return pd.DataFrame()
        useful_df = df.replace(r'<(.*)', r'\1', regex=True)
        try:
            useful_df["OIL KM's"] = pd.to_numeric(df["OIL KM's"], 'coerce')
            useful_df = useful_df[~useful_df["OIL KM's"].isnull()]
            useful_df.dropna(how='all', inplace=True)
            return useful_df
        except:
            useful_df.dropna(how='all', inplace=True)
            return useful_df

# get useful data from dataset
@app.callback(Output('output-data-upload', 'children'),
              [Input('upload-data', 'contents'),
              Input('xaxis-column', 'value'), Input('yaxis-column', 'value'),
              Input('zaxis-column', 'value'), Input('class-column', 'value'),
              Input('chart-title', 'value'), Input('scatter-mode', 'value')],
              [State('upload-data', 'filename'), State('upload-data', 'last_modified')])
def parse_contents(contents, xName, yName, zName, species,
                   chartTitle, marker_mode, filename, status):
    if contents is not None:
        df = global_store(contents, filename, status)
        if marker_mode == 'markers':
            marker = {'size': 10, 'opacity': 0.65, 'line': {'width': 0.5, 'color': 'white'}}
        else:
            marker = {'size': 7, 'opacity': 0.65}
        if '' in [xName, yName, zName, species]:
            # print('sth is wrong...')
            PreventUpdate
        else:
            # print(df.head(5))
            # trace = [go.Scatter(x=df[xName].values, y=df[yName].values)]
            fig = px.scatter_3d(df,
                            x=xName,
                            y=yName,
                            z=zName,
                            color=species,
                            size_max=marker['size'],
                            opacity=0.7)
            fig.update_layout(margin=dict(l=0, r=0, b=0, t=0), height=800)
            print('Working...')
            # return fig
            return dcc.Graph(figure=fig)


@app.callback(Output('xaxis-column', 'options'),
			  [Input('upload-data', 'contents')],
			  [State('upload-data', 'filename'),
               State('upload-data', 'last_modified')])
def get_available_indicators(contents, filename, status):
    if contents is not None:
        df = global_store(contents, filename, status)
        available_indicators = list(df.columns)
        options=[{'label': i, 'value': i} for i in available_indicators]
        # print(options)
        return options
    else:
        return []

@app.callback(Output('yaxis-column', 'options'),
			  [Input('upload-data', 'contents')],
			  [State('upload-data', 'filename'),
               State('upload-data', 'last_modified')])
def get_available_indicators1(contents, filename, status):
    if contents is not None:
        df = global_store(contents, filename, status)
        available_indicators = list(df.columns)
        options=[{'label': i, 'value': i} for i in available_indicators]
        return options
    else:
        return []

@app.callback(Output('zaxis-column', 'options'),
			  [Input('upload-data', 'contents')],
			  [State('upload-data', 'filename'),
               State('upload-data', 'last_modified')])
def get_available_indicators2(contents, filename, status):
    if contents is not None:
        df = global_store(contents, filename, status)
        available_indicators = list(df.columns)
        options=[{'label': i, 'value': i} for i in available_indicators]
        return options
    else:
        return []

@app.callback(Output('class-column', 'options'),
			  [Input('upload-data', 'contents')],
			  [State('upload-data', 'filename'),
               State('upload-data', 'last_modified')])
def get_available_indicators3(contents, filename, status):
    if contents is not None:
        df = global_store(contents, filename, status)
        available_indicators = list(df.columns)
        options=[{'label': i, 'value': i} for i in available_indicators]
        return options
    else:
        return []

if __name__ == '__main__':
    app.run_server(debug=False, port=8050)
    # app.run_server(host='192.168.1.18', port=8051)