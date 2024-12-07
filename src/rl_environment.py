# File: src/rl_environment.py
# Part 4: Reinforcement Learning Setup
#
# This module defines a Gym-like environment that simulates trading using preprocessed features.
# The RL agent will interact with this environment, selecting actions (buy, sell, hold),
# and receiving rewards based on trading performance.
# Later, we will integrate the predictive models for forecasts, incorporate slippage, commissions,
# and handle multiple instruments.

import gym
import numpy as np
from gym import spaces
from typing import Dict, Any, Optional, List

class TradingEnv(gym.Env):
    """
    A simplified trading environment for RL.
    The agent observes a window of features and decides an action: buy, sell, or hold.
    Eventually, we'll add multiple instruments, scaling, transaction costs, and realistic PnL calculations.
    """
    metadata = {'render.modes': ['human']}

    def __init__(self,
                 feature_df: np.ndarray,
                 initial_balance: float = 100000.0,
                 max_position: float = 10.0,
                 window_size: int = 30):
        """
        feature_df: (T, D) array of features, where T is time steps, D is feature dimension.
        initial_balance: starting capital
        max_position: maximum number of units (e.g. lots, shares) the agent can hold
        window_size: how many time steps the agent sees as input
        """
        super(TradingEnv, self).__init__()
        self.feature_df = feature_df
        self.initial_balance = initial_balance
        self.balance = initial_balance
        self.max_position = max_position
        self.position = 0.0
        self.window_size = window_size

        # Assume last column of feature_df is price (for simplicity now)
        self.price_idx = -1
        self.current_step = window_size

        # Observation space: flattened window of features
        obs_dim = self.window_size * self.feature_df.shape[1]
        self.observation_space = spaces.Box(low=-np.inf, high=np.inf, shape=(obs_dim,), dtype=np.float32)

        # Action space: discrete actions -> 0: sell 1 unit, 1: hold, 2: buy 1 unit
        # We'll allow position increments of 1 unit. In future parts, might switch to continuous actions.
        self.action_space = spaces.Discrete(3)

    def _get_observation(self) -> np.ndarray:
        # Extract last 'window_size' steps of features
        start = self.current_step - self.window_size
        end = self.current_step
        window = self.feature_df[start:end, :]
        return window.flatten()

    def _get_price(self) -> float:
        # Price is taken as the last column for now
        return float(self.feature_df[self.current_step - 1, self.price_idx])

    def step(self, action: int):
        done = False
        reward = 0.0

        old_price = self._get_price()

        # Execute action
        if action == 0:  # Sell 1 unit
            if self.position > 0:
                self.position -= 1.0
                # Realized PnL from selling at old_price
                # We'll assume we 'bought' the position at previous times.
                # For now, ignore cost basis; future parts will store avg entry price.
                reward += 0.0  # Will refine in future parts.
        elif action == 2:  # Buy 1 unit
            if self.position < self.max_position:
                self.position += 1.0
                # No immediate reward for buying, unrealized PnL only shows up later.

        # Move forward in time
        self.current_step += 1
        if self.current_step >= self.feature_df.shape[0]:
            done = True
            # Final reward: mark-to-market all positions at last price
            final_price = old_price
            # Simplistic: PnL = position * (final_price - initial reference price)
            # In future: track cost basis for each trade
            reward += self.position * (final_price - old_price)
        else:
            # Mark-to-market unrealized PnL at new price
            new_price = self._get_price()
            # Incremental reward: difference in mark-to-market
            reward += self.position * (new_price - old_price)

        obs = self._get_observation()
        info = {}
        return obs, reward, done, info

    def reset(self):
        self.balance = self.initial_balance
        self.position = 0.0
        self.current_step = self.window_size
        return self._get_observation()

    def render(self, mode='human'):
        # Placeholder: could print current step, position, PnL, etc.
        print(f"Step: {self.current_step}, Pos: {self.position}, Price: {self._get_price()}")

if __name__ == "__main__":
    # Example usage:
    # Mock feature data: 200 timesteps, 10 features, last feature is price
    mock_data = np.random.randn(200, 10)
    # Make price positive and trending upwards
    mock_data[:, -1] = np.cumsum(np.abs(np.random.randn(200))) + 100
    env = TradingEnv(mock_data)
    obs = env.reset()
    for _ in range(5):
        action = env.action_space.sample()
        obs, reward, done, info = env.step(action)
        env.render()
        if done:
            break
