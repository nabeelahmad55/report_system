import os

def send_email(to_email, subject, body, pdf_path):
    """
    Simplified email function for testing
    In production, replace with actual SMTP code
    """
    print(f"[EMAIL] Would send to: {to_email}")
    print(f"[EMAIL] Subject: {subject}")
    print(f"[EMAIL] PDF Path: {pdf_path}")
    
    # Log to file
    with open("email_log.txt", "a") as f:
        f.write(f"To: {to_email}, Subject: {subject}, PDF: {pdf_path}\n")
    
    return True