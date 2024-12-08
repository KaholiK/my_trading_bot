# src/rl_environment.py

import numpy as np
import logging

logger = logging.getLogger(__name__)

class RLEnvironment:
    def __init__(self, initial_balance: float = 10000.0):
        self.initial_balance = initial_balance
        self.balance = initial_balance
        self.position = 0.0  # Current position size
        logger.info("RLEnvironment initialized with initial_balance=%.2f", self.initial_balance)
    
    def reset(self):
        self.balance = self.initial_balance
        self.position = 0.0
        logger.info("RLEnvironment reset.")
        return self._get_state()
    
    def step(self, action: int, price: float):
        """
        Execute an action in the environment.
        
        :param action: 0 = Hold, 1 = Buy, 2 = Sell
        :param price: Current price of the asset
        :return: (next_state, reward, done, info)
        """
        done = False
        reward = 0.0
        info = {}
        
        if action == 1:  # Buy
            if self.balance > price:
                self.position += 1.0
                self.balance -= price
                logger.info("Executed Buy: position=%.2f, balance=%.2f", self.position, self.balance)
        elif action == 2:  # Sell
            if self.position > 0:
                self.position -= 1.0
                self.balance += price
                logger.info("Executed Sell: position=%.2f, balance=%.2f", self.position, self.balance)
        
        # Calculate reward as profit/loss
        current_value = self.balance + self.position * price
        reward = current_value - self.initial_balance
        
        # Optionally, set done based on certain conditions
        if reward < -self.initial_balance * 0.2:  # 20% loss
            done = True
            logger.info("Environment done due to significant loss.")
        
        next_state = self._get_state()
        return next_state, reward, done, info
    
    def _get_state(self):
        """
        Get the current state of the environment.
        """
        return np.array([self.balance, self.position])

