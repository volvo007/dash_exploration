import json, time, datetime
import base64, os, io, re

import numpy as np
import pandas as pd
import plotly.graph_objs as go

# marker - symbol
MARKERS1 = [i for i in range(45)] + [int('1{:02d}'.format(j)) for j in range(25)]
MARKERS2 = [int('2{:02d}'.format(k)) for k in range(25)] + [int('1{:02d}'.format(k)) for k in range(25, 45)]

MARKERS = MARKERS1 + MARKERS2

# 初步清理，去除数字列内非数字
def cleanup(df):
    if "OIL KM's" in df.columns:
        df["OIL KM's"] = pd.to_numeric(df["OIL KM's"], errors='coerce')
        if "KV @ 100 D445" in df.columns:
            df["KV @ 100 D445"] = pd.to_numeric(df["KV @ 100 D445"], errors='coerce')
        df = df[~df["OIL KM's"].isnull()]
        df.dropna(how='all', inplace=True)
        df.replace('<(.*)', r'\1', regex=True, inplace=True)
    else:
        df.dropna(how='all', inplace=True)
        df.replace('<(.*)', r'\1', regex=True, inplace=True)
    return df

def get_symbol_dict(df, level3, level3_value, marker_symbol):
    if 'all' in level3_value:
        level3_value = list(df[level3].unique())
    filter3_length = len(level3_value)
    if filter3_length > len(marker_symbol):
        new_markers = marker_symbol * 3
    return {i:j for i,j in zip(level3_value, marker_symbol[:filter3_length])}

def get_uesful(df, level1, level1_value, level2, level2_value, 
                    level3, level3_value, marker_symbol):
    if level1 != '':
        if 'all' in level1_value:
            df_lv1 = df
        else:
            df_lv1 = df[df[level1].isin(level1_value)]
            
        if level2 != '':
            if 'all' in level2_value:
                df_lv2 = df_lv1
            else:
                df_lv2 = df_lv1[df_lv1[level2].isin(level2_value)]
                
            df_final = df_lv2.copy() 
            # print(level2_value)
            if level3 != '':
                if 'all' in level3_value:
                    marker_dict = get_symbol_dict(df, level3, level3_value, marker_symbol)
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
            df_lv1['symbol'] = 0
            return get_dfs(df_lv1, [level1])
    else:
        df = df.copy()
        df['symbol'] = 0
        return df

def get_dfs(df, group_condition):
    dfs = []
    for name, group in df.groupby(group_condition):
        dfs.append((name, group))
    return dfs

def one_scatter(df, xName, yName, marker_mode, symbol, name, hovertext):
    x = df.loc[:, xName]
    y = df.loc[:, yName]
    if marker_mode == 'markers':
        marker = {'size': 10, 'opacity': 0.65, 'symbol': symbol,
                  'line': {'width': 0.5, 'color': 'white'}}
    else:
        marker = {'size': 7, 'opacity': 0.65, 'symbol': symbol}
    return go.Scatter(x=x, y=y, mode=marker_mode, marker=marker, hoverinfo='x+y+text', 
                      opacity=0.7, name=name, hovertext=hovertext)
    

def generate_scatter(dfs, xName, yName, marker_mode):
    traces = []
    # 如果什么都没选，返回一个df
    if type(dfs) != type([]):
        traces.append(one_scatter(dfs, xName, yName, marker_mode, 0, '', ''))
        return traces
    # 第一过滤有内容，返回df 组成的 list
    else:
        # 通过查询第一分组的过滤器长度，决定 lengacy 与 hover 名称
        if len(dfs[0][0]) == 1:
            name_index = 0
        if len(dfs[0][0]) == 2:
            name_index = 1
        if len(dfs[0][0]) == 3:
            name_index = 1
            
        for group in dfs:
            df_temp = group[1]
            marker_mode = marker_mode
            symbol = df_temp['symbol'].iloc[0]
            name = group[0][name_index]
            hovertext = [' '.join([i for i in group[0]])] * len(group[1])
            # print(hovertext)
            traces.append(one_scatter(df_temp, xName, yName,  marker_mode, 
                                      symbol, name, hovertext))
        return traces