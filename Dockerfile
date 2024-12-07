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

# Use the official Python image as a base
FROM python:3.10-slim

# Set the working directory in the container
WORKDIR /app

# Copy the current directory contents into the container at /app
COPY . /app

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Expose the port FastAPI uses
EXPOSE 8000

# Run the application
CMD ["python", "main.py"]
