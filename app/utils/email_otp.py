# app/utils/email_otp.py - Updated

import random
import requests
import os
from datetime import datetime, timedelta

otp_storage = {}

def generate_otp():
    return "".join(str(random.randint(0, 9)) for _ in range(6))

def send_email_otp(email, otp, user_type="student"):
    try:
        api_key = os.getenv("BREVO_API_KEY")
        
        # Debug: Check if API key exists
        print(f"🔍 DEBUG: BREVO_API_KEY exists: {'Yes' if api_key else 'No'}")
        if api_key:
            print(f"🔍 DEBUG: API Key starts with: {api_key[:15]}...")
        
        use_email = os.getenv("USE_REAL_EMAIL", "False").lower() == "true"
        
        if not api_key or not use_email:
            print(f"⚠️ Email mode: {'ON' if use_email else 'OFF'}")
            print(f"⚠️ API Key: {'Found' if api_key else 'Missing'}")
            print(f"\n{'='*60}")
            print(f"📧 OTP FOR {email}")
            print(f"🔐 {otp}")
            print(f"⏰ Valid for 10 minutes")
            print(f"{'='*60}\n")
            return True
        
        # Try sending real email
        subject = (
            "🔐 Admin Login OTP - SJS Global Tech Academy"
            if user_type == "admin"
            else "🔐 Email Verification OTP - SJS Global Tech Academy"
        )

        payload = {
            "sender": {
                "name": "SJS Global Tech Academy",
                "email": "sjsglobaltech@gmail.com",
            },
            "to": [{"email": email}],
            "subject": subject,
            "htmlContent": f"""
            <html>
            <body style="font-family: Arial, sans-serif; text-align: center;">
                <h2 style="color: #1a3a5c;">SJS Global Tech Academy</h2>
                <p>Your OTP code is:</p>
                <div style="
                    font-size: 48px;
                    font-weight: bold;
                    color: #0d6efd;
                    margin: 20px 0;
                    padding: 20px;
                    background: #f0f7ff;
                    border-radius: 10px;
                    letter-spacing: 10px;
                ">
                    {otp}
                </div>
                <p>This OTP is valid for <b>10 minutes</b>.</p>
                <p style="color: #ff6b6b;">⚠️ Never share this OTP with anyone.</p>
                <hr>
                <p style="color: #666;">SJS Global Tech Academy</p>
            </body>
            </html>
            """,
        }

        headers = {
            "accept": "application/json",
            "api-key": api_key,
            "content-type": "application/json",
        }

        print(f"📧 Sending OTP to {email} via Brevo...")
        response = requests.post(
            "https://api.brevo.com/v3/smtp/email",
            json=payload,
            headers=headers,
            timeout=15,
        )

        print(f"Brevo Response: {response.status_code}")
        
        if response.status_code in [200, 201]:
            print(f"✅ OTP email sent successfully to {email}")
            print(f"🔐 OTP: {otp}")
            return True
        else:
            print(f"❌ Brevo error: {response.text}")
            print(f"🔐 Console OTP for {email}: {otp}")
            return True
            
    except Exception as e:
        print(f"❌ Email Error: {e}")
        print(f"🔐 Console OTP for {email}: {otp}")
        return True

def send_otp(email, user_type="student"):
    otp = generate_otp()
    
    print(f"\n{'='*50}")
    print(f"🔐 Generating OTP for: {email}")
    print(f"📝 OTP Code: {otp}")
    print(f"👤 User Type: {user_type}")
    print(f"{'='*50}\n")
    
    otp_storage[email] = {
        "otp": otp,
        "expires_at": datetime.utcnow() + timedelta(minutes=10),
        "attempts": 0,
    }
    
    success = send_email_otp(email, otp, user_type)
    return success, otp

def verify_otp(email, user_otp):
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
        print(f"✅ OTP verified successfully for {email}")
        del otp_storage[email]
        return True
    
    print(f"❌ Invalid OTP for {email}")
    return False

def resend_otp(email, user_type="student"):
    if email in otp_storage:
        del otp_storage[email]
    return send_otp(email, user_type)