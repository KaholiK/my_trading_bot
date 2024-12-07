FROM python:3.10-slim

WORKDIR /app

RUN apt-get update && apt-get install -y build-essential && rm -rf /var/lib/apt/lists/*

COPY requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

COPY src /app/src
COPY tests /app/tests
COPY main.py /app/main.py

EXPOSE 8000

CMD ["python", "main.py"]

docker build -t kaholik/my-trading-bot:latest .
