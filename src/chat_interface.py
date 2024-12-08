# src/chat_interface.py

from fastapi import FastAPI, HTTPException, Body, Depends, WebSocket, WebSocketDisconnect
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from typing import Dict, Optional, List
import logging
from pydantic import BaseModel
from cryptography.fernet import Fernet
import os

app = FastAPI(title="AI Trading Bot Chat Interface")

# Configure Logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger("ChatInterface")

# Security Setup
security = HTTPBasic()

# Generate or load an encryption key for encrypting sensitive data
ENCRYPTION_KEY = os.getenv("ENCRYPTION_KEY") or Fernet.generate_key()
cipher_suite = Fernet(ENCRYPTION_KEY)

# Secure admin credentials
ADMIN_USERNAME = os.getenv("ADMIN_USERNAME", "admin")
ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD", "securepassword123")

# In-memory storage for credentials (replace with a secure storage in production)
credentials_store: Dict[str, Dict[str, str]] = {}

# WebSocket Connections for Notifications
notification_connections: List[WebSocket] = []

class CredentialStore:
    """
    Manages storage and retrieval of encrypted API credentials.
    """
    def __init__(self):
        self.credentials: Dict[str, Dict[str, str]] = {}

    def set_credentials(self, exchange: str, api_key: str, secret_key: str):
        encrypted_api_key = cipher_suite.encrypt(api_key.encode()).decode()
        encrypted_secret_key = cipher_suite.encrypt(secret_key.encode()).decode()
        self.credentials[exchange.lower()] = {
            "api_key": encrypted_api_key,
            "secret_key": encrypted_secret_key,
        }

    def get_credentials(self, exchange: str) -> Dict[str, str]:
        if exchange.lower() not in self.credentials:
            raise ValueError(f"Credentials for {exchange} not found.")
        decrypted_api_key = cipher_suite.decrypt(
            self.credentials[exchange.lower()]["api_key"].encode()
        ).decode()
        decrypted_secret_key = cipher_suite.decrypt(
            self.credentials[exchange.lower()]["secret_key"].encode()
        ).decode()
        return {
            "api_key": decrypted_api_key,
            "secret_key": decrypted_secret_key,
        }

    def delete_credentials(self, exchange: str):
        if exchange.lower() in self.credentials:
            del self.credentials[exchange.lower()]
        else:
            raise ValueError(f"Credentials for {exchange} not found.")

credential_store = CredentialStore()

def authenticate(credentials: HTTPBasicCredentials = Depends(security)):
    """
    Basic authentication for admin endpoints.
    """
    correct_username = credentials.username == ADMIN_USERNAME
    correct_password = credentials.password == ADMIN_PASSWORD
    if not (correct_username and correct_password):
        logger.warning("Failed authentication attempt.")
        raise HTTPException(status_code=401, detail="Invalid credentials")
    return credentials

# Pydantic Models
class CredentialInput(BaseModel):
    exchange: str = Body(..., example="binance")
    api_key: str = Body(..., example="your_api_key")
    secret_key: str = Body(..., example="your_secret_key")

class TradeInsight(BaseModel):
    symbol: str
    trade_type: str
    price: float
    timestamp: str

class Prediction(BaseModel):
    next_move: str
    confidence: float

# API Endpoints

@app.post("/set_credentials", dependencies=[Depends(authenticate)])
def set_credentials(input: CredentialInput):
    """
    Add or update API credentials for a specific exchange.
    """
    try:
        credential_store.set_credentials(input.exchange, input.api_key, input.secret_key)
        logger.info(f"Credentials stored for exchange: {input.exchange}")
        return {"status": "success", "message": f"Credentials stored for {input.exchange}"}
    except Exception as e:
        logger.error(f"Error storing credentials: {e}")
        raise HTTPException(status_code=500, detail="Failed to store credentials.")

@app.get("/get_credentials/{exchange}", dependencies=[Depends(authenticate)])
def get_credentials(exchange: str):
    """
    Retrieve stored credentials for a specific exchange.
    """
    try:
        creds = credential_store.get_credentials(exchange)
        logger.info(f"Credentials retrieved for exchange: {exchange}")
        return {"status": "success", "credentials": creds}
    except ValueError as ve:
        logger.warning(f"Credential retrieval error: {ve}")
        raise HTTPException(status_code=404, detail=str(ve))
    except Exception as e:
        logger.error(f"Error retrieving credentials: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve credentials.")

@app.delete("/delete_credentials/{exchange}", dependencies=[Depends(authenticate)])
def delete_credentials(exchange: str):
    """
    Remove stored credentials for a specific exchange.
    """
    try:
        credential_store.delete_credentials(exchange)
        logger.info(f"Credentials deleted for exchange: {exchange}")
        return {"status": "success", "message": f"Credentials for {exchange} deleted."}
    except ValueError as ve:
        logger.warning(f"Credential deletion error: {ve}")
        raise HTTPException(status_code=404, detail=str(ve))
    except Exception as e:
        logger.error(f"Error deleting credentials: {e}")
        raise HTTPException(status_code=500, detail="Failed to delete credentials.")

@app.get("/list_exchanges", dependencies=[Depends(authenticate)])
def list_exchanges():
    """
    List all exchanges with stored credentials.
    """
    exchanges = list(credential_store.credentials.keys())
    logger.info("Listed all exchanges with stored credentials.")
    return {"status": "success", "exchanges": exchanges}

@app.websocket("/ws/notifications")
async def websocket_notifications(websocket: WebSocket):
    """
    WebSocket endpoint for receiving real-time notifications.
    """
    await websocket.accept()
    notification_connections.append(websocket)
    logger.info(f"Notification WebSocket connected: {websocket.client}")

    try:
        while True:
            await websocket.receive_text()  # Keep the connection alive
    except WebSocketDisconnect:
        notification_connections.remove(websocket)
        logger.info(f"Notification WebSocket disconnected: {websocket.client}")

# Utility Functions for Broadcasting Notifications
async def broadcast_notification(notification: dict):
    """
    Broadcast a notification to all connected WebSocket clients.
    """
    for connection in notification_connections:
        try:
            await connection.send_json(notification)
        except Exception as e:
            logger.error(f"Failed to send notification: {e}")
            notification_connections.remove(connection)

# Example Notification Endpoint (secured)
@app.post("/send_notification", dependencies=[Depends(authenticate)])
async def send_notification(message: str = Body(..., example="Trade executed successfully.")):
    """
    Send a custom notification to all connected WebSocket clients.
    """
    notification = {"type": "custom_notification", "message": message}
    await broadcast_notification(notification)
    logger.info("Custom notification sent to all clients.")
    return {"status": "success", "message": "Notification sent to all clients."}
