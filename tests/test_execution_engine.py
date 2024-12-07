import pytest
from src.execution_engine import ExecutionEngine

@pytest.fixture
def mock_trade():
    """
    Mock a trade object for testing.
    """
    return {
        "symbol": "BTC-USD",
        "side": "buy",
        "quantity": 0.1,
        "price": 50000.0,
    }

@pytest.fixture
def execution_engine():
    """
    Create an instance of the ExecutionEngine for testing.
    """
    return ExecutionEngine()

def test_execute_trade_success(mock_trade, execution_engine):
    """
    Test if the execution engine successfully executes a trade.
    """
    result = execution_engine.execute_trade(
        symbol=mock_trade["symbol"],
        side=mock_trade["side"],
        quantity=mock_trade["quantity"],
        price=mock_trade["price"],
    )
    assert result["status"] == "success", "Trade execution should be successful"
    assert "trade_id" in result, "Trade execution result should include a trade ID"

def test_execute_trade_invalid_symbol(execution_engine):
    """
    Test if the execution engine handles invalid trade symbols.
    """
    invalid_trade = {"symbol": "INVALID", "side": "buy", "quantity": 0.1, "price": 50000.0}
    result = execution_engine.execute_trade(
        symbol=invalid_trade["symbol"],
        side=invalid_trade["side"],
        quantity=invalid_trade["quantity"],
        price=invalid_trade["price"],
    )
    assert result["status"] == "error", "Trade execution should fail for invalid symbols"
    assert "message" in result, "Error result should include a message"

def test_monitor_open_trades(execution_engine):
    """
    Test monitoring of open trades.
    """
    execution_engine.open_trades = [
        {"trade_id": 1, "symbol": "BTC-USD", "status": "open"},
        {"trade_id": 2, "symbol": "ETH-USD", "status": "closed"},
    ]
    open_trades = execution_engine.monitor_open_trades()
    assert len(open_trades) == 1, "There should be exactly one open trade"
    assert open_trades[0]["symbol"] == "BTC-USD", "The open trade should be for BTC-USD"

def test_close_trade(execution_engine):
    """
    Test the functionality to close a trade.
    """
    trade_to_close = {"trade_id": 1, "symbol": "BTC-USD", "status": "open"}
    execution_engine.open_trades = [trade_to_close]
    result = execution_engine.close_trade(trade_id=1)
    assert result["status"] == "success", "Closing a trade should return success"
    assert len(execution_engine.open_trades) == 0, "No open trades should remain after closing"
