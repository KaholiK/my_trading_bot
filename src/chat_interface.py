from fastapi import FastAPI, HTTPException, Depends, status
from pydantic import BaseModel, Field
from typing import List
from fastapi.security import HTTPBasic, HTTPBasicCredentials
import secrets

app = FastAPI()

security = HTTPBasic()

# In-memory storage for credentials
credentials_db = {}

class CredentialInput(BaseModel):
    broker: str = Field(..., examples={"example1": "binance", "example2": "coinbase"})
    api_key: str = Field(..., examples={"example": "your_api_key"})
    api_secret: str = Field(..., examples={"example": "your_api_secret"})

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

