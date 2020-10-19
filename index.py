import json
# import pandas as pd
# import plotly.graph_objs as go
from flask import Flask

import dash
import dash_core_components as dcc
import dash_html_components as html
import dash_auth
import dash_table

# external_stylesheets = ['https://cdn.jsdelivr.net/npm/bootstrap@3.3.7/dist/css/bootstrap.min.css']
external_stylesheets = ['https://unpkg.com/spectre.css/dist/spectre.min.css']
server = Flask(__name__)
app = dash.Dash(__name__, server=server,
                # url_base_pathname='/stdhd/',
                # requests_pathname_prefix='/stdcheck/',
                external_stylesheets=external_stylesheets)
# auth = dash_auth.BasicAuth(
#     app,
#     VALID_USERNAME_PASSWORD_PAIRS
# )

app.layout = html.Div([
    html.H2('Welcome to DUSKASH'),
    html.H6('This site provides toolkits to plot charts. You only need to upload specific format excel/csv. And you will get 2d/3d chart after several mouse clicking.'),
    html.Div([
        html.Table([
            html.Tr([
                html.Th('Tools'),
                html.Th('Description'),
                html.Th('Version')]
            ),
            html.Tr([   # row of s2d
                html.Td(
                    html.A('S2d', href='/s2d/'),
                ),
                html.Td('After upload the dataset, it returns a 2d scatter chart. No classification fuction, but you can plot multiple features on the screen'
                ),
                html.Td(
                    '1.2'
                )], className='active'
            ),
            html.Tr([   # row of m2d
                html.Td(
                    html.A('M2d', href='/m2d/'),
                ),
                html.Td('After upload the dataset, it returns a 2d scatter chart. Provide classification fuction, and different classes will be plotted by using differnt colors or markers'
                ),
                html.Td(
                    '2.0'
                )], className='active'
            ),
            html.Tr([   # row of s3d
                html.Td(
                    html.A('S3d', href='/s3d/'),
                ),
                html.Td('After upload the dataset, it returns a 3d scatter chart. Provice simple classification fuction based on the final parameter.'
                ),
                html.Td(
                    '1.0'
                )], className='active'
            ),
            html.Tr([   # row of stdhd
                html.Td(
                    html.A('STDHD', href='/stdhd/'),
                ),
                html.Td(
                    'A simple tool for HD standard checking'
                ),
                html.Td(
                    '1.0'
                )], className='active'
            )
        ], className='table table-striped table-hover'),
    ], className='container'),
    # dcc.Markdown('''
    # Tools | Description | Screenshot | Version
    # ---|---|---|---
    # [S2d](www.duskash.com/s2d/) |  | ![s2d_pic](/static/s2d.jpg "snap of s2d"){:width="300px"} | 1.2
    # [M2d](www.duskash.com/m2d/) |  | ![s3d_pic](/static/s3d.jpg "snap of m2d" =300x) | 2.0
    # [S3d](www.duskash.com/s3d/) |  | ![s3d_pic](/static/s3d.jpg "snap of s3d" =300x) | 1.0
    # [StdHD](www.duskash.com/stdhd/) |  | ![stdhd_pic](/static/stdhd.jpg "snap of stdhd" =300x) | 1.2
    # '''),
    # registration according to China Internet Policy
    html.Div([html.A('沪ICP备19043992号-1', href='http://beian.miit.gov.cn',
                        style={'font-size': 11, 'color': '#101010'}),
              html.P('      ',
                        style={'display': 'inline-block'}),
              html.A('沪公网备: 100012127306', href='http://www.zx110.org/picp?sn=:100012127306',
                        style={'display': 'inline-block', 'font-size': 11, 'color': '#101010'}),
              ], style={'textAlign': 'right', 'white-space': 'pre', 
                        'width': '95%', 'position': 'absolute', 'bottom': 0}
    ),
], style={'margin': '40px'})

if __name__ == '__main__':
    app.run_server(debug=True)
