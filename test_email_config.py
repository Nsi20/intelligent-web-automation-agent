import sys
import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# Add project root to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from config.settings import settings

def test_email_sending():
    print("--- Testing Email Configuration ---")
    print(f"SMTP Host: {settings.smtp_host}")
    print(f"SMTP Port: {settings.smtp_port}")
    print(f"SMTP User: {settings.smtp_user}")
    print(f"Email From: {settings.email_from}")
    print(f"Email To: {settings.email_to}")
    print("-----------------------------------")

    try:
        msg = MIMEMultipart()
        msg['From'] = settings.email_from
        msg['To'] = settings.email_to
        msg['Subject'] = "Test Email from Web Automation Agent"
        
        body = "This is a test email to verify your SMTP configuration."
        msg.attach(MIMEText(body, 'plain'))

        print(f"Attempting to connect to {settings.smtp_host}:{settings.smtp_port}...")
        server = smtplib.SMTP(settings.smtp_host, settings.smtp_port)
        server.set_debuglevel(1) # Enable debug output
        
        print("Starting TLS...")
        server.starttls()
        
        print("Logging in...")
        server.login(settings.smtp_user, settings.smtp_password)
        
        print("Sending message...")
        server.send_message(msg)
        
        print("Quitting...")
        server.quit()
        
        print("\nSUCCESS: Email sent successfully!")
        return True
        
    except Exception as e:
        print(f"\nERROR: Failed to send email.")
        print(f"Error details: {str(e)}")
        
        if "Username and Password not accepted" in str(e):
            print("\nTIP: For Gmail, you often need to use an 'App Password' instead of your regular password.")
            print("Go to Google Account > Security > 2-Step Verification > App passwords.")
        
        return False

if __name__ == "__main__":
    test_email_sending()
