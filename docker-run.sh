#!/bin/bash

# Docker run script for InternetToggle application
# This script runs the InternetToggle application in a Docker container
# using environment variables from the .env file

# Load environment variables from .env file
if [ -f .env ]; then
  export $(grep -v '^#' .env | xargs)
else
  echo "Error: .env file not found"
  exit 1
fi

# Build the Docker image if needed
docker build -t internet-toggle .

# Run the Docker container
docker run -it --rm \
  --name internet-toggle \
  --network host \
  -e INTERNET_IP="${INTERNET_IP:-8.8.8.8}" \
  -e CHECK_INTERVAL="${CHECK_INTERVAL:-60}" \
  -e EMAIL_ADDRESS="${EMAIL_ADDRESS}" \
  -e EMAIL_PASSWORD="${EMAIL_PASSWORD}" \
  -e RECIPIENT_EMAIL="${RECIPIENT_EMAIL}" \
  -e SMTP_SERVER="${SMTP_SERVER:-smtp.gmail.com}" \
  -e SMTP_PORT="${SMTP_PORT:-587}" \
  -e KASA_PLUG_IP="${KASA_PLUG_IP}" \
  -e AUDIT_MODE="${AUDIT_MODE:-False}" \
  -e PYTHONUNBUFFERED=1 \
  -v "$(pwd):/app" \
  internet-toggle

# The --rm flag removes the container when it exits
# The -it flags allocate a pseudo-TTY and keep stdin open
# The --network host flag is required for proper ping functionality
# The -v flag mounts the current directory to /app in the container