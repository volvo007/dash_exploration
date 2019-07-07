import base64
import datetime
import io

import dash
import dash_auth
from dash.dependencies import Input, Output, State
import dash_core_components as dcc
import dash_html_components as html
import dash_table

import pandas as pd
import plotly.graph_objs as go

# Keep this out of source code repository - save in a file or a database
VALID_USERNAME_PASSWORD_PAIRS = {
    'Jason': 'shell'
}

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)
auth = dash_auth.BasicAuth(
    app,
    VALID_USERNAME_PASSWORD_PAIRS
)
 
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

    # xaxis, need lower limitation or not, limitation value
    html.H2('Step 2. Choose the xaxis and yaxis.'),
    html.Div([
        dcc.Dropdown(
            id='xaxis-column',
            # options=options,
            value='',
            # value='ENGINE KM'
            placeholder='Select a feature as xaxis...'
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
                id='min-lim-value',
                placeholder='Enter a value...',
                type='text',
                value=''
		),
        ],
            style={'border': '2px dashed #999', 'borderRadius': '5px', 
                    'padding': '10px', 'margin': '5px 5px'}
        )
    ],
    style={'width': '48%', 'display': 'inline-block'}),

    # yaxis, need upper limitation or not, limitation value
    html.Div([
        dcc.Dropdown(
            id='yaxis-column',
            # options=options,
            value='',
            # value='Iron ppm FE',
            placeholder='Select features as yaxis...',
            multi=True
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
                id='max-lim-value',
                placeholder='Enter a value...',
                type='text',
                value=''
		    )],
            style={
                'border': '2px dashed #999', 'borderRadius': '5px', 
                'padding': '10px', 'margin': '5px 5px'}),
            ],
    style={'width': '48%', 'display': 'inline-block'}),
    html.Div(id='output-data-upload'),
])


# get useful data from dataset
def parse_contents(contents, xName, minLim, minLimVal, yNames, maxLim, maxLimVal, filename, states):
    content_type, content_string = contents.split(',')
    decoded = base64.b64decode(content_string)
    try:
        if 'csv' in filename:
            # Assume that the user uploaded a CSV file
            df = pd.read_csv(
                io.StringIO(decoded.decode('utf-8')))
        elif 'xls' in filename:
            # Assume that the user uploaded an excel file
            df = pd.read_excel(io.BytesIO(decoded))
    except Exception as e:
        print(e)
        return html.Div([
            'There was an error processing this file.'
        ])

    # df_required = df.loc[:, nameList]
    traces = []
    # print(yNames)
    # print(df.columns)
    for i in yNames:
    	traces.append(go.Scatter(
    							x=df.loc[:, xName],
    							y=df.loc[:, i],
    							mode='markers',
    							marker={'size': 12, 'opacity': 0.5,
    									'line': {'width': 0.5, 'color': 'white'}},
    							name=i,
    		))

    # 根据 minLim等的情况，决定是否加线
    # plt.vlines(0, 0, 0.5, colors = "c", linestyles = "dashed")
    # plotly 里面加线：https://plot.ly/python/shapes/
    if (minLim == 'No Need') & (maxLim == 'No Need'):
    	    layout = go.Layout(xaxis={'title': xName},
    					margin={'l': 40, 'r':20, 't':20, 'b':30},
    					hovermode='closest')
    if (minLim != 'No Need') & (maxLim == 'No Need'):
            layout = go.Layout(xaxis={'title': xName},
    					margin={'l': 40, 'r':20, 't':20, 'b':30},
    					hovermode='closest',
                        shapes=[
                            {'type': 'line', 'x0': min(df[xName])*0.9, 'y0': minLimVal, 
                            'x1': max(df[xName])*1.1, 'y1': minLimVal,
                            'line': {'color': 'rgb(240, 48, 48)', 'width':2, 'dash': 'dashdot'}}
                        ])
    if (minLim == 'No Need') & (maxLim != 'No Need'):
            layout = go.Layout(xaxis={'title': xName},
    					margin={'l': 40, 'r':20, 't':20, 'b':30},
    					hovermode='closest',
                        shapes=[
                            {'type': 'line', 'x0': min(df[xName])*0.9, 'y0': maxLimVal, 
                            'x1': max(df[xName])*1.1, 'y1': maxLimVal,
                            'line': {'color': 'rgb(240, 48, 48)', 'width':2, 'dash': 'dashdot'}}
                        ])
    if (minLim != 'No Need') & (maxLim != 'No Need'):
            layout = go.Layout(xaxis={'title': xName},
    					margin={'l': 40, 'r':20, 't':20, 'b':30},
    					hovermode='closest',
                        shapes=[
                            {'type': 'line', 'x0': min(df[xName])*0.9, 'y0': maxLimVal, 
                            'x1': max(df[xName])*1.1, 'y1': maxLimVal,
                            'line': {'color': 'rgb(240, 48, 48)', 'width':2, 'dash': 'dashdot'}},
                            {'type': 'line', 'x0': min(df[xName])*0.9, 'y0': minLimVal, 
                            'x1': max(df[xName])*1.1, 'y1': minLimVal,
                            'line': {'color': 'rgb(240, 48, 48)', 'width':2, 'dash': 'dashdot'}
                            }
                        ])

    return html.Div([
        html.H5('Filename: {}'.format(filename)),
        html.H5('Last modified: {}'.format(str(datetime.datetime.fromtimestamp(states))[:-7])),
	    dcc.Graph(
	    	figure={
	         'data': traces,
	         'layout': layout,}
	    	)
    ])

@app.callback(Output('output-data-upload', 'children'),
			 [Input('upload-data', 'contents'),
			  Input('xaxis-column', 'value'),
			  Input('min-limit-value', 'value'),
			  Input('min-lim-value', 'value'),
			  Input('yaxis-column', 'value'),
			  Input('upper-limit-value', 'value'),
			  Input('max-lim-value', 'value')],
			 [State('upload-data', 'filename'),
			  State('upload-data', 'last_modified')])
def update_output(contents, xName, minLim, minLimVal, yNames, maxLim, maxLimVal, filename, states):
	if contents is not None:
		children = parse_contents(contents, xName, minLim, minLimVal, yNames, maxLim, maxLimVal, filename, states)
		return children


@app.callback(Output('xaxis-column', 'options'),
			  [Input('upload-data', 'contents')],
			  [State('upload-data', 'filename'),])
def get_available_indicators(contents, filename):
    if contents is not None:
        content_type, content_string = contents.split(',')
        decoded = base64.b64decode(content_string)
        try:
            if 'csv' in filename:
                # Assume that the user uploaded a CSV file
                df = pd.read_csv(
                    io.StringIO(decoded.decode('utf-8')))
            elif 'xls' in filename:
                # Assume that the user uploaded an excel file
                df = pd.read_excel(io.BytesIO(decoded))
        except Exception as e:
            print(e)
            return html.Div([
                'There was an error processing this file.'
            ])
        available_indicators = list(df.columns)
        options=[{'label': i, 'value': i} for i in available_indicators]
        return options
    else:
        return ''

@app.callback(Output('yaxis-column', 'options'),
			  [Input('upload-data', 'contents')],
			  [State('upload-data', 'filename')])
def get_available_indicators1(contents, filename):
    if contents is not None:
        content_type, content_string = contents.split(',')
        decoded = base64.b64decode(content_string)
        try:
            if 'csv' in filename:
                # Assume that the user uploaded a CSV file
                df = pd.read_csv(
                    io.StringIO(decoded.decode('utf-8')))
            elif 'xls' in filename:
                # Assume that the user uploaded an excel file
                df = pd.read_excel(io.BytesIO(decoded))
        except Exception as e:
            print(e)
            return html.Div([
                'There was an error processing this file.'
            ])
        available_indicators = list(df.columns)
        options=[{'label': i, 'value': i} for i in available_indicators]
        return options
    else:
        return ''

if __name__ == '__main__':
    app.run_server(debug=True)