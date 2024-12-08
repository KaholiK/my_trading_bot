# tests/test_predictive_models.py

import pytest
import torch
from src.predictive_models import TimeSeriesPredictor

def test_train_step():
    """
    Test the train_step method of TimeSeriesPredictor.
    """
    predictor = TimeSeriesPredictor()
    X = torch.randn(16, 30, 10)  # Example input
    y = torch.randn(16, 1)       # Example target
    loss = predictor.train_step(X, y)
    assert isinstance(loss, float), "Loss should be a float value"

def test_evaluate():
    """
    Test the evaluate method of TimeSeriesPredictor.
    """
    predictor = TimeSeriesPredictor()
    X = torch.randn(16, 30, 10)  # Example input
    y = torch.randn(16, 1)       # Example target
    loss = predictor.evaluate(X, y)
    assert isinstance(loss, float), "Loss should be a float value"

def test_predict():
    """
    Test the predict method of TimeSeriesPredictor.
    """
    predictor = TimeSeriesPredictor()
    X = torch.randn(16, 30, 10)  # Example input
    predictions = predictor.predict(X)
    assert isinstance(predictions, np.ndarray), "Predictions should be a numpy array"
    assert predictions.shape == (16, 1), "Predictions shape mismatch"

def test_predict_with_invalid_input():
    """
    Test the predict method with invalid input to ensure it raises appropriate errors.
    """
    predictor = TimeSeriesPredictor()
    invalid_X = {"invalid_key": 123}
    with pytest.raises(AttributeError):
        predictor.predict(invalid_X)
