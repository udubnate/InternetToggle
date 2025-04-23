import os
import time
import smtplib
import json
import requests
import asyncio
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# Configuration
INTERNET_IP = os.getenv('INTLOG_INTERNETIP') # Replace with a reliable IP address to ping (e.g., Google DNS)
CHECK_INTERVAL = os.getenv('INTTOG_CHECKINTERVAL')  # Time in seconds between pings, defaults to 60
EMAIL_ADDRESS =  os.getenv('INTTOG_EMAILADDRESS')  # Replace with your email address
EMAIL_PASSWORD = os.getenv('INTTOG_EMAILPASSWORD')  # Replace with your app password (not your regular password)
RECIPIENT_EMAIL =  os.getenv('INTTOG_TOEMAILADDRESS') # Replace with recipient's email address
SMTP_SERVER = os.getenv('INTTOG_SMTPSERVER')  # Replace with your SMTP server
SMTP_PORT = os.getenv('INTTOG_SMTPSERVERPORT')  # Port for Gmail with TLS 587 for example
T
# Kasa device configuration
KASA_DEVICE_IP = "192.168.1.100"  # Replace with your Kasa smart plug IP address
KASA_USERNAME = "your_username"  # Replace with your Kasa account username
KASA_PASSWORD = "your_password"  # Replace with your Kasa account password

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
    
    while True:
        current_state = ping_internetip()
        
        if not current_state and (previous_state is None or previous_state):
            print("Router is down. Sending alert email...")
            # restart kasa device plug
            restart_kasa_plug()
            send_email(is_down=True)
        elif current_state and (previous_state is None or not previous_state):
            print("Router is up. Sending recovery email...")
            send_email(is_down=False)
        elif current_state:
            print("Router is still up.")
        else:
            print("Router is still down.")
            
        previous_state = current_state
        time.sleep(CHECK_INTERVAL)

if __name__ == "__main__":
    main()