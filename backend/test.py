import extract
from datetime import datetime
import collections
import matplotlib as pyplot
import numpy

# This has bitcoin data fro the last 10 days 
bitcoin_test = extract.bitcoin_ten_days

prices,market,volume = extract.extract_dictionaries(bitcoin_test)


print(bitcoin_test)

# extract.convert_date_in_prices(prices)


# This relies on having the data converted to date time format
# WHAT ARE WE DOING BELOW, is this useful i dont want to do this again
# times = []
# for lists in prices:
#     # Iterate through the dict of prices, append each time in date time format to times
#     times.append(lists[1])
    
# hour = []
# for i in range(len(times)):
#     # This will get just the hours
#     # HH:MM:SSSS
#     curr = times[i]
#     split = curr.split(" ")
#     curr_hour = split[1]
#     hour.append(curr_hour)



