# src/execution_engine.py

from src.logging_monitoring import TRADE_EXECUTED, TRADE_FAILED, PORTFOLIO_VALUE

class AlpacaExecutionEngine:
    # ... [existing code] ...
    
    def execute_trade(self, trade):
        """
        Executes a single trade based on action, considering risk management.
        """
        if not self.risk_manager.can_trade():
            logger.warning("Risk management disallows trading at this time.")
            TRADE_FAILED.inc()
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
            TRADE_EXECUTED.inc()
            # Update portfolio value (fetch current portfolio)
            portfolio = self.api.get_account()
            current_equity = float(portfolio.equity)
            self.risk_manager.update_portfolio_value(current_equity)
            PORTFOLIO_VALUE.set(current_equity)
            return {"symbol": trade["symbol"], "action": trade["action"], "status": "executed"}
        except Exception as e:
            logger.error(f"Failed to execute trade {trade}: {e}")
            TRADE_FAILED.inc()
            return {"symbol": trade["symbol"], "action": trade["action"], "status": "failed"}
