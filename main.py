import uvicorn
from src import app
from src.continuous_learning import ContinuousLearning
import os
import signal
import sys

# Initialize Continuous Learning with desired symbol
continuous_learning = ContinuousLearning(symbol='BTCUSDT')  # Change symbol as needed

def shutdown_handler(*args):
    continuous_learning.shutdown()
    sys.exit(0)

# Register shutdown handler
for sig in (signal.SIGINT, signal.SIGTERM):
    signal.signal(sig, shutdown_handler)

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
