import pytest
import pandas as pd
import numpy as np
from src.feature_engineering import FeatureEngineer

@pytest.fixture
def mock_data():
    """
    Create mock data for testing feature engineering.
    """
    dates = pd.date_range("2020-01-01", periods=10, freq="D")
    return pd.DataFrame({
        "timestamp": dates,
        "open": np.random.rand(10) * 100,
        "high": np.random.rand(10) * 100,
        "low": np.random.rand(10) * 100,
        "close": np.random.rand(10) * 100,
        "volume": (np.random.rand(10) * 1000).astype(int),
    })

def test_rsi_calculation(mock_data):
    """
    Test if RSI is correctly calculated.
    """
    fe = FeatureEngineer()
    result = fe.generate_features(mock_data)
    
    assert "rsi" in result.columns, "RSI column should be present"
    assert not result["rsi"].isnull().all(), "RSI values should not be all null"

def test_moving_average(mock_data):
    """
    Test if moving averages are correctly calculated.
    """
    fe = FeatureEngineer()
    result = fe.generate_features(mock_data)
    
    assert "moving_average" in result.columns, "Moving average column should be present"
    assert not result["moving_average"].isnull().all(), "Moving average values should not be all null"

def test_feature_scaling(mock_data):
    """
    Test if features are scaled correctly (if scaling is implemented).
    """
    fe = FeatureEngineer()
    result = fe.generate_features(mock_data)
    
    if "scaled_close" in result.columns:
        assert not result["scaled_close"].isnull().all(), "Scaled close values should not be all null"
        assert result["scaled_close"].max() <= 1, "Scaled close max value should be <= 1"
        assert result["scaled_close"].min() >= 0, "Scaled close min value should be >= 0"
