# app/email_utils.py
from flask_mail import Mail, Message

mail = Mail()

def init_mail(app):
    mail.init_app(app)

def send_enquiry_email(app, enquiry):
    subject = f"New Website Enquiry — {enquiry.phone}"
    body = f"""
New enquiry received:

Name: {enquiry.name or "-"}
Email: {enquiry.email or "-"}
Phone: {enquiry.phone}
Subject: {enquiry.subject or "-"}

Message:
{enquiry.message}

---
IP: {enquiry.ip_address or "-"}
User Agent: {enquiry.user_agent or "-"}
Time (UTC): {enquiry.created_at}
""".strip()

    msg = Message(
        subject=subject,
        recipients=[app.config["OCHIRLAW_INBOX"]],
        body=body
    )
    mail.send(msg)
