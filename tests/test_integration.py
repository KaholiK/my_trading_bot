import pytest
import asyncio
from httpx import AsyncClient
from src.chat_interface import app
from src.execution_engine import ExecutionEngine
from src.feature_engineering import FeatureEngineer
from src.predictive_models import PredictiveModel
from src.logging_monitoring import setup_logging, log_event

@pytest.fixture
def test_client():
    """
    Fixture to provide an HTTP client for testing FastAPI endpoints.
    """
    client = AsyncClient(app=app, base_url="http://testserver")
    yield client
    asyncio.run(client.aclose())

@pytest.fixture
def mock_execution_engine():
    """
    Fixture to provide a mock execution engine for testing integration.
    """
    return ExecutionEngine()

@pytest.fixture
def mock_feature_engineer():
    """
    Fixture to provide a mock feature engineer for testing integration.
    """
    return FeatureEngineer()

@pytest.fixture
def mock_predictive_model():
    """
    Fixture to provide a mock predictive model for testing integration.
    """
    return PredictiveModel()

def test_logging_setup():
    """
    Test the integration of the logging system.
    """
    setup_logging(log_file="integration_test.log")
    log_event("info", "Integration test log initialized")
    log_event("error", "Simulated error in integration test")

    with open("integration_test.log", "r") as log_file:
        logs = log_file.read()
    assert "INFO:trading_bot:Integration test log initialized" in logs, "Info log should be written to the log file"
    assert "ERROR:trading_bot:Simulated error in integration test" in logs, "Error log should be written to the log file"

@pytest.mark.asyncio
async def test_chat_endpoint(test_client):
    """
    Test the chat interface endpoint for integration with the AI model.
    """
    payload = {"query": "What is the current trading status?"}
    response = await test_client.post("/chat", json=payload)
    assert response.status_code == 200, "Chat endpoint should return HTTP 200"
    assert "response" in response.json(), "Response should include a 'response' key"

@pytest.mark.asyncio
async def test_trade_execution_integration(mock_execution_engine):
    """
    Test the integration of the execution engine with trades.
    """
    trade_result = await mock_execution_engine.execute_trade(
        symbol="BTC-USD", action="BUY", amount=1.5
    )
    assert trade_result["status"] == "success", "Trade execution should return success status"
    assert trade_result["symbol"] == "BTC-USD", "Trade symbol should match input"

@pytest.mark.asyncio
async def test_feature_engineering_integration(mock_feature_engineer):
    """
    Test the integration of feature engineering with mock data.
    """
    mock_data = {
        "timestamp": [1, 2, 3],
        "open": [100, 110, 105],
        "close": [105, 115, 110],
        "high": [110, 120, 115],
        "low": [95, 100, 102],
        "volume": [1000, 1200, 1100],
    }
    features = mock_feature_engineer.generate_features(mock_data)
    assert "rsi" in features.columns, "Feature engineering should compute RSI"
    assert "moving_average" in features.columns, "Feature engineering should compute moving average"

@pytest.mark.asyncio
async def test_predictive_model_integration(mock_predictive_model):
    """
    Test the integration of the predictive model with features.
    """
    mock_features = {
        "rsi": [30, 40, 50],
        "moving_average": [100, 110, 105],
        "volume": [1000, 1200, 1100],
    }
    prediction = await mock_predictive_model.predict(mock_features)
    assert "action" in prediction, "Prediction should include an 'action' key"
    assert prediction["action"] in ["BUY", "SELL", "HOLD"], "Action should be valid"
