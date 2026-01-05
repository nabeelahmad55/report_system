# app/email_service.py
import smtplib
import os
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
from datetime import datetime  # ✅ Make sure this line exists

# ✅ ADD THESE 2 LINES
from dotenv import load_dotenv
if os.environ.get("ENV") != "PRODUCTION":
    load_dotenv()

def send_email(to_email: str, subject: str, body: str, pdf_path: str) -> bool:
    """
    Main email sending function
    Returns: True if successful, False if failed
    """
    print(f"\n{'='*60}")
    print(f"📧 EMAIL SERVICE - {datetime.now().strftime('%H:%M:%S')}")
    print('='*60)
    
    # Get credentials from environment
    sender_email = os.environ.get("EMAIL_SENDER")
    sender_password = os.environ.get("EMAIL_PASSWORD")
    
    if not sender_email or not sender_password:
        print("❌ Email credentials not found in environment variables")
        return False
    
    sender_password = str(sender_password).replace(" ", "")
    
    print(f"From: {sender_email}")
    print(f"To: {to_email}")
    print(f"Subject: {subject}")
    print(f"PDF: {pdf_path}")
    print(f"Password: {sender_password[:4]}... ({len(sender_password)} chars)")
    
    if not os.path.exists(pdf_path):
        print(f"❌ ERROR: PDF file not found: {pdf_path}")
        return False
    
    try:
        # Create email message
        msg = MIMEMultipart()
        msg['From'] = sender_email
        msg['To'] = to_email
        msg['Subject'] = subject
        
        # Add body text
        msg.attach(MIMEText(body, 'plain'))
        
        # Attach PDF file
        filename = os.path.basename(pdf_path)
        with open(pdf_path, "rb") as file:
            part = MIMEBase("application", "octet-stream")
            part.set_payload(file.read())
        
        encoders.encode_base64(part)
        part.add_header(
            "Content-Disposition",
            f"attachment; filename={filename}",
        )
        msg.attach(part)
        
        # Connect to Gmail SMTP server
        print("\n🔌 Connecting to Gmail SMTP server...")
        server = smtplib.SMTP("smtp.gmail.com", 587)
        server.starttls()  # Secure the connection
        print("✅ Connected successfully")
        
        print("🔑 Authenticating...")
        server.login(sender_email, sender_password)
        print("✅ Authentication successful")
        
        print("📤 Sending email...")
        text = msg.as_string()
        server.sendmail(sender_email, to_email, text)
        server.quit()
        
        print(f"✅ Email sent successfully to {to_email}")
        print('='*60)
        
        # Log the successful send
        log_email_success(to_email, subject, pdf_path)
        
        return True
        
    except smtplib.SMTPAuthenticationError:
        print("❌ SMTP Authentication Failed!")
        print("\n⚠️  Common Solutions:")
        print("1. Make sure 2-Step Verification is ON in Google Account")
        print("2. Generate App Password at: https://myaccount.google.com/apppasswords")
        print("3. Select 'Mail' as app and 'Other' as device")
        print("4. Use the 16-character password (no spaces) in .env file")
        print(f"5. Current password: {sender_password}")
        return False
        
    except Exception as e:
        print(f"❌ Error sending email: {type(e).__name__}: {str(e)}")
        log_email_error(to_email, str(e))
        return False

def log_email_success(to_email: str, subject: str, pdf_path: str):
    """Log successful email sends"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_entry = f"[SUCCESS] {timestamp} | To: {to_email} | Subject: {subject} | PDF: {pdf_path}"
    
    with open("email_success.log", "a", encoding="utf-8") as f:
        f.write(log_entry + "\n")
    print(f"📝 Logged success to email_success.log")

def log_email_error(to_email: str, error: str):
    """Log email errors"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_entry = f"[ERROR] {timestamp} | To: {to_email} | Error: {error}"
    
    with open("email_errors.log", "a", encoding="utf-8") as f:
        f.write(log_entry + "\n")
    print(f"📝 Logged error to email_errors.log")