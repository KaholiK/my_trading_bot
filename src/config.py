# config.py

import os
from dotenv import load_dotenv

load_dotenv()

ALPACA_API_KEY = os.getenv("ALPACA_API_KEY")
ALPACA_SECRET_KEY = os.getenv("ALPACA_SECRET_KEY")
ALPACA_PAPER = True  # Set to False for live trading
ALPACA_BASE_URL = "https://paper-api.alpaca.markets" if ALPACA_PAPER else "https://api.alpaca.markets"
