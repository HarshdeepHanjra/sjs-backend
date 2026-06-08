# from flask import Blueprint, request, jsonify
# from app import db, bcrypt
# from app.models.user import Student, Admin
# from app.utils.helpers import generate_student_id
# from app.utils.decorators import verify_token
# from app.utils.email import send_password_reset_email  # Add this import
# from app.utils.decorators import token_required
# import jwt
# from datetime import datetime, timedelta
# import os
# import secrets

# auth_bp = Blueprint('auth', __name__)
# JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY', 'sjs-academy-secret-key')




# # Add this new endpoint for changing password
# @auth_bp.route('/change-password', methods=['POST', 'OPTIONS'])
# @token_required
# def change_password():
#     if request.method == 'OPTIONS':
#         return '', 200
    
#     try:
#         data = request.get_json()
#         current_password = data.get('current_password')
#         new_password = data.get('new_password')
        
#         if not current_password or not new_password:
#             return jsonify({'error': 'Current password and new password are required'}), 400
        
#         if len(new_password) < 6:
#             return jsonify({'error': 'New password must be at least 6 characters'}), 400
        
#         # Get user based on role
#         user = None
#         if request.user.get('role') == 'student':
#             user = Student.query.get(request.user['id'])
#         elif request.user.get('role') == 'admin':
#             user = Admin.query.get(request.user['id'])
        
#         if not user:
#             return jsonify({'error': 'User not found'}), 404
        
#         # Verify current password
#         if not bcrypt.check_password_hash(user.password_hash, current_password):
#             return jsonify({'error': 'Current password is incorrect'}), 401
        
#         # Hash new password
#         hashed_password = bcrypt.generate_password_hash(new_password).decode('utf-8')
#         user.password_hash = hashed_password
#         user.updated_at = datetime.utcnow()
        
#         db.session.commit()
        
#         return jsonify({
#             'success': True,
#             'message': 'Password changed successfully! Please login again.'
#         }), 200
        
#     except Exception as e:
#         db.session.rollback()
#         print(f"Error changing password: {e}")
#         return jsonify({'error': str(e)}), 500



# # =====================================================
# # PASSWORD RESET FUNCTIONS
# # =====================================================

# def generate_reset_token():
#     """Generate a secure random reset token"""
#     return secrets.token_urlsafe(32)

# def send_reset_email(email, reset_token):
#     """Send password reset email (for production, use actual email service)"""
#     # For development, log the reset link
#     reset_link = f"http://localhost:3000/reset-password?token={reset_token}"
#     print(f"\n{'='*60}")
#     print(f"PASSWORD RESET LINK FOR {email}")
#     print(f"Reset Link: {reset_link}")
#     print(f"{'='*60}\n")
    
#     # In production, send actual email:
#     # import smtplib
#     # from email.mime.text import MIMEText
#     # from email.mime.multipart import MIMEMultipart
#     # ... email sending code
    
#     return True


# @auth_bp.route('/forgot-password', methods=['POST', 'OPTIONS'])
# def forgot_password():
#     if request.method == 'OPTIONS':
#         return '', 200
    
#     try:
#         data = request.get_json()
#         email = data.get('email')
        
#         if not email:
#             return jsonify({'error': 'Email is required'}), 400
        
#         # Check if user exists
#         user = Student.query.filter_by(email=email).first()
#         user_type = 'student'
        
#         if not user:
#             user = Admin.query.filter_by(email=email).first()
#             user_type = 'admin'
        
#         # Always return success for security (don't reveal if email exists)
#         if user:
#             # Generate reset token and expiry
#             reset_token = generate_reset_token()
#             reset_expiry = datetime.utcnow() + timedelta(hours=1)
            
#             # Store reset token
#             user.reset_token = reset_token
#             user.reset_expiry = reset_expiry
#             db.session.commit()
            
#             # Send email with reset link
#             email_sent = send_password_reset_email(user, reset_token)
            
#             if email_sent:
#                 print(f"✅ Reset email sent to {email}")
#             else:
#                 print(f"❌ Failed to send email to {email}")
        
#         return jsonify({
#             'success': True,
#             'message': 'If your email is registered, you will receive a password reset link.'
#         }), 200
        
#     except Exception as e:
#         print(f"Forgot password error: {e}")
#         db.session.rollback()
#         return jsonify({'error': str(e)}), 500

# @auth_bp.route('/reset-password', methods=['POST', 'OPTIONS'])
# def reset_password():
#     if request.method == 'OPTIONS':
#         return '', 200
    
#     try:
#         data = request.get_json()
#         token = data.get('token')
#         new_password = data.get('new_password')
        
#         if not token or not new_password:
#             return jsonify({'error': 'Token and new password are required'}), 400
        
#         if len(new_password) < 6:
#             return jsonify({'error': 'Password must be at least 6 characters'}), 400
        
#         # Check for student with valid reset token
#         student = Student.query.filter_by(reset_token=token).first()
#         user = None
#         user_type = None
        
#         if student and student.reset_expiry and student.reset_expiry > datetime.utcnow():
#             user = student
#             user_type = 'student'
#         else:
#             # Check for admin with valid reset token
#             admin = Admin.query.filter_by(reset_token=token).first()
#             if admin and admin.reset_expiry and admin.reset_expiry > datetime.utcnow():
#                 user = admin
#                 user_type = 'admin'
        
#         if not user:
#             return jsonify({'error': 'Invalid or expired reset token'}), 400
        
#         # Update password
#         hashed_password = bcrypt.generate_password_hash(new_password).decode('utf-8')
#         user.password_hash = hashed_password
        
#         # Clear reset token
#         user.reset_token = None
#         user.reset_expiry = None
        
#         db.session.commit()
        
#         return jsonify({
#             'success': True,
#             'message': 'Password reset successfully! Please login with your new password.'
#         }), 200
        
#     except Exception as e:
#         db.session.rollback()
#         print(f"Reset password error: {e}")
#         return jsonify({'error': str(e)}), 500

# @auth_bp.route('/verify-reset-token', methods=['GET', 'OPTIONS'])
# def verify_reset_token():
#     if request.method == 'OPTIONS':
#         return '', 200
    
#     try:
#         token = request.args.get('token')
        
#         if not token:
#             return jsonify({'valid': False, 'error': 'Token required'}), 400
        
#         # Check for student
#         student = Student.query.filter_by(reset_token=token).first()
        
#         if student and student.reset_expiry and student.reset_expiry > datetime.utcnow():
#             return jsonify({'valid': True}), 200
        
#         # Check for admin
#         admin = Admin.query.filter_by(reset_token=token).first()
#         if admin and admin.reset_expiry and admin.reset_expiry > datetime.utcnow():
#             return jsonify({'valid': True}), 200
        
#         return jsonify({'valid': False, 'error': 'Invalid or expired token'}), 400
        
#     except Exception as e:
#         return jsonify({'valid': False, 'error': str(e)}), 500

    
    

# @auth_bp.route('/student/register', methods=['POST', 'OPTIONS'])
# def student_register():
#     if request.method == 'OPTIONS':
#         return '', 200
    
#     try:
#         data = request.get_json()
#         name = data.get('name')
#         email = data.get('email')
#         password = data.get('password')
#         phone = data.get('phone', '')
        
#         existing = Student.query.filter_by(email=email).first()
#         if existing:
#             return jsonify({'error': 'Email already registered'}), 400
        
#         password_hash = bcrypt.generate_password_hash(password).decode('utf-8')
#         student_id = generate_student_id()
        
#         new_student = Student(
#             student_id=student_id,
#             name=name,
#             email=email,
#             phone=phone,
#             password_hash=password_hash,
#             status='active',
#             course_ids=[]
#         )
        
#         db.session.add(new_student)
#         db.session.commit()
        
#         return jsonify({
#             'success': True,
#             'message': 'Registration successful',
#             'student_id': student_id,
#             'student': {'id': new_student.id, 'name': name, 'email': email}
#         }), 201
#     except Exception as e:
#         db.session.rollback()
#         return jsonify({'error': str(e)}), 500

# @auth_bp.route('/student/login', methods=['POST', 'OPTIONS'])
# def student_login():
#     if request.method == 'OPTIONS':
#         return '', 200
    
#     try:
#         data = request.get_json()
#         email = data.get('email')
#         password = data.get('password')
        
#         student = Student.query.filter_by(email=email).first()
        
#         if not student or not bcrypt.check_password_hash(student.password_hash, password):
#             return jsonify({'error': 'Invalid email or password'}), 401
        
#         token = jwt.encode(
#             {'id': student.id, 'role': 'student', 'email': student.email, 'name': student.name, 
#              'student_id': student.student_id, 'exp': datetime.utcnow() + timedelta(days=30)},
#             JWT_SECRET_KEY, algorithm='HS256'
#         )
        
#         return jsonify({
#             'success': True,
#             'access_token': token,
#             'student': {'id': student.id, 'student_id': student.student_id, 'name': student.name, 
#                        'email': student.email, 'phone': student.phone or ''}
#         }), 200
#     except Exception as e:
#         return jsonify({'error': str(e)}), 500

# @auth_bp.route('/admin/login', methods=['POST', 'OPTIONS'])
# def admin_login():
#     if request.method == 'OPTIONS':
#         return '', 200
    
#     try:
#         email = request.json.get('email')
#         password = request.json.get('password')
        
#         if email == 'admin@sjsacademy.com' and password == 'Admin@123':
#             token = jwt.encode(
#                 {'id': 1, 'role': 'admin', 'email': email, 'is_admin': True, 
#                  'exp': datetime.utcnow() + timedelta(days=30)},
#                 JWT_SECRET_KEY, algorithm='HS256'
#             )
#             return jsonify({
#                 'success': True,
#                 'access_token': token,
#                 'admin': {'id': 1, 'username': 'admin', 'email': email, 
#                          'full_name': 'Super Admin', 'role': 'super'}
#             }), 200
        
#         return jsonify({'error': 'Invalid credentials'}), 401
#     except Exception as e:
#         return jsonify({'error': str(e)}), 500

# @auth_bp.route('/verify-token', methods=['GET', 'OPTIONS'])
# def verify_auth_token():
#     if request.method == 'OPTIONS':
#         return '', 200
    
#     try:
#         auth_header = request.headers.get('Authorization')
#         if not auth_header:
#             return jsonify({'valid': False, 'error': 'No token provided'}), 401
        
#         token = auth_header.replace('Bearer ', '')
#         payload = verify_token(token)
        
#         if payload:
#             if payload.get('role') == 'student':
#                 user = Student.query.get(payload.get('id'))
#                 if not user:
#                     return jsonify({'valid': False, 'error': 'User not found'}), 401
                    
#                 return jsonify({
#                     'valid': True,
#                     'user': {
#                         'id': user.id,
#                         'role': 'student',
#                         'name': user.name,
#                         'email': user.email,
#                         'student_id': user.student_id
#                     }
#                 }), 200
                
#             elif payload.get('role') == 'admin':
#                 return jsonify({
#                     'valid': True,
#                     'user': {
#                         'id': payload.get('id'),
#                         'role': 'admin',
#                         'name': 'Admin',
#                         'email': payload.get('email')
#                     }
#                 }), 200
            
#             return jsonify({'valid': True, 'user': payload}), 200
#         else:
#             return jsonify({'valid': False, 'error': 'Invalid token'}), 401
#     except Exception as e:
#         return jsonify({'valid': False, 'error': str(e)}), 401

from flask import Blueprint, request, jsonify
from app import db, bcrypt
from app.models.user import Student, Admin
from app.utils.helpers import generate_student_id
from app.utils.decorators import verify_token, token_required
import jwt
from datetime import datetime, timedelta
import os
import secrets

auth_bp = Blueprint('auth', __name__)
JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY', 'sjs-academy-secret-key')


# =====================================================
# PASSWORD RESET FUNCTIONS (without model dependencies)
# =====================================================

# Store reset tokens in memory (for development)
# In production, use Redis or database
reset_tokens = {}

def generate_reset_token():
    """Generate a secure random reset token"""
    return secrets.token_urlsafe(32)

def send_reset_email(email, reset_token):
    """Send password reset email"""
    reset_link = f"http://localhost:3000/reset-password?token={reset_token}"
    print(f"\n{'='*60}")
    print(f"PASSWORD RESET LINK FOR {email}")
    print(f"Reset Link: {reset_link}")
    print(f"{'='*60}\n")
    return True


# =====================================================
# CHANGE PASSWORD
# =====================================================

@auth_bp.route('/change-password', methods=['POST', 'OPTIONS'])
@token_required
def change_password():
    if request.method == 'OPTIONS':
        return '', 200
    
    try:
        data = request.get_json()
        current_password = data.get('current_password')
        new_password = data.get('new_password')
        
        if not current_password or not new_password:
            return jsonify({'error': 'Current password and new password are required'}), 400
        
        if len(new_password) < 6:
            return jsonify({'error': 'New password must be at least 6 characters'}), 400
        
        # Get user based on role
        user = None
        if request.user.get('role') == 'student':
            user = Student.query.get(request.user['id'])
        elif request.user.get('role') == 'admin':
            user = Admin.query.get(request.user['id'])
        
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        # Check if user has password_hash attribute
        if not hasattr(user, 'password_hash') or not user.password_hash:
            return jsonify({'error': 'Password reset not supported for this account type'}), 400
        
        # Verify current password
        if not bcrypt.check_password_hash(user.password_hash, current_password):
            return jsonify({'error': 'Current password is incorrect'}), 401
        
        # Hash new password
        hashed_password = bcrypt.generate_password_hash(new_password).decode('utf-8')
        user.password_hash = hashed_password
        
        # Update updated_at if column exists
        if hasattr(user, 'updated_at'):
            user.updated_at = datetime.utcnow()
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Password changed successfully! Please login again.'
        }), 200
        
    except Exception as e:
        db.session.rollback()
        print(f"Error changing password: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500


# =====================================================
# FORGOT PASSWORD
# =====================================================

@auth_bp.route('/forgot-password', methods=['POST', 'OPTIONS'])
def forgot_password():
    if request.method == 'OPTIONS':
        return '', 200
    
    try:
        data = request.get_json()
        email = data.get('email')
        
        if not email:
            return jsonify({'error': 'Email is required'}), 400
        
        # Check if user exists in Student model
        student = Student.query.filter_by(email=email).first()
        
        if student:
            # Generate token and store in memory (or database)
            reset_token = generate_reset_token()
            reset_tokens[reset_token] = {
                'email': email,
                'user_type': 'student',
                'expiry': datetime.utcnow() + timedelta(hours=1)
            }
            
            # Send email
            send_reset_email(email, reset_token)
            print(f"✅ Reset token generated for student: {email}")
        
        # Check Admin model
        admin = Admin.query.filter_by(email=email).first()
        if admin:
            reset_token = generate_reset_token()
            reset_tokens[reset_token] = {
                'email': email,
                'user_type': 'admin',
                'expiry': datetime.utcnow() + timedelta(hours=1)
            }
            send_reset_email(email, reset_token)
            print(f"✅ Reset token generated for admin: {email}")
        
        # Always return success for security (don't reveal if email exists)
        return jsonify({
            'success': True,
            'message': 'If your email is registered, you will receive a password reset link.'
        }), 200
        
    except Exception as e:
        print(f"Forgot password error: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500


# =====================================================
# RESET PASSWORD
# =====================================================

@auth_bp.route('/reset-password', methods=['POST', 'OPTIONS'])
def reset_password():
    if request.method == 'OPTIONS':
        return '', 200
    
    try:
        data = request.get_json()
        token = data.get('token')
        new_password = data.get('new_password')
        
        if not token or not new_password:
            return jsonify({'error': 'Token and new password are required'}), 400
        
        if len(new_password) < 6:
            return jsonify({'error': 'Password must be at least 6 characters'}), 400
        
        # Check token in memory storage
        token_data = reset_tokens.get(token)
        
        if not token_data:
            return jsonify({'error': 'Invalid or expired reset token'}), 400
        
        # Check expiry
        if token_data['expiry'] < datetime.utcnow():
            del reset_tokens[token]
            return jsonify({'error': 'Reset token has expired'}), 400
        
        # Find user
        email = token_data['email']
        user_type = token_data['user_type']
        
        user = None
        if user_type == 'student':
            user = Student.query.filter_by(email=email).first()
        else:
            user = Admin.query.filter_by(email=email).first()
        
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        # Check if user has password_hash attribute
        if not hasattr(user, 'password_hash'):
            return jsonify({'error': 'Password reset not supported for this account'}), 400
        
        # Update password
        hashed_password = bcrypt.generate_password_hash(new_password).decode('utf-8')
        user.password_hash = hashed_password
        
        # Clear token
        del reset_tokens[token]
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Password reset successfully! Please login with your new password.'
        }), 200
        
    except Exception as e:
        db.session.rollback()
        print(f"Reset password error: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500


# =====================================================
# VERIFY RESET TOKEN
# =====================================================

@auth_bp.route('/verify-reset-token', methods=['GET', 'OPTIONS'])
def verify_reset_token():
    if request.method == 'OPTIONS':
        return '', 200
    
    try:
        token = request.args.get('token')
        
        if not token:
            return jsonify({'valid': False, 'error': 'Token required'}), 400
        
        # Check token in memory storage
        token_data = reset_tokens.get(token)
        
        if token_data and token_data['expiry'] > datetime.utcnow():
            return jsonify({'valid': True}), 200
        
        return jsonify({'valid': False, 'error': 'Invalid or expired token'}), 400
        
    except Exception as e:
        print(f"Verify token error: {e}")
        return jsonify({'valid': False, 'error': str(e)}), 500


# =====================================================
# STUDENT REGISTER
# =====================================================

@auth_bp.route('/student/register', methods=['POST', 'OPTIONS'])
def student_register():
    if request.method == 'OPTIONS':
        return '', 200
    
    try:
        data = request.get_json()
        name = data.get('name')
        email = data.get('email')
        password = data.get('password')
        phone = data.get('phone', '')
        
        # Check if student already exists
        existing = Student.query.filter_by(email=email).first()
        if existing:
            return jsonify({'error': 'Email already registered'}), 400
        
        # Check if password_hash column exists, otherwise use password
        password_hash = bcrypt.generate_password_hash(password).decode('utf-8')
        student_id = generate_student_id()
        
        # Create student based on available columns
        new_student = Student(
            student_id=student_id,
            name=name,
            email=email,
            phone=phone,
            status='active'
        )
        
        # Add password_hash if column exists
        if hasattr(new_student, 'password_hash'):
            new_student.password_hash = password_hash
        elif hasattr(new_student, 'password'):
            new_student.password = password_hash
        
        db.session.add(new_student)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Registration successful',
            'student_id': student_id,
            'student': {'id': new_student.id, 'name': name, 'email': email}
        }), 201
        
    except Exception as e:
        db.session.rollback()
        print(f"Registration error: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500


# =====================================================
# STUDENT LOGIN
# =====================================================

@auth_bp.route('/student/login', methods=['POST', 'OPTIONS'])
def student_login():
    if request.method == 'OPTIONS':
        return '', 200
    
    try:
        data = request.get_json()
        email = data.get('email')
        password = data.get('password')
        
        student = Student.query.filter_by(email=email).first()
        
        if not student:
            return jsonify({'error': 'Invalid email or password'}), 401
        
        # Check password based on available column
        password_valid = False
        if hasattr(student, 'password_hash') and student.password_hash:
            password_valid = bcrypt.check_password_hash(student.password_hash, password)
        elif hasattr(student, 'password') and student.password:
            password_valid = bcrypt.check_password_hash(student.password, password)
        
        if not password_valid:
            return jsonify({'error': 'Invalid email or password'}), 401
        
        token = jwt.encode(
            {'id': student.id, 'role': 'student', 'email': student.email, 'name': student.name, 
             'student_id': student.student_id, 'exp': datetime.utcnow() + timedelta(days=30)},
            JWT_SECRET_KEY, algorithm='HS256'
        )
        
        return jsonify({
            'success': True,
            'access_token': token,
            'student': {
                'id': student.id, 
                'student_id': student.student_id, 
                'name': student.name, 
                'email': student.email, 
                'phone': student.phone or ''
            }
        }), 200
        
    except Exception as e:
        print(f"Student login error: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500


# =====================================================
# ADMIN LOGIN
# =====================================================

@auth_bp.route('/admin/login', methods=['POST', 'OPTIONS'])
def admin_login():
    if request.method == 'OPTIONS':
        return '', 200
    
    try:
        email = request.json.get('email')
        password = request.json.get('password')
        
        # Check for default admin
        if email == 'admin@sjsacademy.com' and password == 'Admin@123':
            token = jwt.encode(
                {'id': 1, 'role': 'admin', 'email': email, 'is_admin': True, 
                 'exp': datetime.utcnow() + timedelta(days=30)},
                JWT_SECRET_KEY, algorithm='HS256'
            )
            return jsonify({
                'success': True,
                'access_token': token,
                'admin': {'id': 1, 'username': 'admin', 'email': email, 
                         'full_name': 'Super Admin', 'role': 'super'}
            }), 200
        
        # Check database admin
        admin = Admin.query.filter_by(email=email).first()
        if admin:
            # Check password
            if hasattr(admin, 'password_hash') and admin.password_hash:
                if bcrypt.check_password_hash(admin.password_hash, password):
                    token = jwt.encode(
                        {'id': admin.id, 'role': 'admin', 'email': admin.email,
                         'exp': datetime.utcnow() + timedelta(days=30)},
                        JWT_SECRET_KEY, algorithm='HS256'
                    )
                    return jsonify({
                        'success': True,
                        'access_token': token,
                        'admin': {'id': admin.id, 'username': admin.username, 'email': admin.email}
                    }), 200
        
        return jsonify({'error': 'Invalid credentials'}), 401
        
    except Exception as e:
        print(f"Admin login error: {e}")
        return jsonify({'error': str(e)}), 500


# =====================================================
# VERIFY TOKEN
# =====================================================

@auth_bp.route('/verify-token', methods=['GET', 'OPTIONS'])
def verify_auth_token():
    if request.method == 'OPTIONS':
        return '', 200
    
    try:
        auth_header = request.headers.get('Authorization')
        if not auth_header:
            return jsonify({'valid': False, 'error': 'No token provided'}), 401
        
        token = auth_header.replace('Bearer ', '')
        payload = verify_token(token)
        
        if payload:
            if payload.get('role') == 'student':
                user = Student.query.get(payload.get('id'))
                if not user:
                    return jsonify({'valid': False, 'error': 'User not found'}), 401
                    
                return jsonify({
                    'valid': True,
                    'user': {
                        'id': user.id,
                        'role': 'student',
                        'name': user.name,
                        'email': user.email,
                        'student_id': user.student_id
                    }
                }), 200
                
            elif payload.get('role') == 'admin':
                return jsonify({
                    'valid': True,
                    'user': {
                        'id': payload.get('id'),
                        'role': 'admin',
                        'name': 'Admin',
                        'email': payload.get('email')
                    }
                }), 200
            
            return jsonify({'valid': True, 'user': payload}), 200
        else:
            return jsonify({'valid': False, 'error': 'Invalid token'}), 401
    except Exception as e:
        print(f"Verify token error: {e}")
        return jsonify({'valid': False, 'error': str(e)}), 401