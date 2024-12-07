# File: src/risk_management.py
# Part 7: Risk Management & Portfolio Optimization
#
# This module ensures that trades made by the system are constrained by risk rules.
# It can:
# - Determine position sizes based on volatility and max risk parameters
# - Apply stop-loss/take-profit logic
# - Perform simple portfolio optimization to avoid overconcentration in one asset
#
# In future parts, we’ll integrate actual volatility calculations, correlation matrices,
# and possibly a more advanced optimization algorithm (like mean-variance optimization or RL-based optimization).

import numpy as np
from typing import Dict, Any, List

class RiskManager:
    """
    The RiskManager enforces global and per-trade risk rules.
    This includes:
    - Max daily drawdown limit
    - Position sizing based on volatility
    - Stop-loss and take-profit calculations
    """
    def __init__(self,
                 initial_equity: float = 100000.0,
                 max_daily_drawdown: float = 0.02,  # 2% of equity
                 max_position_pct: float = 0.10,     # Max 10% of equity in one trade
                 stop_loss_pct: float = 0.01,        # 1% stop loss per trade
                 take_profit_pct: float = 0.03):     # 3% take profit per trade
        self.initial_equity = initial_equity
        self.current_equity = initial_equity
        self.max_daily_drawdown = max_daily_drawdown
        self.max_position_pct = max_position_pct
        self.stop_loss_pct = stop_loss_pct
        self.take_profit_pct = take_profit_pct
        self.daily_high_equity = initial_equity
        self.trades: List[Dict[str, Any]] = []

    def update_equity(self, new_equity: float):
        self.current_equity = new_equity
        if new_equity > self.daily_high_equity:
            self.daily_high_equity = new_equity

    def check_drawdown(self) -> bool:
        """
        Check if daily drawdown limit is hit.
        """
        drawdown = (self.daily_high_equity - self.current_equity) / self.daily_high_equity
        return drawdown > self.max_daily_drawdown

    def calculate_position_size(self, symbol: str, price: float, volatility: float = 0.02) -> float:
        """
        Calculate position size based on current equity and volatility.
        A simple rule: invest max_position_pct of equity / (volatility factor).
        More volatile instruments = smaller position sizes.
        """
        max_position_size = self.current_equity * self.max_position_pct / price
        # Scale down by volatility: more volatile => smaller size
        # If volatility = 0.02 (2%), we might reduce position by a factor of say (1 + 10*volatility)
        # Just a placeholder heuristic
        size_factor = (1 + 10 * volatility)
        final_size = max_position_size / size_factor
        return max(0.0, final_size)

    def apply_stops(self, entry_price: float) -> Dict[str, float]:
        """
        Given an entry price, calculate stop_loss and take_profit levels.
        """
        stop_loss_price = entry_price * (1 - self.stop_loss_pct)
        take_profit_price = entry_price * (1 + self.take_profit_pct)
        return {"stop_loss": stop_loss_price, "take_profit": take_profit_price}

class PortfolioOptimizer:
    """
    A basic portfolio optimizer that tries to maintain a balanced exposure.
    In future parts, we might integrate a full mean-variance optimizer,
    or factor-model-based optimization.
    For now, a simple heuristic: if too much capital is concentrated in one asset,
    reduce future allocations to that asset.
    """
    def __init__(self,
                 max_concentration: float = 0.20):
        # No single asset should exceed 20% of total portfolio value.
        self.max_concentration = max_concentration
        self.positions: Dict[str, float] = {}  # symbol -> position value

    def update_positions(self, symbol: str, value: float):
        self.positions[symbol] = value

    def get_portfolio_value(self) -> float:
        return sum(self.positions.values())

    def can_increase_position(self, symbol: str, additional_value: float) -> bool:
        total_val = self.get_portfolio_value() + additional_value
        if total_val == 0:
            return True
        # Check concentration
        new_val_for_symbol = self.positions.get(symbol, 0.0) + additional_value
        concentration = new_val_for_symbol / total_val
        return concentration <= self.max_concentration

if __name__ == "__main__":
    # Example usage:
    risk = RiskManager()
    port = PortfolioOptimizer()
    
    current_price = 150.0
    pos_size = risk.calculate_position_size("AAPL", price=current_price, volatility=0.02)
    stops = risk.apply_stops(entry_price=current_price)
    print(f"Position size: {pos_size} shares, Stop Loss: {stops['stop_loss']}, Take Profit: {stops['take_profit']}")

    # Update portfolio
    position_value = pos_size * current_price
    port.update_positions("AAPL", position_value)
    can_add_more = port.can_increase_position("AAPL", additional_value=5000)
    print("Can add more AAPL?:", can_add_more)
