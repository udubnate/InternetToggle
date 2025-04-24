import os
import time
import smtplib
import json
import requests
import asyncio
import sys
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Configuration from environment variables
INTERNET_IP = os.getenv("INTERNET_IP", "8.8.8.8")
CHECK_INTERVAL = int(os.getenv("CHECK_INTERVAL", "60"))
EMAIL_ADDRESS = os.getenv("EMAIL_ADDRESS")
EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD")
RECIPIENT_EMAIL = os.getenv("RECIPIENT_EMAIL")
SMTP_SERVER = os.getenv("SMTP_SERVER", "smtp.gmail.com")
SMTP_PORT = int(os.getenv("SMTP_PORT", "587"))

# Kasa device configuration from environment variables
KASA_DEVICE_IP = os.getenv("KASA_DEVICE_IP")
KASA_USERNAME = os.getenv("KASA_USERNAME")
KASA_PASSWORD = os.getenv("KASA_PASSWORD")

# Additional configuration for retry behavior
RETRY_INTERVAL = 180  # 3 minutes in seconds
MAX_RETRY_ATTEMPTS = 3  # Maximum number of retry attempts

def restart_kasa_plug():
    """
    Restart a Kasa smart plug by turning it off, waiting a few seconds, and turning it back on.
    """
    try:
        print("Restarting Kasa smart plug...")
        
        # Turn off the plug
        turn_off_url = f"http://{KASA_DEVICE_IP}/api/v1/device/plugs/power"
        off_payload = {"state": "off"}
        requests.post(turn_off_url, json=off_payload, auth=(KASA_USERNAME, KASA_PASSWORD), timeout=10)
        print("Kasa plug turned off")
        
        # Wait for a few seconds
        time.sleep(5)
        
        # Turn on the plug
        turn_on_url = f"http://{KASA_DEVICE_IP}/api/v1/device/plugs/power"
        on_payload = {"state": "on"}
        requests.post(turn_on_url, json=on_payload, auth=(KASA_USERNAME, KASA_PASSWORD), timeout=10)
        print("Kasa plug turned back on")
        
        return True
    except Exception as e:
        print(f"Failed to restart Kasa plug: {e}")
        return False

def send_email(is_down=True):
    try:
        # Create the email
        msg = MIMEMultipart()
        msg['From'] = EMAIL_ADDRESS
        msg['To'] = RECIPIENT_EMAIL
        
        if is_down:
            msg['Subject'] = "Router Down Alert"
            body = "The router is not responding to pings. Please check your network."
        else:
            msg['Subject'] = "Router Restored Alert"
            body = "The router is back online and responding to pings."
            
        msg.attach(MIMEText(body, 'plain'))

        # Connect to the SMTP server and send the email
        server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
        server.ehlo()  # Identify to the SMTP server
        server.starttls()  # Secure the connection
        server.ehlo()  # Re-identify over TLS connection
        server.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
        server.send_message(msg)
        server.quit()
        print("Alert email sent.")
    except Exception as e:
        print(f"Failed to send email: {e}")

def ping_internetip():
    response = os.system(f"ping -n 1 {INTERNET_IP} >nul 2>&1")
    return response == 0

def main():
    previous_state = None
    down_count = 0
    retry_count = 0
    
    while True:
        current_state = ping_internetip()
        
        if not current_state and (previous_state is None or previous_state):
            # Router just went down
            print("Router is down. Sending alert email...")
            send_email(is_down=True)
            restart_kasa_plug()
            
            # Reset retry counter on initial detection
            retry_count = 0
            
            while (retry_count < MAX_RETRY_ATTEMPTS):
                restart_kasa_plug()
                print(f"Waiting {RETRY_INTERVAL // 60} minutes to check if router recovers (attempt {retry_count + 1}/{MAX_RETRY_ATTEMPTS})...")
                time.sleep(RETRY_INTERVAL)
                
                # Check if router recovered
                if ping_internetip():
                    print("Router is back up after restart!")
                    send_email(is_down=False)
                    break
                else:
                    retry_count += 1
                    print(f"Router still down after restart attempt {retry_count}/{MAX_RETRY_ATTEMPTS}")
                
                # If we've exhausted all retry attempts and router is still down, quit
            if retry_count >= MAX_RETRY_ATTEMPTS:
                    print(f"Router still down after {MAX_RETRY_ATTEMPTS} restart attempts. Exiting program.")
                    send_email(is_down=True)  # Send a final alert
                    sys.exit(1)
            else:
                print("Router recovered before restart was needed.")
                send_email(is_down=False)
                
        elif current_state and (previous_state is None or not previous_state):
            print("Router is up. Sending recovery email...")
            send_email(is_down=False)
            # Reset counters when router comes back
            down_count = 0
            retry_count = 0
            
        elif current_state:
            print("Router is still up.")
        else:
            print("Router is still down, but already being handled by retry logic.")
            
        previous_state = current_state
        time.sleep(CHECK_INTERVAL)

if __name__ == "__main__":
    main()