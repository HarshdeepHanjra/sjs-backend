# app/utils/email_otp.py - Full Debug Version

import random
import requests
import os
from datetime import datetime, timedelta

otp_storage = {}

def generate_otp():
    return "".join(str(random.randint(0, 9)) for _ in range(6))

def send_email_otp(email, otp, user_type="student"):
    print("\n" + "="*60)
    print("🔍 SEND_EMAIL_OTP FUNCTION STARTED")
    print("="*60)
    
    # Debug: Check API Key
    api_key = os.getenv("BREVO_API_KEY")
    print(f"1️⃣ BREVO_API_KEY from env: {api_key}")
    print(f"1️⃣ API Key exists: {api_key is not None}")
    if api_key:
        print(f"1️⃣ API Key length: {len(api_key)}")
        print(f"1️⃣ API Key first 15 chars: {api_key[:15]}...")
    
    # Debug: Check USE_REAL_EMAIL
    use_real_email = os.getenv("USE_REAL_EMAIL", "False")
    print(f"2️⃣ USE_REAL_EMAIL from env: {use_real_email}")
    
    # Convert to boolean
    send_real_email = use_real_email.lower() == "true"
    print(f"3️⃣ Send real email: {send_real_email}")
    
    if not send_real_email:
        print("4️⃣ REAL EMAIL MODE: OFF - Using console mode")
        print(f"📧 OTP FOR {email}: {otp}")
        return True
    
    if not api_key:
        print("❌ BREVO_API_KEY is missing or empty!")
        print(f"5️⃣ API key value: '{api_key}'")
        return False
    
    print("6️⃣ Attempting to send real email via Brevo...")
    
    try:
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
            "htmlContent": f"<html><body><h1>Your OTP is: {otp}</h1><p>Valid for 10 minutes.</p></body></html>",
        }

        headers = {
            "accept": "application/json",
            "api-key": api_key,
            "content-type": "application/json",
        }

        print(f"7️⃣ Sending request to Brevo API...")
        print(f"7️⃣ URL: https://api.brevo.com/v3/smtp/email")
        print(f"7️⃣ To: {email}")
        print(f"7️⃣ Subject: {subject}")
        
        response = requests.post(
            "https://api.brevo.com/v3/smtp/email",
            json=payload,
            headers=headers,
            timeout=15,
        )

        print(f"8️⃣ Brevo Response Status Code: {response.status_code}")
        print(f"8️⃣ Brevo Response Body: {response.text}")
        
        if response.status_code in [200, 201]:
            print(f"✅ Email sent successfully to {email}")
            return True
        else:
            print(f"❌ Brevo API error: {response.status_code} - {response.text}")
            return False
            
    except requests.exceptions.Timeout:
        print("❌ Request timeout - Brevo not responding")
        return False
    except requests.exceptions.ConnectionError as e:
        print(f"❌ Connection error: {e}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        return False

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
        print(f"✅ OTP verified for {email}")
        del otp_storage[email]
        return True
    
    print(f"❌ Invalid OTP for {email}")
    return False

def resend_otp(email, user_type="student"):
    if email in otp_storage:
        del otp_storage[email]
    return send_otp(email, user_type)