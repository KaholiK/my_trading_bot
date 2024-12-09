# src/risk_management.py

import logging

logger = logging.getLogger(__name__)

class RiskManager:
    def __init__(self, max_drawdown=0.05, max_position_size=0.02):
        """
        Initialize risk management parameters.
        
        :param max_drawdown: Maximum allowed drawdown (e.g., 0.05 for 5%)
        :param max_position_size: Maximum position size relative to portfolio (e.g., 0.02 for 2%)
        """
        self.max_drawdown = max_drawdown
        self.max_position_size = max_position_size
        self.portfolio_value = 100000  # Example initial portfolio value, replace as needed
        self.current_drawdown = 0
    
    def update_portfolio_value(self, new_value):
        """
        Update the current portfolio value and calculate drawdown.
        """
        if new_value < self.portfolio_value:
            drawdown = (self.portfolio_value - new_value) / self.portfolio_value
            self.current_drawdown = max(self.current_drawdown, drawdown)
            logger.info(f"Current drawdown: {self.current_drawdown*100}%")
        else:
            self.portfolio_value = new_value
            logger.info(f"Portfolio value updated to: {self.portfolio_value}")
    
    def can_trade(self):
        """
        Determine if trading is allowed based on drawdown.
        """
        if self.current_drawdown > self.max_drawdown:
            logger.warning("Maximum drawdown exceeded. Trading halted.")
            return False
        return True
    
    def calculate_position_size(self, risk_factor=0.01):
        """
        Calculate position size based on risk factor and portfolio value.
        """
        position_size = self.portfolio_value * self.max_position_size * risk_factor
        logger.info(f"Calculated position size: {position_size}")
        return position_size
