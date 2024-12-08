import pytest
import pandas as pd
from src.feature_engineering import FeatureEngineer

@pytest.fixture
def mock_data():
    # Sample data with 'close' column which will be renamed to 'price'
    data = pd.DataFrame({
        'timestamp': pd.date_range(start='2020-01-01', periods=60, freq='D'),
        'open': [100 + i for i in range(60)],
        'high': [110 + i for i in range(60)],
        'low': [90 + i for i in range(60)],
        'close': [105 + i for i in range(60)],
        'volume': [1000 + i*10 for i in range(60)]
    })
    return data

def test_rsi_calculation(mock_data):
    """
    Test if RSI is correctly calculated.
    """
    fe = FeatureEngineer()
    result = fe.generate_features(mock_data)
    assert 'rsi' in result.columns, "RSI column should be present"
    assert not result['rsi'].isnull().all(), "RSI should have valid values"
    # Optionally, check RSI values are within expected range
    assert result['rsi'].min() >= 0 and result['rsi'].max() <= 100, "RSI values should be between 0 and 100"

def test_moving_average(mock_data):
    """
    Test if moving averages are correctly calculated.
    """
    fe = FeatureEngineer()
    result = fe.generate_features(mock_data)
    assert 'moving_average' in result.columns, "Moving Average column should be present"
    assert not result['moving_average'].isnull().all(), "Moving Average should have valid values"
    # Optionally, check if moving average is correctly calculated
    expected_ma = mock_data['close'].rolling(window=14, min_periods=1).mean()
    pd.testing.assert_series_equal(result['moving_average'], expected_ma.rename('moving_average'), check_names=False)

def test_feature_scaling(mock_data):
    """
    Test if feature scaling is correctly applied.
    """
    # Assuming feature scaling is another step; since it's not implemented, this is a placeholder
    fe = FeatureEngineer()
    result = fe.generate_features(mock_data)
    # Example assertion; adjust based on actual scaling implementation
    assert 'rsi' in result.columns and 'moving_average' in result.columns, "Scaled features should be present"
