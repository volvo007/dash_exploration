import json, time, datetime
import base64, os, io, re

import numpy as np
import pandas as pd
import plotly.graph_objs as go

def cleanup(df):
    if "OIL KM's" in df.columns:
        df["OIL KM's"] = pd.to_numeric(df["OIL KM's"], errors='coerce')
        df = df[~df["OIL KM's"].isnull()]
        df.dropna(how='all', inplace=True)
    else:
        df.dropna(how='all', inplace=True)
    return df