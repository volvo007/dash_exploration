import json, time, datetime
import base64, os, io, re

import numpy as np
import pandas as pd
import plotly.graph_objs as go

# marker - symbol
MARKERS = [str(i) for i in range(45)] + ['1{:02d}'.format(j) for j in range(25)] + \
            ['2{:02d}'.format(k) for k in range(25)] + ['1{:02d}'.format(k) for k in range(25, 45)]

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

def get_uesful(df, level1, level1_value, level2, level2_value, 
                    level3, level3_value, marker_symbol):
    if level1 != '':
        if 'all' in level1_value:
            df_lv1 = df
        else:
            df_lv1 = df[df[level1].isin(level1_value)]
        if 'all' in level2_value:
            df_lv2 = df_lv1
        else:
            df_lv2 = df_lv1[df_lv1[level2].isin(level2_value)]
        df_final = df_lv2.copy()   
        if level3 != '':
            marker_dict = get_symbol_dict(df, level3, level3_value, marker_symbol)
            df_final['symbol'] = df_final[level3].apply(lambda x: marker_dict[x])
        else:
            df_final['symbol'] = '0'
        return df_final
    else:
        return None

def get_symbol_dict(df, level3, level3_value, marker_list):
    filter3_length = len(df[level3].unique())
    if filter3_length <= len(marker_list):
        return {i:j for i,j in zip(df[level3].unique(), marker_list[:filter3_length])}
    else:
        return 'Too much classes. Error.'

def generate_scatter(df, xName, yName, level1, level1_value, level2, level2_value, 
                    level3, level3_value):
    

# 一般 lv2name 是设备名；lv3name 是油品名
def go_scatter(x, y, marker_mode, symbol, lv2name, lv3name):
    if marker_mode == 'markers':
        marker = {'size': 10, 'opacity': 0.65, 'symbol': symbol,
                  'line': {'width': 0.5, 'color': 'white'}}
    else:
        marker = {'size': 7, 'opacity': 0.65, 'symbol': symbol}
    return go.Scatter(x=x, y=y, mode=marker_mode, marker=marker, 
                      opacity=0.7, name=lv2name, hovertext=[lv2name,lv3name])