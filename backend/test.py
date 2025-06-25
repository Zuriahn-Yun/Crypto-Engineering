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

# This has bitcoin data fro the last 10 days 
df_plot = extract.bitcoin_ten_days

# Add datetime and set it as index
df_plot["datetime"] = pd.to_datetime(df_plot["timestamp"], unit="ms")
df_plot.set_index("datetime", inplace=True)

# Keep only the needed columns in correct order
df_plot = df_plot[["open", "high", "low", "close", "volume"]]

# 15 minute intevals only works if you look at the last 24H, otherwise we only have hourly data 
mpf.plot(df_plot,type="candle",volume = True,style="yahoo")