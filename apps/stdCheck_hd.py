import json
import pandas as pd
import plotly.graph_objs as go
import flask

import dash
import dash_core_components as dcc
import dash_html_components as html
import dash_auth
import dash_table
from dash.dependencies import Input, Output
from dash.exceptions import PreventUpdate

VALID_USERNAME_PASSWORD_PAIRS = {
    'Jason': 'shell'
}

external_stylesheets = ['https://cdn.jsdelivr.net/npm/bootstrap@3.3.7/dist/css/bootstrap.min.css']
server = flask.Flask(__name__)
app = dash.Dash(__name__,
                server=server,
                url_base_pathname='/stdhd/',
                # requests_pathname_prefix='/stdcheck/',
                external_stylesheets=external_stylesheets)
auth = dash_auth.BasicAuth(
    app,
    VALID_USERNAME_PASSWORD_PAIRS
)

with open('../static/stds/standards_hd.json', encoding='utf-8') as f:
    content = json.load(f)

columnList = list(content.keys())
# print(columnList)
testName = [i for i in list(content['Bench'].keys())]

stdDict = {
    # 注意测试的名字，可能含有空格
    'API': ['API FA-4 ', 'API CK-4', 'API CJ-4', 'API CI-4', 'API CH-4', 'API SL'],
    'ACEA': ['ACEA E9', 'ACEA E7', 'ACEA E6', 'ACEA E4'],
    'JASO': ['JASO DH-2', 'JASO DH-1'],
    'CUMMINS CES': ['CES 20086', 'CES 20081', 'CES 20078', 'CES 20077', 'CES 20076'],
    'CATERPILLAR ECF': ['Cat ECF-3', 'Cat ECF-2', 'Cat ECF-1-A'],
    'MB': ['MB 228.51', 'MB 228.31', 'MB 228.5', 'MB 228.3'],
    'VOLVO/MACK/RENAULT': ['Volvo VDS-4.5', 'Volvo VDS-4', 'Volvo VDS-3'],
    'MACK EO-M+': ["MACK EOS-4.5", "MACK EO-O PP", "MACK EO-N"],
    'MAN': ['M3777', 'M3677', 'M3575', 'M3477', 'M3377', 'M3275-1 (FILE only)'],
    'MTU': ['MTU Cat 3.1', 'MTU Cat 2.1', 'MTU Cat 3', 'MTU Cat 2'],
    'DEUTZ': ['DQC II-18', 'DQC III-18', 'DQC III-18 LA', 'DQC IV-18', 'DQC IV-18 LA', 'DQC III-18'],
    'DFS': ['93K222', '93K218', '93K215']
}
style_cell_condi = [
                    {'if': {'column_id': c},
                    'maxWidth': '100px',
                    # 'whiteSpace': 'normal',
                    'height': 'auto',
                    'overflow': 'hidden',
                    'dataOverfolow': 'ellipsis'} for c in columnList[:3]
] + [
        {'if': {'column_id': 'Bench',
        'filter_query': '{{{}}} eq "{}"'.format('Bench', n)},
        'fontWeight': 'bold',
        'backgroundColor': '#66CCFF',
        'textAlign': 'center',
        'height': 'auto',
        'margin': '5px',
        'fontSize': 16} for n in testName
] + [
        {'if': {'column_id': c,'filter_query': '{{{}}} ne ""'.format(c)},
        'backgroundColor': '#FFFACD', 'fontWeight': 'bold'
        } for c in columnList[3:]
] 

app.layout = html.Div([
    html.H2('Lite page for HDDEO bench checking'),
    html.Div([
        html.Div([
            html.H4('Choose standard group firstly,\n and then choose specific standards.'),
            html.Hr(),
            html.P('Select group here:'),
            dcc.Dropdown(
                id='stdFather',
                options=[{'label': k, 'value': k} for k in stdDict.keys()],
                multi=True,
                placeholder='Select basic ones...'
            ),
            html.P('Select standard(s) here:'),
            dcc.Dropdown(
                id='stdSon',
                multi=True,
                placeholder='Select subs ones...'
            )
        ], className='col-md-3'),
        html.Div([
            html.H4('If no standard is selected, it shows only bench tests name defaultly.'),
            dash_table.DataTable(
                id = 'std_table',
                # columns = [{'id':h, 'name':h} for h in df.columns],
                # data = df.to_dict('records'),
                # fixed_rows={'headers': True, 'data': 0},
                # cell means whole table, header just work for header, data for data rows
                style_cell={'minWidth': '5px', 'maxWidth': '120px', 
                            'overflow': 'hidden', 'margin': '2px 5px 5px',
                            'textOverflow': 'ellipsis', 'padding': '0.5em',
                            'minHeight': '10px', 'height': 'auto', 'textAlign': 'center'},
                style_data_conditional=style_cell_condi,
                style_header={'fontWeight': 'bold',
                            'textAlign': 'center',
                            'fontSize': 20},
                style_table={'height': '900px',
                            'width': '95%',
                            'overflowY': 'scroll',
                            'overflowX': 'scroll',
                            'border': 'thin lightgrey solid'},
            )
        ], className='col-md-9')
    ], className='row')
], style={'margin': '10px 20px 20px'})

@app.callback(
    Output('stdSon', 'options'),
    [Input('stdFather', 'value')]
)
def set_son_options(selected_father):
    if selected_father is None:
        raise PreventUpdate
    else:
        sonOptions = []
        for i in selected_father:
            # stdDict is a global varible
            for tempOption in stdDict[i]:
                sonOptions.append(tempOption)
        return [{'label': i, 'value': i} for i in sonOptions]

# @@app.callback(
#     [Output('std_table', 'data'),
#      Output('std_table', 'columns')],
#     [Input('stdSon', 'value')]
# )
# def gen_df(selected_son):
#     if selected_son is None:
#         data = deal_json(columnList[:3])
#     else:
#         data = deal_json(columnList[:3] + list(selected_son))
#     columns = [{'id':h, 'name':h} for h in data.columns]
#     return data.to_dict('records'), columns

# def deal_json(nameList):
#     raw_data = {}
#     for id, name in enumerate(nameList):
#         if id == 0:
#             temp = [list(i.keys()) + list(i.values())[0] for i in content[0][name]]
#         else:
#             temp = [[''] + list(i.values())[0] for i in content[0][name]]
#         raw_data[name] = [i for k in temp for i in k]
#     return pd.DataFrame(raw_data)

@app.callback(
    [Output('std_table', 'data'),
     Output('std_table', 'columns')],
    [Input('stdSon', 'value')]
)
def gen_df(selected_son):
    if not selected_son:
        data = deal_json(columnList[:3])
        # print(columnList[:3])
        # print(len(data))
    else:
        data = deal_json(columnList[:3] + list(selected_son))
    columns = [{'id':h, 'name':h} for h in data.columns]
    return data.to_dict('records'), columns

def deal_json(nameList):
    raw_data = {}
    if len(nameList) <= 3:
        for id, name in enumerate(nameList):
            if id == 0:
                temp = [[i] + content[name][i] for i in sorted(list(content[name].keys()))]
            else:
                temp = [[''] + content[name][i] for i in sorted(list(content[name].keys()))]
            raw_data[name] = [i for k in temp for i in k]
    else:
        testSet = set()
        for name in nameList[3:]:   # 更新存在的测试列表
            # print(content[name])
            # 遍历该标准的所有测试名，如果测试名下的测试项目全为空，则不会添加到要显示的测试中
            # content 为大字典，name 为每一个标准下属的字典，i 为每个小测试的名字
            valid_list = []
            for i in content[name].keys():
                # print(content[name][i])
                if any(content[name][i]):
                    valid_list.append(i)
            # print(valid_list)
            testSet.update(valid_list)
        for id, name in enumerate(nameList):
            if id == 0:
                temp = [[i] + content[name][i] for i in sorted(list(testSet))]
            else:
                temp = []
                for subName in sorted(list(testSet)):
                    # print(subName)
                    if subName in content[name].keys():
                        temp.append([''] + content[name][subName])
                    else:
                        temp.append([''] * (len(content['Bench Data'][subName]) + 1))
            raw_data[name] = [i for k in temp for i in k]
        # print(testSet)
    return pd.DataFrame(raw_data)

def getDict(nameList):
    raw_data = {}
    for id, name in enumerate(nameList):
        if id == 0:
            temp = [list(i.keys()) + list(i.values())[0] for i in content[0][name]]
        else:
            temp = [[''] + list(i.values())[0] for i in content[0][name]]
        raw_data[name] = [i for k in temp for i in k]
    return pd.DataFrame(raw_data)

if __name__ == '__main__':
    # app.run_server(debug=False)
    app.run_server(debug=True, port=8150)
