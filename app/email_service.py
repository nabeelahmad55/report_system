import smtplib
from email.message import EmailMessage


def send_email(to_email, subject, body, pdf_path):
msg = EmailMessage()
msg['Subject'] = subject
msg['From'] = "admin@example.com"
msg['To'] = to_email
msg.set_content(body)


with open(pdf_path, 'rb') as f:
msg.add_attachment(f.read(), maintype='application', subtype='pdf', filename='report.pdf')


with smtplib.SMTP('smtp.gmail.com', 587) as server:
server.starttls()
server.login("nab.ahmad55@gmail.com", "APP_PASSWORD")
server.send_message(msg)