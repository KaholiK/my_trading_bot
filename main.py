# main.py

from fastapi import FastAPI, HTTPException
from src.strategies.scalping import ScalpingStrategy

app = FastAPI()
strategy = ScalpingStrategy()

@app.get("/health")
def health_check():
    return {"status": "healthy"}

@app.post("/trade")
def trade(symbol: str):
    try:
        result = strategy.execute_trade(symbol)
        return {"trade_result": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
