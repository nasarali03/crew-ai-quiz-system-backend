import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os
import requests
import json
from dotenv import load_dotenv
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail

load_dotenv()

class EmailService:
    def __init__(self):
        self.smtp_host = os.getenv("SMTP_HOST")
        self.smtp_port = int(os.getenv("SMTP_PORT", 587))
        self.smtp_username = os.getenv("SMTP_USERNAME")
        self.smtp_password = os.getenv("SMTP_PASSWORD")
        self.from_email = os.getenv("SMTP_FROM_EMAIL")
        self.sendgrid_api_key = os.getenv("SENDGRID_API_KEY")
        
        # Determine which email service to use (priority: Mailtrap > Gmail SMTP > SendGrid > Other SMTP)
        if self.smtp_host == "sandbox.smtp.mailtrap.io":
            self.email_service = "mailtrap"
        elif self.smtp_host == "smtp.gmail.com":
            self.email_service = "gmail"
        elif self.sendgrid_api_key:
            self.email_service = "sendgrid"
        else:
            self.email_service = "smtp"
        
        print(f"📧 EmailService: Using {self.email_service.upper()} for email delivery")
    
    async def send_email(self, to_email: str, subject: str, body: str) -> bool:
        """Send email using Mailtrap, Gmail SMTP, SendGrid, or other SMTP"""
        try:
            if self.email_service == "mailtrap":
                return await self._send_with_mailtrap(to_email, subject, body)
            elif self.email_service == "gmail":
                return await self._send_with_gmail(to_email, subject, body)
            elif self.email_service == "sendgrid":
                return await self._send_with_sendgrid(to_email, subject, body)
            else:
                return await self._send_with_smtp(to_email, subject, body)
        except Exception as e:
            print(f"❌ EmailService: Error sending email: {e}")
            return False
    
    async def _send_with_mailtrap(self, to_email: str, subject: str, body: str) -> bool:
        """Send email using Mailtrap SMTP"""
        try:
            print(f"📧 Mailtrap: Sending email to {to_email}")
            
            # Create message
            msg = MIMEMultipart()
            msg['From'] = self.from_email
            msg['To'] = to_email
            msg['Subject'] = subject
            
            # Add body
            msg.attach(MIMEText(body, 'html'))
            
            # Send email via Mailtrap SMTP
            server = smtplib.SMTP(self.smtp_host, self.smtp_port)
            server.starttls()
            server.login(self.smtp_username, self.smtp_password)
            text = msg.as_string()
            server.sendmail(self.from_email, to_email, text)
            server.quit()
            
            print(f"✅ Mailtrap: Email sent successfully to {to_email}")
            return True
        except Exception as e:
            print(f"❌ Mailtrap: Error sending email: {e}")
            return False
    
    async def _send_with_gmail(self, to_email: str, subject: str, body: str) -> bool:
        """Send email using Gmail SMTP"""
        try:
            print(f"📧 Gmail: Sending email to {to_email}")
            
            # Create message
            msg = MIMEMultipart()
            msg['From'] = self.from_email
            msg['To'] = to_email
            msg['Subject'] = subject
            
            # Add body
            msg.attach(MIMEText(body, 'html'))
            
            # Send email via Gmail SMTP
            server = smtplib.SMTP(self.smtp_host, self.smtp_port)
            server.starttls()
            server.login(self.smtp_username, self.smtp_password)
            text = msg.as_string()
            server.sendmail(self.from_email, to_email, text)
            server.quit()
            
            print(f"✅ Gmail: Email sent successfully to {to_email}")
            return True
        except Exception as e:
            print(f"❌ Gmail: Error sending email: {e}")
            return False
    
    async def _send_with_smtp(self, to_email: str, subject: str, body: str) -> bool:
        """Send email using SMTP"""
        try:
            # Create message
            msg = MIMEMultipart()
            msg['From'] = self.from_email
            msg['To'] = to_email
            msg['Subject'] = subject
            
            # Add body
            msg.attach(MIMEText(body, 'html'))
            
            # Send email
            server = smtplib.SMTP(self.smtp_host, self.smtp_port)
            server.starttls()
            server.login(self.smtp_username, self.smtp_password)
            text = msg.as_string()
            server.sendmail(self.from_email, to_email, text)
            server.quit()
            
            return True
        except Exception as e:
            print(f"SMTP error: {e}")
            return False
    
    
    async def _send_with_sendgrid(self, to_email: str, subject: str, body: str) -> bool:
        """Send email using SendGrid"""
        try:
            message = Mail(
                from_email=self.from_email,
                to_emails=to_email,
                subject=subject,
                html_content=body
            )
            
            sg = SendGridAPIClient(api_key=self.sendgrid_api_key)
            response = sg.send(message)
            
            return response.status_code == 202
        except Exception as e:
            print(f"SendGrid error: {e}")
            return False
