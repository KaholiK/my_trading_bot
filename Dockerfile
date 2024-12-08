# Dockerfile

# Use the official Python image as the base
FROM python:3.10-slim AS builder

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Set work directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && \
    apt-get install -y --no-install-recommends gcc && \
    rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copy project files
COPY src/ src/
COPY main.py .

# Create logs directory
RUN mkdir -p logs

# Use a smaller base image for the final stage
FROM python:3.10-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Set work directory
WORKDIR /app

# Copy installed packages from the builder stage
COPY --from=builder /usr/local/lib/python3.10/site-packages /usr/local/lib/python3.10/site-packages
COPY --from=builder /app/src /app/src
COPY --from=builder /app/main.py /app/main.py
COPY --from=builder /app/logs /app/logs

# Expose the port FastAPI runs on
EXPOSE 8000

# Define the default command to run the application
CMD ["python", "main.py"]
