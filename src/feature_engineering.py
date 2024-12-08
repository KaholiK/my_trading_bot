import pandas as pd
import logging

logger = logging.getLogger(__name__)

class FeatureEngineer:
    def generate_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Generate features from raw data.
        """
        try:
            df = self.add_technical_indicators(df)
            logger.info("Feature engineering completed successfully.")
        except KeyError as e:
            logger.error(f"Feature engineering failed: {e}")
            raise e
        # Add more feature engineering steps as needed
        return df

    def add_technical_indicators(self, df: pd.DataFrame) -> pd.DataFrame:
        # Check for 'price', else use 'close'
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
        df['delta'] = df['price'].diff()
        gain = (df['delta'] > 0) * df['delta']
        loss = (df['delta'] < 0) * -df['delta']
        window_length = 14
        avg_gain = gain.rolling(window=window_length, min_periods=1).mean()
        avg_loss = loss.rolling(window=window_length, min_periods=1).mean()
        rs = avg_gain / avg_loss
        df['rsi'] = 100 - (100 / (1 + rs))

        # Example: Moving Average
        df['moving_average'] = df['price'].rolling(window=window_length, min_periods=1).mean()

        # Drop intermediate columns
        df.drop(['delta'], axis=1, inplace=True)

        logger.info("Technical indicators added to the dataset.")
        return df

