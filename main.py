# main.py

import logging
import uvicorn
from src.data_ingestion import BinanceDataSource, CoinbaseDataSource
from src.feature_engineering import FeatureEngineer
from src.predictive_models import TimeSeriesPredictor
from src.decision_fusion import MetaController
from src.execution_engine import BinanceExecutionEngine, CoinbaseExecutionEngine
from src.chat_interface import app as chat_app
from src.logging_monitoring import setup_prometheus, logger

import threading

def main():
    logger.info("Starting AI Trading Bot...")

    # Initialize data ingestion for multiple exchanges
    logger.info("Initializing data ingestion...")
    data_sources = {
        "binance": BinanceDataSource(),
        "coinbase": CoinbaseDataSource()
    }
    for name, source in data_sources.items():
        source.connect()
        source.subscribe(["btcusdt@trade", "ethusdt@trade"])  # Example symbols

    # Initialize feature engineering
    logger.info("Initializing feature engineering...")
    feature_engineer = FeatureEngineer()

    # Initialize predictive model
    logger.info("Initializing predictive model...")
    predictor = TimeSeriesPredictor(input_dim=10, output_dim=1)
    predictor.load_model("models/predictive_model.pt")  # Load saved model

    # Initialize meta-controller
    logger.info("Initializing meta-controller...")
    meta_controller = MetaController()

    # Initialize execution engines for multiple exchanges
    logger.info("Initializing execution engines...")
    execution_engines = {
        "binance": BinanceExecutionEngine(),
        "coinbase": CoinbaseExecutionEngine()
    }

    # Set API credentials for each exchange (replace with actual credentials)
    execution_engines["binance"].set_credentials("binance", "your_binance_api_key", "your_binance_secret_key")
    execution_engines["coinbase"].set_credentials("coinbase", "your_coinbase_api_key", "your_coinbase_secret_key")

    # Start Prometheus metrics server
    threading.Thread(target=setup_prometheus, daemon=True).start()

    # Start the FastAPI chat interface in a separate thread
    def start_chat_interface():
        uvicorn.run(chat_app, host="0.0.0.0", port=8000)

    threading.Thread(target=start_chat_interface, daemon=True).start()

    # Main trading loop
    logger.info("Starting main trading loop...")
    try:
        while True:
            for exchange_name, data_source in data_sources.items():
                # Get raw data from the exchange
                raw_data = data_source.handle_message("{...}")  # Replace with actual data handling
                feature_data = feature_engineer.generate_features(raw_data)

                # Predict next step
                prediction = predictor.predict(feature_data)

                # Fuse signals
                decision = meta_controller.fuse_signals(
                    predictive_signal=prediction[0],
                    rl_action=1,  # Placeholder RL action
                    sentiment_score=0.0  # Placeholder sentiment score
                )

                # Execute trade if necessary
                if decision["final_action"] in ["buy", "sell"]:
                    execution_engines[exchange_name].send_order(
                        symbol="BTCUSDT",  # Example symbol
                        side=decision["final_action"].upper(),
                        quantity=0.01,  # Example quantity
                        order_type="MARKET",
                        price=None
                    )

    except KeyboardInterrupt:
        logger.info("Shutting down AI Trading Bot...")
        for source in data_sources.values():
            source.disconnect()

# Start the application
if __name__ == "__main__":
    main()
