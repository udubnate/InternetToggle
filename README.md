# InternetToggle

A Python application that monitors internet connectivity, automatically restarts a TP-Link Kasa smart plug when connectivity fails, and sends email notifications about status changes.

## Set Environment Variables

In Windows:
```
setx /M VAR_NAME "VALUE"
```

## Dependencies

For direct installation (without Docker):
```
pip install python-kasa python-dotenv requests asyncio
```

## Docker Setup

### Prerequisites

- [Docker](https://www.docker.com/products/docker-desktop) installed on your system
- [Docker Compose](https://docs.docker.com/compose/install/) (included with Docker Desktop for Windows)

### Environment Variables

Create a `.env` file in the root directory with the following variables:

```
INTERNET_IP="8.8.8.8"
CHECK_INTERVAL="60"
EMAIL_ADDRESS="your-email@example.com"
EMAIL_PASSWORD="your-password"
RECIPIENT_EMAIL="recipient@example.com"
SMTP_SERVER="smtp.gmail.com"
SMTP_PORT="587"
KASA_PLUG_IP="192.168.1.100"
```

### Option 1: Using Docker Compose (Recommended)

1. Build and start the container in one command:

```
docker-compose up -d
```

The `-d` flag runs the container in detached mode (in the background).

2. View logs of the running container:

```
docker-compose logs -f
```

3. Stop the container:

```
docker-compose down
```

### Option 2: Using Docker Run Directly

1. Build the Docker image:

```
docker build -t internet-toggle .
```

2. Run the container with environment variables from `.env` file:

```
docker run -d --network host --name internet-toggle --env-file .env internet-toggle
```

3. Alternatively, specify environment variables directly:

```
docker run -d --network host --name internet-toggle \
  -e INTERNET_IP="8.8.8.8" \
  -e CHECK_INTERVAL="60" \
  -e EMAIL_ADDRESS="your-email@example.com" \
  -e EMAIL_PASSWORD="your-password" \
  -e RECIPIENT_EMAIL="recipient@example.com" \
  -e SMTP_SERVER="smtp.gmail.com" \
  -e SMTP_PORT="587" \
  -e KASA_PLUG_IP="192.168.1.100" \
  internet-toggle
```

4. View logs:

```
docker logs -f internet-toggle
```

5. Stop the container:

```
docker stop internet-toggle
```

6. Remove the container:

```
docker rm internet-toggle
```

## Troubleshooting

- **Network Connectivity Issues**: The container uses host network mode to ensure proper ping functionality. If you're having network issues, make sure your Docker configuration allows host networking.
- **Smart Plug Connection Errors**: Ensure the Kasa smart plug IP address is correct and that the container can reach the device on your network.
- **Email Sending Failures**: Check that your email provider allows SMTP connections from applications. For Gmail, you may need to enable "Less secure app access" or use an App Password.

## Notes

- The application will continuously monitor internet connectivity by pinging the specified IP address.
- When connectivity fails, it will restart the Kasa smart plug and send notification emails.
- Default values are provided for some environment variables if not specified.
