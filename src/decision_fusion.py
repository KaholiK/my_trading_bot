# src/decision_fusion.py

import pandas as pd
import logging

logger = logging.getLogger(__name__)

class DecisionFusion:
    def __init__(self, strategies):
        """
        Initialize with a list of strategy instances.
        """
        self.strategies = strategies
    
    def combine_signals(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Combine signals from multiple strategies to make a final decision.
        """
        df['combined_signal'] = 0
        for strategy in self.strategies:
            signals = strategy.generate_signals(df)
            df['combined_signal'] += signals['signal']
        
        # Normalize combined signals
        df['combined_signal'] = df['combined_signal'].apply(lambda x: 1 if x > 0 else (-1 if x < 0 else 0))
        
        logger.info("Signals combined from all strategies.")
        return df
