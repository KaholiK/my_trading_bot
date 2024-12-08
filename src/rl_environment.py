# src/rl_environment.py

import gym
from gym import spaces
import numpy as np
import pandas as pd
from typing import Tuple
from src.feature_engineering import FeatureEngineer
from src.logging_monitoring import logger

class TradingEnv(gym.Env):
    """
    Custom Environment for Reinforcement Learning in Trading.
    """
    metadata = {'render.modes': ['human']}

    def __init__(self, data: pd.DataFrame, feature_engineer: FeatureEngineer):
        super(TradingEnv, self).__init__()
        
        self.data = data.reset_index(drop=True)
        self.feature_engineer = feature_engineer
        self.current_step = 0
        self.total_steps = len(data) - 1
        
        # Define action and observation space
        # Actions: 0 = Hold, 1 = Buy, 2 = Sell
        self.action_space = spaces.Discrete(3)
        
        # Observations: Feature vector
        self.observation_space = spaces.Box(
            low=-np.inf, high=np.inf, shape=(self.feature_engineer.get_feature_dimension(),), dtype=np.float32
        )
        
        # Initialize state
        self.state = self._next_observation()
        
        # Initialize portfolio
        self.initial_balance = 10000.0
        self.balance = self.initial_balance
        self.holding = 0.0  # Amount of BTC held
        self.max_steps = self.total_steps
        self.trades = []

    def _next_observation(self) -> np.ndarray:
        """
        Get the next observation.
        """
        if self.current_step >= self.total_steps:
            self.current_step = self.total_steps - 1  # Prevent overflow
        
        current_data = self.data.iloc[self.current_step:self.current_step + self.feature_engineer.lookback]
        features = self.feature_engineer.generate_features(current_data)
        obs = features.iloc[-1].values  # Latest features
        logger.debug(f"Observation at step {self.current_step}: {obs}")
        return obs

    def step(self, action: int) -> Tuple[np.ndarray, float, bool, dict]:
        """
        Execute one time step within the environment.
        
        :param action: Action taken by the agent.
        :return: Tuple of (observation, reward, done, info)
        """
        current_price = self.data.loc[self.current_step, 'close']
        logger.debug(f"Step {self.current_step}: Action {action}, Price {current_price}")

        # Define transaction cost
        transaction_cost = 0.001  # 0.1%

        # Execute action
        if action == 1:  # Buy
            if self.balance > 0:
                buy_amount = self.balance / current_price
                self.holding += buy_amount * (1 - transaction_cost)
                logger.info(f"Bought {buy_amount * (1 - transaction_cost)} BTC at {current_price}")
                self.balance = 0.0
                self.trades.append(('buy', current_price))
        elif action == 2:  # Sell
            if self.holding > 0:
                sell_amount = self.holding
                self.balance += sell_amount * current_price * (1 - transaction_cost)
                logger.info(f"Sold {sell_amount} BTC at {current_price}")
                self.holding = 0.0
                self.trades.append(('sell', current_price))
        # Action 0: Hold, do nothing

        # Calculate reward: change in portfolio value
        portfolio_value = self.balance + self.holding * current_price
        reward = portfolio_value - self.initial_balance
        logger.debug(f"Reward: {reward}")

        # Move to next step
        self.current_step += 1
        done = self.current_step >= self.max_steps
        if done:
            logger.info("Reached end of data. Episode done.")

        # Update observation
        self.state = self._next_observation()

        return self.state, reward, done, {}

    def reset(self) -> np.ndarray:
        """
        Reset the state of the environment to an initial state.
        """
        self.current_step = 0
        self.balance = self.initial_balance
        self.holding = 0.0
        self.trades = []
        self.state = self._next_observation()
        logger.debug("Environment reset.")
        return self.state

    def render(self, mode='human'):
        """
        Render the environment to the screen.
        """
        portfolio_value = self.balance + self.holding * self.data.loc[self.current_step, 'close']
        print(f"Step: {self.current_step}")
        print(f"Balance: {self.balance}")
        print(f"Holding: {self.holding} BTC")
        print(f"Portfolio Value: {portfolio_value}")
