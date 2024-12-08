# src/predictive_models.py

import torch
import torch.nn as nn
import torch.optim as optim
from typing import Optional, Tuple
import numpy as np

class PredictiveModel:
    """
    Abstract base class for predictive models.
    Defines the interface for training and prediction.
    """
    def train_step(self, X: torch.Tensor, y: torch.Tensor) -> float:
        raise NotImplementedError("train_step must be implemented by subclasses.")

    def evaluate(self, X: torch.Tensor, y: torch.Tensor) -> float:
        raise NotImplementedError("evaluate must be implemented by subclasses.")

    def predict(self, X: torch.Tensor) -> np.ndarray:
        raise NotImplementedError("predict must be implemented by subclasses.")

class LSTMForecaster(nn.Module):
    """
    A simple LSTM-based forecasting model.
    Input: (batch_size, seq_len, input_dim)
    Output: (batch_size, output_dim)
    """
    def __init__(self, input_dim: int = 10, hidden_dim: int = 64, num_layers: int = 2, output_dim: int = 1):
        super(LSTMForecaster, self).__init__()
        self.input_dim = input_dim
        self.hidden_dim = hidden_dim
        self.num_layers = num_layers
        self.output_dim = output_dim

        self.lstm = nn.LSTM(input_size=input_dim, hidden_size=hidden_dim, num_layers=num_layers, batch_first=True)
        self.fc = nn.Linear(hidden_dim, output_dim)
    
    def forward(self, x: torch.Tensor) -> torch.Tensor:
        # x: (B, T, input_dim)
        h0 = torch.zeros(self.num_layers, x.size(0), self.hidden_dim, device=x.device)
        c0 = torch.zeros(self.num_layers, x.size(0), self.hidden_dim, device=x.device)

        out, _ = self.lstm(x, (h0, c0))  # out: (B, T, hidden_dim)
        # Take the last time step's output
        last_output = out[:, -1, :]  # (B, hidden_dim)
        pred = self.fc(last_output)  # (B, output_dim)
        return pred

class TimeSeriesPredictor(PredictiveModel):
    """
    Wraps around LSTMForecaster for training and inference.
    Integrates with feature engineering and data loaders.
    """
    def __init__(self, input_dim: int = 10, hidden_dim: int = 64, num_layers: int = 2, output_dim: int = 1, lr: float = 1e-3):
        self.model = LSTMForecaster(input_dim, hidden_dim, num_layers, output_dim)
        self.criterion = nn.MSELoss()
        self.optimizer = optim.Adam(self.model.parameters(), lr=lr)

    def train_step(self, X: torch.Tensor, y: torch.Tensor) -> float:
        """
        One training step: forward pass, loss, backward pass, optimize.
        X: (B, T, input_dim), y: (B, output_dim)
        """
        self.model.train()
        self.optimizer.zero_grad()
        pred = self.model(X)
        loss = self.criterion(pred, y)
        loss.backward()
        self.optimizer.step()
        return loss.item()

    def evaluate(self, X: torch.Tensor, y: torch.Tensor) -> float:
        """
        Evaluate on a validation or test set.
        """
        self.model.eval()
        with torch.no_grad():
            pred = self.model(X)
            loss = self.criterion(pred, y)
        return loss.item()

    def predict(self, X: torch.Tensor) -> np.ndarray:
        """
        Predict given input data.
        """
        self.model.eval()
        with torch.no_grad():
            pred = self.model(X)
        return pred.cpu().numpy()


if __name__ == "__main__":
    # Mock training example
    # Suppose input_dim=10, sequence_length=30 steps, and we want to predict 1 step ahead price.
    batch_size = 16
    seq_len = 30
    input_dim = 10
    output_dim = 1

    predictor = TimeSeriesPredictor(input_dim=input_dim, output_dim=output_dim)

    # Random data for demonstration
    X_train = torch.randn(batch_size, seq_len, input_dim)
    y_train = torch.randn(batch_size, output_dim)

    loss = predictor.train_step(X_train, y_train)
    print("Training step loss:", loss)

    # In future parts, we’ll integrate real feature data, hyperparameter tuning, and Transformer models.

