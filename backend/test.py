import extract
from datetime import datetime
import collections
import matplotlib as pyplot
import numpy


# This has bitcoin data fro the last 10 days 
bitcoin_test = extract.bitcoin_ten_days


# for lists in bitcoin_test["prices"]:
#     usd = lists[0]
#     date = extract.convert_miliseconds_datetime(lists[1])
#     lists[1] = date

prices,market,volume = extract.extract_dictionaries(bitcoin_test)

times = []

extract.convert_date_in_prices(prices)

for lists in prices:
    times.append(lists[1])
hour = []
for i in range(len(times)):
    # HH:MM:SSSS
    curr = times[i]
    curr.split(" ")
    hour = curr[1]
    print(hour)