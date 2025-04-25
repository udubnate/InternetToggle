import os
import time
import asyncio
import sys
from dotenv import load_dotenv
from Utilities.EmailSender import EmailSender
from Utilities.KasaDevice import KasaDevice

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
KASA_PLUG_IP = os.getenv("KASA_PLUG_IP")

# Additional configuration for retry behavior
RETRY_INTERVAL = 180  # 3 minutes in seconds
MAX_RETRY_ATTEMPTS = 3  # Maximum number of retry attempts

# Initialize email sender
email_sender = EmailSender(
    email_address=EMAIL_ADDRESS,
    email_password=EMAIL_PASSWORD,
    smtp_server=SMTP_SERVER,
    smtp_port=SMTP_PORT
)

def restart_kasa_plug():
    """
    Restart a Kasa smart plug by turning it off, waiting a few seconds, and turning it back on.
    """
    try:
        print("Restarting Kasa smart plug...")
        # Write Kasa device restart logic here
        return True
    except Exception as e:
        print(f"Failed to restart Kasa plug: {e}")
        return False

def send_email(is_down=True):
    if is_down:
        subject = "Router Down Alert"
        body = "The router is not responding to pings. Please check your network."
    else:
        subject = "Router Restored Alert"
        body = "The router is back online and responding to pings."
        
    email_sender.send_email(RECIPIENT_EMAIL, subject, body)

def ping_internetip():
    response = os.system(f"ping -n 1 {INTERNET_IP} >nul 2>&1")
    return response == 0

async def main():
    previous_state = None
    retry_count = 0

    kasa = KasaDevice(ip_address=KASA_PLUG_IP)
    

    
    while True:
        current_state = ping_internetip()
        
        if not current_state and (previous_state is None or previous_state):
            # Router just went down
            print("Router is down. Sending alert email...")
            send_email(is_down=True)
            await kasa.restart_device()
            
            # Reset retry counter on initial detection
            retry_count = 0
            
            while (retry_count < MAX_RETRY_ATTEMPTS):
                await kasa.restart_device()
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
            retry_count = 0
            
        elif current_state:
            print("Router is still up.")
        else:
            print("Router is still down, but already being handled by retry logic.")
            
        previous_state = current_state
        time.sleep(CHECK_INTERVAL)

if __name__ == "__main__":
    asyncio.run(main())