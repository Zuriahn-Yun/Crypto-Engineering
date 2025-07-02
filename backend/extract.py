import os
import requests
from datetime import datetime
import pandas as pd

"""
This script will have functions to extract coin data from any coing
https://docs.coingecko.com/reference/coins-list
^ This is the coin list 
"""

def request_coin(coin_id,days):
    """
    coin_id - is the coin we want data for as a stirng
    days - the past x many days we want data for
        IF days is 1 it does it per minute data
        If days is 7-30 it does it hourly, we might want to try 1
    Output
        A json file with a prices dictionary
        response["prices"][0] = [num1,num2]
        num1 is a timestap in milliseconds since Jan1,1970
        num2 is a prices in USD, can be set to another currency below
        
        market_caps dictionary - this is total value of the coin in circulation
        total_volumes dictionary - this is the total dollar value of the coin being traded in 24 hours
    """

    url = f"https://api.coingecko.com/api/v3/coins/{coin_id}/market_chart"
    key = os.getenv("COINGECKO_API_KEY")
    params = {
        "vs_currency": "usd",
        "id": coin_id,
        "days": days,
        "x_cg_demo_api": key
    }
    response = requests.get(url,params=params)
    res = response.json()
    # Create base price DataFrame
    df_price = pd.DataFrame(res["prices"], columns=["timestamp", "price"])
    df_price["datetime"] = pd.to_datetime(df_price["timestamp"], unit="ms")

    # Determine resample interval
    interval = "15T" if params["days"] == 1 else "1h"

    # Use datetime for indexing temporarily to resample
    df_price.set_index("datetime", inplace=True)

    # Calculate OHLC
    df_ohlc = df_price["price"].resample(interval).ohlc()

    # Reset index to get datetime column back
    df_ohlc = df_ohlc.reset_index()

    # Volume
    df_vol = pd.DataFrame(res["total_volumes"], columns=["timestamp", "volume"])
    df_vol["datetime"] = pd.to_datetime(df_vol["timestamp"], unit="ms")
    df_vol.set_index("datetime", inplace=True)
    df_vol_resampled = df_vol["volume"].resample(interval).sum().reset_index()

    # Market Cap
    df_mc = pd.DataFrame(res["market_caps"], columns=["timestamp", "market_cap"])
    df_mc["datetime"] = pd.to_datetime(df_mc["timestamp"], unit="ms")
    df_mc.set_index("datetime", inplace=True)
    df_mc_resampled = df_mc["market_cap"].resample(interval).mean().reset_index()

    # Merge everything on datetime
    df_final = df_ohlc.merge(df_vol_resampled, on="datetime")
    df_final = df_final.merge(df_mc_resampled, on="datetime")

    # If you want to include raw timestamp (in ms) instead of datetime
    df_final["timestamp"] = (df_final["datetime"].astype('int64') // 10**6)

    # Reorder columns
    df_final = df_final[["timestamp", "open", "high", "low", "close", "volume", "market_cap"]]
    return df_final
def convert_miliseconds_datetime(miliseconds):
    """
    Input miliseconds as an int
    
    Output datetime in this format:
    YYYY-MM-DD  HH-MM-SS-MILISECONDS
    """
    seconds = miliseconds / 1000
    return str(datetime.fromtimestamp(seconds))
def heikin_ashi(df):
    """
    Create the df for Heiken Ashi Candles as a seperate df

    Args:
        df: df with stock candle data

    Returns:
        df: df with heiken ashi candle data
    """
    ha_df = df.copy()
    
    # HA_Close
    ha_df['ha_close'] = (df['open'] + df['high'] + df['low'] + df['close']) / 4
    
    # HA_Open (initialize first row)
    ha_open = [(df['open'][0] + df['close'][0]) / 2]
    
    # Compute remaining HA_Open values
    for i in range(1, len(df)):
        ha_open.append((ha_open[i-1] + ha_df['ha_close'][i-1]) / 2)
    
    ha_df['ha_open'] = ha_open
    
    # HA_High and HA_Low
    ha_df['ha_high'] = ha_df[['high', 'ha_open', 'ha_close']].max(axis=1)
    ha_df['ha_low'] = ha_df[['low', 'ha_open', 'ha_close']].min(axis=1)
    
    # Return only HA candles (or merge as needed)
    return ha_df[['timestamp','ha_open', 'ha_high', 'ha_low', 'ha_close','volume','market_cap']]
def bitcoin_main():
    bitcoin_df = request_coin("bitcoin",days=1)
    data1 = bitcoin_df.to_dict(orient="records")
    hieken = heikin_ashi(bitcoin_df)
    data2 = hieken.to_dict(orient="records")
    return {
        "df1": data1,
        "df2": data2
    }
def coin_data(coin_id):
    coin_df = request_coin(coin_id=coin_id,days=1)
    heiken_df = heikin_ashi(coin_df)
    #coin_df = coin_df.to_dict(orient="records")
    #heiken_df = heiken_df.to_dict(orient="records")
    return coin_df,heiken_df
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