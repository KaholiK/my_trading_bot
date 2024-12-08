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
from src.continuous_learning import ModelRetrainer
from src.llm_integration import LLMIntegration
from src.risk_management import RiskManager
from src.rl_environment import TradingEnv

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

    # Initialize Risk Manager
    logger.info("Initializing risk manager...")
    risk_manager = RiskManager(
        max_position_size=0.5,
        max_drawdown=0.10,  # 10%
        stop_loss_percentage=0.03  # 3%
    )

    # Initialize LLM Integration
    logger.info("Initializing LLM Integration...")
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
    if not OPENAI_API_KEY:
        logger.error("OpenAI API key not found. Please set the OPENAI_API_KEY environment variable.")
        exit(1)
    llm = LLMIntegration(api_key=OPENAI_API_KEY)

    # Initialize RL Environment and Agent
    logger.info("Initializing RL Environment...")
    # Fetch historical data required for the RL environment
    historical_data = data_sources["binance"].fetch_historical_data(symbol="BTCUSDT", interval="1d", lookback_days=60)
    env = TradingEnv(data=historical_data, feature_engineer=feature_engineer)

    # Initialize Model Retrainer
    logger.info("Initializing model retrainer...")
    retrainer = ModelRetrainer(
        predictor=predictor,
        feature_engineer=feature_engineer,
        data_sources=data_sources,
        retrain_interval=86400  # 24 hours
    )
    retrainer.start()

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

                # Get sentiment score
                sentiment = llm.get_sentiment_scores(symbol=exchange_name.upper() + "USDT", count=5)

                # Fuse signals
                decision = meta_controller.fuse_signals(
                    predictive_signal=prediction[0],
                    rl_action=1,  # Placeholder RL action
                    sentiment_score=sentiment
                )

                # Enforce risk before executing trade
                approved_size = risk_manager.enforce_risk(symbol="BTCUSDT", desired_size=0.1)
                if approved_size > 0:
                    # Execute trade
                    execution_engines[exchange_name].send_order(
                        symbol="BTCUSDT",  # Example symbol
                        side=decision["final_action"].upper(),
                        quantity=approved_size,
                        order_type="MARKET",
                        price=None
                    )

    except KeyboardInterrupt:
        logger.info("Shutting down AI Trading Bot...")
        retrainer.stop()
        for source in data_sources.values():
            source.disconnect()

# Start the application
if __name__ == "__main__":
    main()
