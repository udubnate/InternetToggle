FROM python:3.10-slim

WORKDIR /app

# Install ping utility for network connectivity tests
RUN apt-get update && apt-get install -y iputils-ping && apt-get clean

# Copy requirements first to leverage Docker cache
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Default command, can be overridden
CMD ["python", "start.py"]