# app/utils/email_otp.py
import random
from datetime import datetime, timedelta
from flask_mail import Message
from flask import current_app
from threading import Thread
from app import mail
import traceback

# Store OTPs temporarily
otp_storage = {}

def generate_otp():
    """Generate 6-digit OTP"""
    return ''.join([str(random.randint(0, 9)) for _ in range(6)])

def send_async_email(app, msg):
    """Send email asynchronously"""
    with app.app_context():
        mail.send(msg)

def send_email_otp(email, otp, user_type='student'):
    """Send OTP via Email"""
    try:
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
                .footer {{
                    background-color: #f8f9fa;
                    padding: 15px;
                    text-align: center;
                    font-size: 11px;
                    color: #666;
                }}
                .warning {{
                    background-color: #fff3cd;
                    border-left: 4px solid #ffc107;
                    padding: 12px;
                    margin: 15px 0;
                    font-size: 12px;
                }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>SJS GLOBAL TECH ACADEMY</h1>
                </div>
                <div class="content">
                    <h2>Verification Code</h2>
                    <p>Your OTP for login is:</p>
                    <div class="otp-code">{otp}</div>
                    <p>This OTP is valid for <strong>10 minutes</strong>.</p>
                    <div class="warning">
                        ⚠️ Never share this OTP with anyone.
                    </div>
                </div>
                <div class="footer">
                    <p>&copy; 2024 SJS Global Tech Academy</p>
                </div>
            </div>
        </body>
        </html>
        """
        
        msg = Message(
            subject=subject,
            recipients=[email],
            html=html_content
        )
        
        print(f"📧 Sending OTP email to: {email}")
        print(f"📧 Subject: {subject}")
        
        mail.send(msg)

        print(f"✅ OTP Email Sent Successfully To: {email}")

        return True
    except Exception as e:
        print("❌ EMAIL ERROR")
        print(str(e))
        traceback.print_exc()
        return False

def send_otp(email, user_type='student'):
    """Generate and send OTP"""
    
    otp = generate_otp()
    
    print(f"🔐 OTP Generated For {email}: {otp}")
    
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
    
    if stored['attempts'] >= 5:
        del otp_storage[email]
        return False
    
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