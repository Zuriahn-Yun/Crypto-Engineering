import extract
from datetime import datetime
import collections
import matplotlib as pyplot
import numpy
import pandas as pd
import mplfinance as mpf
from extract import coin_data
import os
from plotly.subplots import make_subplots
import plotly.graph_objects as go
import requests

"""
This exists as a test script file to test backend functions and make sure things are working as expected
"""

coin_id = "solana"

def get_name(coin_id):
    url = f"https://api.coingecko.com/api/v3/coins/{coin_id}"
    key = os.getenv("COINGECKO_API_KEY")
    params = {
        "x_cg_demo_api": key
    }
    response = requests.get(url,params=params)
    res = response.json()
    name = res["name"]
    return str(name)

name = get_name(coin_id=coin_id)
print(name)

coin_df,heiken_df = extract.coin_data(coin_id=coin_id)
coin_df['timestamp'] = coin_df['timestamp'].apply(extract.convert_miliseconds_datetime)
heiken_df['timestamp'] = heiken_df['timestamp'].apply(extract.convert_miliseconds_datetime)

fig = make_subplots(rows=1, cols=1, subplot_titles=("Candles", "Heiken Ashi Candles"))

fig.add_trace(go.Candlestick(x=coin_df['timestamp'],
                open=coin_df['open'],
                high=coin_df['high'],
                low=coin_df['low'],
                close=coin_df['close'],name="Traditional Candles"))

fig.add_trace(go.Candlestick(x=heiken_df['timestamp'],
                open=heiken_df['ha_open'],
                high=heiken_df['ha_high'],
                low=heiken_df['ha_low'],
                close=heiken_df['ha_close'],name="Heiken Ashi Candles"))
print(name)
fig.update_layout(title=dict(text=name + " Stock Data From the past 24 Hours, Candles every 15 Minutes"))

fig.write_html("graph.html",include_plotlyjs='cdn', full_html=True)
