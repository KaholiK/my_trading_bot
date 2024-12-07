# File: src/feature_engineering.py
# Part 2: Feature Engineering
#
# This module handles the transformation of raw price and market data into enriched feature sets.
# We'll add technical indicators, normalization, and placeholders for sentiment/fundamental data.
# Eventually, this pipeline will be integrated with the data ingestion layer and the ML modeling steps.

import pandas as pd
import numpy as np
from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta

class FeatureEngineer:
    """
    The FeatureEngineer class will take in raw market data (ticks, OHLCV, order book data)
    and produce a standardized feature DataFrame with technical indicators and other signals.
    """
    def __init__(self, window_sizes: Optional[List[int]] = None):
        # window_sizes might be used for rolling indicators, e.g. [5, 20, 50]
        self.window_sizes = window_sizes if window_sizes else [5, 20, 50]
    
    def add_technical_indicators(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Add common technical indicators (e.g. moving averages) to the DataFrame.
        Expects a DataFrame with columns: ['timestamp', 'open', 'high', 'low', 'close', 'volume'].
        Returns a DataFrame with additional columns for indicators.
        """
        # Ensure sorted by timestamp
        df = df.sort_values('timestamp')
        
        for w in self.window_sizes:
            # Simple Moving Average
            df[f'sma_{w}'] = df['close'].rolling(window=w).mean()
            # Exponential Moving Average
            df[f'ema_{w}'] = df['close'].ewm(span=w, adjust=False).mean()
        
        # Relative Strength Index (RSI) calculation placeholder
        # RSI requires price differences over a period
        df['change'] = df['close'].diff()
        gain = df['change'].clip(lower=0)
        loss = -1 * df['change'].clip(upper=0)
        window = 14
        avg_gain = gain.ewm(alpha=1/window, adjust=False).mean()
        avg_loss = loss.ewm(alpha=1/window, adjust=False).mean()
        rs = avg_gain / (avg_loss + 1e-10)
        df['rsi'] = 100 - (100 / (1 + rs))
        df.drop('change', axis=1, inplace=True)

        # Bollinger Bands as an example
        df['std_20'] = df['close'].rolling(window=20).std()
        df['bb_upper'] = df['sma_20'] + 2 * df['std_20']
        df['bb_lower'] = df['sma_20'] - 2 * df['std_20']

        return df

    def normalize_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Normalize certain columns (e.g., close, volume, indicators) so models can handle them better.
        In reality, we might fit a scaler (like StandardScaler) on historical data and apply it here.
        For now, do a simple normalization as a placeholder.
        """
        # Columns to normalize (just a placeholder)
        cols_to_normalize = [c for c in df.columns if c not in ['timestamp', 'open', 'high', 'low', 'close', 'volume']]
        for c in cols_to_normalize:
            series = df[c].astype(float)
            mean_val = series.mean()
            std_val = series.std() + 1e-9
            df[c] = (series - mean_val) / std_val
        return df

    def generate_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Full pipeline: Add indicators, then normalize. Eventually, we’ll integrate sentiment/fundamental data.
        """
        df = df.copy()
        df = self.add_technical_indicators(df)
        df = self.normalize_features(df)
        # Future: integrate sentiment scores, fundamental metrics, macro features
        return df


if __name__ == "__main__":
    # Example usage (this will be expanded later as we integrate with data ingestion):
    # Mock some OHLCV data
    dates = pd.date_range(datetime.now() - timedelta(days=60), periods=60, freq='D')
    mock_data = pd.DataFrame({
        'timestamp': dates,
        'open': np.random.rand(60)*100,
        'high': np.random.rand(60)*100 + 100,
        'low': np.random.rand(60)*100,
        'close': np.random.rand(60)*100 + 50,
        'volume': (np.random.rand(60)*1000).astype(int)
    })

    fe = FeatureEngineer()
    feature_df = fe.generate_features(mock_data)
    print(feature_df.head(10))
