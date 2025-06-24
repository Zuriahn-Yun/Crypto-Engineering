import extract
from datetime import datetime
import collections
import matplotlib as pyplot
import numpy
import pandas as pd
"""
This exists as a test script file to test backend functions and make sure things are working as expected
"""

# This has bitcoin data fro the last 10 days 
bitcoin_test = extract.bitcoin_ten_days

# 15 minute intevals only works if you look at the last 24H, otherwise we only have hourly data 
print(bitcoin_test)
