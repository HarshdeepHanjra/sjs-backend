# app/utils/email.py
import os
import requests
import json
from flask import current_app
from datetime import datetime

def send_email_via_brevo(to_email, to_name, subject, html_content, text_content=None):
    """
    Send email using Brevo (Sendinblue) API
    """
    try:
        api_key = os.getenv('BREVO_API_KEY')
        sender_email = os.getenv('BREVO_SENDER_EMAIL', 'sjsglobaltech@gmail.com')
        sender_name = os.getenv('BREVO_SENDER_NAME', 'SJS Academy')
        
        if not api_key:
            print("❌ BREVO_API_KEY not configured in environment variables")
            return False
        
        url = "https://api.brevo.com/v3/smtp/email"
        
        payload = {
            "sender": {
                "name": sender_name,
                "email": sender_email
            },
            "to": [
                {
                    "email": to_email,
                    "name": to_name
                }
            ],
            "subject": subject,
            "htmlContent": html_content
        }
        
        if text_content:
            payload["textContent"] = text_content
        
        headers = {
            "accept": "application/json",
            "api-key": api_key,
            "content-type": "application/json"
        }
        
        response = requests.post(url, json=payload, headers=headers)
        
        if response.status_code == 201:
            print(f"✅ Email sent successfully to {to_email}")
            return True
        else:
            print(f"❌ Brevo API error: {response.status_code} - {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Error sending email via Brevo: {e}")
        return False


def send_password_reset_email(user, reset_token):
    """
    Send password reset email to user using Brevo
    """
    try:
        frontend_url = os.getenv('FRONTEND_URL', 'https://sjs-frontend-delta.vercel.app')
        reset_url = f"{frontend_url}/reset-password?token={reset_token}"
        
        subject = "Password Reset Request - SJS Academy"
        
        # HTML Email Template
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <style>
                body {{ font-family: 'Segoe UI', Arial, sans-serif; line-height: 1.6; color: #333; margin: 0; padding: 0; background-color: #f4f4f4; }}
                .container {{ max-width: 600px; margin: 0 auto; padding: 20px; background-color: #ffffff; }}
                .header {{ background: linear-gradient(135deg, #1a3a5c 0%, #2c5a8c 100%); color: white; padding: 30px; text-align: center; border-radius: 10px 10px 0 0; }}
                .content {{ padding: 30px; }}
                .button {{ display: inline-block; background: linear-gradient(135deg, #1a3a5c 0%, #2c5a8c 100%); color: white; padding: 12px 30px; text-decoration: none; border-radius: 5px; font-weight: bold; }}
                .warning {{ background: #fff3cd; padding: 15px; margin: 20px 0; border-left: 4px solid #ffc107; border-radius: 5px; }}
                .footer {{ text-align: center; padding: 20px; font-size: 12px; color: #666; border-top: 1px solid #eee; }}
                .footer a {{ color: #1a3a5c; text-decoration: none; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1 style="margin: 0;">SJS Academy</h1>
                    <p style="margin: 10px 0 0; opacity: 0.9;">Password Reset Request</p>
                </div>
                <div class="content">
                    <p>Dear <strong>{user.name}</strong>,</p>
                    <p>We received a request to reset the password for your SJS Academy account.</p>
                    <p>Click the button below to create a new password:</p>
                    <p style="text-align: center;">
                        <a href="{reset_url}" class="button" style="color: white;">Reset Password</a>
                    </p>
                    <p>Or copy and paste this link into your browser:</p>
                    <p><small style="word-break: break-all; color: #1a3a5c;">{reset_url}</small></p>
                    <div class="warning">
                        <strong>⚠️ Important:</strong> This link will expire in <strong>1 hour</strong>. 
                        If you did not request a password reset, please ignore this email. Your password will remain unchanged.
                    </div>
                </div>
                <div class="footer">
                    <p>SJS Global Tech Academy</p>
                    <p>© 2024 SJS Academy. All rights reserved.</p>
                    <p><a href="{frontend_url}">Visit our website</a></p>
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
        https://sjs-frontend-delta.vercel.app
        """
        
        # Send via Brevo
        return send_email_via_brevo(user.email, user.name, subject, html_content, text_content)
        
    except Exception as e:
        print(f"❌ Failed to send password reset email to {user.email}: {e}")
        return False


def send_welcome_email(user):
    """Send welcome email to new user using Brevo"""
    try:
        frontend_url = os.getenv('FRONTEND_URL', 'https://sjs-frontend-delta.vercel.app')
        subject = "Welcome to SJS Academy!"
        
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <style>
                body {{ font-family: 'Segoe UI', Arial, sans-serif; line-height: 1.6; color: #333; margin: 0; padding: 0; background-color: #f4f4f4; }}
                .container {{ max-width: 600px; margin: 0 auto; padding: 20px; background-color: #ffffff; border-radius: 10px; }}
                .header {{ background: linear-gradient(135deg, #1a3a5c 0%, #2c5a8c 100%); color: white; padding: 30px; text-align: center; border-radius: 10px 10px 0 0; }}
                .content {{ padding: 30px; }}
                .button {{ display: inline-block; background: linear-gradient(135deg, #1a3a5c 0%, #2c5a8c 100%); color: white; padding: 12px 30px; text-decoration: none; border-radius: 5px; font-weight: bold; }}
                .features {{ display: flex; justify-content: space-between; margin: 30px 0; }}
                .feature {{ text-align: center; flex: 1; }}
                .feature h3 {{ color: #1a3a5c; margin: 10px 0; }}
                .footer {{ text-align: center; padding: 20px; font-size: 12px; color: #666; border-top: 1px solid #eee; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1 style="margin: 0;">Welcome to SJS Academy! 🎉</h1>
                </div>
                <div class="content">
                    <p>Dear <strong>{user.name}</strong>,</p>
                    <p>Thank you for registering with SJS Academy. We're excited to have you on board!</p>
                    
                    <div class="features">
                        <div class="feature">
                            <h3>📚 Expert-Led Courses</h3>
                            <p style="font-size: 12px;">Learn from industry professionals</p>
                        </div>
                        <div class="feature">
                            <h3>🎓 Certifications</h3>
                            <p style="font-size: 12px;">Get certified on completion</p>
                        </div>
                        <div class="feature">
                            <h3>💼 Placement Support</h3>
                            <p style="font-size: 12px;">Job assistance after training</p>
                        </div>
                    </div>
                    
                    <p>Start exploring our courses and begin your learning journey today.</p>
                    <p style="text-align: center;">
                        <a href="{frontend_url}/courses" class="button" style="color: white;">Browse Courses →</a>
                    </p>
                </div>
                <div class="footer">
                    <p>SJS Global Tech Academy</p>
                    <p>© 2024 SJS Academy. All rights reserved.</p>
                    <p>Need help? <a href="{frontend_url}/contact">Contact Support</a></p>
                </div>
            </div>
        </body>
        </html>
        """
        
        text_content = f"""
        Welcome to SJS Academy!
        
        Dear {user.name},
        
        Thank you for registering with SJS Academy. We're excited to have you on board!
        
        Start exploring our courses and begin your learning journey today.
        
        Browse Courses: {frontend_url}/courses
        
        ---
        SJS Global Tech Academy
        """
        
        return send_email_via_brevo(user.email, user.name, subject, html_content, text_content)
        
    except Exception as e:
        print(f"❌ Failed to send welcome email: {e}")
        return False


def send_course_enrollment_email(user, course_name, order_id):
    """Send course enrollment confirmation email"""
    try:
        frontend_url = os.getenv('FRONTEND_URL', 'https://sjs-frontend-delta.vercel.app')
        subject = f"Course Enrollment Confirmation - {course_name}"
        
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <style>
                body {{ font-family: 'Segoe UI', Arial, sans-serif; line-height: 1.6; color: #333; }}
                .container {{ max-width: 600px; margin: 0 auto; padding: 20px; background-color: #ffffff; }}
                .header {{ background: linear-gradient(135deg, #28a745 0%, #20c997 100%); color: white; padding: 30px; text-align: center; border-radius: 10px 10px 0 0; }}
                .content {{ padding: 30px; }}
                .button {{ display: inline-block; background: #28a745; color: white; padding: 12px 30px; text-decoration: none; border-radius: 5px; }}
                .footer {{ text-align: center; padding: 20px; font-size: 12px; color: #666; border-top: 1px solid #eee; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1 style="margin: 0;">🎉 Enrollment Confirmed!</h1>
                </div>
                <div class="content">
                    <p>Dear <strong>{user.name}</strong>,</p>
                    <p>You have successfully enrolled in <strong>{course_name}</strong>!</p>
                    <p><strong>Order ID:</strong> {order_id}</p>
                    <p>Start learning now and take your skills to the next level.</p>
                    <p style="text-align: center;">
                        <a href="{frontend_url}/my-courses" class="button" style="color: white;">Go to My Courses →</a>
                    </p>
                </div>
                <div class="footer">
                    <p>SJS Global Tech Academy</p>
                </div>
            </div>
        </body>
        </html>
        """
        
        return send_email_via_brevo(user.email, user.name, subject, html_content)
        
    except Exception as e:
        print(f"❌ Failed to send enrollment email: {e}")
        return False