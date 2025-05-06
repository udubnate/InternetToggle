@echo off
rem Docker run script for InternetToggle application
rem This script uses PowerShell to load environment variables from .env file
rem and then runs the InternetToggle application in a Docker container

echo Loading environment variables from .env file...
powershell -ExecutionPolicy Bypass -File ".\scripts\Load-Env.ps1"

echo Building Docker image...
docker build -t internet-toggle .

echo Running Docker container...
docker run -it --rm ^
  --name internet-toggle ^
  --network host ^
  -e INTERNET_IP="%INTERNET_IP%" ^
  -e CHECK_INTERVAL="%CHECK_INTERVAL%" ^
  -e EMAIL_ADDRESS="%EMAIL_ADDRESS%" ^
  -e EMAIL_PASSWORD="%EMAIL_PASSWORD%" ^
  -e RECIPIENT_EMAIL="%RECIPIENT_EMAIL%" ^
  -e SMTP_SERVER="%SMTP_SERVER%" ^
  -e SMTP_PORT="%SMTP_PORT%" ^
  -e KASA_PLUG_IP="%KASA_PLUG_IP%" ^
  -e AUDIT_MODE="%AUDIT_MODE%" ^
  -e PYTHONUNBUFFERED=1 ^
  -v "%cd%:/app" ^
  internet-toggle

rem The --rm flag removes the container when it exits
rem The -it flags allocate a pseudo-TTY and keep stdin open
rem The --network host flag is required for proper ping functionality
rem The -v flag mounts the current directory to /app in the container