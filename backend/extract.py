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
        response["prices][0] = [num1,num2]
        num1 is a timestap in milliseconds since Jan1,1970
        num2 is a prices in USD, can be set to another currency below
        
        market_caps dictionary - this is total value of the coin in circulation
        total_volumes dictionary - this is the total dollar value of the coin being traded in 24 hours
        
        
    """

    url = f"https://api.coingecko.com/api/v3/coins/{coin_id}/market_chart"
    params = {
        "vs_currency": "usd",
        "id": coin_id,
        "days": days,
        "x_cg_demo_apkey": os.getenv("COINGGECKO_API_KEY")
    }
    res = requests.get(url,params=params)
    #df_prices = pd.DataFrame.from_dict(res["prices"])
    return res.json()

def extract_dictionaries(data):
    return data["prices"],data["market_caps"],data["total_volumes"]

def convert_miliseconds_datetime(miliseconds):
    """
    Input miliseconds as an int
    
    Output datetime in this format:
    YYYY-MM-DD  HH-MM-SS-MILISECONDS
    """
    seconds = miliseconds / 1000
    return str(datetime.fromtimestamp(seconds))

def convert_date_in_prices(data):
    """
    Input: Pass the prices dictionary
    Output: The prices dictionary with converted date time
    """
    # DATA SHOULD BE THE PRICES DICTIONARY
    for lists in data:
        usd = lists[0]
        date = lists[1]
        lists[1] = convert_miliseconds_datetime(date)
# Test extact data
bitcoin_ten_days = request_coin("bitcoin",days=10)