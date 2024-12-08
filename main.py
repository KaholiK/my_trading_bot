# main.py

from src.logging_monitoring import setup_prometheus, setup_logging
from fastapi import FastAPI
import uvicorn

# Initialize logging
logger = setup_logging()

# Initialize Prometheus metrics
setup_prometheus(port=8001)

app = FastAPI()

# Define your routes here
@app.get("/")
def read_root():
    return {"Hello": "World"}

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
