# app/utils/email_otp.py

import random
import requests
import os
from datetime import datetime, timedelta

otp_storage = {}

def generate_otp():
    return ''.join(str(random.randint(0, 9)) for _ in range(6))


def send_email_otp(email, otp, user_type='student'):
    try:
        api_key = os.getenv("BREVO_API_KEY")

        if not api_key:
            print("❌ BREVO_API_KEY not found")
            return False

        subject = (
            "🔐 Admin Login OTP - SJS Global Tech Academy"
            if user_type == "admin"
            else "🔐 Email Verification OTP - SJS Global Tech Academy"
        )

        payload = {
            "sender": {
                "name": "SJS Global Tech Academy",
                "email": "sjsglobaltech@gmail.com"
            },
            "to": [
                {
                    "email": email
                }
            ],
            "subject": subject,
            "htmlContent": f"""
            <html>
            <body style="font-family: Arial, sans-serif;">
                <h2>SJS Global Tech Academy</h2>

                <p>Your OTP code is:</p>

                <div style="
                    font-size:32px;
                    font-weight:bold;
                    color:#0d6efd;
                    margin:20px 0;
                ">
                    {otp}
                </div>

                <p>This OTP is valid for <b>10 minutes</b>.</p>

                <p>⚠️ Never share this OTP with anyone.</p>

                <hr>

                <p>SJS Global Tech Academy</p>
            </body>
            </html>
            """
        }

        headers = {
            "accept": "application/json",
            "api-key": api_key,
            "content-type": "application/json"
        }

        response = requests.post(
            "https://api.brevo.com/v3/smtp/email",
            json=payload,
            headers=headers,
            timeout=15
        )

        print("Brevo Status:", response.status_code)
        print("Brevo Response:", response.text)

        return response.status_code in [200, 201]

    except Exception as e:
        print(f"❌ Email Send Error: {e}")
        return False


def send_otp(email, user_type='student'):
    otp = generate_otp()

    print(f"🔐 OTP Generated For {email}: {otp}")

    otp_storage[email] = {
        "otp": otp,
        "expires_at": datetime.utcnow() + timedelta(minutes=10),
        "attempts": 0
    }

    success = send_email_otp(email, otp, user_type)

    return success, otp


def verify_otp(email, user_otp):
    if email not in otp_storage:
        return False

    stored = otp_storage[email]

    if stored["attempts"] >= 5:
        del otp_storage[email]
        return False

    if datetime.utcnow() > stored["expires_at"]:
        del otp_storage[email]
        return False

    stored["attempts"] += 1

    if stored["otp"] == user_otp:
        del otp_storage[email]
        return True

    return False


def resend_otp(email, user_type='student'):
    if email in otp_storage:
        del otp_storage[email]

    return send_otp(email, user_type)