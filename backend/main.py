# main.py - Fixed FastAPI server
import uvicorn
from extract import bitcoin_main, coin_data,convert_miliseconds_datetime,get_name
from fastapi import FastAPI, Query
from plotly.subplots import make_subplots
import plotly.graph_objects as go
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


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
        """Get comprehensive crypto analysis with candlestick, Heikin Ashi, technical indicators, and volume data"""   
        coin_df, heiken_df = coin_data(coin_id)
        
        # Convert timestamps
        coin_df['timestamp'] = coin_df['timestamp'].apply(convert_miliseconds_datetime)
        heiken_df['timestamp'] = heiken_df['timestamp'].apply(convert_miliseconds_datetime)
        
        # Calculate technical indicators
        def calculate_sma(data, window):
            return data.rolling(window=window).mean()
        
        def calculate_ema(data, window):
            return data.ewm(span=window).mean()
        
        def calculate_rsi(data, window=14):
            delta = data.diff()
            gain = (delta.where(delta > 0, 0)).rolling(window=window).mean()
            loss = (-delta.where(delta < 0, 0)).rolling(window=window).mean()
            rs = gain / loss
            return 100 - (100 / (1 + rs))
        
        def calculate_bollinger_bands(data, window=20, num_std=2):
            sma = data.rolling(window=window).mean()
            std = data.rolling(window=window).std()
            upper = sma + (std * num_std)
            lower = sma - (std * num_std)
            return upper, sma, lower
        
        def calculate_macd(data, fast=12, slow=26, signal=9):
            ema_fast = data.ewm(span=fast).mean()
            ema_slow = data.ewm(span=slow).mean()
            macd_line = ema_fast - ema_slow
            signal_line = macd_line.ewm(span=signal).mean()
            histogram = macd_line - signal_line
            return macd_line, signal_line, histogram
        
        # Calculate indicators
        coin_df['sma_20'] = calculate_sma(coin_df['close'], 20)
        coin_df['sma_50'] = calculate_sma(coin_df['close'], 50)
        coin_df['ema_12'] = calculate_ema(coin_df['close'], 12)
        coin_df['ema_26'] = calculate_ema(coin_df['close'], 26)
        coin_df['rsi'] = calculate_rsi(coin_df['close'])
        
        bb_upper, bb_middle, bb_lower = calculate_bollinger_bands(coin_df['close'])
        coin_df['bb_upper'] = bb_upper
        coin_df['bb_middle'] = bb_middle
        coin_df['bb_lower'] = bb_lower
        
        macd_line, signal_line, histogram = calculate_macd(coin_df['close'])
        coin_df['macd'] = macd_line
        coin_df['macd_signal'] = signal_line
        coin_df['macd_histogram'] = histogram
        
        # Calculate volume moving average
        coin_df['volume_sma'] = calculate_sma(coin_df['volume'], 20)
        
        # Create subplots
        fig = make_subplots(
            rows=4, cols=2,
            subplot_titles=(
                "Price Chart with Technical Indicators", "Heikin Ashi Candles",
                "Volume Analysis", "RSI (Relative Strength Index)",
                "MACD Indicator", "Price vs Moving Averages"
            ),
            specs=[
                [{"secondary_y": False}, {"secondary_y": False}],
                [{"secondary_y": True}, {"secondary_y": False}],
                [{"secondary_y": False}, {"secondary_y": False}],
                [{"secondary_y": False}, {"secondary_y": False}]
            ],
            vertical_spacing=0.08,
            horizontal_spacing=0.1,
            row_heights=[0.4, 0.25, 0.25, 0.1]
        )
        
        # 1. Main candlestick chart with Bollinger Bands
        fig.add_trace(go.Candlestick(
            x=coin_df['timestamp'],
            open=coin_df['open'],
            high=coin_df['high'],
            low=coin_df['low'],
            close=coin_df['close'],
            name="Price",
            increasing_line_color='#00ff88',
            decreasing_line_color='#ff4444'
        ), row=1, col=1)
        
        # Bollinger Bands
        fig.add_trace(go.Scatter(
            x=coin_df['timestamp'], y=coin_df['bb_upper'],
            mode='lines', name='BB Upper', line=dict(color='rgba(128,128,128,0.3)'),
            showlegend=False
        ), row=1, col=1)
        
        fig.add_trace(go.Scatter(
            x=coin_df['timestamp'], y=coin_df['bb_lower'],
            mode='lines', name='BB Lower', line=dict(color='rgba(128,128,128,0.3)'),
            fill='tonexty', fillcolor='rgba(128,128,128,0.1)',
            showlegend=False
        ), row=1, col=1)
        
        fig.add_trace(go.Scatter(
            x=coin_df['timestamp'], y=coin_df['bb_middle'],
            mode='lines', name='BB Middle', line=dict(color='orange', width=1)
        ), row=1, col=1)
        
        # 2. Heikin Ashi candles
        fig.add_trace(go.Candlestick(
            x=heiken_df['timestamp'],
            open=heiken_df['ha_open'],
            high=heiken_df['ha_high'],
            low=heiken_df['ha_low'],
            close=heiken_df['ha_close'],
            name="Heikin Ashi",
            increasing_line_color='#00cc66',
            decreasing_line_color='#cc3333'
        ), row=1, col=2)
        
        # 3. Volume analysis
        colors = ['green' if close >= open else 'red' 
                 for close, open in zip(coin_df['close'], coin_df['open'])]
        
        fig.add_trace(go.Bar(
            x=coin_df['timestamp'], y=coin_df['volume'],
            name='Volume', marker_color=colors, opacity=0.7
        ), row=2, col=1)
        
        fig.add_trace(go.Scatter(
            x=coin_df['timestamp'], y=coin_df['volume_sma'],
            mode='lines', name='Volume SMA', line=dict(color='purple', width=2)
        ), row=2, col=1)
        
        # 4. RSI
        fig.add_trace(go.Scatter(
            x=coin_df['timestamp'], y=coin_df['rsi'],
            mode='lines', name='RSI', line=dict(color='blue', width=2)
        ), row=2, col=2)
        
        # RSI overbought/oversold lines
        fig.add_hline(y=70, line_dash="dash", line_color="red", opacity=0.5, row=2, col=2)
        fig.add_hline(y=30, line_dash="dash", line_color="green", opacity=0.5, row=2, col=2)
        fig.add_hline(y=50, line_dash="dot", line_color="gray", opacity=0.3, row=2, col=2)
        
        # 5. MACD
        fig.add_trace(go.Scatter(
            x=coin_df['timestamp'], y=coin_df['macd'],
            mode='lines', name='MACD', line=dict(color='blue', width=2)
        ), row=3, col=1)
        
        fig.add_trace(go.Scatter(
            x=coin_df['timestamp'], y=coin_df['macd_signal'],
            mode='lines', name='Signal', line=dict(color='red', width=2)
        ), row=3, col=1)
        
        # MACD histogram
        histogram_colors = ['green' if val >= 0 else 'red' for val in coin_df['macd_histogram']]
        fig.add_trace(go.Bar(
            x=coin_df['timestamp'], y=coin_df['macd_histogram'],
            name='MACD Histogram', marker_color=histogram_colors, opacity=0.6
        ), row=3, col=1)
        
        # 6. Moving averages comparison
        fig.add_trace(go.Scatter(
            x=coin_df['timestamp'], y=coin_df['close'],
            mode='lines', name='Price', line=dict(color='black', width=3)
        ), row=3, col=2)
        
        fig.add_trace(go.Scatter(
            x=coin_df['timestamp'], y=coin_df['sma_20'],
            mode='lines', name='SMA 20', line=dict(color='blue', width=2)
        ), row=3, col=2)
        
        fig.add_trace(go.Scatter(
            x=coin_df['timestamp'], y=coin_df['sma_50'],
            mode='lines', name='SMA 50', line=dict(color='red', width=2)
        ), row=3, col=2)
        
        fig.add_trace(go.Scatter(
            x=coin_df['timestamp'], y=coin_df['ema_12'],
            mode='lines', name='EMA 12', line=dict(color='green', width=1, dash='dash')
        ), row=3, col=2)
        
        # Get coin name and current stats
        name = get_name(coin_id=coin_id)
        current_price = coin_df['close'].iloc[-1]
        price_change = ((current_price - coin_df['close'].iloc[0]) / coin_df['close'].iloc[0]) * 100
        volume_24h = coin_df['volume'].sum()
        current_rsi = coin_df['rsi'].iloc[-1] if not coin_df['rsi'].isna().all() else 0
        
        # Update layout with enhanced styling
        fig.update_layout(
            title=dict(
                text=f"{name} - Comprehensive Technical Analysis<br>" +
                     f"<span style='font-size:14px'>Current: ${current_price:.4f} | " +
                     f"24h Change: {price_change:+.2f}% | " +
                     f"RSI: {current_rsi:.1f} | " +
                     f"24h Volume: {volume_24h:,.0f}</span>",
                x=0.5,
                font=dict(size=20)
            ),
            height=1200,
            showlegend=True,
            plot_bgcolor='rgba(240,240,240,0.8)',
            paper_bgcolor='white',
            font=dict(size=10),
            margin=dict(t=120, b=50, l=50, r=50)
        )
        
        # Update y-axis labels
        fig.update_yaxes(title_text="Price ($)", row=1, col=1)
        fig.update_yaxes(title_text="Price ($)", row=1, col=2)
        fig.update_yaxes(title_text="Volume", row=2, col=1)
        fig.update_yaxes(title_text="RSI", row=2, col=2, range=[0, 100])
        fig.update_yaxes(title_text="MACD", row=3, col=1)
        fig.update_yaxes(title_text="Price ($)", row=3, col=2)
        
        # Update x-axis labels
        fig.update_xaxes(title_text="Time", row=3, col=1)
        fig.update_xaxes(title_text="Time", row=3, col=2)
        
        # Remove x-axis rangeslider for cleaner look
        fig.update_layout(xaxis=dict(rangeslider=dict(visible=False)))
        fig.update_layout(xaxis2=dict(rangeslider=dict(visible=False)))
        
        html = fig.to_html(include_plotlyjs='cdn', full_html=True)
        
        return HTMLResponse(html)
    
    except Exception as e:
        import traceback
        traceback.print_exc()
        return HTMLResponse(
            content=f"<center><h2>Error: Not a valid coin ID</h2><p>Please check the coin ID and try again.</p></center>", 
            status_code=500
        )

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