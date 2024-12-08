import pytest
import pandas as pd
import numpy as np
import torch
from src.execution_engine import BinanceExecutionEngine
from src.feature_engineering import FeatureEngineer
from src.predictive_models import TimeSeriesPredictor

@pytest.fixture
def integration_components():
    execution_engine = BinanceExecutionEngine()
    feature_engineer = FeatureEngineer()
    predictor = TimeSeriesPredictor(input_dim=1)  # Assuming 'price' as the input feature
    mock_feature_data = pd.DataFrame({
        'timestamp': pd.date_range(start='2020-01-01', periods=100, freq='D'),
        'close': np.random.uniform(low=100, high=200, size=100)  # 'close' will be renamed to 'price'
    })
    return {
        'execution_engine': execution_engine,
        'feature_engineer': feature_engineer,
        'predictor': predictor,
        'mock_feature_data': mock_feature_data
    }

def test_integration_flow_success(integration_components):
    """
    Test the entire flow: feature engineering, predictive modeling, and trade execution.
    """
    fe = integration_components["feature_engineer"]
    predictor = integration_components["predictor"]
    execution_engine = integration_components["execution_engine"]
    mock_feature_data = integration_components["mock_feature_data"]

    # Step 1: Feature Engineering
    features = fe.generate_features(mock_feature_data)
    assert not features.empty, "Features should not be empty"

    # Step 2: Predictive Modeling
    # Ensure all feature columns are numeric
    features_numeric = features[['price']].astype(float)
    if features_numeric.empty:
        raise ValueError("No numeric features available for prediction")

    # Reshape to 3D tensor for LSTM: (batch_size, sequence_length, input_dim)
    X = torch.tensor(features_numeric.values, dtype=torch.float32).unsqueeze(0)  # Batch size of 1
    predictions = predictor.predict(X)
    assert isinstance(predictions, np.ndarray), "Predictions should be a numpy array"
    assert predictions.shape == (1, 1), "Predictions shape should be (1, 1)"

def test_integration_flow_failure_handling(integration_components):
    """
    Test how the system handles invalid data or failures in the pipeline.
    """
    fe = integration_components["feature_engineer"]
    predictor = integration_components["predictor"]
    execution_engine = integration_components["execution_engine"]

    # Mock invalid feature data by passing DataFrame without 'timestamp' column
    with pytest.raises(KeyError):
        fe.generate_features(pd.DataFrame({"feature1": [1, 2, 3], "feature2": [4, 5, 6]}))

def test_integration_concurrent_executions(integration_components):
    """
    Test handling multiple concurrent trade executions.
    """
    execution_engine = integration_components["execution_engine"]
    # Assuming the execution_engine has a method to handle concurrent trades
    trades = [
        {"symbol": "BTCUSD", "quantity": 0.1, "price": 30000},
        {"symbol": "ETHUSD", "quantity": 2, "price": 2000},
        {"symbol": "BNBUSD", "quantity": 5, "price": 300}
    ]
    results = execution_engine.execute_trades_concurrently(trades)
    assert len(results) == len(trades), "All trades should be processed"
    for result, trade in zip(results, trades):
        assert result["symbol"] == trade["symbol"], "Trade symbol should match"
        assert result["quantity"] == trade["quantity"], "Trade quantity should match"
        assert result["price"] == trade["price"], "Trade price should match"
        assert result["status"] == "executed", "Trade status should be 'executed'"

def test_integration_real_data_integration(integration_components):
    """
    Test the system with real-time data (mocked).
    """
    fe = integration_components["feature_engineer"]
    predictor = integration_components["predictor"]
    execution_engine = integration_components["execution_engine"]
    mock_feature_data = integration_components["mock_feature_data"]

    # Perform feature engineering
    features = fe.generate_features(mock_feature_data)

    # Perform prediction
    # Ensure all feature columns are numeric
    features_numeric = features[['price']].astype(float)
    if features_numeric.empty:
        raise ValueError("No numeric features available for prediction")

    # Reshape to 3D tensor for LSTM
    X = torch.tensor(features_numeric.values, dtype=torch.float32).unsqueeze(0)  # Batch size of 1
    predictions = predictor.predict(X)
    assert isinstance(predictions, np.ndarray), "Predictions should be a numpy array"
    assert predictions.shape == (1, 1), "Predictions shape should be (1, 1)"
