# src/chat_interface.py

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from src.execution_engine import AlpacaExecutionEngine
from src.config import ALPACA_API_KEY, ALPACA_API_SECRET
from src.logging_monitoring import logger
from src.risk_management import RiskManager
import os

router = APIRouter()

# Initialize Execution Engine
BASE_URL = "https://paper-api.alpaca.markets"
execution_engine = AlpacaExecutionEngine(api_key=ALPACA_API_KEY, api_secret=ALPACA_API_SECRET, base_url=BASE_URL, device='cpu')

# Initialize Risk Manager
risk_manager = RiskManager()

# Authentication Dependency
def authenticate(username: str, password: str):
    # Implement authentication logic
    if username != "admin" or password != "securepassword123":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials",
            headers={"WWW-Authenticate": "Basic"},
        )

# Pydantic Models
class CredentialsInput(BaseModel):
    broker: str
    api_key: str
    api_secret: str

class TradeCommand(BaseModel):
    symbol: str
    action: str
    quantity: int

class PerformanceQuery(BaseModel):
    metric: str

@router.post("/set_credentials")
def set_credentials(credentials: CredentialsInput, username: str = Depends(authenticate)):
    # Securely store credentials, e.g., in environment variables or encrypted storage
    os.environ[f"{credentials.broker.upper()}_API_KEY"] = credentials.api_key
    os.environ[f"{credentials.broker.upper()}_API_SECRET"] = credentials.api_secret
    logger.info(f"Credentials for {credentials.broker} set successfully.")
    return {"message": f"Credentials for {credentials.broker} set successfully"}

@router.get("/get_credentials/{broker}")
def get_credentials(broker: str, username: str = Depends(authenticate)):
    api_key = os.getenv(f"{broker.upper()}_API_KEY")
    api_secret = os.getenv(f"{broker.upper()}_API_SECRET")
    if not api_key or not api_secret:
        raise HTTPException(status_code=404, detail=f"Credentials for {broker} not found")
    return {"api_key": api_key, "api_secret": api_secret}

@router.post("/execute_trade")
def execute_trade(command: TradeCommand, username: str = Depends(authenticate)):
    # Execute trade based on command
    trade = {
        "symbol": command.symbol,
        "quantity": command.quantity,
        "action": command.action,
        "price": 0  # Placeholder, implement actual price retrieval
    }
    result = execution_engine.execute_trade(trade)
    return {"trade_result": result}

@router.post("/query_performance")
def query_performance(query: PerformanceQuery, username: str = Depends(authenticate)):
    # Handle performance queries
    if query.metric == "current_drawdown":
        return {"current_drawdown": risk_manager.current_drawdown}
    elif query.metric == "portfolio_value":
        return {"portfolio_value": risk_manager.portfolio_value}
    else:
        raise HTTPException(status_code=400, detail="Invalid performance metric")


# src/chat_interface.py

from cryptography.fernet import Fernet

# Generate a key and instantiate a Fernet instance
# In production, store this key securely and do not hardcode
key = Fernet.generate_key()
cipher_suite = Fernet(key)

@router.post("/set_credentials")
def set_credentials(credentials: CredentialsInput, username: str = Depends(authenticate)):
    encrypted_api_key = cipher_suite.encrypt(credentials.api_key.encode()).decode()
    encrypted_api_secret = cipher_suite.encrypt(credentials.api_secret.encode()).decode()
    os.environ[f"{credentials.broker.upper()}_ENCRYPTED_API_KEY"] = encrypted_api_key
    os.environ[f"{credentials.broker.upper()}_ENCRYPTED_API_SECRET"] = encrypted_api_secret
    logger.info(f"Credentials for {credentials.broker} set successfully.")
    return {"message": f"Credentials for {credentials.broker} set successfully"}

@router.get("/get_credentials/{broker}")
def get_credentials(broker: str, username: str = Depends(authenticate)):
    encrypted_api_key = os.getenv(f"{broker.upper()}_ENCRYPTED_API_KEY")
    encrypted_api_secret = os.getenv(f"{broker.upper()}_ENCRYPTED_API_SECRET")
    if not encrypted_api_key or not encrypted_api_secret:
        raise HTTPException(status_code=404, detail=f"Credentials for {broker} not found")
    api_key = cipher_suite.decrypt(encrypted_api_key.encode()).decode()
    api_secret = cipher_suite.decrypt(encrypted_api_secret.encode()).decode()
    return {"api_key": api_key, "api_secret": api_secret}
