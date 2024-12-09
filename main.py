# main.py

from src.logging_monitoring import setup_prometheus, setup_logging
from fastapi import FastAPI
import uvicorn
from src.execution_engine import AlpacaExecutionEngine
from src.feature_engineering import FeatureEngineer
from src.decision_fusion import DecisionFusion
from src.strategies.scalping import ScalpingStrategy
from src.strategies.swing_trading import SwingTradingStrategy
from src.config import ALPACA_API_KEY, ALPACA_API_SECRET
from src.chat_interface import router as chat_router
import pandas as pd

# Initialize logging
logger = setup_logging()

# Initialize Prometheus metrics
setup_prometheus(port=8001)

app = FastAPI()

# Include Chat Interface Router
app.include_router(chat_router)

# Initialize Execution Engine with your Alpaca API credentials
BASE_URL = "https://paper-api.alpaca.markets"

execution_engine = AlpacaExecutionEngine(api_key=ALPACA_API_KEY, api_secret=ALPACA_API_SECRET, base_url=BASE_URL, device='cpu')

# Initialize Strategies
scalping = ScalpingStrategy()
swing_trading = SwingTradingStrategy()
decision_fusion = DecisionFusion(strategies=[scalping, swing_trading])

# Example route to trigger trading decision
@app.post("/trade")
def trigger_trade(symbol: str = "AAPL"):
    # Fetch latest market data
    market_data = execution_engine.api.get_barset(symbol, 'minute', limit=100).df[symbol]
    df = market_data.reset_index()
    df.rename(columns={'time': 'timestamp', 'close': 'price'}, inplace=True)
    
    # Feature Engineering
    fe = FeatureEngineer()
    features = fe.generate_features(df)
    
    # Decision Fusion
    fused_signals = decision_fusion.combine_signals(features)
    
    # Get the latest signal
    latest_signal = fused_signals.iloc[-1]['combined_signal']
    
    # Map signal to action
    action_map = {1: 'buy', -1: 'sell', 0: 'hold'}
    action = action_map.get(latest_signal, 'hold')
    
    # Prepare state for RL agent
    latest_features = features.iloc[-1][['rsi', 'moving_average', 'price_change', 'volatility', 'momentum']].values
    state = latest_features.tolist()
    
    # Decide and trade using RL agent
    result = execution_engine.decide_and_trade(state)
    
    return {"trade_result": result, "action": action, "symbol": symbol}

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
