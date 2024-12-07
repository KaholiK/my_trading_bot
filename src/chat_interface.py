from fastapi import FastAPI, HTTPException, Body
from typing import Dict, Optional

app = FastAPI()

# In-memory storage for credentials (temporary, for production use encrypted storage)
credentials_store: Dict[str, Dict[str, str]] = {}

@app.post("/set_credentials")
def set_credentials(
    exchange: str = Body(..., example="binance"),
    api_key: str = Body(..., example="your_api_key"),
    secret_key: str = Body(..., example="your_secret_key")
):
    """
    Add or update API credentials for a specific exchange.
    """
    if not exchange or not api_key or not secret_key:
        raise HTTPException(status_code=400, detail="Invalid input. All fields are required.")

    credentials_store[exchange.lower()] = {
        "api_key": api_key,
        "secret_key": secret_key
    }
    return {"status": "success", "message": f"Credentials stored for {exchange}"}


@app.get("/get_credentials/{exchange}")
def get_credentials(exchange: str):
    """
    Retrieve stored credentials for a specific exchange.
    """
    exchange = exchange.lower()
    if exchange not in credentials_store:
        raise HTTPException(status_code=404, detail=f"No credentials found for {exchange}")

    return {"status": "success", "credentials": credentials_store[exchange]}


@app.delete("/delete_credentials/{exchange}")
def delete_credentials(exchange: str):
    """
    Remove stored credentials for a specific exchange.
    """
    exchange = exchange.lower()
    if exchange not in credentials_store:
        raise HTTPException(status_code=404, detail=f"No credentials found for {exchange}")

    del credentials_store[exchange]
    return {"status": "success", "message": f"Credentials for {exchange} deleted."}


@app.get("/list_exchanges")
def list_exchanges():
    """
    List all exchanges with stored credentials.
    """
    if not credentials_store:
        return {"status": "success", "exchanges": []}

    return {"status": "success", "exchanges": list(credentials_store.keys())}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
from fastapi import FastAPI, HTTPException, Body
from typing import Optional, Dict
import random

app = FastAPI()

# Mock for predictive insights and trade history
mock_trade_history = [
    {"symbol": "BTCUSDT", "trade_type": "BUY", "price": 34000, "timestamp": "2024-12-01T12:30:00Z"},
    {"symbol": "ETHUSDT", "trade_type": "SELL", "price": 1800, "timestamp": "2024-12-02T14:45:00Z"},
]

mock_predictions = {
    "BTCUSDT": {"next_move": "UP", "confidence": 87.5},
    "ETHUSDT": {"next_move": "DOWN", "confidence": 78.3},
}


@app.get("/trade_insights/{symbol}")
def get_trade_insights(symbol: str):
    """
    Fetch recent trade history and prediction for a specific symbol.
    """
    symbol = symbol.upper()
    trade = [t for t in mock_trade_history if t["symbol"] == symbol]
    prediction = mock_predictions.get(symbol, None)

    if not trade and not prediction:
        raise HTTPException(status_code=404, detail=f"No trade insights available for {symbol}.")

    return {
        "status": "success",
        "trade_history": trade,
        "prediction": prediction,
    }


@app.post("/analyze_trade")
def analyze_trade(
    symbol: str = Body(..., example="BTCUSDT"),
    price: float = Body(..., example=34000),
    trade_type: str = Body(..., example="BUY")
):
    """
    Analyze a potential trade and return the bot's suggestion.
    """
    symbol = symbol.upper()
    trade_type = trade_type.upper()

    if trade_type not in ["BUY", "SELL"]:
        raise HTTPException(status_code=400, detail="Invalid trade type. Must be 'BUY' or 'SELL'.")

    # Mock analysis logic
    confidence = random.uniform(70, 95)
    suggestion = "APPROVED" if confidence > 80 else "REJECTED"

    return {
        "status": "success",
        "symbol": symbol,
        "trade_type": trade_type,
        "suggestion": suggestion,
        "confidence": round(confidence, 2),
        "note": f"This is a simulated suggestion for the trade: {trade_type} {symbol} at {price}.",
    }


@app.get("/prediction/{symbol}")
def get_prediction(symbol: str):
    """
    Fetch a prediction for the given symbol.
    """
    symbol = symbol.upper()
    prediction = mock_predictions.get(symbol, None)

    if not prediction:
        raise HTTPException(status_code=404, detail=f"No predictions available for {symbol}.")

    return {"status": "success", "symbol": symbol, "prediction": prediction}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from typing import List
import asyncio
import random

app = FastAPI()

# List of connected WebSocket clients
connected_clients: List[WebSocket] = []


class ConnectionManager:
    """
    Manages WebSocket connections for real-time notifications.
    """
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def broadcast(self, message: str):
        """
        Send a message to all connected clients.
        """
        for connection in self.active_connections:
            try:
                await connection.send_text(message)
            except WebSocketDisconnect:
                self.disconnect(connection)


manager = ConnectionManager()


@app.websocket("/ws/notifications")
async def websocket_notifications(websocket: WebSocket):
    """
    WebSocket endpoint for real-time notifications.
    """
    await manager.connect(websocket)
    try:
        while True:
            # Simulate a market update or notification every 5-10 seconds
            await asyncio.sleep(random.randint(5, 10))
            market_update = {
                "type": "market_update",
                "symbol": "BTCUSDT",
                "price": round(random.uniform(30000, 35000), 2),
                "timestamp": "2024-12-07T15:30:00Z",
            }
            await manager.broadcast(f"Market Update: {market_update}")
    except WebSocketDisconnect:
        manager.disconnect(websocket)


@app.get("/send_notification")
async def send_notification(message: str):
    """
    Send a custom notification to all connected WebSocket clients.
    """
    await manager.broadcast(f"Custom Notification: {message}")
    return {"status": "success", "message": f"Notification sent: {message}"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
from fastapi import FastAPI, HTTPException, Depends
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from cryptography.fernet import Fernet
import os
import secrets

app = FastAPI()

# Basic security for authentication
security = HTTPBasic()

# Generate or load an encryption key for encrypting sensitive data
ENCRYPTION_KEY = os.getenv("ENCRYPTION_KEY") or Fernet.generate_key()
cipher_suite = Fernet(ENCRYPTION_KEY)

# Encrypted credential storage
secure_credentials = {}

# Secure admin password
ADMIN_USERNAME = os.getenv("ADMIN_USERNAME", "admin")
ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD", "securepassword123")


def authenticate(credentials: HTTPBasicCredentials = Depends(security)):
    """
    Basic authentication for admin endpoints.
    """
    if credentials.username != ADMIN_USERNAME or credentials.password != ADMIN_PASSWORD:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    return credentials


@app.post("/secure_credentials")
def set_secure_credentials(exchange: str, api_key: str, secret_key: str, credentials: HTTPBasicCredentials = Depends(authenticate)):
    """
    Store encrypted API credentials for an exchange.
    """
    encrypted_api_key = cipher_suite.encrypt(api_key.encode()).decode()
    encrypted_secret_key = cipher_suite.encrypt(secret_key.encode()).decode()

    secure_credentials[exchange] = {
        "api_key": encrypted_api_key,
        "secret_key": encrypted_secret_key,
    }

    return {"status": "success", "message": f"Credentials for {exchange} securely stored"}


@app.get("/secure_credentials/{exchange}")
def get_secure_credentials(exchange: str, credentials: HTTPBasicCredentials = Depends(authenticate)):
    """
    Retrieve decrypted API credentials for an exchange.
    """
    if exchange not in secure_credentials:
        raise HTTPException(status_code=404, detail="Exchange credentials not found")

    decrypted_api_key = cipher_suite.decrypt(secure_credentials[exchange]["api_key"].encode()).decode()
    decrypted_secret_key = cipher_suite.decrypt(secure_credentials[exchange]["secret_key"].encode()).decode()

    return {
        "exchange": exchange,
        "api_key": decrypted_api_key,
        "secret_key": decrypted_secret_key,
    }


@app.get("/secure_ping")
def secure_ping():
    """
    Public endpoint to test secure server setup.
    """
    return {"status": "success", "message": "Secure API is live"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, ssl_keyfile="path/to/your/key.pem", ssl_certfile="path/to/your/cert.pem")
from fastapi import FastAPI, HTTPException, Request
import logging
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from typing import Optional
import datetime

app = FastAPI()

# Set up logging
logging.basicConfig(
    filename="chat_interface.log",
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger("ChatInterface")

# CORS middleware for cross-origin requests
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Adjust this in production to restrict domains
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Example in-memory storage for credentials
credentials_store = {}

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """
    Global exception handler for unhandled errors.
    Logs the error and returns a standardized response.
    """
    logger.error(f"Unhandled exception at {request.url}: {exc}")
    return JSONResponse(
        status_code=500,
        content={"status": "error", "message": "An unexpected error occurred"},
    )

@app.post("/set_credentials")
def set_credentials(exchange: str, api_key: str, secret_key: str):
    """
    Endpoint to store API credentials for an exchange.
    Includes error handling for invalid inputs.
    """
    try:
        if not exchange or not api_key or not secret_key:
            raise ValueError("Exchange, API key, and Secret key must all be provided.")
        
        credentials_store[exchange] = {
            "api_key": api_key,
            "secret_key": secret_key,
        }
        logger.info(f"Credentials stored for exchange: {exchange}")
        return {"status": "success", "message": f"Credentials for {exchange} stored successfully."}

    except ValueError as ve:
        logger.warning(f"Input validation error: {ve}")
        raise HTTPException(status_code=400, detail=str(ve))
    except Exception as e:
        logger.error(f"Error storing credentials: {e}")
        raise HTTPException(status_code=500, detail="Failed to store credentials.")

@app.get("/get_credentials/{exchange}")
def get_credentials(exchange: str):
    """
    Endpoint to retrieve stored credentials for an exchange.
    Handles cases where credentials are missing or invalid.
    """
    try:
        if exchange not in credentials_store:
            raise ValueError(f"Credentials for {exchange} not found.")

        logger.info(f"Credentials retrieved for exchange: {exchange}")
        return {"exchange": exchange, "credentials": credentials_store[exchange]}

    except ValueError as ve:
        logger.warning(f"Credential retrieval error: {ve}")
        raise HTTPException(status_code=404, detail=str(ve))
    except Exception as e:
        logger.error(f"Error retrieving credentials: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve credentials.")

@app.middleware("http")
async def log_requests(request: Request, call_next):
    """
    Middleware to log all incoming requests and responses.
    """
    start_time = datetime.datetime.utcnow()
    logger.info(f"Received request: {request.method} {request.url}")
    
    response = await call_next(request)
    
    process_time = (datetime.datetime.utcnow() - start_time).total_seconds()
    logger.info(f"Processed request: {request.method} {request.url} in {process_time:.2f}s")
    
    return response

@app.get("/ping")
def ping():
    """
    Simple endpoint to verify server health.
    """
    logger.info("Ping request received.")
    return {"status": "success", "message": "Server is live."}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
import logging
from typing import List

app = FastAPI()

# Set up CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Adjust in production to restrict domains
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Set up logging
logging.basicConfig(
    filename="websocket.log",
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger("WebSocketInterface")

class ConnectionManager:
    """
    Manages WebSocket connections to support multiple clients.
    """
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)
        logger.info("New client connected.")

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)
        logger.info("Client disconnected.")

    async def send_message(self, message: str):
        """
        Broadcast a message to all connected clients.
        """
        logger.info(f"Broadcasting message: {message}")
        for connection in self.active_connections:
            try:
                await connection.send_text(message)
            except Exception as e:
                logger.warning(f"Failed to send message: {e}")

    async def send_message_to_client(self, websocket: WebSocket, message: str):
        """
        Send a message to a specific client.
        """
        try:
            await websocket.send_text(message)
        except Exception as e:
            logger.warning(f"Failed to send message to client: {e}")

manager = ConnectionManager()

@app.get("/")
async def get_home():
    """
    Home route to test WebSocket functionality.
    """
    return HTMLResponse("""
    <!DOCTYPE html>
    <html>
        <head>
            <title>WebSocket Test</title>
        </head>
        <body>
            <h1>WebSocket Test</h1>
            <textarea id="messages" rows="10" cols="30"></textarea><br>
            <input id="messageInput" type="text" placeholder="Type a message"><br>
            <button onclick="sendMessage()">Send</button>
            <script>
                let ws = new WebSocket("ws://localhost:8000/ws");
                ws.onmessage = function(event) {
                    let messages = document.getElementById("messages");
                    messages.value += event.data + "\\n";
                };
                function sendMessage() {
                    let input = document.getElementById("messageInput");
                    ws.send(input.value);
                    input.value = "";
                }
            </script>
        </body>
    </html>
    """)

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """
    WebSocket endpoint to handle real-time communication.
    """
    await manager.connect(websocket)
    try:
        while True:
            data = await websocket.receive_text()
            logger.info(f"Received message: {data}")
            await manager.send_message(f"Server: {data}")
    except WebSocketDisconnect:
        manager.disconnect(websocket)
        logger.info("WebSocket disconnected.")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
from fastapi import FastAPI, Body, HTTPException
from transformers import pipeline
from typing import Dict, Any

app = FastAPI()

# Initialize NLP model for intent recognition
intent_recognizer = pipeline("text-classification", model="facebook/bart-large-mnli")

# Mock intent-response map
intent_responses = {
    "get_trade_info": "Fetching trade information...",
    "get_performance": "Fetching performance data...",
    "set_risk_parameters": "Risk parameters updated.",
    "get_api_status": "Checking API connectivity...",
}

def recognize_intent(user_message: str) -> str:
    """
    Recognize user intent from the message.
    """
    intents = list(intent_responses.keys())
    results = intent_recognizer(user_message, candidate_labels=intents)
    intent = results.get("labels", [""])[0]
    confidence = results.get("scores", [0])[0]
    if confidence < 0.6:
        raise ValueError("Low confidence in intent recognition.")
    return intent

@app.post("/nlp_query")
def nlp_query(user_message: str = Body(...)):
    """
    Process user query using NLP for intent recognition.
    """
    try:
        intent = recognize_intent(user_message)
        response = intent_responses.get(intent, "Unable to process request.")
        return {"status": "success", "intent": intent, "response": response}
    except ValueError as e:
        return {"status": "error", "message": str(e)}

# Example usage
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from typing import List

app = FastAPI()

class ConnectionManager:
    """
    Manages WebSocket connections.
    """
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def broadcast(self, message: str):
        """
        Broadcast a message to all active WebSocket connections.
        """
        for connection in self.active_connections:
            try:
                await connection.send_text(message)
            except WebSocketDisconnect:
                self.disconnect(connection)

manager = ConnectionManager()

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """
    WebSocket endpoint to handle real-time communication.
    """
    await manager.connect(websocket)
    try:
        while True:
            data = await websocket.receive_text()
            # Echo the received message back to the client
            await websocket.send_text(f"Message received: {data}")
    except WebSocketDisconnect:
        manager.disconnect(websocket)

@app.post("/notify")
async def notify_all_clients(message: str = Body(...)):
    """
    Endpoint to send notifications to all connected WebSocket clients.
    """
    await manager.broadcast(message)
    return {"status": "success", "message": "Notification sent to all clients."}

import logging
from fastapi.responses import JSONResponse
from prometheus_client import Counter, Histogram, generate_latest
from fastapi.middleware.cors import CORSMiddleware
from starlette.exceptions import HTTPException as StarletteHTTPException

# Configure Logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("ChatInterface")

# Metrics Setup
REQUEST_COUNT = Counter("requests_total", "Total number of requests received", ["method", "endpoint"])
REQUEST_DURATION = Histogram("request_duration_seconds", "Request duration in seconds", ["method", "endpoint"])

# CORS middleware (if you need external clients)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Replace '*' with specific origins in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Custom Exception Handling
@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    logger.error(f"Unexpected error: {exc}")
    return JSONResponse(
        status_code=500,
        content={"detail": "An internal server error occurred."},
    )

@app.middleware("http")
async def metrics_middleware(request, call_next):
    """
    Middleware to track metrics and log request details.
    """
    method = request.method
    endpoint = request.url.path

    # Increment request counter
    REQUEST_COUNT.labels(method=method, endpoint=endpoint).inc()

    logger.info(f"Incoming request: {method} {endpoint}")
    start_time = request.state.start_time = request.state.time()
    try:
        response = await call_next(request)
        duration = request.state.time() - start_time
        REQUEST_DURATION.labels(method=method, endpoint=endpoint).observe(duration)
        logger.info(f"Processed request: {method} {endpoint} in {duration:.4f} seconds")
        return response
    except Exception as exc:
        logger.error(f"Error processing request: {method} {endpoint} - {exc}")
        raise exc

@app.get("/metrics")
async def metrics():
    """
    Endpoint to expose metrics for Prometheus.
    """
    return Response(content=generate_latest(), media_type="text/plain")
from transformers import pipeline
from typing import Dict, Any

# Load NLP Models (can load at startup for efficiency)
# Sentiment Analysis Model
sentiment_analyzer = pipeline("sentiment-analysis")

# Named Entity Recognition Model (Optional)
ner_model = pipeline("ner")

# Question Answering Model (Optional - requires a context document)
qa_model = pipeline("question-answering")

@app.post("/nlp/sentiment")
async def analyze_sentiment(user_query: str = Body(...)):
    """
    Analyze the sentiment of a user query.
    """
    try:
        result = sentiment_analyzer(user_query)
        return {"query": user_query, "sentiment_analysis": result}
    except Exception as e:
        logger.error(f"Sentiment analysis error: {e}")
        return JSONResponse(
            status_code=500,
            content={"detail": "Failed to process sentiment analysis."},
        )

@app.post("/nlp/ner")
async def extract_entities(user_query: str = Body(...)):
    """
    Extract named entities from a user query.
    """
    try:
        result = ner_model(user_query)
        return {"query": user_query, "entities": result}
    except Exception as e:
        logger.error(f"NER error: {e}")
        return JSONResponse(
            status_code=500,
            content={"detail": "Failed to extract entities."},
        )

@app.post("/nlp/qa")
async def answer_question(user_query: str = Body(...), context: str = Body(...)):
    """
    Answer a user question based on a given context.
    """
    try:
        result = qa_model(question=user_query, context=context)
        return {"query": user_query, "answer": result}
    except Exception as e:
        logger.error(f"QA error: {e}")
        return JSONResponse(
            status_code=500,
            content={"detail": "Failed to answer the question."},
        )
from fastapi.websockets import WebSocket
from fastapi.websockets import WebSocketDisconnect
from typing import List
import asyncio

# Maintain active WebSocket connections
active_connections: List[WebSocket] = []

@app.websocket("/ws/chat")
async def websocket_endpoint(websocket: WebSocket):
    """
    WebSocket endpoint for real-time chat interaction.
    """
    await websocket.accept()
    active_connections.append(websocket)
    logger.info(f"New WebSocket connection: {websocket.client}")

    try:
        while True:
            data = await websocket.receive_text()
            logger.info(f"Message received: {data}")
            
            # Example response logic
            response = f"Server received: {data}"
            await websocket.send_text(response)
    except WebSocketDisconnect:
        active_connections.remove(websocket)
        logger.info(f"WebSocket connection closed: {websocket.client}")


@app.websocket("/ws/updates")
async def websocket_market_updates(websocket: WebSocket):
    """
    WebSocket endpoint for streaming real-time market updates.
    """
    await websocket.accept()
    active_connections.append(websocket)
    logger.info(f"Market updates WebSocket connected: {websocket.client}")

    try:
        while True:
            # Mock real-time market updates
            await asyncio.sleep(1)  # Simulate a delay for updates
            update = {"symbol": "BTC-USD", "price": 42000.0, "timestamp": "2024-12-07T12:00:00"}
            await websocket.send_json(update)
    except WebSocketDisconnect:
        active_connections.remove(websocket)
        logger.info(f"Market updates WebSocket disconnected: {websocket.client}")
import json

# Store active WebSocket connections for notification broadcasting
notification_connections: List[WebSocket] = []


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
            await websocket.receive_text()  # Keep the connection open
    except WebSocketDisconnect:
        notification_connections.remove(websocket)
        logger.info(f"Notification WebSocket disconnected: {websocket.client}")
from src.execution_engine import ExecutionEngine

execution_engine = ExecutionEngine()  # Assuming a unified execution engine for all brokers


async def monitor_trades():
    """
    Monitor active trades and trigger notifications for significant events.
    Example: Profit targets hit, stop-loss triggered, or errors in trade execution.
    """
    while True:
        # Mock trade data (replace with real trade monitoring)
        trades = [
            {"symbol": "BTC-USD", "status": "OPEN", "profit": 200.5},
            {"symbol": "ETH-USD", "status": "CLOSED", "profit": -50.0},
        ]

        for trade in trades:
            # Example: Notify on closed trades or significant profit/loss
            if trade["status"] == "CLOSED":
                notification = {
                    "type": "trade_update",
                    "message": f"Trade closed: {trade['symbol']} with profit {trade['profit']:.2f}",
                }
                await broadcast_notification(notification)

        await asyncio.sleep(5)  # Check trades every 5 seconds
price_alerts = {"BTC-USD": 42000, "ETH-USD": 3000}  # Example thresholds


async def monitor_prices():
    """
    Monitor market prices and send alerts when thresholds are crossed.
    """
    while True:
        # Mock price data (replace with real-time price feeds)
        market_prices = {"BTC-USD": 42100, "ETH-USD": 2990}

        for symbol, alert_price in price_alerts.items():
            current_price = market_prices.get(symbol, 0)
            if current_price >= alert_price:
                notification = {
                    "type": "price_alert",
                    "message": f"Price alert for {symbol}: {current_price} >= {alert_price}",
                }
                await broadcast_notification(notification)

        await asyncio.sleep(10)  # Check prices every 10 seconds
from transformers import pipeline

class NLPQueryProcessor:
    """
    Process natural language queries and map them to appropriate actions or responses.
    """
    def __init__(self):
        self.model = pipeline("text2text-generation", model="google/flan-t5-base")  # Example model
        self.action_map = {
            "ROI": self.get_roi,
            "price alert": self.set_price_alert,
            "trade reason": self.get_trade_reason,
        }

    def process_query(self, query: str):
        """
        Process a user's natural language query and return a structured response.
        """
        # Generate intent using NLP model
        result = self.model(query, max_length=50, num_return_sequences=1)
        intent = result[0]["generated_text"].lower()

        # Match intent to action
        for key, action in self.action_map.items():
            if key in intent:
                return action(query)

        # Default response for unsupported queries
        return {"response": "I'm sorry, I didn't understand your request. Can you rephrase?"}

    def get_roi(self, query: str):
        """
        Example: Calculate ROI for the last 10 trades.
        """
        # Placeholder logic - replace with real trade data logic
        roi = 12.5  # Mocked ROI value
        return {"response": f"The ROI for your last 10 trades is {roi}%"}

    def set_price_alert(self, query: str):
        """
        Example: Set a price alert for a specific asset.
        """
        # Extract asset and price from the query (mocked logic here)
        asset = "ETH"
        price = 3000
        price_alerts[asset] = price
        return {"response": f"Price alert set for {asset} at ${price}."}

    def get_trade_reason(self, query: str):
        """
        Example: Explain why the last trade was executed.
        """
        # Placeholder logic - integrate with trade history
        reason = "The last trade was executed due to a positive signal from the predictive model."
        return {"response": reason}
Code to Add to chat_interface.py:
1. Notification Broadcasting System
python
Copy code
import json

# Store active WebSocket connections for notification broadcasting
notification_connections: List[WebSocket] = []


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
            await websocket.receive_text()  # Keep the connection open
    except WebSocketDisconnect:
        notification_connections.remove(websocket)
        logger.info(f"Notification WebSocket disconnected: {websocket.client}")
2. Trade Monitoring and Alerting
Incorporate real-time trade monitoring and trigger notifications when certain conditions are met.

python
Copy code
from src.execution_engine import ExecutionEngine

execution_engine = ExecutionEngine()  # Assuming a unified execution engine for all brokers


async def monitor_trades():
    """
    Monitor active trades and trigger notifications for significant events.
    Example: Profit targets hit, stop-loss triggered, or errors in trade execution.
    """
    while True:
        # Mock trade data (replace with real trade monitoring)
        trades = [
            {"symbol": "BTC-USD", "status": "OPEN", "profit": 200.5},
            {"symbol": "ETH-USD", "status": "CLOSED", "profit": -50.0},
        ]

        for trade in trades:
            # Example: Notify on closed trades or significant profit/loss
            if trade["status"] == "CLOSED":
                notification = {
                    "type": "trade_update",
                    "message": f"Trade closed: {trade['symbol']} with profit {trade['profit']:.2f}",
                }
                await broadcast_notification(notification)

        await asyncio.sleep(5)  # Check trades every 5 seconds
3. Price Threshold Alerts
Add functionality to notify users when a price threshold is crossed.

python
Copy code
price_alerts = {"BTC-USD": 42000, "ETH-USD": 3000}  # Example thresholds


async def monitor_prices():
    """
    Monitor market prices and send alerts when thresholds are crossed.
    """
    while True:
        # Mock price data (replace with real-time price feeds)
        market_prices = {"BTC-USD": 42100, "ETH-USD": 2990}

        for symbol, alert_price in price_alerts.items():
            current_price = market_prices.get(symbol, 0)
            if current_price >= alert_price:
                notification = {
                    "type": "price_alert",
                    "message": f"Price alert for {symbol}: {current_price} >= {alert_price}",
                }
                await broadcast_notification(notification)

        await asyncio.sleep(10)  # Check prices every 10 seconds
user_preferences: Dict[str, dict] = {}  # Store user-specific preferences


@app.post("/set_preferences")
async def set_user_preferences(user_id: str = Body(...), preferences: dict = Body(...)):
    """
    Set or update user-specific preferences, such as alert thresholds or trade monitoring options.
    """
    user_preferences[user_id] = preferences
    return {"status": "success", "message": "Preferences updated"}


@app.get("/get_preferences")
async def get_user_preferences(user_id: str = Query(...)):
    """
    Retrieve user-specific preferences.
    """
    preferences = user_preferences.get(user_id, {})
    return {"status": "success", "preferences": preferences}
from src.execution_engine import ExecutionEngine

execution_engine = ExecutionEngine()  # Assuming unified execution engine setup


@app.post("/execute_trade")
async def execute_trade(user_id: str = Body(...), trade_details: dict = Body(...)):
    """
    Execute a trade and notify the user about the status.
    """
    try:
        # Example: Simulate order execution (replace with real API calls)
        order_id = execution_engine.send_order(**trade_details)
        notification = {
            "type": "trade_execution",
            "message": f"Trade executed successfully. Order ID: {order_id}",
        }
        await add_user_notification(user_id, notification)
        return {"status": "success", "message": "Trade executed", "order_id": order_id}
    except Exception as e:
        notification = {
            "type": "trade_execution_error",
            "message": f"Trade execution failed: {str(e)}",
        }
        await add_user_notification(user_id, notification)
        return {"status": "error", "message": str(e)}
