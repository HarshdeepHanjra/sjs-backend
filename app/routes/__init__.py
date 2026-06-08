# app/routes/__init__.py
from app.routes.auth import auth_bp
from app.routes.courses import courses_bp
from app.routes.cart import cart_bp
from app.routes.payments import payments_bp
from app.routes.admin import admin_bp
from app.routes.attendance import attendance_bp
from app.routes.internships import internships_bp
from app.routes.certificates import certificates_bp
from app.routes.user import user_bp

# Remove or comment out this line if it's causing issues
# from app.utils.decorators import token_required, admin_required, student_required, role_required, verify_token as verify_token_decorator

__all__ = [
    'auth_bp', 'courses_bp', 'cart_bp', 'payments_bp',
    'admin_bp', 'attendance_bp', 'internships_bp',
    'certificates_bp', 'user_bp'
]