import pytest
import torch
import numpy as np
from src.predictive_models import TimeSeriesPredictor

@pytest.fixture
def predictor():
    return TimeSeriesPredictor(input_dim=1)

def test_predictor_forward(predictor):
    """
    Test the forward pass of the predictor.
    """
    # Create a dummy input tensor with shape (batch_size, sequence_length, input_dim)
    X = torch.randn(1, 10, 1)
    output = predictor.forward(X)
    assert isinstance(output, np.ndarray), "Output should be a numpy array"
    assert output.shape == (1, 1), "Output shape should be (1, 1)"

def test_predictor_predict(predictor):
    """
    Test the predict method of the predictor.
    """
    X = torch.randn(1, 10, 1)
    predictions = predictor.predict(X)
    assert isinstance(predictions, np.ndarray), "Predictions should be a numpy array"
    assert predictions.shape == (1, 1), "Predictions shape should be (1, 1)"

def test_predictor_invalid_input(predictor):
    """
    Test the predictor with invalid input dimensions.
    """
    X = torch.randn(10, 1)  # 2D tensor instead of 3D
    with pytest.raises(ValueError):
        predictor.predict(X)
