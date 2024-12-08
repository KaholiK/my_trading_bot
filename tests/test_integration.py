import pytest
from src.feature_engineering import FeatureEngineer
from src.predictive_models import PredictiveModel
from src.execution_engine import ExecutionEngine

@pytest.mark.asyncio
async def test_integration_flow():
    # Initialize components
    feature_engineer = FeatureEngineer()
    predictive_model = PredictiveModel()
    execution_engine = ExecutionEngine()

    # Mock data for integration
    mock_data = {
        "timestamp": "2024-12-07",
        "open": 50000,
        "high": 52000,
        "low": 49000,
        "close": 51000,
        "volume": 1000,
    }

    # Step 1: Feature Engineering
    features = feature_engineer.generate_features(mock_data)
    assert "rsi" in features.columns, "RSI should be computed"

    # Step 2: Predictive Modeling
    prediction = predictive_model.predict(features)
    assert prediction is not None, "Prediction should not be None"

    # Step 3: Execution
    trade_result = await execution_engine.execute_trade(prediction)
    assert trade_result.get("status") == "SUCCESS", "Trade execution should succeed"
