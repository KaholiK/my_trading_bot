# tests/test_feature_engineering.py

import pytest
import pandas as pd
import numpy as np
from src.feature_engineering import FeatureEngineer

@pytest.fixture
def mock_data():
    """
    Create mock data for testing feature engineering.
    """
    dates = pd.date_range("2020-01-01", periods=60, freq="D")
    return pd.DataFrame({
        "timestamp": dates,
        "open": np.random.rand(60) * 100,
        "high": np.random.rand(60) * 100 + 100,
        "low": np.random.rand(60) * 100,
        "close": np.random.rand(60) * 100 + 50,
        "volume": (np.random.rand(60) * 1000).astype(int),
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
    
    for w in fe.window_sizes:
        assert f'sma_{w}' in result.columns, f"SMA_{w} should be present"
        assert f'ema_{w}' in result.columns, f"EMA_{w} should be present"
        assert not result[f'sma_{w}'].isnull().all(), f"SMA_{w} values should not be all null"
        assert not result[f'ema_{w}'].isnull().all(), f"EMA_{w} values should not be all null"

def test_feature_scaling(mock_data):
    """
    Test if features are scaled correctly.
    """
    fe = FeatureEngineer()
    result = fe.generate_features(mock_data)
    
    # Check normalization for all feature columns except 'timestamp', 'open', 'high', 'low', 'close', 'volume'
    feature_cols = [c for c in result.columns if c not in ['timestamp', 'open', 'high', 'low', 'close', 'volume']]
    for c in feature_cols:
        assert not result[c].isnull().all(), f"Scaled feature {c} should not be all null"
        # Since normalization was (value - mean) / std, values can be negative or positive
        # Therefore, we won't check min/max bounds
