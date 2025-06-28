# plot_from_api.py
import requests
import pandas as pd
import mplfinance as mpf

# Fetch from FastAPI endpoint, make sure the server is running
res = requests.get("http://127.0.0.1:8000/bitcoin_data")
data = res.json()
# Convert
df = pd.DataFrame(data)
df["datetime"] = pd.to_datetime(df["timestamp"], unit="ms")
df.set_index("datetime", inplace=True)
# Plot
mpf.plot(df, type='candle', style='yahoo', title="Heikin Ashi Bitcoin Chart")
