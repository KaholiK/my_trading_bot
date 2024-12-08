import logging
from apscheduler.schedulers.background import BackgroundScheduler
from src.data_ingestion import DataIngestion
from src.feature_engineering import FeatureEngineer
from src.predictive_models import TimeSeriesPredictor
import torch
import pandas as pd
import os

logger = logging.getLogger(__name__)

class ContinuousLearning:
    def __init__(self, symbol: str):
        self.symbol = symbol
        self.data_ingestion = DataIngestion(symbol=self.symbol)
        self.feature_engineer = FeatureEngineer()
        self.model_path = f"models/{self.symbol}_predictor.pt"
        self.predictor = TimeSeriesPredictor(input_dim=1)  # Adjust input_dim based on features
        self._load_model()
        self.scheduler = BackgroundScheduler()
        self.scheduler.add_job(self.retrain_model, 'interval', hours=24)  # Retrain daily
        self.scheduler.start()
        logger.info("Continuous Learning initialized and scheduler started.")

    def _load_model(self):
        """
        Load the model if it exists.
        """
        if os.path.exists(self.model_path):
            self.predictor.load_state_dict(torch.load(self.model_path))
            self.predictor.eval()
            logger.info(f"Loaded existing model from {self.model_path}.")
        else:
            logger.info("No existing model found. Initializing a new model.")

    def retrain_model(self):
        """
        Fetch new data, engineer features, and retrain the predictive model.
        """
        logger.info("Starting model retraining process.")
        # Fetch historical data
        df = self.data_ingestion.fetch_historical_data()
        if df.empty:
            logger.warning("No data fetched. Skipping retraining.")
            return
        
        # Feature Engineering
        try:
            features = self.feature_engineer.generate_features(df)
            logger.info("Feature engineering completed.")
        except KeyError as e:
            logger.error(f"Feature engineering failed: {e}")
            return
        
        # Prepare data for training
        X = features[['price']].values  # Assuming 'price' is the feature
        y = self._generate_labels(X)
        
        # Convert to tensors
        X_tensor = torch.tensor(X, dtype=torch.float32).unsqueeze(0)  # Shape: (batch_size, seq_length, input_dim)
        y_tensor = torch.tensor(y, dtype=torch.float32).unsqueeze(1)  # Shape: (batch_size, output_dim)
        
        # Train the model
        self.predictor.train()
        criterion = torch.nn.MSELoss()
        optimizer = torch.optim.Adam(self.predictor.parameters(), lr=0.001)
        
        epochs = 10
        for epoch in range(epochs):
            optimizer.zero_grad()
            outputs = self.predictor(X_tensor)
            loss = criterion(outputs, y_tensor)
            loss.backward()
            optimizer.step()
            logger.info(f"Epoch {epoch+1}/{epochs}, Loss: {loss.item():.4f}")
        
        # Save the model
        os.makedirs(os.path.dirname(self.model_path), exist_ok=True)
        torch.save(self.predictor.state_dict(), self.model_path)
        logger.info(f"Model retrained and saved to {self.model_path}.")

    def _generate_labels(self, X):
        """
        Generate labels for training. For example, next time step price.
        """
        return X[1:].flatten()  # Shifted prices as labels

    def shutdown(self):
        """
        Shutdown the scheduler.
        """
        self.scheduler.shutdown()
        logger.info("Continuous Learning scheduler shut down.")

