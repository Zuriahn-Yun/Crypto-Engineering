# main.py - Fixed FastAPI server
import uvicorn
from extract import bitcoin_main, coin_data,convert_miliseconds_datetime
from fastapi import FastAPI, Query
from plotly.subplots import make_subplots
import plotly.graph_objects as go
from fastapi.responses import HTMLResponse

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
    try:
        """Get candlestick and Heikin Ashi data for any coin, query prompts for coin ID"""
        coin_df,heiken_df = coin_data(coin_id)
        
        coin_df['timestamp'] = coin_df['timestamp'].apply(convert_miliseconds_datetime)
        
        heiken_df['timestamp'] = heiken_df['timestamp'].apply(convert_miliseconds_datetime)
        
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

        fig.update_layout(title=dict(text=f"{coin_id} Stock Data From the Last Day"))

        html = fig.to_html(include_plotlyjs='cdn',full_html = True)
        
        return HTMLResponse(html)
    
    except Exception as e:
        import traceback
        traceback.print_exc()
        return HTMLResponse(content=f"<h3>Internal Error:</h3><pre>{str(e)}</pre>", status_code=500)

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