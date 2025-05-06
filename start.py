import os
import time
import asyncio
import sys
from dotenv import load_dotenv
from Utilities.EmailSender import EmailSender
from Utilities.KasaDevice import KasaDevice
from Utilities.Logger import Logger

# Initialize logger
logger = Logger("Main")

# Add startup message immediately
logger.info("InternetToggle application starting...")
logger.info("------------------------------------------")

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
AUDIT_MODE = os.getenv("AUDIT_MODE", "False").lower() in ("true", "1", "t", "yes")

# Print configuration (without sensitive data)
logger.info(f"Configuration loaded:")
logger.info(f"INTERNET_IP: {INTERNET_IP}")
logger.info(f"CHECK_INTERVAL: {CHECK_INTERVAL} seconds")
logger.info(f"SMTP_SERVER: {SMTP_SERVER}")
logger.info(f"SMTP_PORT: {SMTP_PORT}")
logger.info(f"KASA_PLUG_IP: {KASA_PLUG_IP}")
logger.info(f"AUDIT_MODE: {AUDIT_MODE}")
logger.info("------------------------------------------")

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
        logger.info("Restarting Kasa smart plug...")
        # Write Kasa device restart logic here
        return True
    except Exception as e:
        logger.error(f"Failed to restart Kasa plug: {e}")
        return False

def send_email(is_down=True):
    if is_down:
        subject = "Router Down Alert"
        body = "The router is not responding to pings. Please check your network."
        if AUDIT_MODE:
            subject = "[AUDIT MODE] " + subject
            body = "[AUDIT MODE] " + body
    else:
        subject = "Router Restored Alert"
        body = "The router is back online and responding to pings."
        if AUDIT_MODE:
            subject = "[AUDIT MODE] " + subject
            body = "[AUDIT MODE] " + body
        
    email_sender.send_email(RECIPIENT_EMAIL, subject, body)

def ping_internetip():
    """
    Ping the configured internet IP to check connectivity.
    Works on both Windows and Linux.
    """
    # Detect operating system
    if os.name == 'nt':  # Windows
        command = f"ping -n 1 {INTERNET_IP} >nul 2>&1"
    else:  # Linux/Unix
        command = f"ping -c 1 {INTERNET_IP} >/dev/null 2>&1"
    
    response = os.system(command)
    return response == 0

async def main():
    previous_state = None
    retry_count = 0

    logger.info("Initializing Kasa device...")
    kasa = KasaDevice(ip_address=KASA_PLUG_IP)
    
    if AUDIT_MODE:
        logger.info("AUDIT MODE ENABLED: Device interactions will be simulated")
    
    while True:
        logger.info("Checking router status...")
        current_state = ping_internetip()
        
        if not current_state and (previous_state is None or previous_state):
            # Router might be down - verify with 3 consecutive ping tests
            logger.warning("Initial ping test failed. Performing 3 additional tests to confirm...")
            confirmation_count = 0
            for i in range(3):
                logger.info(f"Confirmation test {i+1}/3...")
                time.sleep(5)  # Wait 5 seconds between tests
                if not ping_internetip():
                    confirmation_count += 1
                else:
                    logger.info("Ping test passed during confirmation. Router appears to be working.")
                    break
            
            # Only proceed with restart if all 3 confirmation tests failed
            if confirmation_count == 3:
                # Router confirmed to be down
                logger.warning("Router is down (confirmed by 3 failed tests). Sending alert email...")
                send_email(is_down=True)
                await kasa.restart_device()
                
                # Reset retry counter on initial detection
                retry_count = 0
                
                while (retry_count < MAX_RETRY_ATTEMPTS):
                    await kasa.restart_device()
                    logger.info(f"Waiting {RETRY_INTERVAL // 60} minutes to check if router recovers (attempt {retry_count + 1}/{MAX_RETRY_ATTEMPTS})...")
                    time.sleep(RETRY_INTERVAL)
                    
                    # Check if router recovered
                    if ping_internetip():
                        logger.info("Router is back up after restart!")
                        send_email(is_down=False)
                        break
                    else:
                        retry_count += 1
                        logger.warning(f"Router still down after restart attempt {retry_count}/{MAX_RETRY_ATTEMPTS}")
                    
                # If we've exhausted all retry attempts and router is still down, quit
                if retry_count >= MAX_RETRY_ATTEMPTS:
                    logger.error(f"Router still down after {MAX_RETRY_ATTEMPTS} restart attempts. Exiting program.")
                    send_email(is_down=True)  # Send a final alert
                    sys.exit(1)
                else:
                    logger.info("Router recovered before restart was needed.")
                    send_email(is_down=False)
            else:
                logger.info(f"Router connectivity restored during confirmation tests ({3-confirmation_count}/3 tests passed). No restart needed.")
                
        elif current_state and (previous_state is None or not previous_state):
            logger.info("Router is up. Sending recovery email...")
            send_email(is_down=False)
            # Reset counters when router comes back
            retry_count = 0
            
        elif current_state:
            logger.debug("Router is still up.")
        else:
            logger.debug("Router is still down, but already being handled by retry logic.")
            
        previous_state = current_state
        time.sleep(CHECK_INTERVAL)

if __name__ == "__main__":
    asyncio.run(main())