import requests
import pandas as pd
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)

class DataIngestion:
    def __init__(self, symbol: str, interval: str = '1h', limit: int = 1000):
        self.symbol = symbol
        self.interval = interval
        self.limit = limit
        self.base_url = 'https://api.binance.com/api/v3/klines'

    def fetch_historical_data(self):
        """
        Fetch historical klines data from Binance API.
        """
        params = {
            'symbol': self.symbol,
            'interval': self.interval,
            'limit': self.limit
        }
        try:
            response = requests.get(self.base_url, params=params)
            response.raise_for_status()
            data = response.json()
            df = pd.DataFrame(data, columns=[
                'timestamp', 'open', 'high', 'low', 'close', 'volume',
                'close_time', 'quote_asset_volume', 'number_of_trades',
                'taker_buy_base_asset_volume', 'taker_buy_quote_asset_volume', 'ignore'
            ])
            df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
            df['close'] = df['close'].astype(float)
            logger.info(f"Fetched {len(df)} rows of historical data for {self.symbol}")
            return df[['timestamp', 'close']]
        except requests.exceptions.HTTPError as http_err:
            logger.error(f"HTTP error occurred while fetching data: {http_err}")
            return pd.DataFrame()
        except Exception as err:
            logger.error(f"Other error occurred while fetching data: {err}")
            return pd.DataFrame()
    
    def fetch_latest_data(self):
        """
        Fetch the latest kline data point.
        """
        params = {
            'symbol': self.symbol,
            'interval': self.interval,
            'limit': 1
        }
        try:
            response = requests.get(self.base_url, params=params)
            response.raise_for_status()
            data = response.json()
            df = pd.DataFrame(data, columns=[
                'timestamp', 'open', 'high', 'low', 'close', 'volume',
                'close_time', 'quote_asset_volume', 'number_of_trades',
                'taker_buy_base_asset_volume', 'taker_buy_quote_asset_volume', 'ignore'
            ])
            df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
            df['close'] = df['close'].astype(float)
            logger.info(f"Fetched latest data point for {self.symbol}")
            return df[['timestamp', 'close']]
        except requests.exceptions.HTTPError as http_err:
            logger.error(f"HTTP error occurred while fetching latest data: {http_err}")
            return pd.DataFrame()
        except Exception as err:
            logger.error(f"Other error occurred while fetching latest data: {err}")
            return pd.DataFrame()

