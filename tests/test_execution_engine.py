import pytest
from src.execution_engine import AlpacaExecutionEngine

@pytest.fixture
def execution_engine():
    return AlpacaExecutionEngine(api_key='test_key', api_secret='test_secret', base_url='https://paper-api.alpaca.markets')

def test_execute_trade(execution_engine):
    """
    Test executing a single trade.
    """
    trade = {"symbol": "BTCUSD", "quantity": 0.1, "price": 30000}
    result = execution_engine.execute_trade(trade)
    assert result["symbol"] == trade["symbol"], "Trade symbol should match"
    assert result["quantity"] == trade["quantity"], "Trade quantity should match"
    assert result["price"] == trade["price"], "Trade price should match"
    assert result["status"] == "executed", "Trade status should be 'executed'"

def test_execute_trades_concurrently(execution_engine):
    """
    Test executing multiple trades concurrently.
    """
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
