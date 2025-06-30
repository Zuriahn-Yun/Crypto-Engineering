import extract
from datetime import datetime
import collections
import matplotlib as pyplot
import numpy
import pandas as pd
import mplfinance as mpf
"""
This exists as a test script file to test backend functions and make sure things are working as expected
"""

coin_df,heiken_df = extract.coin_data("bitcoin")
coin_df['timestamp'] = coin_df['timestamp'].apply(extract.convert_miliseconds_datetime)
heiken_df['timestamp'] = heiken_df['timestamp'].apply(extract.convert_miliseconds_datetime)

from plotly.subplots import make_subplots
import plotly.graph_objects as go

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

fig.update_layout(title=dict(text="Bitcoin Stock Data From the last Day"))

fig.show()

