# import uuid

# from flask import Blueprint, current_app, request, jsonify
# from app import db, bcrypt
# from app.models.user import Student, Admin
# from app.utils.helpers import generate_student_id
# from app.utils.decorators import verify_token, token_required
# import jwt
# from datetime import datetime, timedelta
# import os
# import secrets
# from app.utils.email_otp import send_otp, verify_otp, resend_otp


# auth_bp = Blueprint('auth', __name__)
# JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY', 'sjs-academy-jwt-secret-2024')


# # =====================================================
# # PASSWORD RESET FUNCTIONS (without model dependencies)
# # =====================================================

# # Store reset tokens in memory (for development)
# # In production, use Redis or database
# reset_tokens = {}

# def generate_reset_token():
#     """Generate a secure random reset token"""
#     return secrets.token_urlsafe(32)

# def send_reset_email(email, reset_token):
#     """Send password reset email"""
#     # ✅ Get frontend URL from environment
#     frontend_url = os.getenv('FRONTEND_URL', 'https://sjs-frontend-delta.vercel.app')
#     reset_link = f"{frontend_url}/reset-password?token={reset_token}"
#     print(f"\n{'='*60}")
#     print(f"PASSWORD RESET LINK FOR {email}")
#     print(f"Reset Link: {reset_link}")
#     print(f"{'='*60}\n")
#     return True


# # =====================================================
# # CHANGE PASSWORD
# # =====================================================

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
        
#         # Check if user has password_hash attribute
#         if not hasattr(user, 'password_hash') or not user.password_hash:
#             return jsonify({'error': 'Password reset not supported for this account type'}), 400
        
#         # Verify current password
#         if not bcrypt.check_password_hash(user.password_hash, current_password):
#             return jsonify({'error': 'Current password is incorrect'}), 401
        
#         # Hash new password
#         hashed_password = bcrypt.generate_password_hash(new_password).decode('utf-8')
#         user.password_hash = hashed_password
        
#         # Update updated_at if column exists
#         if hasattr(user, 'updated_at'):
#             user.updated_at = datetime.utcnow()
        
#         db.session.commit()
        
#         return jsonify({
#             'success': True,
#             'message': 'Password changed successfully! Please login again.'
#         }), 200
        
#     except Exception as e:
#         db.session.rollback()
#         print(f"Error changing password: {e}")
#         import traceback
#         traceback.print_exc()
#         return jsonify({'error': str(e)}), 500


# # =====================================================
# # FORGOT PASSWORD
# # =====================================================

# @auth_bp.route('/forgot-password', methods=['POST', 'OPTIONS'])
# def forgot_password():
#     if request.method == 'OPTIONS':
#         return '', 200
    
#     try:
#         data = request.get_json()
#         email = data.get('email')
        
#         if not email:
#             return jsonify({'error': 'Email is required'}), 400
        
#         # Check if user exists in Student model
#         student = Student.query.filter_by(email=email).first()
        
#         if student:
#             # Generate token and store in memory (or database)
#             reset_token = generate_reset_token()
#             reset_tokens[reset_token] = {
#                 'email': email,
#                 'user_type': 'student',
#                 'expiry': datetime.utcnow() + timedelta(hours=1)
#             }
            
#             # Send email
#             send_reset_email(email, reset_token)
#             print(f"✅ Reset token generated for student: {email}")
        
#         # Check Admin model
#         admin = Admin.query.filter_by(email=email).first()
#         if admin:
#             reset_token = generate_reset_token()
#             reset_tokens[reset_token] = {
#                 'email': email,
#                 'user_type': 'admin',
#                 'expiry': datetime.utcnow() + timedelta(hours=1)
#             }
#             send_reset_email(email, reset_token)
#             print(f"✅ Reset token generated for admin: {email}")
        
#         # Always return success for security (don't reveal if email exists)
#         return jsonify({
#             'success': True,
#             'message': 'If your email is registered, you will receive a password reset link.'
#         }), 200
        
#     except Exception as e:
#         print(f"Forgot password error: {e}")
#         import traceback
#         traceback.print_exc()
#         return jsonify({'error': str(e)}), 500


# # =====================================================
# # RESET PASSWORD
# # =====================================================

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
        
#         # Check token in memory storage
#         token_data = reset_tokens.get(token)
        
#         if not token_data:
#             return jsonify({'error': 'Invalid or expired reset token'}), 400
        
#         # Check expiry
#         if token_data['expiry'] < datetime.utcnow():
#             del reset_tokens[token]
#             return jsonify({'error': 'Reset token has expired'}), 400
        
#         # Find user
#         email = token_data['email']
#         user_type = token_data['user_type']
        
#         user = None
#         if user_type == 'student':
#             user = Student.query.filter_by(email=email).first()
#         else:
#             user = Admin.query.filter_by(email=email).first()
        
#         if not user:
#             return jsonify({'error': 'User not found'}), 404
        
#         # Check if user has password_hash attribute
#         if not hasattr(user, 'password_hash'):
#             return jsonify({'error': 'Password reset not supported for this account'}), 400
        
#         # Update password
#         hashed_password = bcrypt.generate_password_hash(new_password).decode('utf-8')
#         user.password_hash = hashed_password
        
#         # Clear token
#         del reset_tokens[token]
        
#         db.session.commit()
        
#         return jsonify({
#             'success': True,
#             'message': 'Password reset successfully! Please login with your new password.'
#         }), 200
        
#     except Exception as e:
#         db.session.rollback()
#         print(f"Reset password error: {e}")
#         import traceback
#         traceback.print_exc()
#         return jsonify({'error': str(e)}), 500


# # =====================================================
# # VERIFY RESET TOKEN
# # =====================================================

# @auth_bp.route('/verify-reset-token', methods=['GET', 'OPTIONS'])
# def verify_reset_token():
#     if request.method == 'OPTIONS':
#         return '', 200
    
#     try:
#         token = request.args.get('token')
        
#         if not token:
#             return jsonify({'valid': False, 'error': 'Token required'}), 400
        
#         # Check token in memory storage
#         token_data = reset_tokens.get(token)
        
#         if token_data and token_data['expiry'] > datetime.utcnow():
#             return jsonify({'valid': True}), 200
        
#         return jsonify({'valid': False, 'error': 'Invalid or expired token'}), 400
        
#     except Exception as e:
#         print(f"Verify token error: {e}")
#         return jsonify({'valid': False, 'error': str(e)}), 500


# # =====================================================
# # STUDENT REGISTER
# # =====================================================

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
        
#         # Check if student already exists
#         existing = Student.query.filter_by(email=email).first()
#         if existing:
#             return jsonify({'error': 'Email already registered'}), 400
        
#         # Check if password_hash column exists, otherwise use password
#         password_hash = bcrypt.generate_password_hash(password).decode('utf-8')
#         student_id = generate_student_id()
        
#         # Create student based on available columns
#         new_student = Student(
#             student_id=student_id,
#             name=name,
#             email=email,
#             phone=phone,
#             status='active'
#         )
        
#         # Add password_hash if column exists
#         if hasattr(new_student, 'password_hash'):
#             new_student.password_hash = password_hash
#         elif hasattr(new_student, 'password'):
#             new_student.password = password_hash
        
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
#         print(f"Registration error: {e}")
#         import traceback
#         traceback.print_exc()
#         return jsonify({'error': str(e)}), 500




# # =====================================================
# # STUDENT LOGIN
# # =====================================================

# # @auth_bp.route('/student/login', methods=['POST', 'OPTIONS'])
# # def student_login():
# #     if request.method == 'OPTIONS':
# #         return '', 200
    
# #     try:
# #         data = request.get_json()
# #         email = data.get('email')
# #         password = data.get('password')
        
# #         student = Student.query.filter_by(email=email).first()
        
# #         if not student:
# #             return jsonify({'error': 'Invalid email or password'}), 401
        
# #         # Check password based on available column
# #         password_valid = False
# #         if hasattr(student, 'password_hash') and student.password_hash:
# #             password_valid = bcrypt.check_password_hash(student.password_hash, password)
# #         elif hasattr(student, 'password') and student.password:
# #             password_valid = bcrypt.check_password_hash(student.password, password)
        
# #         if not password_valid:
# #             return jsonify({'error': 'Invalid email or password'}), 401
        
# #         token = jwt.encode(
# #             {'id': student.id, 'role': 'student', 'email': student.email, 'name': student.name, 
# #              'student_id': student.student_id, 'exp': datetime.utcnow() + timedelta(days=30)},
# #             JWT_SECRET_KEY, algorithm='HS256'
# #         )
        
# #         return jsonify({
# #             'success': True,
# #             'access_token': token,
# #             'student': {
# #                 'id': student.id, 
# #                 'student_id': student.student_id, 
# #                 'name': student.name, 
# #                 'email': student.email, 
# #                 'phone': student.phone or ''
# #             }
# #         }), 200
        
# #     except Exception as e:
# #         print(f"Student login error: {e}")
# #         import traceback
# #         traceback.print_exc()
# #         return jsonify({'error': str(e)}), 500


# # Update student_login function (replace existing one)
# @auth_bp.route('/student/login', methods=['POST'])
# def student_login():
#     try:
#         data = request.get_json()
#         email = data.get('email')
#         password = data.get('password')
#         otp = data.get('otp')
#         session_id = data.get('session_id')
        
#         student = Student.query.filter_by(email=email).first()
        
#         if not student or not bcrypt.check_password_hash(student.password_hash, password):
#             return jsonify({'error': 'Invalid email or password'}), 401
        
#         # First step - password verified, need OTP
#         if not otp and not session_id:
#             session_id = str(uuid.uuid4())
#             success, otp_code = send_otp(student.email, 'student')
            
#             if success:
#                 if not hasattr(current_app, 'login_sessions'):
#                     current_app.login_sessions = {}
                
#                 current_app.login_sessions[session_id] = {
#                     'user_id': student.id,
#                     'role': 'student',
#                     'email': student.email,
#                     'expires_at': datetime.utcnow() + timedelta(minutes=10)
#                 }
                
#                 return jsonify({
#                     'requires_otp': True,
#                     'session_id': session_id,
#                     'message': f'OTP sent to {student.email}'
#                 }), 200
#             else:
#                 return jsonify({'error': 'Failed to send OTP'}), 500
        
#         # Second step - Verify OTP
#         elif otp and session_id:
#             if not hasattr(current_app, 'login_sessions') or session_id not in current_app.login_sessions:
#                 return jsonify({'error': 'Session expired'}), 401
            
#             session_data = current_app.login_sessions[session_id]
            
#             if datetime.utcnow() > session_data['expires_at']:
#                 del current_app.login_sessions[session_id]
#                 return jsonify({'error': 'Session expired'}), 401
            
#             if verify_otp(session_data['email'], otp):
#                 del current_app.login_sessions[session_id]
                
#                 token = jwt.encode(
#                     {'id': student.id, 'role': 'student', 'email': student.email, 
#                      'name': student.name, 'student_id': student.student_id, 
#                      'exp': datetime.utcnow() + timedelta(days=30)},
#                     current_app.config['JWT_SECRET_KEY'], algorithm='HS256'
#                 )
                
#                 return jsonify({
#                     'success': True,
#                     'access_token': token,
#                     'student': {
#                         'id': student.id, 
#                         'student_id': student.student_id, 
#                         'name': student.name, 
#                         'email': student.email
#                     }
#                 }), 200
#             else:
#                 return jsonify({'error': 'Invalid OTP'}), 401
#         else:
#             return jsonify({'error': 'Invalid request'}), 400
            
#     except Exception as e:
#         print(f"Student login error: {e}")
#         return jsonify({'error': str(e)}), 500


# # =====================================================
# # ADMIN LOGIN
# # =====================================================

# # @auth_bp.route('/admin/login', methods=['POST', 'OPTIONS'])
# # def admin_login():
# #     if request.method == 'OPTIONS':
# #         return '', 200
    
# #     try:
# #         email = request.json.get('email')
# #         password = request.json.get('password')
        
# #         # Check for default admin
# #         if email == 'admin@sjsacademy.com' and password == 'Admin@123':
# #             token = jwt.encode(
# #                 {'id': 1, 'role': 'admin', 'email': email, 'is_admin': True, 
# #                  'exp': datetime.utcnow() + timedelta(days=30)},
# #                 JWT_SECRET_KEY, algorithm='HS256'
# #             )
# #             return jsonify({
# #                 'success': True,
# #                 'access_token': token,
# #                 'admin': {'id': 1, 'username': 'admin', 'email': email, 
# #                          'full_name': 'Super Admin', 'role': 'super'}
# #             }), 200
        
# #         # Check database admin
# #         admin = Admin.query.filter_by(email=email).first()
# #         if admin:
# #             # Check password
# #             if hasattr(admin, 'password_hash') and admin.password_hash:
# #                 if bcrypt.check_password_hash(admin.password_hash, password):
# #                     token = jwt.encode(
# #                         {'id': admin.id, 'role': 'admin', 'email': admin.email,
# #                          'exp': datetime.utcnow() + timedelta(days=30)},
# #                         JWT_SECRET_KEY, algorithm='HS256'
# #                     )
# #                     return jsonify({
# #                         'success': True,
# #                         'access_token': token,
# #                         'admin': {'id': admin.id, 'username': admin.username, 'email': admin.email}
# #                     }), 200
        
# #         return jsonify({'error': 'Invalid credentials'}), 401
        
# #     except Exception as e:
# #         print(f"Admin login error: {e}")
# #         return jsonify({'error': str(e)}), 500

# @auth_bp.route('/admin/login', methods=['POST'])
# def admin_login():
#     try:
#         data = request.get_json()
#         email = data.get('email')
#         password = data.get('password')
#         otp = data.get('otp')
#         session_id = data.get('session_id')
        
#         ADMIN_EMAIL = "harshdeephanjra22@gmail.com"
        
#         if email == 'admin@sjsacademy.com' and password == 'Admin@123':
            
#             if not otp and not session_id:
#                 session_id = str(uuid.uuid4())
#                 success, otp_code = send_otp(ADMIN_EMAIL, 'admin')
                
#                 if success:
#                     if not hasattr(current_app, 'login_sessions'):
#                         current_app.login_sessions = {}
                    
#                     current_app.login_sessions[session_id] = {
#                         'user_id': 1,
#                         'role': 'admin',
#                         'email': ADMIN_EMAIL,
#                         'expires_at': datetime.utcnow() + timedelta(minutes=10)
#                     }
                    
#                     return jsonify({
#                         'requires_otp': True,
#                         'session_id': session_id,
#                         'message': f'OTP sent to {ADMIN_EMAIL}'
#                     }), 200
#                 else:
#                     return jsonify({'error': 'Failed to send OTP'}), 500
            
#             elif otp and session_id:
#                 if not hasattr(current_app, 'login_sessions') or session_id not in current_app.login_sessions:
#                     return jsonify({'error': 'Session expired'}), 401
                
#                 session_data = current_app.login_sessions[session_id]
                
#                 if datetime.utcnow() > session_data['expires_at']:
#                     del current_app.login_sessions[session_id]
#                     return jsonify({'error': 'Session expired'}), 401
                
#                 if verify_otp(session_data['email'], otp):
#                     del current_app.login_sessions[session_id]
                    
#                     token = jwt.encode(
#                         {'id': 1, 'role': 'admin', 'email': email, 'is_admin': True,
#                          'exp': datetime.utcnow() + timedelta(days=30)},
#                         current_app.config['JWT_SECRET_KEY'], algorithm='HS256'
#                     )
#                     return jsonify({
#                         'success': True,
#                         'access_token': token,
#                         'admin': {
#                             'id': 1, 
#                             'username': 'admin', 
#                             'email': email, 
#                             'full_name': 'Super Admin', 
#                             'role': 'super'
#                         }
#                     }), 200
#                 else:
#                     return jsonify({'error': 'Invalid OTP'}), 401
#             else:
#                 return jsonify({'error': 'Invalid request'}), 400
        
#         return jsonify({'error': 'Invalid credentials'}), 401
#     except Exception as e:
#         print(f"Admin login error: {e}")
#         return jsonify({'error': str(e)}), 500

# # =====================================================
# # VERIFY TOKEN
# # =====================================================

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
#         print(f"Verify token error: {e}")
#         return jsonify({'valid': False, 'error': str(e)}), 401
    



# # Add new route for resend OTP
# @auth_bp.route('/resend-otp', methods=['POST'])
# def resend_otp_code():
#     try:
#         data = request.get_json()
#         session_id = data.get('session_id')
#         user_type = data.get('user_type', 'student')
        
#         if not hasattr(current_app, 'login_sessions') or session_id not in current_app.login_sessions:
#             return jsonify({'error': 'Session expired'}), 401
        
#         session_data = current_app.login_sessions[session_id]
#         success, otp_code = resend_otp(session_data['email'], user_type)
        
#         if success:
#             session_data['expires_at'] = datetime.utcnow() + timedelta(minutes=10)
#             current_app.login_sessions[session_id] = session_data
            
#             return jsonify({'success': True, 'message': 'OTP resent successfully'}), 200
#         else:
#             return jsonify({'error': 'Failed to resend OTP'}), 500
#     except Exception as e:
#         print(f"Resend OTP error: {e}")
#         return jsonify({'error': str(e)}), 500






import uuid
import requests
from flask import Blueprint, current_app, request, jsonify
from app import db, bcrypt
from app.models.user import Student, Admin
from app.utils.helpers import generate_student_id
from app.utils.decorators import verify_token, token_required
import jwt
from datetime import datetime, timedelta
import os
import secrets
from app.utils.email_otp import send_otp, verify_otp, resend_otp

auth_bp = Blueprint('auth', __name__)
JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY', 'sjs-academy-jwt-secret-2024')

# Store reset tokens in memory
reset_tokens = {}

def generate_reset_token():
    """Generate a secure random reset token"""
    return secrets.token_urlsafe(32)

def send_reset_email(email, reset_token):
    """Send password reset email"""
    frontend_url = os.getenv('FRONTEND_URL', 'https://sjs-frontend-delta.vercel.app')
    reset_link = f"{frontend_url}/reset-password?token={reset_token}"
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
        
        user = None
        if request.user.get('role') == 'student':
            user = Student.query.get(request.user['id'])
        elif request.user.get('role') == 'admin':
            user = Admin.query.get(request.user['id'])
        
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        if not hasattr(user, 'password_hash') or not user.password_hash:
            return jsonify({'error': 'Password reset not supported for this account type'}), 400
        
        if not bcrypt.check_password_hash(user.password_hash, current_password):
            return jsonify({'error': 'Current password is incorrect'}), 401
        
        hashed_password = bcrypt.generate_password_hash(new_password).decode('utf-8')
        user.password_hash = hashed_password
        
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
        
        # Check for student
        student = Student.query.filter_by(email=email).first()
        
        if student:
            reset_token = generate_reset_token()
            reset_tokens[reset_token] = {
                'email': email,
                'user_type': 'student',
                'user_id': student.id,
                'expiry': datetime.utcnow() + timedelta(hours=1)
            }
            
            # Send email using Brevo
            email_sent = send_password_reset_email_brevo(student, reset_token)
            
            if email_sent:
                print(f"✅ Reset email sent to student: {email}")
            else:
                print(f"❌ Failed to send reset email to student: {email}")
        
        # Check for admin
        admin = Admin.query.filter_by(email=email).first()
        if admin:
            reset_token = generate_reset_token()
            reset_tokens[reset_token] = {
                'email': email,
                'user_type': 'admin',
                'user_id': admin.id,
                'expiry': datetime.utcnow() + timedelta(hours=1)
            }
            
            # Send email using Brevo
            email_sent = send_password_reset_email_brevo(admin, reset_token)
            
            if email_sent:
                print(f"✅ Reset email sent to admin: {email}")
            else:
                print(f"❌ Failed to send reset email to admin: {email}")
        
        # Always return success for security (don't reveal if email exists or not)
        return jsonify({
            'success': True,
            'message': 'If your email is registered, you will receive a password reset link.'
        }), 200
        
    except Exception as e:
        print(f"Forgot password error: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500


def send_password_reset_email_brevo(user, reset_token):
    """
    Send password reset email using Brevo API
    """
    try:
        frontend_url = os.getenv('FRONTEND_URL', 'https://sjs-frontend-delta.vercel.app')
        reset_url = f"{frontend_url}/reset-password?token={reset_token}"
        
        brevo_api_key = os.getenv('BREVO_API_KEY')
        
        if not brevo_api_key:
            print("❌ BREVO_API_KEY not configured")
            return False
        
        sender_email = os.getenv('BREVO_SENDER_EMAIL', 'sjsglobaltech@gmail.com')
        sender_name = os.getenv('BREVO_SENDER_NAME', 'SJS Academy')
        
        subject = "Password Reset Request - SJS Academy"
        
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Password Reset</title>
            <style>
                body {{
                    font-family: 'Segoe UI', Arial, sans-serif;
                    line-height: 1.6;
                    color: #333;
                    margin: 0;
                    padding: 0;
                    background-color: #f4f4f4;
                }}
                .container {{
                    max-width: 600px;
                    margin: 50px auto;
                    background-color: #ffffff;
                    border-radius: 10px;
                    box-shadow: 0 2px 10px rgba(0,0,0,0.1);
                    overflow: hidden;
                }}
                .header {{
                    background: linear-gradient(135deg, #1a3a5c 0%, #2c5a8c 100%);
                    color: white;
                    padding: 30px;
                    text-align: center;
                }}
                .header h1 {{
                    margin: 0;
                    font-size: 24px;
                }}
                .header p {{
                    margin: 10px 0 0;
                    opacity: 0.9;
                }}
                .content {{
                    padding: 30px;
                }}
                .button {{
                    display: inline-block;
                    background: linear-gradient(135deg, #1a3a5c 0%, #2c5a8c 100%);
                    color: white;
                    padding: 12px 30px;
                    text-decoration: none;
                    border-radius: 5px;
                    font-weight: bold;
                    margin: 20px 0;
                }}
                .warning {{
                    background: #fff3cd;
                    padding: 15px;
                    margin: 20px 0;
                    border-left: 4px solid #ffc107;
                    border-radius: 5px;
                }}
                .footer {{
                    text-align: center;
                    padding: 20px;
                    font-size: 12px;
                    color: #666;
                    border-top: 1px solid #eee;
                    background-color: #f9f9f9;
                }}
                .footer a {{
                    color: #1a3a5c;
                    text-decoration: none;
                }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>SJS Global Tech Academy</h1>
                    <p>Password Reset Request</p>
                </div>
                <div class="content">
                    <p>Dear <strong>{user.name}</strong>,</p>
                    <p>We received a request to reset the password for your SJS Academy account.</p>
                    <p>Click the button below to create a new password:</p>
                    <p style="text-align: center;">
                        <a href="{reset_url}" class="button">Reset Password</a>
                    </p>
                    <p>Or copy and paste this link into your browser:</p>
                    <p><small style="word-break: break-all; color: #1a3a5c;">{reset_url}</small></p>
                    <div class="warning">
                        <strong>⚠️ Important:</strong> This link will expire in <strong>1 hour</strong>.<br>
                        If you did not request a password reset, please ignore this email. Your password will remain unchanged.
                    </div>
                </div>
                <div class="footer">
                    <p>SJS Global Tech Academy</p>
                    <p>© 2024 SJS Academy. All rights reserved.</p>
                    <p><a href="{frontend_url}">Visit our website</a></p>
                </div>
            </div>
        </body>
        </html>
        """
        
        url = "https://api.brevo.com/v3/smtp/email"
        
        payload = {
            "sender": {
                "name": sender_name,
                "email": sender_email
            },
            "to": [
                {
                    "email": user.email,
                    "name": user.name
                }
            ],
            "subject": subject,
            "htmlContent": html_content
        }
        
        headers = {
            "accept": "application/json",
            "api-key": brevo_api_key,
            "content-type": "application/json"
        }
        
        response = requests.post(url, json=payload, headers=headers)
        
        if response.status_code == 201:
            print(f"✅ Password reset email sent to {user.email}")
            return True
        else:
            print(f"❌ Brevo API error: {response.status_code} - {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Error sending email: {e}")
        return False

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
        
        token_data = reset_tokens.get(token)
        
        if not token_data:
            return jsonify({'error': 'Invalid or expired reset token'}), 400
        
        if token_data['expiry'] < datetime.utcnow():
            del reset_tokens[token]
            return jsonify({'error': 'Reset token has expired'}), 400
        
        email = token_data['email']
        user_type = token_data['user_type']
        
        user = None
        if user_type == 'student':
            user = Student.query.filter_by(email=email).first()
        else:
            user = Admin.query.filter_by(email=email).first()
        
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        if not hasattr(user, 'password_hash'):
            return jsonify({'error': 'Password reset not supported for this account'}), 400
        
        hashed_password = bcrypt.generate_password_hash(new_password).decode('utf-8')
        user.password_hash = hashed_password
        
        del reset_tokens[token]
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Password reset successfully! Please login with your new password.'
        }), 200
        
    except Exception as e:
        db.session.rollback()
        print(f"Reset password error: {e}")
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
        
        token_data = reset_tokens.get(token)
        
        if token_data and token_data['expiry'] > datetime.utcnow():
            return jsonify({'valid': True}), 200
        
        return jsonify({'valid': False, 'error': 'Invalid or expired token'}), 400
        
    except Exception as e:
        print(f"Verify token error: {e}")
        return jsonify({'valid': False, 'error': str(e)}), 400

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
        
        existing = Student.query.filter_by(email=email).first()
        if existing:
            return jsonify({'error': 'Email already registered'}), 400
        
        password_hash = bcrypt.generate_password_hash(password).decode('utf-8')
        student_id = generate_student_id()
        
        new_student = Student(
            student_id=student_id,
            name=name,
            email=email,
            phone=phone,
            status='active',
            password_hash=password_hash
        )
        
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
        return jsonify({'error': str(e)}), 500

# =====================================================
# STUDENT LOGIN (WITH OTP)
# =====================================================

# =====================================================
# STUDENT LOGIN (WITH OTP)
# =====================================================

@auth_bp.route('/student/login', methods=['POST', 'OPTIONS'])
def student_login():
    if request.method == 'OPTIONS':
        return '', 200
    
    try:
        data = request.get_json()
        email = data.get('email')
        password = data.get('password')
        
        print(f"Student login attempt: {email}")
        
        student = Student.query.filter_by(email=email).first()
        
        if not student:
            print(f"Student not found: {email}")
            return jsonify({'error': 'Invalid email or password'}), 401
        
        # Check password
        password_valid = False
        if hasattr(student, 'password_hash') and student.password_hash:
            password_valid = bcrypt.check_password_hash(student.password_hash, password)
        
        if not password_valid:
            print(f"Invalid password for: {email}")
            return jsonify({'error': 'Invalid email or password'}), 401
        
        # Generate token directly (NO OTP)
        jwt_secret = current_app.config.get('JWT_SECRET_KEY', os.getenv('JWT_SECRET_KEY', 'sjs-academy-secret-key-2024'))
        
        token = jwt.encode(
            {
                'id': student.id, 
                'role': 'student', 
                'email': student.email, 
                'name': student.name, 
                'student_id': student.student_id, 
                'exp': datetime.utcnow() + timedelta(days=30)
            },
            jwt_secret, 
            algorithm='HS256'
        )
        
        print(f"✅ Student login successful: {email}")
        
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
# ADMIN LOGIN (WITH OTP)
# =====================================================

@auth_bp.route('/admin/login', methods=['POST', 'OPTIONS'])
def admin_login():
    if request.method == 'OPTIONS':
        return '', 200
    
    try:
        data = request.get_json()
        email = data.get('email')
        password = data.get('password')
        otp = data.get('otp')
        session_id = data.get('session_id')
        
        ADMIN_EMAIL = "harshdeephanjra22@gmail.com"
        
        print(f"Admin login attempt: {email}")
        
        if email == 'admin@sjsacademy.com' and password == 'Admin@123':
            
            # First step - password verified, need OTP
            if not otp and not session_id:
                session_id = str(uuid.uuid4())
                success, otp_code = send_otp(ADMIN_EMAIL, 'admin')
                
                if success:
                    if not hasattr(current_app, 'login_sessions'):
                        current_app.login_sessions = {}
                    
                    current_app.login_sessions[session_id] = {
                        'user_id': 1,
                        'role': 'admin',
                        'email': ADMIN_EMAIL,
                        'expires_at': datetime.utcnow() + timedelta(minutes=10)
                    }
                    
                    print(f"Admin OTP sent to: {ADMIN_EMAIL}")
                    
                    return jsonify({
                        'requires_otp': True,
                        'session_id': session_id,
                        'message': f'OTP sent to {ADMIN_EMAIL}'
                    }), 200
                else:
                    return jsonify({'error': 'Failed to send OTP. Please try again.'}), 500
            
            # Second step - Verify OTP
            elif otp and session_id:
                if not hasattr(current_app, 'login_sessions') or session_id not in current_app.login_sessions:
                    return jsonify({'error': 'Session expired. Please login again.'}), 401
                
                session_data = current_app.login_sessions[session_id]
                
                if datetime.utcnow() > session_data['expires_at']:
                    del current_app.login_sessions[session_id]
                    return jsonify({'error': 'Session expired. Please login again.'}), 401
                
                if verify_otp(session_data['email'], otp):
                    del current_app.login_sessions[session_id]
                    
                    jwt_secret = current_app.config.get('JWT_SECRET_KEY', os.getenv('JWT_SECRET_KEY', 'sjs-academy-secret-key-2024'))
                    
                    token = jwt.encode(
                        {
                            'id': 1, 
                            'role': 'admin', 
                            'email': email, 
                            'is_admin': True,
                            'exp': datetime.utcnow() + timedelta(days=30)
                        },
                        jwt_secret, 
                        algorithm='HS256'
                    )
                    
                    return jsonify({
                        'success': True,
                        'access_token': token,
                        'admin': {
                            'id': 1, 
                            'username': 'admin', 
                            'email': email, 
                            'full_name': 'Super Admin', 
                            'role': 'super'
                        }
                    }), 200
                else:
                    return jsonify({'error': 'Invalid or expired OTP'}), 401
            else:
                return jsonify({'error': 'Invalid request'}), 400
        
        return jsonify({'error': 'Invalid credentials'}), 401
        
    except Exception as e:
        print(f"Admin login error: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500

# =====================================================
# RESEND OTP
# =====================================================

@auth_bp.route('/resend-otp', methods=['POST', 'OPTIONS'])
def resend_otp_code():
    if request.method == 'OPTIONS':
        return '', 200
    
    try:
        data = request.get_json()
        session_id = data.get('session_id')
        user_type = data.get('user_type', 'student')
        
        if not session_id:
            return jsonify({'error': 'Session ID required'}), 400
        
        if not hasattr(current_app, 'login_sessions') or session_id not in current_app.login_sessions:
            return jsonify({'error': 'Session expired. Please login again.'}), 401
        
        session_data = current_app.login_sessions[session_id]
        success, otp_code = resend_otp(session_data['email'], user_type)
        
        if success:
            session_data['expires_at'] = datetime.utcnow() + timedelta(minutes=10)
            current_app.login_sessions[session_id] = session_data
            
            return jsonify({
                'success': True, 
                'message': 'OTP resent successfully'
            }), 200
        else:
            return jsonify({'error': 'Failed to resend OTP'}), 500
            
    except Exception as e:
        print(f"Resend OTP error: {e}")
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