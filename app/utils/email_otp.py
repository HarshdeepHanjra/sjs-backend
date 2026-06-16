# # app/utils/email_otp.py - Full Debug Version

# import random
# import requests
# import os
# from datetime import datetime, timedelta

# otp_storage = {}

# def generate_otp():
#     return "".join(str(random.randint(0, 9)) for _ in range(6))

# def send_email_otp(email, otp, user_type="student"):
#     print("\n" + "="*60)
#     print("🔍 SEND_EMAIL_OTP FUNCTION STARTED")
#     print("="*60)
    
#     # Debug: Check API Key
#     api_key = os.getenv("BREVO_API_KEY")
#     print(f"1️⃣ BREVO_API_KEY from env: {api_key}")
#     print(f"1️⃣ API Key exists: {api_key is not None}")
#     if api_key:
#         print(f"1️⃣ API Key length: {len(api_key)}")
#         print(f"1️⃣ API Key first 15 chars: {api_key[:15]}...")
    
#     # Debug: Check USE_REAL_EMAIL
#     use_real_email = os.getenv("USE_REAL_EMAIL", "False")
#     print(f"2️⃣ USE_REAL_EMAIL from env: {use_real_email}")
    
#     # Convert to boolean
#     send_real_email = use_real_email.lower() == "true"
#     print(f"3️⃣ Send real email: {send_real_email}")
    
#     if not send_real_email:
#         print("4️⃣ REAL EMAIL MODE: OFF - Using console mode")
#         print(f"📧 OTP FOR {email}: {otp}")
#         return True
    
#     if not api_key:
#         print("❌ BREVO_API_KEY is missing or empty!")
#         print(f"5️⃣ API key value: '{api_key}'")
#         return False
    
#     print("6️⃣ Attempting to send real email via Brevo...")
    
#     try:
#         subject = (
#             "🔐 Admin Login OTP - SJS Global Tech Academy"
#             if user_type == "admin"
#             else "🔐 Email Verification OTP - SJS Global Tech Academy"
#         )

#         payload = {
#             "sender": {
#                 "name": "SJS Global Tech Academy",
#                 "email": "sjsglobaltech@gmail.com",
#             },
#             "to": [{"email": email}],
#             "subject": subject,
#             "htmlContent": f"<html><body><h1>Your OTP is: {otp}</h1><p>Valid for 10 minutes.</p></body></html>",
#         }

#         headers = {
#             "accept": "application/json",
#             "api-key": api_key,
#             "content-type": "application/json",
#         }

#         print(f"7️⃣ Sending request to Brevo API...")
#         print(f"7️⃣ URL: https://api.brevo.com/v3/smtp/email")
#         print(f"7️⃣ To: {email}")
#         print(f"7️⃣ Subject: {subject}")
        
#         response = requests.post(
#             "https://api.brevo.com/v3/smtp/email",
#             json=payload,
#             headers=headers,
#             timeout=15,
#         )

#         print(f"8️⃣ Brevo Response Status Code: {response.status_code}")
#         print(f"8️⃣ Brevo Response Body: {response.text}")
        
#         if response.status_code in [200, 201]:
#             print(f"✅ Email sent successfully to {email}")
#             return True
#         else:
#             print(f"❌ Brevo API error: {response.status_code} - {response.text}")
#             return False
            
#     except requests.exceptions.Timeout:
#         print("❌ Request timeout - Brevo not responding")
#         return False
#     except requests.exceptions.ConnectionError as e:
#         print(f"❌ Connection error: {e}")
#         return False
#     except Exception as e:
#         print(f"❌ Unexpected error: {e}")
#         import traceback
#         traceback.print_exc()
#         return False

# def send_otp(email, user_type="student"):
#     otp = generate_otp()
    
#     print(f"\n{'='*50}")
#     print(f"🔐 Generating OTP for: {email}")
#     print(f"📝 OTP Code: {otp}")
#     print(f"👤 User Type: {user_type}")
#     print(f"{'='*50}\n")
    
#     otp_storage[email] = {
#         "otp": otp,
#         "expires_at": datetime.utcnow() + timedelta(minutes=10),
#         "attempts": 0,
#     }
    
#     success = send_email_otp(email, otp, user_type)
#     return success, otp

# def verify_otp(email, user_otp):
#     if email not in otp_storage:
#         print(f"❌ No OTP found for {email}")
#         return False
    
#     stored = otp_storage[email]
    
#     if stored["attempts"] >= 5:
#         print(f"❌ Too many attempts for {email}")
#         del otp_storage[email]
#         return False
    
#     if datetime.utcnow() > stored["expires_at"]:
#         print(f"❌ OTP expired for {email}")
#         del otp_storage[email]
#         return False
    
#     stored["attempts"] += 1
    
#     if stored["otp"] == user_otp:
#         print(f"✅ OTP verified for {email}")
#         del otp_storage[email]
#         return True
    
#     print(f"❌ Invalid OTP for {email}")
#     return False

# def resend_otp(email, user_type="student"):
#     if email in otp_storage:
#         del otp_storage[email]
#     return send_otp(email, user_type)



# app/utils/email_otp.py - Gmail SMTP Version

import random
import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime, timedelta

otp_storage = {}

# =====================================================
# GMAIL SMTP CONFIGURATION
# =====================================================
MAIL_SERVER = os.getenv('MAIL_SERVER', 'smtp.gmail.com')
MAIL_PORT = int(os.getenv('MAIL_PORT', 587))
MAIL_USE_TLS = os.getenv('MAIL_USE_TLS', 'True').lower() == 'true'
MAIL_USERNAME = os.getenv('MAIL_USERNAME', 'sjsglobaltech@gmail.com')
MAIL_PASSWORD = os.getenv('MAIL_PASSWORD', '')  # Gmail App Password
MAIL_DEFAULT_SENDER = os.getenv('MAIL_DEFAULT_SENDER', 'sjsglobaltech@gmail.com')
USE_REAL_EMAIL = os.getenv('USE_REAL_EMAIL', 'True').lower() == 'true'


def generate_otp():
    """Generate 6-digit OTP"""
    return "".join(str(random.randint(0, 9)) for _ in range(6))


def send_email_otp(email, otp, user_type="student"):
    """Send OTP via Gmail SMTP directly"""
    print("\n" + "="*60)
    print("🔍 SEND_EMAIL_OTP FUNCTION STARTED (GMAIL SMTP)")
    print("="*60)
    
    # Debug: Check credentials
    print(f"1️⃣ MAIL_USERNAME: {MAIL_USERNAME}")
    print(f"2️⃣ MAIL_PASSWORD set: {'✅ Yes' if MAIL_PASSWORD else '❌ No'}")
    print(f"3️⃣ USE_REAL_EMAIL: {USE_REAL_EMAIL}")
    
    if not USE_REAL_EMAIL:
        print("4️⃣ REAL EMAIL MODE: OFF - Using console mode")
        print(f"📧 OTP FOR {email}: {otp}")
        return True
    
    if not MAIL_PASSWORD:
        print("❌ MAIL_PASSWORD is missing! Please set Gmail App Password")
        print("   Steps: Google Account → Security → App Passwords")
        return False
    
    try:
        print("5️⃣ Attempting to send real email via Gmail SMTP...")
        
        subject = (
            "🔐 Admin Login OTP - SJS Global Tech Academy"
            if user_type == "admin"
            else "🔐 Email Verification OTP - SJS Global Tech Academy"
        )
        
        # HTML email body
        html_body = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
        </head>
        <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333; max-width: 500px; margin: 0 auto; padding: 20px;">
            <div style="background: #f8f9fa; border-radius: 8px; padding: 20px; border: 1px solid #e0e0e0;">
                <h2 style="color: #4a90d9; margin-top: 0;">🔐 Verification Code</h2>
                <p>Hello User,</p>
                <p>Your OTP for login is:</p>
                <div style="background: white; padding: 15px; border-radius: 6px; text-align: center; font-size: 32px; font-weight: bold; color: #4a90d9; letter-spacing: 5px; border: 1px dashed #4a90d9; margin: 20px 0;">
                    {otp}
                </div>
                <p style="font-size: 14px; color: #666;">This OTP is valid for <strong>10 minutes</strong>.</p>
                <p style="font-size: 12px; color: #999; margin-top: 20px;">SJS Global Tech Academy</p>
            </div>
        </body>
        </html>
        """
        
        # Plain text version
        text_body = f"""
        Your OTP for SJS Global Tech Academy is: {otp}
        
        This OTP is valid for 10 minutes.
        
        SJS Global Tech Academy
        """
        
        # Create email message
        msg = MIMEMultipart('alternative')
        msg['From'] = f"SJS Global Tech Academy <{MAIL_USERNAME}>"
        msg['To'] = email
        msg['Subject'] = subject
        msg['X-Mailer'] = 'SJS Academy'
        msg['X-Priority'] = '1'
        
        # Attach both text and HTML
        msg.attach(MIMEText(text_body, 'plain'))
        msg.attach(MIMEText(html_body, 'html'))
        
        print(f"6️⃣ Sending email via Gmail SMTP to: {email}")
        print(f"6️⃣ Subject: {subject}")
        print(f"6️⃣ SMTP Server: {MAIL_SERVER}:{MAIL_PORT}")
        
        # Send via Gmail SMTP
        with smtplib.SMTP(MAIL_SERVER, MAIL_PORT) as server:
            if MAIL_USE_TLS:
                server.starttls()
            server.login(MAIL_USERNAME, MAIL_PASSWORD)
            server.send_message(msg)
        
        print(f"✅ Email sent successfully to {email}")
        print(f"   OTP: {otp}")
        return True
        
    except smtplib.SMTPAuthenticationError as e:
        print(f"❌ Gmail Authentication error: {e}")
        print("   Solution: Use App Password, not regular Gmail password")
        print("   Steps: Google Account → Security → App Passwords")
        return False
    except smtplib.SMTPException as e:
        print(f"❌ SMTP error: {e}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        return False


def send_otp(email, user_type="student"):
    """Generate and send OTP to user"""
    otp = generate_otp()
    
    print(f"\n{'='*50}")
    print(f"🔐 Generating OTP for: {email}")
    print(f"📝 OTP Code: {otp}")
    print(f"👤 User Type: {user_type}")
    print(f"{'='*50}\n")
    
    # Store OTP
    otp_storage[email] = {
        "otp": otp,
        "expires_at": datetime.utcnow() + timedelta(minutes=10),
        "attempts": 0,
    }
    
    success = send_email_otp(email, otp, user_type)
    return success, otp


def verify_otp(email, user_otp):
    """Verify OTP"""
    if email not in otp_storage:
        print(f"❌ No OTP found for {email}")
        return False
    
    stored = otp_storage[email]
    
    if stored["attempts"] >= 5:
        print(f"❌ Too many attempts for {email}")
        del otp_storage[email]
        return False
    
    if datetime.utcnow() > stored["expires_at"]:
        print(f"❌ OTP expired for {email}")
        del otp_storage[email]
        return False
    
    stored["attempts"] += 1
    
    if stored["otp"] == user_otp:
        print(f"✅ OTP verified for {email}")
        del otp_storage[email]
        return True
    
    print(f"❌ Invalid OTP for {email}")
    return False


def resend_otp(email, user_type="student"):
    """Resend OTP"""
    if email in otp_storage:
        del otp_storage[email]
    return send_otp(email, user_type)