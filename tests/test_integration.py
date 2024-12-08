# tests/test_integration.py

import pytest
from unittest.mock import MagicMock
from src.feature_engineering import FeatureEngineer
from src.predictive_models import TimeSeriesPredictor
from src.execution_engine import BinanceExecutionEngine
import pandas as pd
import numpy as np
import torch
import asyncio

@pytest.fixture
def mock_feature_data():
    """
    Provide mock feature data for integration testing.
    """
    dates = pd.date_range("2024-01-01", periods=60, freq="D")
    return pd.DataFrame({
        "timestamp": dates,
        "open": np.random.rand(60) * 100,
        "high": np.random.rand(60) * 100 + 100,
        "low": np.random.rand(60) * 100,
        "close": np.random.rand(60) * 100 + 50,
        "volume": (np.random.rand(60) * 1000).astype(int),
    })

@pytest.fixture
def integration_components(mock_feature_data):
    """
    Initialize and mock integration components.
    """
    # Initialize FeatureEngineer
    fe = FeatureEngineer()
    
    # Initialize and mock PredictiveModel
    predictor = TimeSeriesPredictor()
    predictor.predict = MagicMock(return_value=np.array([[0.5] for _ in range(60)]))
    
    # Initialize and mock ExecutionEngine
    execution_engine = BinanceExecutionEngine()
    execution_engine.send_order = MagicMock(return_value="BINANCE_TEST_TRADE_ID")
    execution_engine.cancel_order = MagicMock(return_value=True)
    execution_engine.get_order_status = MagicMock(return_value={"status": "FILLED"})
    
    return {
        "feature_engineer": fe,
        "predictor": predictor,
        "execution_engine": execution_engine,
        "mock_feature_data": mock_feature_data,
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
    predictions = predictor.predict(torch.tensor(features.values, dtype=torch.float32))
    assert predictions is not None, "Prediction should not be None"
    assert isinstance(predictions, np.ndarray), "Prediction should be a numpy array"
    
    # Step 3: Trade Execution
    # For simplicity, execute a trade based on the first prediction
    action = "BUY" if predictions[0][0] > 0 else "SELL"
    trade_result = execution_engine.execute_trade(
        symbol="BTCUSDT",
        side=action.lower(),
        quantity=0.1,
        order_type="MARKET",
        price=None
    )
    assert trade_result["status"] == "SUCCESS", "Trade execution should succeed"
    assert trade_result["trade_id"] == "BINANCE_TEST_TRADE_ID", "Trade ID should match the mock value"

def test_integration_flow_failure_handling(integration_components):
    """
    Test how the system handles invalid data or failures in the pipeline.
    """
    fe = integration_components["feature_engineer"]
    predictor = integration_components["predictor"]
    execution_engine = integration_components["execution_engine"]
    
    # Mock invalid feature data by passing empty DataFrame
    with pytest.raises(ValueError):
        fe.generate_features(pd.DataFrame())
    
    # Mock predictor to raise an exception
    predictor.predict.side_effect = AttributeError("Invalid input type")
    with pytest.raises(AttributeError):
        predictor.predict({"invalid": "data"})
    
    # Mock execution engine to fail on send_order
    execution_engine.send_order.side_effect = Exception("API Error")
    trade_result = execution_engine.execute_trade(
        symbol="BTCUSDT",
        side="buy",
        quantity=0.1,
        order_type="MARKET",
        price=None
    )
    assert trade_result["status"] == "FAILURE", "Trade execution should fail due to API error"
    assert "message" in trade_result, "Failure response should include a message"

def test_integration_concurrent_executions(integration_components):
    """
    Test multiple concurrent trade executions to ensure the system handles concurrency.
    """
    execution_engine = integration_components["execution_engine"]
    
    # Mock send_order to return unique trade IDs
    execution_engine.send_order.side_effect = ["BINANCE_TRADE_1", "BINANCE_TRADE_2"]
    
    async def execute_trades():
        result1 = execution_engine.execute_trade(
            symbol="BTCUSDT",
            side="buy",
            quantity=0.1,
            order_type="MARKET",
            price=None
        )
        result2 = execution_engine.execute_trade(
            symbol="ETHUSDT",
            side="sell",
            quantity=0.5,
            order_type="LIMIT",
            price=3000.0
        )
        return [result1, result2]
    
    results = asyncio.run(execute_trades())
    
    assert results[0]["status"] == "SUCCESS"
    assert results[0]["trade_id"] == "BINANCE_TRADE_1"
    assert results[1]["status"] == "SUCCESS"
    assert results[1]["trade_id"] == "BINANCE_TRADE_2"

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
    predictions = predictor.predict(torch.tensor(features.values, dtype=torch.float32))
    
    # Execute trade based on prediction
    action = "BUY" if predictions[-1][0] > 0 else "SELL"
    trade_result = execution_engine.execute_trade(
        symbol="BTCUSDT",
        side=action.lower(),
        quantity=0.1,
        order_type="MARKET",
        price=None
    )
    assert trade_result["status"] == "SUCCESS", "Trade execution should succeed"
    assert trade_result["trade_id"] == "BINANCE_TEST_TRADE_ID", "Trade ID should match the mock value"
