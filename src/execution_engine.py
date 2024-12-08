# src/execution_engine.py

import logging
from concurrent.futures import ThreadPoolExecutor
from alpaca_trade_api import REST

logger = logging.getLogger(__name__)

class AlpacaExecutionEngine:
    def __init__(self):
        self.api = REST('APCA-API-KEY-ID', 'APCA-API-SECRET-KEY', base_url='https://paper-api.alpaca.markets')

    def execute_trade(self, trade):
        """
        Executes a single trade.
        """
        try:
            order = self.api.submit_order(
                symbol=trade["symbol"],
                qty=trade["quantity"],
                side=trade["side"],
                type='market',
                time_in_force='gtc'
            )
            logger.info(f"Trade executed: {trade}")
            return {"symbol": trade["symbol"], "quantity": trade["quantity"], "price": trade["price"], "status": "executed"}
        except Exception as e:
            logger.error(f"Failed to execute trade {trade}: {e}")
            return {"symbol": trade["symbol"], "quantity": trade["quantity"], "price": trade["price"], "status": "failed"}

    def execute_trades_concurrently(self, trades):
        """
        Executes multiple trades concurrently.
        """
        results = []
        with ThreadPoolExecutor(max_workers=5) as executor:
            futures = [executor.submit(self.execute_trade, trade) for trade in trades]
            for future in futures:
                results.append(future.result())
        return results
