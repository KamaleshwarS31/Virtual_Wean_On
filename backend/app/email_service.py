"""
Email Service for OTP and Notifications
Uses Gmail SMTP (free)
"""

import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from .config import settings

class EmailService:
    def __init__(self):
        self.smtp_host = settings.SMTP_HOST
        self.smtp_port = settings.SMTP_PORT
        self.smtp_user = settings.SMTP_USER
        self.smtp_password = settings.SMTP_PASSWORD
        self.from_email = settings.FROM_EMAIL
        
        # Check if SMTP is configured
        self.enabled = (
            self.smtp_user and 
            self.smtp_password and 
            self.smtp_user != "your-email@gmail.com" and
            self.smtp_password != "your-app-password"
        )
        
        if not self.enabled:
            print("⚠️  Email service disabled - SMTP not configured (OTP will be printed to console)")
    
    def send_email(self, to_email: str, subject: str, body: str, html: bool = True):
        """Send email via SMTP"""
        msg = MIMEMultipart('alternative')
        msg['From'] = self.from_email
        msg['To'] = to_email
        msg['Subject'] = subject
        
        if html:
            msg.attach(MIMEText(body, 'html'))
        else:
            msg.attach(MIMEText(body, 'plain'))
        
        try:
            with smtplib.SMTP(self.smtp_host, self.smtp_port) as server:
                server.starttls()
                server.login(self.smtp_user, self.smtp_password)
                server.send_message(msg)
            return True
        except Exception as e:
            print(f"Email send failed: {str(e)}")
            return False
    
    def send_otp_email(self, to_email: str, otp: str):
        """Send OTP verification email"""
        
        # If email is not configured, print OTP to console for testing
        if not self.enabled:
            print(f"\n{'='*60}")
            print(f"📧 OTP for {to_email}: {otp}")
            print(f"{'='*60}\n")
            return True  # Return success for testing
        
        subject = "Virtual Try-On - Email Verification"
        
        body = f"""
        <html>
            <body style="font-family: Arial, sans-serif; padding: 20px; background-color: #f5f5f5;">
                <div style="max-width: 600px; margin: 0 auto; background-color: white; padding: 30px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1);">
                    <h2 style="color: #333; margin-bottom: 20px;">Email Verification</h2>
                    <p style="color: #666; font-size: 16px; line-height: 1.6;">
                        Thank you for signing up for the Virtual Merchandise Try-On system!
                    </p>
                    <p style="color: #666; font-size: 16px; line-height: 1.6;">
                        Your verification code is:
                    </p>
                    <div style="background-color: #f0f0f0; padding: 20px; text-align: center; border-radius: 5px; margin: 20px 0;">
                        <h1 style="color: #4CAF50; margin: 0; font-size: 36px; letter-spacing: 5px;">{otp}</h1>
                    </div>
                    <p style="color: #666; font-size: 14px; line-height: 1.6;">
                        This code will expire in 10 minutes.
                    </p>
                    <p style="color: #999; font-size: 12px; margin-top: 30px; padding-top: 20px; border-top: 1px solid #eee;">
                        If you didn't request this code, please ignore this email.
                    </p>
                </div>
            </body>
        </html>
        """
        
        return self.send_email(to_email, subject, body, html=True)
    
    def send_approval_notification(self, to_email: str, approved: bool):
        """Send approval/rejection notification"""
        if approved:
            subject = "Your Try-On Image Has Been Approved!"
            message = "Your virtual try-on image has been approved. You can now download it from your dashboard."
            color = "#4CAF50"
        else:
            subject = "Try-On Image Update"
            message = "Your virtual try-on image needs revision. Please try again with a different photo."
            color = "#FF9800"
        
        body = f"""
        <html>
            <body style="font-family: Arial, sans-serif; padding: 20px; background-color: #f5f5f5;">
                <div style="max-width: 600px; margin: 0 auto; background-color: white; padding: 30px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1);">
                    <h2 style="color: {color}; margin-bottom: 20px;">{subject}</h2>
                    <p style="color: #666; font-size: 16px; line-height: 1.6;">
                        {message}
                    </p>
                    <p style="color: #999; font-size: 12px; margin-top: 30px;">
                        Thank you for using our Virtual Try-On system!
                    </p>
                </div>
            </body>
        </html>
        """
        
        return self.send_email(to_email, subject, body, html=True)

# Global instance
email_service = EmailService()
