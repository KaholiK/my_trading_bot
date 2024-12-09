# src/strategies/scalping.py

import pandas as pd
import numpy as np
import logging

logger = logging.getLogger(__name__)

class ScalpingStrategy:
    def __init__(self, quick_threshold=0.001):
        self.quick_threshold = quick_threshold  # Define threshold for quick trades
    
    def generate_signals(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Generate buy/sell signals based on rapid price movements.
        """
        df['signal'] = 0
        df['price_change'] = df['price'].pct_change()
        
        df.loc[df['price_change'] > self.quick_threshold, 'signal'] = 1  # Buy
        df.loc[df['price_change'] < -self.quick_threshold, 'signal'] = -1  # Sell
        
        logger.info("Scalping signals generated.")
        return df
