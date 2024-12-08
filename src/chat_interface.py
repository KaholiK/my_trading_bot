from fastapi import FastAPI, HTTPException, Depends, status
from pydantic import BaseModel, Field
from typing import List
from fastapi.security import HTTPBasic, HTTPBasicCredentials
import secrets
import os
import openai
import logging
from .logging_monitoring import setup_logging

# Setup logging
setup_logging()
logger = logging.getLogger(__name__)

app = FastAPI()

security = HTTPBasic()

# In-memory storage for credentials
credentials_db = {}

# Load OpenAI API key from environment variable
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
if not OPENAI_API_KEY:
    logger.error("OPENAI_API_KEY environment variable not set.")
    raise RuntimeError("OPENAI_API_KEY environment variable not set.")

openai.api_key = OPENAI_API_KEY

class CredentialInput(BaseModel):
    broker: str = Field(..., examples={"example1": "binance", "example2": "coinbase"})
    api_key: str = Field(..., examples={"example": "your_api_key"})
    api_secret: str = Field(..., examples={"example": "your_api_secret"})

class ChatInput(BaseModel):
    prompt: str = Field(..., example="Generate a trading strategy for BTCUSD based on current market trends.")

@app.post("/set_credentials", status_code=200)
def set_credentials(credential: CredentialInput, credentials: HTTPBasicCredentials = Depends(security)):
    correct_username = secrets.compare_digest(credentials.username, "admin")
    correct_password = secrets.compare_digest(credentials.password, "securepassword123")
    if not (correct_username and correct_password):
        logger.warning("Unauthorized access attempt to set_credentials.")
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Incorrect username or password")
    
    credentials_db[credential.broker] = {
        "api_key": credential.api_key,
        "api_secret": credential.api_secret
    }
    logger.info(f"Credentials for {credential.broker} set successfully.")
    return {"message": f"Credentials for {credential.broker} set successfully"}

@app.get("/get_credentials/{broker}", status_code=200)
def get_credentials(broker: str, credentials: HTTPBasicCredentials = Depends(security)):
    correct_username = secrets.compare_digest(credentials.username, "admin")
    correct_password = secrets.compare_digest(credentials.password, "securepassword123")
    if not (correct_username and correct_password):
        logger.warning("Unauthorized access attempt to get_credentials.")
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Incorrect username or password")
    
    if broker not in credentials_db:
        logger.warning(f"Credentials for {broker} not found.")
        raise HTTPException(status_code=404, detail=f"Credentials for {broker} not found.")
    
    logger.info(f"Credentials for {broker} retrieved successfully.")
    return credentials_db[broker]

@app.delete("/delete_credentials/{broker}", status_code=200)
def delete_credentials(broker: str, credentials: HTTPBasicCredentials = Depends(security)):
    correct_username = secrets.compare_digest(credentials.username, "admin")
    correct_password = secrets.compare_digest(credentials.password, "securepassword123")
    if not (correct_username and correct_password):
        logger.warning("Unauthorized access attempt to delete_credentials.")
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Incorrect username or password")
    
    if broker in credentials_db:
        del credentials_db[broker]
        logger.info(f"Credentials for {broker} deleted successfully.")
        return {"message": f"Credentials for {broker} deleted successfully"}
    else:
        logger.warning(f"Credentials for {broker} not found for deletion.")
        raise HTTPException(status_code=404, detail=f"Credentials for {broker} not found.")

@app.get("/list_exchanges", response_model=List[str], status_code=200)
def list_exchanges(credentials: HTTPBasicCredentials = Depends(security)):
    correct_username = secrets.compare_digest(credentials.username, "admin")
    correct_password = secrets.compare_digest(credentials.password, "securepassword123")
    if not (correct_username and correct_password):
        logger.warning("Unauthorized access attempt to list_exchanges.")
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Incorrect username or password")
    
    exchanges = list(credentials_db.keys())
    logger.info("List of exchanges retrieved successfully.")
    return exchanges

@app.post("/chat", status_code=200)
def chat(chat_input: ChatInput, credentials: HTTPBasicCredentials = Depends(security)):
    """
    Chat endpoint that uses OpenAI's GPT model to generate responses based on user input.
    """
    correct_username = secrets.compare_digest(credentials.username, "admin")
    correct_password = secrets.compare_digest(credentials.password, "securepassword123")
    if not (correct_username and correct_password):
        logger.warning("Unauthorized access attempt to chat endpoint.")
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Incorrect username or password")
    
    try:
        logger.info(f"Received chat prompt: {chat_input.prompt}")
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are a helpful assistant specialized in trading strategies."},
                {"role": "user", "content": chat_input.prompt}
            ]
        )
        reply = response.choices[0].message['content'].strip()
        logger.info("Chat response generated successfully.")
        return {"reply": reply}
    except Exception as e:
        logger.error(f"OpenAI API error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
