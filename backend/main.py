# main.py - Fixed FastAPI server
import uvicorn
from extract import bitcoin_main, coin_data
from fastapi import FastAPI, Query
from plotly.subplots import make_subplots
import plotly.graph_objects as go

app = FastAPI()

"""
Testing Steps:
1. Run: uvicorn main:app --reload
2. Go to http://127.0.0.1:8000/docs
"""

@app.get("/bitcoin_data")
def get_bitcoin_data():
    """Get Bitcoin candlestick and Heikin Ashi data for the last 24 hours"""
    return bitcoin_main()

@app.get("/coin_data")
def get_coin_plot(coin_id: str = Query(..., description="Coin ID from CoinGecko (e.g., 'ethereum', 'cardano')")):
    """Get candlestick and Heikin Ashi data for any coin, query prompts for coin ID"""
    coin_df,heiken_df = coin_data(coin_id)
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

    return fig.to_html(full_html = False)


@app.get("/")
def root():
    """Root endpoint with API information"""
    return {
        "message": "Cryptocurrency Data API",
        "endpoints": {
            "/bitcoin_data": "Get Bitcoin data from the last 24 hours",
            "/coin_data?coin_id=ethereum": "Get Any Coin Data from the last 24 hours",
            "/docs": "API documentation"
        }
    }

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)