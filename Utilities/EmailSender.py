import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from Utilities.Logger import Logger

class EmailSender:
    def __init__(self, email_address, email_password, smtp_server="smtp.gmail.com", smtp_port=587):
        self.email_address = email_address
        self.email_password = email_password
        self.smtp_server = smtp_server
        self.smtp_port = smtp_port
        self.logger = Logger("EmailSender")
    
    def send_email(self, recipient, subject, body):
        """
        Send an email using the configured SMTP settings.
        
        Args:
            recipient (str): Email address of the recipient
            subject (str): Subject line of the email
            body (str): Email body text
        
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            # Create the email
            msg = MIMEMultipart()
            msg['From'] = self.email_address
            msg['To'] = recipient
            msg['Subject'] = subject
            
            msg.attach(MIMEText(body, 'plain'))

            # Connect to the SMTP server and send the email
            server = smtplib.SMTP(self.smtp_server, self.smtp_port)
            server.ehlo()  # Identify to the SMTP server
            server.starttls()  # Secure the connection
            server.ehlo()  # Re-identify over TLS connection
            server.login(self.email_address, self.email_password)
            server.send_message(msg)
            server.quit()
            self.logger.info("Alert email sent.")
            return True
        except Exception as e:
            self.logger.error(f"Failed to send email: {e}")
            return False