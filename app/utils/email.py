# app/utils/email.py
from flask import current_app
from flask_mail import Message
from app import mail
import os

def send_password_reset_email(user, reset_token):
    """
    Send password reset email to user
    """
    try:
        # Get frontend URL from environment
        frontend_url = os.getenv('FRONTEND_URL', 'https://sjs-frontend-delta.vercel.app')
        reset_url = f"{frontend_url}/reset-password?token={reset_token}"
        
        subject = "Password Reset Request - SJS Academy"
        
        # HTML Email Template
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <style>
                body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
                .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                .header {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                           color: white; padding: 30px; text-align: center; }}
                .button {{ display: inline-block; background: #667eea; color: white; 
                          padding: 12px 30px; text-decoration: none; border-radius: 5px; }}
                .warning {{ background: #fff3cd; padding: 10px; margin: 15px 0; }}
                .footer {{ text-align: center; padding: 20px; font-size: 12px; color: #666; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>SJS Academy</h1>
                    <p>Password Reset Request</p>
                </div>
                <div class="content">
                    <p>Dear <strong>{user.name}</strong>,</p>
                    <p>We received a request to reset the password for your SJS Academy account.</p>
                    <p>Click the button below to create a new password:</p>
                    <p style="text-align: center;">
                        <a href="{reset_url}" class="button" style="color: white;">Reset Password</a>
                    </p>
                    <p>Or copy and paste this link into your browser:</p>
                    <p><small>{reset_url}</small></p>
                    <div class="warning">
                        <strong>⚠️ Important:</strong> This link will expire in <strong>1 hour</strong>. If you did not request a password reset, please ignore this email.
                    </div>
                </div>
                <div class="footer">
                    <p>SJS Global Tech Academy</p>
                    <p>© 2024 SJS Academy. All rights reserved.</p>
                </div>
            </div>
        </body>
        </html>
        """
        
        # Plain text version
        text_content = f"""
        SJS Academy - Password Reset Request
        
        Dear {user.name},
        
        We received a request to reset the password for your SJS Academy account.
        
        To reset your password, click the link below (expires in 1 hour):
        {reset_url}
        
        If you did not request a password reset, please ignore this email.
        
        ---
        SJS Global Tech Academy
        """
        
        # Create message
        msg = Message(
            subject=subject,
            recipients=[user.email],
            html=html_content,
            body=text_content
        )
        
        # Send email
        mail.send(msg)
        print(f"✅ Password reset email sent to {user.email}")
        return True
        
    except Exception as e:
        print(f"❌ Failed to send email to {user.email}: {e}")
        return False


def send_welcome_email(user):
    """Send welcome email to new user"""
    try:
        frontend_url = os.getenv('FRONTEND_URL', 'https://sjs-frontend-delta.vercel.app')
        subject = "Welcome to SJS Academy!"
        
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <style>
                body {{ font-family: Arial, sans-serif; }}
                .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                .header {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                           color: white; padding: 30px; text-align: center; }}
                .button {{ display: inline-block; background: #667eea; color: white; 
                          padding: 12px 30px; text-decoration: none; border-radius: 5px; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>Welcome to SJS Academy!</h1>
                </div>
                <div class="content">
                    <p>Dear <strong>{user.name}</strong>,</p>
                    <p>Thank you for registering with SJS Academy. We're excited to have you on board!</p>
                    <p>Start exploring our courses and begin your learning journey today.</p>
                    <p style="text-align: center;">
                        <a href="{frontend_url}/courses" class="button" style="color: white;">Browse Courses →</a>
                    </p>
                </div>
                <div class="footer">
                    <p>SJS Global Tech Academy</p>
                    <p>© 2024 SJS Academy. All rights reserved.</p>
                </div>
            </div>
        </body>
        </html>
        """
        
        msg = Message(
            subject=subject,
            recipients=[user.email],
            html=html_content
        )
        
        mail.send(msg)
        print(f"✅ Welcome email sent to {user.email}")
        return True
    except Exception as e:
        print(f"❌ Failed to send welcome email: {e}")
        return False