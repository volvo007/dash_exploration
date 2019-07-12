import json, time, datetime
import base64, os, io, re

import numpy as np
import pandas as pd
import plotly.graph_objs as go

# 初步清理，去除数字列内非数字
def cleanup(df):
    if "OIL KM's" in df.columns:
        df["OIL KM's"] = pd.to_numeric(df["OIL KM's"], errors='coerce')
        df["KV @ 100 D445"] = pd.to_numeric(df[""], errors='coerce')
        df = df[~df["OIL KM's"].isnull()]
        df.dropna(how='all', inplace=True)
        df.replace('<(.*)', r'\1', regex=True, inplace=True)
    else:
        df.dropna(how='all', inplace=True)
        df.replace('<(.*)', r'\1', regex=True, inplace=True)
    return df

def generate_chart(spec_df, mode_name, class_name):
    return go.Scatter()

def chart_mode(chart_mode: str):
    if chart_mode == 'Markers':
        return 'markers'
    elif chart_mode == 'Lines':
        return 'lines'
    else:
        return 'lines+markers'