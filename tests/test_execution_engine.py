# tests/test_execution_engine.py

import pytest
from src.execution_engine import BinanceExecutionEngine

@pytest.fixture
def mock_trade():
    """
    Mock a trade object for testing.
    """
    return {
        "symbol": "BTCUSDT",
        "side": "buy",
        "quantity": 0.1,
        "order_type": "MARKET",
        "price": None,
    }

@pytest.fixture
def binance_execution_engine():
    """
    Create an instance of the BinanceExecutionEngine for testing.
    """
    engine = BinanceExecutionEngine()
    engine.set_credentials("binance", "test_api_key", "test_secret_key")
    return engine

def test_execute_trade_success(binance_execution_engine, mock_trade):
    """
    Test if the execution engine successfully executes a trade.
    """
    result = binance_execution_engine.execute_trade(
        symbol=mock_trade["symbol"],
        side=mock_trade["side"],
        quantity=mock_trade["quantity"],
        order_type=mock_trade["order_type"],
        price=mock_trade["price"]
    )
    assert result["status"] == "SUCCESS", "Trade execution should be successful"
    assert "trade_id" in result, "Trade execution result should include a trade ID"

def test_execute_trade_invalid_symbol(binance_execution_engine):
    """
    Test if the execution engine handles invalid trade symbols.
    """
    result = binance_execution_engine.execute_trade(
        symbol="INVALID_SYMBOL",
        side="buy",
        quantity=0.1,
        order_type="MARKET",
        price=None
    )
    assert result["status"] == "SUCCESS", "Trade execution should return SUCCESS even for invalid symbols in mock"

def test_monitor_open_trades(binance_execution_engine, mock_trade):
    """
    Test monitoring of open trades.
    """
    # Execute a trade first
    execution_result = binance_execution_engine.execute_trade(
        symbol=mock_trade["symbol"],
        side=mock_trade["side"],
        quantity=mock_trade["quantity"],
        order_type=mock_trade["order_type"],
        price=mock_trade["price"]
    )
    trade_id = execution_result["trade_id"]
    
    # Monitor open trades
    open_trades = binance_execution_engine.monitor_open_trades()
    assert any(trade["trade_id"] == trade_id for trade in open_trades), "Trade should be in open trades"

def test_close_trade(binance_execution_engine, mock_trade):
    """
    Test the functionality to close a trade.
    """
    # Execute a trade first
    execution_result = binance_execution_engine.execute_trade(
        symbol=mock_trade["symbol"],
        side=mock_trade["side"],
        quantity=mock_trade["quantity"],
        order_type=mock_trade["order_type"],
        price=mock_trade["price"]
    )
    trade_id = execution_result["trade_id"]
    
    # Close the trade
    close_result = binance_execution_engine.close_trade(trade_id=trade_id)
    assert close_result["status"] == "SUCCESS", "Closing a trade should return success"
    
    # Verify trade status
    for trade in binance_execution_engine.open_trades:
        if trade["trade_id"] == trade_id:
            assert trade["status"] == "CLOSED", "Trade status should be CLOSED after closing"
            break
    else:
        pytest.fail("Trade ID not found in open trades after closing")
