# src/feature_engineering.py

import pandas as pd
import numpy as np
import logging

logger = logging.getLogger(__name__)

class FeatureEngineer:
    def generate_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Generate features from raw data.
        """
        try:
            # Ensure 'timestamp' column exists
            if 'timestamp' not in df.columns:
                logger.error("Missing required column: timestamp")
                raise KeyError("Missing required column: timestamp")
            
            # Rename 'close' to 'price' if 'price' not present
            if 'price' not in df.columns:
                if 'close' in df.columns:
                    df = df.rename(columns={'close': 'price'})
                    logger.info("Renamed 'close' column to 'price'.")
                else:
                    logger.error("Missing required column: price")
                    raise KeyError("Missing required column: price")
            
            required_columns = ['timestamp', 'price']
            missing_columns = [col for col in required_columns if col not in df.columns]
            if missing_columns:
                logger.error(f"Missing required columns: {', '.join(missing_columns)}")
                raise KeyError(f"Missing required columns: {', '.join(missing_columns)}")
            
            df = df.sort_values('timestamp')
    
            # Example: Calculate RSI
            delta = df['price'].diff()
            gain = (delta > 0) * delta
            loss = (delta < 0) * -delta
            window_length = 14
            avg_gain = gain.rolling(window=window_length, min_periods=1).mean()
            avg_loss = loss.rolling(window=window_length, min_periods=1).mean()
            rs = avg_gain / avg_loss
            df['rsi'] = 100 - (100 / (1 + rs))
    
            # Example: Moving Average
            df['moving_average'] = df['price'].rolling(window=window_length, min_periods=1).mean()
    
            # Additional Features for RL
            df['price_change'] = df['price'].pct_change()
            df['volatility'] = df['price_change'].rolling(window=window_length, min_periods=1).std()
            df['momentum'] = df['price'] - df['price'].shift(window_length)
    
            # Drop intermediate columns
            df.drop(['delta'], axis=1, inplace=True)
    
            logger.info("Technical indicators and RL features added to the dataset.")
            return df
        except KeyError as e:
            logger.error(f"Feature engineering failed: {e}")
            raise e

