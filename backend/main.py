# main.py - Fixed FastAPI server
import uvicorn
from extract import bitcoin_main, coin_data
from fastapi import FastAPI, Query

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
def get_coin_data(coin_id: str = Query(..., description="Coin ID from CoinGecko (e.g., 'ethereum', 'cardano')")):
    """Get candlestick and Heikin Ashi data for any coin"""
    return coin_data(coin_id)

@app.get("/")
def root():
    """Root endpoint with API information"""
    return {
        "message": "Cryptocurrency Data API",
        "endpoints": {
            "/bitcoin_data": "Get Bitcoin data",
            "/coin_data?coin_id=ethereum": "Get data for any coin",
            "/docs": "API documentation"
        }
    }

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)