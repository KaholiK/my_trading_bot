# src/execution_engine.py

import logging
from concurrent.futures import ThreadPoolExecutor
from alpaca_trade_api import REST
from src.continuous_learning import TradingAgent
from src.risk_management import RiskManager
import torch

logger = logging.getLogger(__name__)

class AlpacaExecutionEngine:
    def __init__(self, api_key, api_secret, base_url='https://paper-api.alpaca.markets', device='cpu'):
        self.api = REST(api_key, api_secret, base_url, api_version='v2')
        self.device = device
        # Initialize Trading Agent
        state_size = 10  # Define based on your feature engineering
        action_size = 3  # Example: Buy, Sell, Hold
        self.agent = TradingAgent(state_size, action_size, device=self.device)
        # Initialize Risk Manager
        self.risk_manager = RiskManager()
    
    def execute_trade(self, trade):
        """
        Executes a single trade based on action, considering risk management.
        """
        if not self.risk_manager.can_trade():
            logger.warning("Risk management disallows trading at this time.")
            return {"symbol": trade["symbol"], "action": trade["action"], "status": "risk_limit_exceeded"}
        
        # Calculate position size
        trade["quantity"] = self.risk_manager.calculate_position_size()
        
        try:
            if trade["action"] == "buy":
                order = self.api.submit_order(
                    symbol=trade["symbol"],
                    qty=trade["quantity"],
                    side='buy',
                    type='market',
                    time_in_force='gtc'
                )
            elif trade["action"] == "sell":
                order = self.api.submit_order(
                    symbol=trade["symbol"],
                    qty=trade["quantity"],
                    side='sell',
                    type='market',
                    time_in_force='gtc'
                )
            else:
                logger.info(f"Holding position for {trade['symbol']}")
                return {"symbol": trade["symbol"], "action": trade["action"], "status": "hold"}
            
            logger.info(f"Trade executed: {trade}")
            # Update portfolio value (fetch current portfolio)
            portfolio = self.api.get_account()
            self.risk_manager.update_portfolio_value(float(portfolio.equity))
            return {"symbol": trade["symbol"], "action": trade["action"], "status": "executed"}
        except Exception as e:
            logger.error(f"Failed to execute trade {trade}: {e}")
            return {"symbol": trade["symbol"], "action": trade["action"], "status": "failed"}
    
    def execute_trades_concurrently(self, trades):
        """
        Executes multiple trades concurrently.
        """
        results = []
        with ThreadPoolExecutor(max_workers=5) as executor:
            futures = [executor.submit(self.execute_trade, trade) for trade in trades]
            for future in futures:
                results.append(future.result())
        return results
    
    def decide_and_trade(self, state):
        """
        Decides on an action based on the current state and executes the trade.
        """
        action = self.agent.select_action(state)
        action_map = {0: 'buy', 1: 'sell', 2: 'hold'}
        selected_action = action_map[action]
        
        trade = {
            "symbol": "AAPL",  # Example symbol, replace as needed
            "quantity": 10,     # Placeholder, will be adjusted by RiskManager
            "action": selected_action,
            "price": 0          # Placeholder, implement actual price retrieval
        }
        
        result = self.execute_trade(trade)
        # Here, you would store the transition (state, action, reward, next_state, done) in ReplayMemory
        # and call self.agent.optimize_model()
        
        return result
