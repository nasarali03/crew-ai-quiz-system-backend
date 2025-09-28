import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os
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
        self.use_sendgrid = bool(self.sendgrid_api_key)
    
    async def send_email(self, to_email: str, subject: str, body: str) -> bool:
        """Send email using SMTP or SendGrid"""
        try:
            if self.use_sendgrid:
                return await self._send_with_sendgrid(to_email, subject, body)
            else:
                return await self._send_with_smtp(to_email, subject, body)
        except Exception as e:
            print(f"Error sending email: {e}")
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
