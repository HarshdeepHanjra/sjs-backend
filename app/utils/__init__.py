# # app/utils/__init__.py
# from app.utils.decorators import token_required, admin_required, student_required, role_required, verify_token as verify_token_decorator
# from app.utils.helpers import (
#     generate_student_id,
#     generate_order_id,
#     generate_verification_id,
#     generate_certificate_id,
#     generate_verification_token,
#     generate_certificate_hash,
#     verify_token,
#     allowed_file,
#     upload_file,
#     generate_qr_code_url,
#     format_currency,
#     calculate_percentage
# )

# __all__ = [
#     # Decorators
#     'token_required',
#     'admin_required',
#     'student_required',
#     'role_required',
#     'verify_token_decorator',
    
#     # Helpers
#     'generate_student_id',
#     'generate_order_id',
#     'generate_verification_id',
#     'generate_certificate_id',
#     'generate_verification_token',
#     'generate_certificate_hash',
#     'verify_token',
#     'allowed_file',
#     'upload_file',
#     'generate_qr_code_url',
#     'format_currency',
#     'calculate_percentage'
    
#      # Email
#     'send_password_reset_email',
#     'send_welcome_email'
# ]


from app.utils.decorators import token_required, admin_required, student_required, role_required, verify_token as verify_token_decorator
from app.utils.helpers import (
    generate_student_id,
    generate_order_id,
    generate_verification_id,
    generate_certificate_id,
    generate_verification_token,
    generate_certificate_hash,
    verify_token,
    allowed_file,
    upload_file,
    generate_qr_code_url,
    format_currency,
    calculate_percentage
)
from app.utils.email import send_password_reset_email, send_welcome_email
from app.utils.email_otp import send_otp, verify_otp, resend_otp

__all__ = [
    # Decorators
    'token_required',
    'admin_required',
    'student_required',
    'role_required',
    'verify_token_decorator',
    
    # Helpers
    'generate_student_id',
    'generate_order_id',
    'generate_verification_id',
    'generate_certificate_id',
    'generate_verification_token',
    'generate_certificate_hash',
    'verify_token',
    'allowed_file',
    'upload_file',
    'generate_qr_code_url',
    'format_currency',
    'calculate_percentage',
    
    # Email
    'send_password_reset_email',
    'send_welcome_email',
    
    # Email OTP
    'send_otp',
    'verify_otp',
    'resend_otp'
]