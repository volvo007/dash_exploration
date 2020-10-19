import pandas as pd
import plotly.offline as py
import plotly.graph_objs as go
from functools import reduce
import base64

MARKERS = [str(i) for i in range(45)] + ['1{:02d}'.format(j) for j in range(25)] + \
            ['2{:02d}'.format(k) for k in range(25)] + ['1{:02d}'.format(k) for k in range(25, 45)]
MARKERS = [int(i) for i in MARKERS]

COLORS = ['#DD1D21', '#FBCE07', '#008443', '#003C88', '#641964', '#EB8705', '#595959', '#ED7578', '#1F82FF', '#1CFF8F',
          '#FCB860', '#FDE26A', '#6D6D6D', '#F3A3A5', '#FDEB9C', '#69ABFF', '#68FFB5', '#FDD095', '#A3A3A3', '#009E9E']

def get_symbol_dict(df, level3, level3_value, marker_symbol):
    if 'all' in level3_value:
        level3_value = list(df[level3].unique())
    filter3_length = len(level3_value)
    while filter3_length > len(marker_symbol):
        marker_symbol = marker_symbol * 3
    return {i:j for i,j in zip(level3_value, marker_symbol[:filter3_length])}

def get_color_dict(df, level2, color_cand):
    if level2:
        names = list(df[level2].unique())
        while len(names) > len(color_cand):
            color_cand = color_cand * 2
        color_dict = {i: j for i,j in zip(names, color_cand)}
        return color_dict
    else:
        return None

def get_useful(df, level1, level1_value, level2, level2_value,
                    level3, level3_value, marker_symbol):
    if bool(level1):
        if 'all' in level1_value:
            df_lv1 = df
        else:
            df_lv1 = df[df[level1].isin(level1_value)]

        if bool(level2):
            if 'all' in level2_value:
                df_lv2 = df_lv1
            else:
                df_lv2 = df_lv1[df_lv1[level2].isin(level2_value)]

            df_final = df_lv2.copy()
            # print(level2_value)
            if bool(level3):
                if 'all' in level3_value:
                    
                    marker_dict = get_symbol_dict(df, level3, level3_value, marker_symbol)
                    # print(marker_dict)
                    df_final['symbol'] = df_final[level3].apply(lambda x: marker_dict[x])
                    df_final.sort_values([level1, level2, level3])
                    # print(level3_value)
                    return get_dfs(df_final, [level1, level2, level3])
                else:
                    df_final = df_final[df_final[level3].isin(level3_value)]
                    marker_dict = get_symbol_dict(df, level3, level3_value, marker_symbol)
                    df_final['symbol'] = df_final[level3].apply(lambda x: marker_dict[x])
                    df_final.sort_values([level1, level2, level3])
                    return get_dfs(df_final, [level1, level2, level3])
            else:
                df_final['symbol'] = 0
                df_final.sort_values([level1, level2])
                return get_dfs(df_final, [level1, level2])
        else:
            df_lv1.sort_values([level1])
            df_final = df_lv1.copy()
            df_final['symbol'] = 0
            return get_dfs(df_final, [level1])
    else:
        df = df.copy()
        df['symbol'] = 0
        return df

def get_dfs(df, group_condition):
    dfs = []
    for name, group in df.groupby(group_condition):
        dfs.append((name, group))
    return dfs

def one_scatter(df, xName, yName, marker_mode, symbol, name, hovertext, color):
    x = df.loc[:, xName]
    y = df.loc[:, yName]
    if color:
        if marker_mode == 'markers':
            marker = {'size': 10, 'opacity': 0.85, 'symbol': symbol, 'color': color,
                    'line': {'width': 0.5, 'color': 'white'}}
        else:
            marker = {'size': 7, 'opacity': 0.85, 'symbol': symbol, 'color': color}
        return go.Scattergl(x=x, y=y, mode=marker_mode, marker=marker, hoverinfo='x+y+text',
                        opacity=0.7, name=name, hovertext=hovertext)
    else:
        if marker_mode == 'markers':
            marker = {'size': 10, 'opacity': 0.85, 'symbol': symbol,
                    'line': {'width': 0.5, 'color': 'white'}}
        else:
            marker = {'size': 7, 'opacity': 0.85, 'symbol': symbol}
        return go.Scattergl(x=x, y=y, mode=marker_mode, marker=marker, hoverinfo='x+y+text',
                        opacity=0.7, name=name, hovertext=hovertext)

def generate_scatter(dfs, xName, yName, marker_mode, colormap):
    traces = []
    # 如果什么都没选，返回一个df
    if type(dfs) != type([]):
        traces.append(one_scatter(dfs, xName, yName, marker_mode, 0, '', '', colormap))
        return traces
    # 第一过滤有内容，返回df 组成的 list
    else:
        # 通过查询第一分组的过滤器长度，决定 lengacy 与 hover 名称
        # if len(dfs[0][0]) == 1:
        #     name_index = 0
        # if len(dfs[0][0]) == 2:
        #     name_index = 1
        # if len(dfs[0][0]) == 3:
        #     name_index = 2

        for group in dfs:
            df_temp = group[1]
            marker_mode = marker_mode
            symbol = df_temp['symbol'].iloc[0]
            # name = group[0][name_index]
            name = ' '.join([str(x) for x in group[0]])
            # 若分组长度大于等于2，说明有第二分类
            # 此时可以通过第二分类找到对应颜色
            if (len(group) >= 2) and (bool(colormap)):
                color = colormap[group[0][1]]
            else:
                color = None
            # 每个点的标记
            hovertext = [' '.join([str(i) for i in group[0]])] * len(group[1])
            # print(hovertext)
            traces.append(one_scatter(df_temp, xName, yName,  marker_mode,
                                      symbol, name, hovertext, color))
        return traces

# def marker_adjust(marker_mode):
#     if marker_mode == 'markers':
#             marker = {'size': 10, 'opacity': 0.65, 'line': {'width': 0.5, 'color': 'white'}}
#     else:
#         marker = {'size': 7, 'opacity': 0.65}
#     return marker

def layout_adjust(df, minLim, maxLim, minLimVal, maxLimVal, xName, yAxisName, chartTitle):
    if (minLim == 'No Need') & (maxLim == 'No Need'):
        shapes = None
    if (minLim != 'No Need') & (maxLim == 'No Need'):
        shapes=[
            {'type': 'line', 'x0': min(df[xName])*0.9, 'y0': minLimVal,
            'x1': max(df[xName]), 'y1': minLimVal,
            'line': {'color': 'rgb(240, 48, 48)', 'width':2, 'dash': 'dashdot'}}
        ]
    if (minLim == 'No Need') & (maxLim != 'No Need'):
        shapes=[
            {'type': 'line', 'x0': min(df[xName])*0.9, 'y0': maxLimVal,
            'x1': max(df[xName]), 'y1': maxLimVal,
            'line': {'color': 'rgb(240, 48, 48)', 'width':2, 'dash': 'dashdot'}}
        ]
    if (minLim != 'No Need') & (maxLim != 'No Need'):
        shapes=[
            {'type': 'line', 'x0': min(df[xName])*0.9, 'y0': maxLimVal,
            'x1': max(df[xName]), 'y1': maxLimVal,
            'line': {'color': 'rgb(240, 48, 48)', 'width':2, 'dash': 'dashdot'}},
            {'type': 'line', 'x0': min(df[xName])*0.9, 'y0': minLimVal,
            'x1': max(df[xName]), 'y1': minLimVal,
            'line': {'color': 'rgb(240, 48, 48)', 'width':2, 'dash': 'dashdot'}}
        ]

    layout = go.Layout(xaxis={'title': xName}, yaxis={'title': yAxisName},
                title=dict(text=chartTitle, font={'size': 20}),
                margin={'l': 50, 'r':20, 't':30, 'b':90}, orientation=45,
                legend={'x': 0.95, 'y': 0.95, 'bgcolor': 'rgba(250, 243, 205, 0.3)'}, hovermode='closest', shapes=shapes)
    return layout