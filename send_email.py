import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import sys
import os

def send_email(subject, body, to_email):
    # Gmail SMTP settings
    smtp_server = "smtp.gmail.com"
    smtp_port = 587
    sender_email = "sujata.saur@gmail.com"  # Your Gmail address
    
    # Create message
    msg = MIMEMultipart()
    msg['From'] = sender_email
    msg['To'] = to_email
    msg['Subject'] = subject

    # Attach body
    msg.attach(MIMEText(body, 'plain'))

    try:
        # Create SMTP session
        server = smtplib.SMTP(smtp_server, smtp_port)
        server.starttls()  # Enable TLS
        
        # Login to Gmail
        # Use environment variable for the app password
        app_password = os.getenv('GMAIL_APP_PASSWORD')
        if not app_password:
            print("Error: GMAIL_APP_PASSWORD environment variable not set")
            sys.exit(1)
            
        server.login(sender_email, app_password)
        
        # Send email
        server.send_message(msg)
        server.quit()
        print(f"Email sent successfully to {to_email}")
        return True
    except Exception as e:
        print(f"Error sending email: {str(e)}")
        return False

if __name__ == "__main__":
    if len(sys.argv) != 4:
        print("Usage: python send_email.py <subject> <body_file> <to_email>")
        sys.exit(1)
    
    subject = sys.argv[1]
    body_file = sys.argv[2]
    to_email = sys.argv[3]
    
    # Read the body from file
    try:
        with open(body_file, 'r') as f:
            body = f.read()
    except Exception as e:
        print(f"Error reading body file: {str(e)}")
        sys.exit(1)
    
    send_email(subject, body, to_email) 