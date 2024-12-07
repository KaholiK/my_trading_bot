# File: tests/test_basic.py
# Basic tests to ensure that the infrastructure is working as intended.
# We'll just do some trivial tests now. Over time, we’ll add more tests for each component.

import pytest
from src.feature_engineering import FeatureEngineer
import pandas as pd
import numpy as np

def test_feature_engineering_basic():
    dates = pd.date_range("2020-01-01", periods=10, freq='D')
    mock_data = pd.DataFrame({
        'timestamp': dates,
        'open': np.random.rand(10)*100,
        'high': np.random.rand(10)*100 + 50,
        'low': np.random.rand(10)*100,
        'close': np.random.rand(10)*100 + 20,
        'volume': (np.random.rand(10)*1000).astype(int)
    })

    fe = FeatureEngineer()
    result = fe.generate_features(mock_data)
    assert 'rsi' in result.columns, "RSI should be computed"
    assert len(result) == 10, "Should have same number of rows"
    # Just a smoke test for now

def test_placeholder():
    assert True, "Just a placeholder test to ensure pytest runs correctly."
