# src/chat_interface.py

from fastapi import FastAPI, HTTPException, Depends, status
from pydantic import BaseModel, Field
from typing import List
from fastapi.security import HTTPBasic, HTTPBasicCredentials
import secrets
import os
import openai

app = FastAPI()

security = HTTPBasic()

# In-memory storage for credentials
credentials_db = {}

# Load OpenAI API key from environment variable
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
if not OPENAI_API_KEY:
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
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Incorrect username or password")
    
    credentials_db[credential.broker] = {
        "api_key": credential.api_key,
        "api_secret": credential.api_secret
    }
    return {"message": f"Credentials for {credential.broker} set successfully"}

@app.get("/get_credentials/{broker}", status_code=200)
def get_credentials(broker: str, credentials: HTTPBasicCredentials = Depends(security)):
    correct_username = secrets.compare_digest(credentials.username, "admin")
    correct_password = secrets.compare_digest(credentials.password, "securepassword123")
    if not (correct_username and correct_password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Incorrect username or password")
    
    if broker not in credentials_db:
        raise HTTPException(status_code=404, detail=f"Credentials for {broker} not found.")
    
    return credentials_db[broker]

@app.delete("/delete_credentials/{broker}", status_code=200)
def delete_credentials(broker: str, credentials: HTTPBasicCredentials = Depends(security)):
    correct_username = secrets.compare_digest(credentials.username, "admin")
    correct_password = secrets.compare_digest(credentials.password, "securepassword123")
    if not (correct_username and correct_password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Incorrect username or password")
    
    if broker in credentials_db:
        del credentials_db[broker]
        return {"message": f"Credentials for {broker} deleted successfully"}
    else:
        raise HTTPException(status_code=404, detail=f"Credentials for {broker} not found.")

@app.get("/list_exchanges", response_model=List[str], status_code=200)
def list_exchanges(credentials: HTTPBasicCredentials = Depends(security)):
    correct_username = secrets.compare_digest(credentials.username, "admin")
    correct_password = secrets.compare_digest(credentials.password, "securepassword123")
    if not (correct_username and correct_password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Incorrect username or password")
    
    return list(credentials_db.keys())

@app.post("/chat", status_code=200)
def chat(chat_input: ChatInput, credentials: HTTPBasicCredentials = Depends(security)):
    """
    Chat endpoint that uses OpenAI's GPT model to generate responses based on user prompts.
    """
    correct_username = secrets.compare_digest(credentials.username, "admin")
    correct_password = secrets.compare_digest(credentials.password, "securepassword123")
    if not (correct_username and correct_password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Incorrect username or password")
    
    try:
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are a helpful assistant specialized in trading strategies."},
                {"role": "user", "content": chat_input.prompt}
            ]
        )
        reply = response.choices[0].message['content'].strip()
        return {"reply": reply}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
