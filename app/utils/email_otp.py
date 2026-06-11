# app/utils/email_otp.py
import random
from datetime import datetime, timedelta
from flask_mail import Message
from flask import current_app
from threading import Thread
import traceback
import os
from app import mail

# Store OTPs temporarily
otp_storage = {}

def generate_otp():
    """Generate 6-digit OTP"""
    return ''.join([str(random.randint(0, 9)) for _ in range(6)])

def send_async_email(app, msg):
    """Send email asynchronously - NO BLOCKING"""
    try:
        with app.app_context():
            # Set timeout for email sending
            import socket
            socket.setdefaulttimeout(10)  # 10 second timeout
            mail.send(msg)
            print(f"✅ Email sent successfully via async thread")
    except Exception as e:
        print(f"❌ Async email failed: {e}")

def send_email_otp(email, otp, user_type='student'):
    """Send OTP via Email - NON BLOCKING"""
    try:
        if user_type == 'admin':
            subject = "🔐 Admin Login OTP - SJS Global Tech Academy"
        else:
            subject = "🔐 Email Verification OTP - SJS Global Tech Academy"
        
        # Simple text email first (faster)
        text_content = f"""
SJS GLOBAL TECH ACADEMY
{'='*40}

Your OTP for login is: {otp}

This OTP is valid for 10 minutes.

⚠️ Never share this OTP with anyone.

{'='*40}
SJS Global Tech Academy
"""
        
        msg = Message(
            subject=subject,
            recipients=[email],
            body=text_content  # Use plain text for speed
        )
        
        print(f"📧 Sending OTP to: {email}")
        
        # Send asynchronously - NON BLOCKING
        from app import create_app
        app = current_app._get_current_object()

        thread = Thread(
            target=send_async_email,
            args=(app, msg),
            daemon=True
        )
        thread.daemon = True  # Thread will exit when main thread exits
        thread.start()
        
        print(f"✅ OTP email queued for: {email}")
        return True
        
    except Exception as e:
        print(f"❌ Failed to queue OTP email: {e}")
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
        print(f"❌ No OTP found for: {email}")
        return False
    
    stored = otp_storage[email]
    
    if stored['attempts'] >= 5:
        print(f"❌ Too many attempts for: {email}")
        del otp_storage[email]
        return False
    
    if datetime.utcnow() > stored['expires_at']:
        print(f"❌ OTP expired for: {email}")
        del otp_storage[email]
        return False
    
    stored['attempts'] += 1
    
    if stored['otp'] == user_otp:
        print(f"✅ OTP verified for: {email}")
        del otp_storage[email]
        return True
    
    print(f"❌ Invalid OTP for: {email}. Expected: {stored['otp']}, Got: {user_otp}")
    return False

def resend_otp(email, user_type='student'):
    """Resend OTP"""
    if email in otp_storage:
        del otp_storage[email]
    return send_otp(email, user_type)