# src/continuous_learning.py

import logging
import time
from threading import Thread
from typing import Optional
from src.feature_engineering import FeatureEngineer
from src.predictive_models import TimeSeriesPredictor
from src.data_ingestion import BinanceDataSource, CoinbaseDataSource
from src.logging_monitoring import logger

class ModelRetrainer:
    """
    Handles the retraining of predictive models with new data.
    """
    def __init__(
        self,
        predictor: TimeSeriesPredictor,
        feature_engineer: FeatureEngineer,
        data_sources: dict,
        retrain_interval: int = 86400  # Retrain every 24 hours by default
    ):
        """
        Initialize the ModelRetrainer.
        
        :param predictor: Instance of the predictive model.
        :param feature_engineer: Instance of FeatureEngineer.
        :param data_sources: Dictionary of data sources.
        :param retrain_interval: Time in seconds between retraining.
        """
        self.predictor = predictor
        self.feature_engineer = feature_engineer
        self.data_sources = data_sources
        self.retrain_interval = retrain_interval
        self.running = False
        self.thread: Optional[Thread] = None

    def fetch_new_data(self) -> list:
        """
        Fetch new data from all data sources.
        
        :return: List of new data frames.
        """
        new_data = []
        for name, source in self.data_sources.items():
            data = source.fetch_historical_data(symbol="BTCUSDT", interval="1d", lookback_days=60)
            new_data.append(data)
            logger.info(f"Fetched new data from {name}")
        return new_data

    def retrain_model(self, data: list):
        """
        Retrain the predictive model with new data.
        
        :param data: List of data frames.
        """
        logger.info("Starting model retraining...")
        # Combine data from all sources
        combined_data = pd.concat(data, ignore_index=True)
        # Generate features
        features = self.feature_engineer.generate_features(combined_data)
        # Assuming the last column is the target
        X = features.iloc[:-1].values
        y = features['close'].shift(-1).dropna().values  # Example target
        # Retrain the model
        self.predictor.train(X, y)
        # Save the updated model
        self.predictor.save_model("models/predictive_model.pt")
        logger.info("Model retraining completed and saved.")

    def run(self):
        """
        Run the retraining process at specified intervals.
        """
        self.running = True
        while self.running:
            try:
                new_data = self.fetch_new_data()
                self.retrain_model(new_data)
            except Exception as e:
                logger.error(f"Error during model retraining: {e}")
            logger.info(f"Retraining completed. Next retrain in {self.retrain_interval} seconds.")
            time.sleep(self.retrain_interval)

    def start(self):
        """
        Start the retraining thread.
        """
        if not self.running:
            self.thread = Thread(target=self.run, daemon=True)
            self.thread.start()
            logger.info("Model retraining thread started.")

    def stop(self):
        """
        Stop the retraining process.
        """
        self.running = False
        if self.thread:
            self.thread.join()
            logger.info("Model retraining thread stopped.")

# Example Usage
if __name__ == "__main__":
    from src.data_ingestion import BinanceDataSource, CoinbaseDataSource
    import pandas as pd

    # Initialize components
    feature_engineer = FeatureEngineer()
    predictor = TimeSeriesPredictor(input_dim=10, output_dim=1)
    predictor.load_model("models/predictive_model.pt")

    # Initialize data sources
    data_sources = {
        "binance": BinanceDataSource(),
        "coinbase": CoinbaseDataSource()
    }

    for source in data_sources.values():
        source.connect()

    # Initialize and start retrainer
    retrainer = ModelRetrainer(
        predictor=predictor,
        feature_engineer=feature_engineer,
        data_sources=data_sources,
        retrain_interval=86400  # 24 hours
    )
    retrainer.start()

    # Keep the main thread alive
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        retrainer.stop()
        for source in data_sources.values():
            source.disconnect()
        logger.info("Shutting down continuous learning module.")
