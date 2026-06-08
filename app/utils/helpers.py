import random
import string
import os
import jwt
import hashlib
from datetime import datetime
from werkzeug.utils import secure_filename
from flask import current_app

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'pdf', 'webp'}
JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY', 'sjs-academy-secret-key-2024')  # ✅ Fixed

def generate_student_id():
    year = datetime.now().strftime('%Y')
    month = datetime.now().strftime('%m')
    day = datetime.now().strftime('%d')
    random_num = ''.join(random.choices(string.digits, k=4))
    return f"SJS{year}{month}{day}{random_num}"

def generate_order_id():
    timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
    random_num = ''.join(random.choices(string.digits, k=4))
    return f"ORD{timestamp}{random_num}"

def generate_verification_id():
    timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
    random_num = ''.join(random.choices(string.digits, k=4))
    return f"VER{timestamp}{random_num}"

def generate_certificate_id():
    timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
    random_num = ''.join(random.choices(string.digits, k=6))
    return f"CERT{timestamp}{random_num}"

def generate_verification_token(student_id, course_id):
    """Generate a unique verification token for certificate"""
    data = f"{student_id}{course_id}{datetime.now().timestamp()}{random.randint(1000, 9999)}"
    return hashlib.sha256(data.encode()).hexdigest()[:32]

def generate_certificate_hash(certificate_id, student_email, course_name):
    """Generate a unique hash for certificate"""
    data = f"{certificate_id}{student_email}{course_name}{datetime.now().timestamp()}"
    return hashlib.sha256(data.encode()).hexdigest()

def verify_token(token):
    try:
        payload = jwt.decode(token, JWT_SECRET_KEY, algorithms=['HS256'])
        return payload
    except:
        return None

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def upload_file(file, folder=None):
    if not file or not allowed_file(file.filename):
        return None
    
    filename = secure_filename(file.filename)
    name, ext = os.path.splitext(filename)
    timestamp = int(datetime.now().timestamp())
    filename = f"{name}_{timestamp}{ext}"
    
    upload_folder = current_app.config.get('UPLOAD_FOLDER', 'uploads')
    if folder:
        upload_folder = os.path.join(upload_folder, folder)
    
    os.makedirs(upload_folder, exist_ok=True)
    filepath = os.path.join(upload_folder, filename)
    file.save(filepath)
    
    return f"/uploads/{folder}/{filename}" if folder else f"/uploads/{filename}"

def generate_qr_code_url(certificate_id):
    """Generate QR code URL for certificate"""
    return f"/api/certificates/verify/{certificate_id}"

def format_currency(amount):
    """Format amount as Indian currency"""
    return f"₹{amount:,.2f}"

def calculate_percentage(part, total):
    """Calculate percentage"""
    if total == 0:
        return 0
    return round((part / total) * 100, 2)