# app/utils/email_otp.py
import random
import os
from datetime import datetime, timedelta
from flask_mail import Message
from flask import current_app
from app import mail

# Store OTPs temporarily
otp_storage = {}

def generate_otp():
    """Generate 6-digit OTP"""
    return ''.join([str(random.randint(0, 9)) for _ in range(6)])

def send_email_otp(email, otp, user_type='student'):
    """Send OTP via Email"""
    try:
        # Company logo and styling
        if user_type == 'admin':
            subject = "🔐 Admin Login OTP - SJS Global Tech Academy"
        else:
            subject = "🔐 Email Verification OTP - SJS Global Tech Academy"
        
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <style>
                body {{
                    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                    line-height: 1.6;
                    color: #333;
                    background-color: #f4f4f4;
                    margin: 0;
                    padding: 20px;
                }}
                .container {{
                    max-width: 550px;
                    margin: 0 auto;
                    background-color: #fff;
                    border-radius: 12px;
                    box-shadow: 0 5px 15px rgba(0,0,0,0.1);
                    overflow: hidden;
                }}
                .header {{
                    background: linear-gradient(135deg, #1a3a5c 0%, #2c5a8c 100%);
                    color: white;
                    padding: 25px;
                    text-align: center;
                }}
                .header h1 {{
                    margin: 0;
                    font-size: 24px;
                    letter-spacing: 2px;
                }}
                .header p {{
                    margin: 5px 0 0;
                    font-size: 12px;
                    opacity: 0.8;
                }}
                .content {{
                    padding: 30px;
                    text-align: center;
                }}
                .otp-code {{
                    font-size: 42px;
                    font-weight: bold;
                    color: #1a3a5c;
                    letter-spacing: 10px;
                    background: #f0f7ff;
                    padding: 15px;
                    border-radius: 10px;
                    margin: 20px 0;
                    font-family: monospace;
                }}
                .button {{
                    display: inline-block;
                    background: linear-gradient(135deg, #1a3a5c 0%, #2c5a8c 100%);
                    color: white;
                    padding: 12px 30px;
                    text-decoration: none;
                    border-radius: 6px;
                    margin: 15px 0;
                }}
                .footer {{
                    background-color: #f8f9fa;
                    padding: 15px;
                    text-align: center;
                    font-size: 11px;
                    color: #666;
                    border-top: 1px solid #eee;
                }}
                .warning {{
                    background-color: #fff3cd;
                    border-left: 4px solid #ffc107;
                    padding: 12px;
                    margin: 15px 0;
                    font-size: 12px;
                    text-align: left;
                }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>SJS GLOBAL TECH ACADEMY</h1>
                    <p>ESTABLISHING EXCELLENCE IN TECHNOLOGY EDUCATION</p>
                </div>
                <div class="content">
                    <h2>Verification Code</h2>
                    <p>Dear User,</p>
                    <p>You have requested to login to your account. Please use the following OTP to complete your login:</p>
                    
                    <div class="otp-code">
                        {otp}
                    </div>
                    
                    <p>This OTP is valid for <strong>10 minutes</strong>.</p>
                    
                    <div class="warning">
                        <strong>⚠️ Security Alert:</strong> Never share this OTP with anyone. SJS Academy will never ask for your OTP.
                    </div>
                    
                    <p>If you did not request this, please ignore this email.</p>
                </div>
                <div class="footer">
                    <p>&copy; 2024 SJS Global Tech Academy. All rights reserved.</p>
                    <p>This is an automated message, please do not reply.</p>
                </div>
            </div>
        </body>
        </html>
        """
        
        # Plain text version
        text_content = f"""
        SJS GLOBAL TECH ACADEMY
        {'='*40}
        
        Your OTP for login is: {otp}
        
        This OTP is valid for 10 minutes.
        
        Never share this OTP with anyone.
        
        If you did not request this, please ignore this email.
        
        {'='*40}
        SJS Global Tech Academy
        """
        
        msg = Message(
            subject=subject,
            recipients=[email],
            html=html_content,
            body=text_content
        )
        
        mail.send(msg)
        print(f"✅ OTP email sent to {email}")
        return True
    except Exception as e:
        print(f"❌ Failed to send OTP email: {e}")
        return False

def send_otp(email, user_type='student'):
    """Generate and send OTP to email"""
    otp = generate_otp()
    
    # Store OTP with expiry
    otp_storage[email] = {
        'otp': otp,
        'expires_at': datetime.utcnow() + timedelta(minutes=10),
        'attempts': 0
    }
    
    success = send_email_otp(email, otp, user_type)
    return success, otp

def verify_otp(email, user_otp):
    """Verify OTP"""
    if email not in otp_storage:
        return False
    
    stored = otp_storage[email]
    
    # Check attempts limit (max 5 attempts)
    if stored['attempts'] >= 5:
        del otp_storage[email]
        return False
    
    # Check expiry
    if datetime.utcnow() > stored['expires_at']:
        del otp_storage[email]
        return False
    
    stored['attempts'] += 1
    
    if stored['otp'] == user_otp:
        del otp_storage[email]
        return True
    
    return False

def resend_otp(email, user_type='student'):
    """Resend OTP"""
    if email in otp_storage:
        del otp_storage[email]
    return send_otp(email, user_type)