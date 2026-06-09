from functools import wraps
from flask import request, jsonify
import jwt
import os

JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY', 'sjs-academy-secret-key')

def verify_token(token):
    """Verify JWT token and return payload"""
    try:
        payload = jwt.decode(token, JWT_SECRET_KEY, algorithms=['HS256'])
        return payload
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None
    except Exception:
        return None

def token_required(f):
    """Decorator to protect routes that require authentication"""
    @wraps(f)
    def decorated(*args, **kwargs):
        
        if request.method == 'OPTIONS':
            return '', 200
        
        auth_header = request.headers.get('Authorization')
        
        if not auth_header:
            return jsonify({'error': 'No token provided'}), 401
        
        try:
            token = auth_header.replace('Bearer ', '')
            payload = verify_token(token)
            
            if not payload:
                return jsonify({'error': 'Invalid or expired token'}), 401
            
            request.user = payload
            return f(*args, **kwargs)
        except Exception as e:
            return jsonify({'error': str(e)}), 401
    
    return decorated

def admin_required(f):
    """Decorator to protect routes that require admin access"""
    @wraps(f)
    def decorated(*args, **kwargs):
        
        if request.method == 'OPTIONS':
            return '', 200
        
        auth_header = request.headers.get('Authorization')
        
        if not auth_header:
            return jsonify({'error': 'No token provided'}), 401
        
        try:
            token = auth_header.replace('Bearer ', '')
            payload = verify_token(token)
            
            if not payload:
                return jsonify({'error': 'Invalid or expired token'}), 401
            
            # Check if user has admin role
            if payload.get('role') != 'admin':
                return jsonify({'error': 'Admin access required'}), 403
            
            request.user = payload
            return f(*args, **kwargs)
        except Exception as e:
            return jsonify({'error': str(e)}), 401
    
    return decorated

def student_required(f):
    """Decorator to protect routes that require student access"""
    @wraps(f)
    def decorated(*args, **kwargs):
        if request.method == 'OPTIONS':
            return '', 200
        
        auth_header = request.headers.get('Authorization')
        
        if not auth_header:
            return jsonify({'error': 'No token provided'}), 401
        
        try:
            token = auth_header.replace('Bearer ', '')
            payload = verify_token(token)
            
            if not payload:
                return jsonify({'error': 'Invalid or expired token'}), 401
            
            # Check if user has student role
            if payload.get('role') != 'student':
                return jsonify({'error': 'Student access required'}), 403
            
            request.user = payload
            return f(*args, **kwargs)
        except Exception as e:
            return jsonify({'error': str(e)}), 401
    
    return decorated

def role_required(allowed_roles):
    """Decorator to protect routes that require specific roles"""
    def decorator(f):
        @wraps(f)
        def decorated(*args, **kwargs):
            if request.method == 'OPTIONS':
                return '', 200
            
            auth_header = request.headers.get('Authorization')
            
            if not auth_header:
                return jsonify({'error': 'No token provided'}), 401
            
            try:
                token = auth_header.replace('Bearer ', '')
                payload = verify_token(token)
                
                if not payload:
                    return jsonify({'error': 'Invalid or expired token'}), 401
                
                # Check if user has allowed role
                user_role = payload.get('role')
                if user_role not in allowed_roles:
                    return jsonify({'error': f'Access denied. Required roles: {allowed_roles}'}), 403
                
                request.user = payload
                return f(*args, **kwargs)
            except Exception as e:
                return jsonify({'error': str(e)}), 401
        
        return decorated
    return decorator