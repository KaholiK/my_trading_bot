import pytest
from src.feature_engineering import FeatureEngineer
from src.predictive_models import PredictiveModel
from src.execution_engine import ExecutionEngine

# Mock Data Example
mock_data = {
    "timestamp": "2024-12-07",
    "open": 50000,
    "high": 52000,
    "low": 49000,
    "close": 51000,
    "volume": 1000,
}

@pytest.mark.asyncio
async def test_integration_flow_success():
    """
    Test the entire flow: feature engineering, predictive modeling, and trade execution.
    """
    # Initialize Components
    feature_engineer = FeatureEngineer()
    predictive_model = PredictiveModel()
    execution_engine = ExecutionEngine()

    # Step 1: Feature Engineering
    features = feature_engineer.generate_features(mock_data)
    assert "rsi" in features.columns, "RSI should be computed in features"
    assert "macd" in features.columns, "MACD should be computed in features"
    assert len(features) > 0, "Features should not be empty"

    # Step 2: Predictive Modeling
    prediction = predictive_model.predict(features)
    assert prediction is not None, "Prediction should not be None"
    assert "action" in prediction, "Prediction should include an 'action' key"
    assert prediction["action"] in ["BUY", "SELL", "HOLD"], "Action should be valid"

    # Step 3: Trade Execution
    trade_result = await execution_engine.execute_trade(prediction)
    assert trade_result.get("status") == "SUCCESS", "Trade execution should succeed"
    assert "trade_id" in trade_result, "Trade result should include a trade ID"

@pytest.mark.asyncio
async def test_integration_flow_failure_handling():
    """
    Test how the system handles invalid data or failures in the pipeline.
    """
    # Initialize Components
    feature_engineer = FeatureEngineer()
    predictive_model = PredictiveModel()
    execution_engine = ExecutionEngine()

    # Mock Invalid Data
    invalid_data = {
        "timestamp": "2024-12-07",
        "open": None,
        "high": None,
        "low": None,
        "close": None,
        "volume": None,
    }

    # Step 1: Feature Engineering
    with pytest.raises(ValueError):
        feature_engineer.generate_features(invalid_data)

    # Step 2: Predictive Modeling (on invalid features)
    invalid_features = {"invalid_feature": 0}
    with pytest.raises(KeyError):
        predictive_model.predict(invalid_features)

    # Step 3: Trade Execution (on invalid predictions)
    invalid_prediction = {"action": "INVALID_ACTION"}
    trade_result = await execution_engine.execute_trade(invalid_prediction)
    assert trade_result.get("status") == "FAILURE", "Trade execution should fail for invalid predictions"

@pytest.mark.asyncio
async def test_integration_concurrent_executions():
    """
    Test multiple concurrent trade executions to ensure the system handles concurrency.
    """
    # Initialize Components
    execution_engine = ExecutionEngine()

    # Mock Predictions
    predictions = [
        {"action": "BUY", "symbol": "BTC-USD", "quantity": 0.1},
        {"action": "SELL", "symbol": "ETH-USD", "quantity": 0.5},
    ]

    # Concurrent Execution
    results = await asyncio.gather(*[execution_engine.execute_trade(p) for p in predictions])

    for result in results:
        assert result.get("status") == "SUCCESS", "All trades should succeed concurrently"

@pytest.mark.asyncio
async def test_real_data_integration():
    """
    Test the system with real-time data (if live APIs are available).
    """
    # Initialize Components
    feature_engineer = FeatureEngineer()
    predictive_model = PredictiveModel()
    execution_engine = ExecutionEngine()

    # Fetch Live Data (replace with actual API call or mock)
    live_data = {
        "timestamp": "2024-12-07",
        "open": 48000,
        "high": 49000,
        "low": 47000,
        "close": 48500,
        "volume": 2000,
    }

    # Integration Test
    features = feature_engineer.generate_features(live_data)
    prediction = predictive_model.predict(features)
    trade_result = await execution_engine.execute_trade(prediction)

    assert trade_result.get("status") == "SUCCESS", "Live trade execution should succeed"
