# src/risk_management.py

import logging
from typing import Dict
from src.logging_monitoring import logger

class RiskManager:
    """
    Manages and enforces trading risk parameters.
    """
    def __init__(
        self,
        max_position_size: float = 1.0,  # Maximum position size in BTC
        max_drawdown: float = 0.05,     # Maximum allowed drawdown (5%)
        stop_loss_percentage: float = 0.02  # Stop-loss at 2%
    ):
        """
        Initialize the RiskManager.
        
        :param max_position_size: Maximum position size per trade.
        :param max_drawdown: Maximum allowed drawdown from peak equity.
        :param stop_loss_percentage: Percentage at which to trigger stop-loss.
        """
        self.max_position_size = max_position_size
        self.max_drawdown = max_drawdown
        self.stop_loss_percentage = stop_loss_percentage
        self.current_position: Dict[str, float] = {}  # e.g., {"BTCUSDT": 0.5}
        self.peak_equity = 10000.0  # Example starting equity
        self.current_equity = self.peak_equity

    def update_equity(self, new_equity: float):
        """
        Update the current equity and adjust peak equity.
        
        :param new_equity: Updated equity value.
        """
        if new_equity > self.peak_equity:
            self.peak_equity = new_equity
            logger.info(f"New peak equity reached: {self.peak_equity}")
        self.current_equity = new_equity
        logger.debug(f"Equity updated to: {self.current_equity}")

    def check_drawdown(self) -> bool:
        """
        Check if the current equity has exceeded the maximum drawdown.
        
        :return: True if drawdown limit exceeded, False otherwise.
        """
        drawdown = (self.peak_equity - self.current_equity) / self.peak_equity
        logger.debug(f"Current drawdown: {drawdown * 100:.2f}%")
        if drawdown > self.max_drawdown:
            logger.warning(f"Drawdown exceeded: {drawdown * 100:.2f}% > {self.max_drawdown * 100}%")
            return True
        return False

    def adjust_position_size(self, desired_size: float) -> float:
        """
        Adjust the desired position size based on risk parameters.
        
        :param desired_size: Desired position size.
        :return: Adjusted position size.
        """
        adjusted_size = min(desired_size, self.max_position_size)
        logger.debug(f"Desired position size: {desired_size}, Adjusted position size: {adjusted_size}")
        return adjusted_size

    def apply_stop_loss(self, symbol: str, entry_price: float, current_price: float) -> bool:
        """
        Determine whether to trigger a stop-loss based on current price.
        
        :param symbol: Trading symbol.
        :param entry_price: Price at which the position was entered.
        :param current_price: Current market price.
        :return: True if stop-loss should be triggered, False otherwise.
        """
        loss = (entry_price - current_price) / entry_price
        logger.debug(f"Stop-loss check for {symbol}: Loss = {loss * 100:.2f}%")
        if loss >= self.stop_loss_percentage:
            logger.info(f"Stop-loss triggered for {symbol}.")
            return True
        return False

    def enforce_risk(self, symbol: str, desired_size: float) -> float:
        """
        Enforce risk parameters and adjust the position size accordingly.
        
        :param symbol: Trading symbol.
        :param desired_size: Desired position size.
        :return: Approved position size after risk checks.
        """
        if self.check_drawdown():
            logger.error("Max drawdown exceeded. No new positions can be taken.")
            return 0.0  # Prevent taking new positions
        
        approved_size = self.adjust_position_size(desired_size)
        self.current_position[symbol] = approved_size
        logger.info(f"Position for {symbol} set to {approved_size} BTC.")
        return approved_size

    def close_position(self, symbol: str):
        """
        Close an open position.
        
        :param symbol: Trading symbol.
        """
        if symbol in self.current_position:
            logger.info(f"Closing position for {symbol} which was {self.current_position[symbol]} BTC.")
            del self.current_position[symbol]
        else:
            logger.warning(f"No open position found for {symbol} to close.")

# Example Usage
if __name__ == "__main__":
    risk_manager = RiskManager(
        max_position_size=0.5,
        max_drawdown=0.10,  # 10%
        stop_loss_percentage=0.03  # 3%
    )
    
    # Update equity based on trading performance
    risk_manager.update_equity(9500.0)
    
    # Enforce risk before taking a new position
    approved_size = risk_manager.enforce_risk("BTCUSDT", desired_size=0.7)
    print(f"Approved position size for BTCUSDT: {approved_size} BTC")
    
    # Example stop-loss check
    should_stop = risk_manager.apply_stop_loss("BTCUSDT", entry_price=10000.0, current_price=9700.0)
    print(f"Should trigger stop-loss: {should_stop}")
    
    # Close a position
    risk_manager.close_position("BTCUSDT")
