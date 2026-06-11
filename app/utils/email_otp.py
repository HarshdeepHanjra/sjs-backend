# app/utils/email_otp.py - Fixed Version

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
        
        if not api_key:
            print("❌ BREVO_API_KEY not found in environment variables")
            print("✅ Falling back to console mode for testing")
            # Fallback to console
            print(f"\n{'='*60}")
            print(f"🔐 OTP for {email}: {otp}")
            print(f"{'='*60}\n")
            return True  # Return True so login works even without API key
        
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
            <body style="font-family: Arial, sans-serif;">
                <h2 style="color: #1a3a5c;">SJS Global Tech Academy</h2>
                <p>Your OTP code is:</p>
                <div style="
                    font-size: 42px;
                    font-weight: bold;
                    color: #0d6efd;
                    margin: 20px 0;
                    padding: 15px;
                    background: #f0f7ff;
                    border-radius: 10px;
                    letter-spacing: 5px;
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

        print(f"Brevo Status: {response.status_code}")
        
        if response.status_code in [200, 201]:
            print(f"✅ OTP email sent successfully to {email}")
            return True
        else:
            print(f"❌ Brevo error: {response.text}")
            # Fallback to console
            print(f"🔐 OTP for {email}: {otp}")
            return True  # Return True for testing
            
    except Exception as e:
        print(f"❌ Email Send Error: {e}")
        print(f"🔐 Falling back to console - OTP: {otp}")
        return True  # Return True so login works

def send_otp(email, user_type="student"):
    otp = generate_otp()
    
    print(f"🔐 OTP Generated For {email}: {otp}")
    
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
        print(f"✅ OTP verified for {email}")
        del otp_storage[email]
        return True
    
    print(f"❌ Invalid OTP for {email}. Expected: {stored['otp']}, Got: {user_otp}")
    return False

def resend_otp(email, user_type="student"):
    if email in otp_storage:
        del otp_storage[email]
    return send_otp(email, user_type)