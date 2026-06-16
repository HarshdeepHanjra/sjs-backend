# import cloudinary
# import cloudinary.uploader
# from flask import Blueprint, request, jsonify, current_app
# from app import db
# from app.models.order import Order
# from app.models.user import Student
# from app.models.payment import PaymentVerification
# from app.models.internship import InternshipOrder
# from app.utils.helpers import generate_verification_id, allowed_file
# from app.utils.decorators import token_required, admin_required
# import os
# from werkzeug.utils import secure_filename
# from datetime import datetime

# payments_bp = Blueprint('payments', __name__)

# # Cloudinary configuration
# CLOUDINARY_CLOUD_NAME = os.getenv('CLOUDINARY_CLOUD_NAME', 'dxxpeilta')
# CLOUDINARY_API_KEY = os.getenv('CLOUDINARY_API_KEY', '375175513582196')
# CLOUDINARY_API_SECRET = os.getenv('CLOUDINARY_API_SECRET')

# def init_cloudinary():
#     """Initialize Cloudinary if credentials are available"""
#     if CLOUDINARY_CLOUD_NAME and CLOUDINARY_API_KEY and CLOUDINARY_API_SECRET:
#         cloudinary.config(
#             cloud_name=CLOUDINARY_CLOUD_NAME,
#             api_key=CLOUDINARY_API_KEY,
#             api_secret=CLOUDINARY_API_SECRET,
#             secure=True
#         )
#         print(f"✅ Cloudinary configured with cloud name: {CLOUDINARY_CLOUD_NAME}")
#         return True
#     print("⚠️ Cloudinary not configured - using local storage")
#     return False

# CLOUDINARY_ENABLED = init_cloudinary()


# # =====================================================
# # USER ENDPOINTS (with /api/ prefix)
# # =====================================================

# # ✅ All routes will be prefixed with /api/payment in blueprint registration
# # So these endpoints become: /api/payment/upload-screenshot, etc.

# @payments_bp.route('/upload-screenshot', methods=['POST', 'OPTIONS'])
# @token_required
# def upload_screenshot():
#     """Upload payment screenshot (User)"""
#     if request.method == 'OPTIONS':
#         return '', 200
    
#     try:
#         if 'screenshot' not in request.files:
#             return jsonify({'error': 'No file uploaded'}), 400
        
#         file = request.files['screenshot']
#         order_id = request.form.get('order_id')
        
#         if not order_id:
#             return jsonify({'error': 'Order ID is required'}), 400
        
#         if file.filename == '':
#             return jsonify({'error': 'No file selected'}), 400
        
#         if not allowed_file(file.filename):
#             return jsonify({'error': 'Invalid file type. Allowed: png, jpg, jpeg, gif, webp'}), 400
        
#         screenshot_url = None
        
#         # Try Cloudinary first
#         if CLOUDINARY_ENABLED:
#             try:
#                 file.seek(0)
#                 upload_result = cloudinary.uploader.upload(
#                     file,
#                     folder='sjs-academy/payments',
#                     public_id=f"{order_id}_{int(datetime.now().timestamp())}",
#                     overwrite=True,
#                     resource_type='auto'
#                 )
#                 screenshot_url = upload_result['secure_url']
#                 print(f"✅ Screenshot uploaded to Cloudinary: {screenshot_url}")
#             except Exception as e:
#                 print(f"Cloudinary upload failed: {e}")
#                 screenshot_url = None
        
#         # Fallback to local storage
#         if not screenshot_url:
#             file.seek(0)
#             original_filename = secure_filename(file.filename)
#             timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
#             filename = f"{order_id}_{timestamp}_{original_filename}"
#             upload_dir = os.path.join('uploads', 'screenshots')
#             os.makedirs(upload_dir, exist_ok=True)
#             filepath = os.path.join(upload_dir, filename)
#             file.save(filepath)
#             screenshot_url = f"/uploads/screenshots/{filename}"
#             print(f"✅ Screenshot saved locally: {filepath}")
        
#         # Update order with screenshot URL
#         order = Order.query.filter_by(order_id=order_id).first()
#         if order:
#             order.screenshot_url = screenshot_url
#             db.session.commit()
        
#         internship_order = InternshipOrder.query.filter_by(order_id=order_id).first()
#         if internship_order:
#             internship_order.screenshot_url = screenshot_url
#             db.session.commit()
        
#         return jsonify({
#             'success': True,
#             'screenshot_url': screenshot_url,
#             'message': 'Screenshot uploaded successfully'
#         }), 200
        
#     except Exception as e:
#         print(f"Upload error: {e}")
#         import traceback
#         traceback.print_exc()
#         return jsonify({'error': str(e)}), 500


# @payments_bp.route('/submit-verification', methods=['POST', 'OPTIONS'])
# @token_required
# def submit_verification():
#     """Submit payment verification (User)"""
#     if request.method == 'OPTIONS':
#         return '', 200
    
#     try:
#         data = request.get_json()
#         order_id = data.get('order_id')
#         transaction_id = data.get('transaction_id')
#         screenshot_url = data.get('screenshot_url')
        
#         if not order_id:
#             return jsonify({'error': 'Order ID is required'}), 400
        
#         if not transaction_id:
#             return jsonify({'error': 'Transaction ID is required'}), 400
        
#         if not screenshot_url:
#             return jsonify({'error': 'Screenshot is required'}), 400
        
#         user = request.user
        
#         # Find order
#         order = Order.query.filter_by(order_id=order_id, student_id=user['id']).first()
#         internship_order = None
        
#         if not order:
#             internship_order = InternshipOrder.query.filter_by(order_id=order_id, student_id=user['id']).first()
        
#         if not order and not internship_order:
#             return jsonify({'error': 'Order not found'}), 404
        
#         # Check for existing verification
#         existing = PaymentVerification.query.filter_by(order_id=order_id).first()
#         if existing:
#             return jsonify({'error': 'Verification already submitted'}), 400
        
#         verification_id = generate_verification_id()
#         student = Student.query.get(user['id'])
        
#         amount = order.total_amount if order else internship_order.amount
        
#         verification = PaymentVerification(
#             verification_id=verification_id,
#             order_id=order_id,
#             student_id=user['id'],
#             student_name=student.name if student else user.get('name', 'Student'),
#             student_email=student.email if student else user.get('email'),
#             amount=amount,
#             transaction_id=transaction_id,
#             screenshot_url=screenshot_url,
#             status='pending',
#             created_at=datetime.utcnow()
#         )
        
#         db.session.add(verification)
        
#         if order:
#             order.transaction_id = transaction_id
#             order.payment_status = 'pending_verification'
#         elif internship_order:
#             internship_order.transaction_id = transaction_id
#             internship_order.payment_status = 'pending_verification'
        
#         db.session.commit()
        
#         print(f"✅ Verification submitted: {verification_id}")
        
#         return jsonify({
#             'success': True,
#             'message': 'Verification submitted successfully!',
#             'verification_id': verification_id
#         }), 201
        
#     except Exception as e:
#         db.session.rollback()
#         print(f"Submit error: {e}")
#         return jsonify({'error': str(e)}), 500


# @payments_bp.route('/status/<verification_id>', methods=['GET', 'OPTIONS'])
# @token_required
# def get_verification_status(verification_id):
#     """Get verification status by ID"""
#     if request.method == 'OPTIONS':
#         return '', 200
    
#     try:
#         verification = PaymentVerification.query.filter_by(verification_id=verification_id).first()
        
#         if not verification:
#             return jsonify({'error': 'Verification not found'}), 404
        
#         user = request.user
#         if verification.student_id != user['id']:
#             return jsonify({'error': 'Unauthorized'}), 403
        
#         status_messages = {
#             'pending': 'Your payment is being verified. We will notify you within 24 hours.',
#             'approved': '✅ Payment verified! Your courses have been activated.',
#             'declined': '❌ Payment verification failed. Please contact support.'
#         }
        
#         return jsonify({
#             'success': True,
#             'status': verification.status,
#             'message': status_messages.get(verification.status, ''),
#             'admin_notes': verification.admin_notes,
#             'verified_at': verification.verified_at.isoformat() if hasattr(verification, 'verified_at') and verification.verified_at else None
#         }), 200
#     except Exception as e:
#         print(f"Status check error: {e}")
#         return jsonify({'error': str(e)}), 500


# # =====================================================
# # ADMIN ENDPOINTS (with /api/ prefix)
# # =====================================================

# @payments_bp.route('/admin/payment-requests', methods=['GET', 'OPTIONS'])
# @admin_required
# def get_payment_requests():
#     """Get all pending payment verifications (Admin)"""
#     if request.method == 'OPTIONS':
#         return '', 200
    
#     try:
#         verifications = PaymentVerification.query.filter_by(
#             status='pending'
#         ).order_by(PaymentVerification.created_at.desc()).all()
        
#         result = []
#         for v in verifications:
#             result.append({
#                 'id': v.id,
#                 'verification_id': v.verification_id,
#                 'order_id': v.order_id,
#                 'student_id': v.student_id,
#                 'student_name': v.student_name,
#                 'student_email': v.student_email,
#                 'amount': float(v.amount) if v.amount else 0,
#                 'transaction_id': v.transaction_id,
#                 'screenshot_url': v.screenshot_url,
#                 'status': v.status,
#                 'created_at': v.created_at.isoformat() if v.created_at else None
#             })
        
#         return jsonify({
#             'success': True,
#             'verifications': result
#         }), 200
#     except Exception as e:
#         print(f"Error: {e}")
#         return jsonify({'error': str(e)}), 500


# @payments_bp.route('/admin/payment-requests/<int:request_id>/approve', methods=['POST', 'OPTIONS'])
# @admin_required
# def approve_payment(request_id):
#     """Approve payment verification (Admin)"""
#     if request.method == 'OPTIONS':
#         return '', 200
    
#     try:
#         data = request.get_json()
#         admin_notes = data.get('notes', 'Payment verified and approved.')
        
#         # Get verification record
#         verification = PaymentVerification.query.get(request_id)
#         if not verification:
#             return jsonify({'error': 'Verification not found'}), 404
        
#         # Update verification status
#         verification.status = 'approved'
#         verification.admin_notes = admin_notes
#         verification.verified_at = datetime.utcnow()
        
#         # Get the order
#         order = Order.query.filter_by(order_id=verification.order_id).first()
#         if not order:
#             return jsonify({'error': 'Order not found'}), 404
        
#         # Update order status
#         order.payment_status = 'completed'
#         order.transaction_id = verification.transaction_id
        
#         # Get courses from order
#         order_courses = order.courses if isinstance(order.courses, list) else []
        
#         print(f"\n{'='*60}")
#         print(f"📝 APPROVING PAYMENT - Adding to Enrollment")
#         print(f"Order ID: {order.order_id}")
#         print(f"Student ID: {verification.student_id}")
#         print(f"Student Email: {verification.student_email}")
#         print(f"Order Courses: {order_courses}")
#         print(f"{'='*60}\n")
        
#         # Import models
#         from app.models.course import Enrollment, Course
        
#         courses_added = []
        
#         # For each course in the order, add to enrollments table
#         for course_data in order_courses:
#             # Get course ID
#             if isinstance(course_data, dict):
#                 course_id = course_data.get('id')
#                 course_name = course_data.get('name', 'Unknown')
#             else:
#                 course_id = getattr(course_data, 'id', None)
#                 course_name = getattr(course_data, 'name', 'Unknown')
            
#             if course_id:
#                 print(f"Processing course ID: {course_id} - {course_name}")
                
#                 # Check if already enrolled
#                 existing = Enrollment.query.filter_by(
#                     student_id=verification.student_id,
#                     course_id=course_id
#                 ).first()
                
#                 if not existing:
#                     # Create enrollment
#                     enrollment = Enrollment(
#                         student_id=verification.student_id,
#                         course_id=course_id,
#                         enrolled_at=datetime.utcnow(),
#                         status='active',
#                         payment_verification_id=verification.verification_id
#                     )
#                     db.session.add(enrollment)
#                     courses_added.append(course_id)
#                     print(f"✅ Added to enrollments table: student_id={verification.student_id}, course_id={course_id}")
                    
#                     # Update student's course_ids JSON field
#                     student = Student.query.get(verification.student_id)
#                     if student:
#                         if student.course_ids is None:
#                             student.course_ids = []
#                         if course_id not in student.course_ids:
#                             student.course_ids.append(course_id)
#                             print(f"✅ Added course {course_id} to student.course_ids")
                    
#                     # Update course student count
#                     course = Course.query.get(course_id)
#                     if course:
#                         course.students_enrolled = (course.students_enrolled or 0) + 1
#                         db.session.add(course)
#                         print(f"✅ Updated course {course_id} students_enrolled to {course.students_enrolled}")
#                 else:
#                     print(f"⚠️ Already enrolled in course {course_id}")
        
#         # Commit all changes
#         db.session.commit()
        
#         # Verify enrollment was added
#         verify_enrollments = Enrollment.query.filter_by(
#             student_id=verification.student_id
#         ).all()
        
#         print(f"\n📊 Enrollment Summary:")
#         print(f"   Total enrollments for student {verification.student_id}: {len(verify_enrollments)}")
#         for enc in verify_enrollments:
#             print(f"   - Course ID: {enc.course_id}, Status: {enc.status}")
        
#         print(f"\n✅ Payment approved successfully!")
#         print(f"   Courses added: {courses_added}")
#         print(f"{'='*60}\n")
        
#         # Update internship order if exists
#         internship_order = InternshipOrder.query.filter_by(order_id=verification.order_id).first()
#         if internship_order:
#             internship_order.payment_status = 'completed'
#             internship_order.status = 'active'
#             db.session.commit()
        
#         return jsonify({
#             'success': True,
#             'message': 'Payment approved successfully! Courses added to student account.',
#             'courses_added': courses_added,
#             'total_enrollments': len(verify_enrollments)
#         }), 200
        
#     except Exception as e:
#         db.session.rollback()
#         print(f"❌ Approve error: {e}")
#         import traceback
#         traceback.print_exc()
#         return jsonify({'error': str(e)}), 500


# @payments_bp.route('/admin/payment-requests/<int:request_id>/decline', methods=['POST', 'OPTIONS'])
# @admin_required
# def decline_payment(request_id):
#     """Decline payment verification (Admin)"""
#     if request.method == 'OPTIONS':
#         return '', 200
    
#     try:
#         data = request.get_json()
#         admin_notes = data.get('notes', 'Payment verification failed.')
        
#         verification = PaymentVerification.query.get(request_id)
#         if not verification:
#             return jsonify({'error': 'Verification not found'}), 404
        
#         verification.status = 'declined'
#         verification.admin_notes = admin_notes
        
#         if hasattr(verification, 'verified_at'):
#             verification.verified_at = datetime.utcnow()
        
#         # Update order status
#         order = Order.query.filter_by(order_id=verification.order_id).first()
#         if order:
#             order.payment_status = 'failed'
        
#         internship_order = InternshipOrder.query.filter_by(order_id=verification.order_id).first()
#         if internship_order:
#             internship_order.payment_status = 'failed'
        
#         db.session.commit()
        
#         print(f"✅ Payment declined: {verification.verification_id}")
        
#         return jsonify({
#             'success': True,
#             'message': 'Payment declined.'
#         }), 200
#     except Exception as e:
#         db.session.rollback()
#         print(f"Decline error: {e}")
#         return jsonify({'error': str(e)}), 500


# @payments_bp.route('/admin/payment-stats', methods=['GET', 'OPTIONS'])
# @admin_required
# def get_payment_stats():
#     """Get payment statistics (Admin)"""
#     if request.method == 'OPTIONS':
#         return '', 200
    
#     try:
#         pending = PaymentVerification.query.filter_by(status='pending').count()
#         approved = PaymentVerification.query.filter_by(status='approved').count()
#         declined = PaymentVerification.query.filter_by(status='declined').count()
        
#         total_amount = db.session.query(db.func.sum(PaymentVerification.amount)).filter(
#             PaymentVerification.status == 'approved'
#         ).scalar() or 0
        
#         return jsonify({
#             'success': True,
#             'stats': {
#                 'pending': pending,
#                 'approved': approved,
#                 'declined': declined,
#                 'total_amount': float(total_amount)
#             }
#         }), 200
#     except Exception as e:
#         return jsonify({'error': str(e)}), 500
    
    
    
    









# import cloudinary
# import cloudinary.uploader
# from flask import Blueprint, request, jsonify, current_app
# from app import db
# from app.models.order import Order
# from app.models.user import Student
# from app.models.payment import PaymentVerification
# from app.models.internship import InternshipOrder
# from app.utils.helpers import generate_verification_id, allowed_file
# from app.utils.decorators import token_required, admin_required
# import os
# from werkzeug.utils import secure_filename
# from datetime import datetime

# payments_bp = Blueprint('payments', __name__)

# # Cloudinary configuration
# CLOUDINARY_CLOUD_NAME = os.getenv('CLOUDINARY_CLOUD_NAME', 'dxxpeilta')
# CLOUDINARY_API_KEY = os.getenv('CLOUDINARY_API_KEY', '375175513582196')
# CLOUDINARY_API_SECRET = os.getenv('CLOUDINARY_API_SECRET')

# def init_cloudinary():
#     """Initialize Cloudinary if credentials are available"""
#     if CLOUDINARY_CLOUD_NAME and CLOUDINARY_API_KEY and CLOUDINARY_API_SECRET:
#         cloudinary.config(
#             cloud_name=CLOUDINARY_CLOUD_NAME,
#             api_key=CLOUDINARY_API_KEY,
#             api_secret=CLOUDINARY_API_SECRET,
#             secure=True
#         )
#         print(f"✅ Cloudinary configured with cloud name: {CLOUDINARY_CLOUD_NAME}")
#         return True
#     print("⚠️ Cloudinary not configured - using local storage")
#     return False

# CLOUDINARY_ENABLED = init_cloudinary()


# # =====================================================
# # BANK DETAILS ENDPOINT
# # =====================================================

# @payments_bp.route('/bank-details', methods=['GET', 'OPTIONS'])
# def get_bank_details():
#     """Get bank transfer details for manual payment"""
#     if request.method == 'OPTIONS':
#         return '', 200
    
#     bank_details = {
#         'account_name': os.getenv('BANK_ACCOUNT_NAME', 'SJS Global Tech Academy'),
#         'account_number': os.getenv('BANK_ACCOUNT_NUMBER', '123456789012'),
#         'bank_name': os.getenv('BANK_NAME', 'State Bank of India'),
#         'ifsc_code': os.getenv('BANK_IFSC_CODE', 'SBIN0012345'),
#         'branch': os.getenv('BANK_BRANCH', 'Main Branch'),
#         'upi_id': os.getenv('UPI_ID', 'sjsacademy@okhdfcbank')
#     }
    
#     return jsonify({
#         'success': True,
#         'bank_details': bank_details
#     }), 200


# # =====================================================
# # PAYMENT METHODS ENDPOINT
# # =====================================================

# @payments_bp.route('/payment-methods', methods=['GET', 'OPTIONS'])
# def get_payment_methods():
#     """Get all available payment methods"""
#     if request.method == 'OPTIONS':
#         return '', 200
    
#     payment_methods = [
#         {
#             'id': 'upi',
#             'name': 'UPI (Google Pay / PhonePe / Paytm)',
#             'description': 'Instant access after payment submission',
#             'icon': 'mobile-alt',
#             'currency': 'INR',
#             'is_available': True,
#             'requires_screenshot': True
#         },
#         {
#             'id': 'paypal',
#             'name': 'PayPal',
#             'description': 'International payments via PayPal',
#             'icon': 'paypal',
#             'currency': 'USD/INR',
#             'is_available': True,
#             'requires_screenshot': True
#         },
#         {
#             'id': 'bank_transfer',
#             'name': 'Bank Transfer / NEFT / RTGS',
#             'description': 'Manual verification (24-48 hours)',
#             'icon': 'university',
#             'currency': 'INR',
#             'is_available': True,
#             'requires_screenshot': True
#         }
#     ]
    
#     return jsonify({
#         'success': True,
#         'payment_methods': payment_methods,
#         'environment': 'production'
#     }), 200


# # =====================================================
# # USER ENDPOINTS
# # =====================================================

# @payments_bp.route('/upload-screenshot', methods=['POST', 'OPTIONS'])
# @token_required
# def upload_screenshot():
#     """Upload payment screenshot (User)"""
#     if request.method == 'OPTIONS':
#         return '', 200
    
#     try:
#         if 'screenshot' not in request.files:
#             return jsonify({'error': 'No file uploaded'}), 400
        
#         file = request.files['screenshot']
#         order_id = request.form.get('order_id')
#         payment_method = request.form.get('payment_method', 'upi')
        
#         if not order_id:
#             return jsonify({'error': 'Order ID is required'}), 400
        
#         if file.filename == '':
#             return jsonify({'error': 'No file selected'}), 400
        
#         if not allowed_file(file.filename):
#             return jsonify({'error': 'Invalid file type. Allowed: png, jpg, jpeg, gif, webp'}), 400
        
#         screenshot_url = None
        
#         # Try Cloudinary first
#         if CLOUDINARY_ENABLED:
#             try:
#                 file.seek(0)
#                 upload_result = cloudinary.uploader.upload(
#                     file,
#                     folder='sjs-academy/payments',
#                     public_id=f"{order_id}_{payment_method}_{int(datetime.now().timestamp())}",
#                     overwrite=True,
#                     resource_type='auto'
#                 )
#                 screenshot_url = upload_result['secure_url']
#                 print(f"✅ Screenshot uploaded to Cloudinary: {screenshot_url}")
#             except Exception as e:
#                 print(f"Cloudinary upload failed: {e}")
#                 screenshot_url = None
        
#         # Fallback to local storage
#         if not screenshot_url:
#             file.seek(0)
#             original_filename = secure_filename(file.filename)
#             timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
#             filename = f"{order_id}_{payment_method}_{timestamp}_{original_filename}"
#             upload_dir = os.path.join('uploads', 'screenshots')
#             os.makedirs(upload_dir, exist_ok=True)
#             filepath = os.path.join(upload_dir, filename)
#             file.save(filepath)
#             screenshot_url = f"/uploads/screenshots/{filename}"
#             print(f"✅ Screenshot saved locally: {filepath}")
        
#         # Update order with screenshot URL
#         order = Order.query.filter_by(order_id=order_id).first()
#         if order:
#             order.screenshot_url = screenshot_url
#             order.payment_method = payment_method
#             db.session.commit()
        
#         internship_order = InternshipOrder.query.filter_by(order_id=order_id).first()
#         if internship_order:
#             internship_order.screenshot_url = screenshot_url
#             internship_order.payment_method = payment_method
#             db.session.commit()
        
#         return jsonify({
#             'success': True,
#             'screenshot_url': screenshot_url,
#             'message': 'Screenshot uploaded successfully'
#         }), 200
        
#     except Exception as e:
#         print(f"Upload error: {e}")
#         import traceback
#         traceback.print_exc()
#         return jsonify({'error': str(e)}), 500


# @payments_bp.route('/submit-verification', methods=['POST', 'OPTIONS'])
# @token_required
# def submit_verification():
#     """Submit payment verification (User)"""
#     if request.method == 'OPTIONS':
#         return '', 200
    
#     try:
#         data = request.get_json()
#         order_id = data.get('order_id')
#         transaction_id = data.get('transaction_id')
#         screenshot_url = data.get('screenshot_url')
#         payment_method = data.get('payment_method', 'upi')
        
#         if not order_id:
#             return jsonify({'error': 'Order ID is required'}), 400
        
#         if not transaction_id:
#             return jsonify({'error': 'Transaction ID is required'}), 400
        
#         if not screenshot_url:
#             return jsonify({'error': 'Screenshot is required'}), 400
        
#         user = request.user
        
#         # Find order
#         order = Order.query.filter_by(order_id=order_id, student_id=user['id']).first()
#         internship_order = None
        
#         if not order:
#             internship_order = InternshipOrder.query.filter_by(order_id=order_id, student_id=user['id']).first()
        
#         if not order and not internship_order:
#             return jsonify({'error': 'Order not found'}), 404
        
#         # Check for existing verification
#         existing = PaymentVerification.query.filter_by(order_id=order_id).first()
#         if existing:
#             return jsonify({'error': 'Verification already submitted'}), 400
        
#         verification_id = generate_verification_id()
#         student = Student.query.get(user['id'])
        
#         amount = order.total_amount if order else internship_order.amount
        
#         verification = PaymentVerification(
#             verification_id=verification_id,
#             order_id=order_id,
#             student_id=user['id'],
#             student_name=student.name if student else user.get('name', 'Student'),
#             student_email=student.email if student else user.get('email'),
#             amount=amount,
#             transaction_id=transaction_id,
#             screenshot_url=screenshot_url,
#             payment_method=payment_method,
#             status='pending',
#             created_at=datetime.utcnow()
#         )
        
#         db.session.add(verification)
        
#         if order:
#             order.transaction_id = transaction_id
#             order.payment_status = 'pending_verification'
#             order.payment_method = payment_method
#         elif internship_order:
#             internship_order.transaction_id = transaction_id
#             internship_order.payment_status = 'pending_verification'
#             internship_order.payment_method = payment_method
        
#         db.session.commit()
        
#         print(f"✅ Verification submitted: {verification_id} via {payment_method}")
        
#         return jsonify({
#             'success': True,
#             'message': 'Verification submitted successfully!',
#             'verification_id': verification_id
#         }), 201
        
#     except Exception as e:
#         db.session.rollback()
#         print(f"Submit error: {e}")
#         return jsonify({'error': str(e)}), 500


# @payments_bp.route('/status/<verification_id>', methods=['GET', 'OPTIONS'])
# @token_required
# def get_verification_status(verification_id):
#     """Get verification status by ID"""
#     if request.method == 'OPTIONS':
#         return '', 200
    
#     try:
#         verification = PaymentVerification.query.filter_by(verification_id=verification_id).first()
        
#         if not verification:
#             return jsonify({'error': 'Verification not found'}), 404
        
#         user = request.user
#         if verification.student_id != user['id'] and user.get('role') != 'admin':
#             return jsonify({'error': 'Unauthorized'}), 403
        
#         status_messages = {
#             'pending': 'Your payment is being verified. We will notify you within 24 hours.',
#             'approved': '✅ Payment verified! Your courses have been activated.',
#             'declined': '❌ Payment verification failed. Please contact support.'
#         }
        
#         return jsonify({
#             'success': True,
#             'status': verification.status,
#             'message': status_messages.get(verification.status, ''),
#             'admin_notes': verification.admin_notes,
#             'payment_method': getattr(verification, 'payment_method', 'upi'),
#             'verified_at': verification.verified_at.isoformat() if hasattr(verification, 'verified_at') and verification.verified_at else None
#         }), 200
#     except Exception as e:
#         print(f"Status check error: {e}")
#         return jsonify({'error': str(e)}), 500


# # =====================================================
# # ADMIN ENDPOINTS
# # =====================================================

# @payments_bp.route('/admin/payment-requests', methods=['GET', 'OPTIONS'])
# @admin_required
# def get_payment_requests():
#     """Get all pending payment verifications (Admin)"""
#     if request.method == 'OPTIONS':
#         return '', 200
    
#     try:
#         verifications = PaymentVerification.query.filter_by(
#             status='pending'
#         ).order_by(PaymentVerification.created_at.desc()).all()
        
#         result = []
#         for v in verifications:
#             result.append({
#                 'id': v.id,
#                 'verification_id': v.verification_id,
#                 'order_id': v.order_id,
#                 'student_id': v.student_id,
#                 'student_name': v.student_name,
#                 'student_email': v.student_email,
#                 'amount': float(v.amount) if v.amount else 0,
#                 'transaction_id': v.transaction_id,
#                 'screenshot_url': v.screenshot_url,
#                 'payment_method': getattr(v, 'payment_method', 'upi'),
#                 'status': v.status,
#                 'created_at': v.created_at.isoformat() if v.created_at else None
#             })
        
#         return jsonify({
#             'success': True,
#             'verifications': result
#         }), 200
#     except Exception as e:
#         print(f"Error: {e}")
#         return jsonify({'error': str(e)}), 500


# @payments_bp.route('/admin/payment-requests/<int:request_id>/approve', methods=['POST', 'OPTIONS'])
# @admin_required
# def approve_payment(request_id):
#     """Approve payment verification (Admin)"""
#     if request.method == 'OPTIONS':
#         return '', 200
    
#     try:
#         data = request.get_json()
#         admin_notes = data.get('notes', 'Payment verified and approved.')
        
#         # Get verification record
#         verification = PaymentVerification.query.get(request_id)
#         if not verification:
#             return jsonify({'error': 'Verification not found'}), 404
        
#         # Update verification status
#         verification.status = 'approved'
#         verification.admin_notes = admin_notes
#         verification.verified_at = datetime.utcnow()
        
#         # Get the order
#         order = Order.query.filter_by(order_id=verification.order_id).first()
#         if not order:
#             # Check if it's an internship order
#             internship_order = InternshipOrder.query.filter_by(order_id=verification.order_id).first()
#             if internship_order:
#                 internship_order.payment_status = 'completed'
#                 internship_order.status = 'active'
#                 db.session.commit()
#                 return jsonify({
#                     'success': True,
#                     'message': 'Internship payment approved successfully!'
#                 }), 200
#             return jsonify({'error': 'Order not found'}), 404
        
#         # Update order status
#         order.payment_status = 'completed'
#         order.transaction_id = verification.transaction_id
        
#         # Get courses from order
#         order_courses = order.courses if isinstance(order.courses, list) else []
        
#         print(f"\n{'='*60}")
#         print(f"📝 APPROVING PAYMENT - Adding to Enrollment")
#         print(f"Order ID: {order.order_id}")
#         print(f"Student ID: {verification.student_id}")
#         print(f"Student Email: {verification.student_email}")
#         print(f"Payment Method: {getattr(verification, 'payment_method', 'upi')}")
#         print(f"Order Courses: {order_courses}")
#         print(f"{'='*60}\n")
        
#         # Import models
#         from app.models.course import Enrollment, Course
        
#         courses_added = []
        
#         # For each course in the order, add to enrollments table
#         for course_data in order_courses:
#             # Get course ID
#             if isinstance(course_data, dict):
#                 course_id = course_data.get('id')
#                 course_name = course_data.get('name', 'Unknown')
#             else:
#                 course_id = getattr(course_data, 'id', None)
#                 course_name = getattr(course_data, 'name', 'Unknown')
            
#             if course_id:
#                 print(f"Processing course ID: {course_id} - {course_name}")
                
#                 # Check if already enrolled
#                 existing = Enrollment.query.filter_by(
#                     student_id=verification.student_id,
#                     course_id=course_id
#                 ).first()
                
#                 if not existing:
#                     # Create enrollment
#                     enrollment = Enrollment(
#                         student_id=verification.student_id,
#                         course_id=course_id,
#                         enrolled_at=datetime.utcnow(),
#                         status='active',
#                         payment_verification_id=verification.verification_id
#                     )
#                     db.session.add(enrollment)
#                     courses_added.append(course_id)
#                     print(f"✅ Added to enrollments table: student_id={verification.student_id}, course_id={course_id}")
                    
#                     # Update student's course_ids JSON field
#                     student = Student.query.get(verification.student_id)
#                     if student:
#                         if student.course_ids is None:
#                             student.course_ids = []
#                         if course_id not in student.course_ids:
#                             student.course_ids.append(course_id)
#                             print(f"✅ Added course {course_id} to student.course_ids")
                    
#                     # Update course student count
#                     course = Course.query.get(course_id)
#                     if course:
#                         course.students_enrolled = (course.students_enrolled or 0) + 1
#                         db.session.add(course)
#                         print(f"✅ Updated course {course_id} students_enrolled to {course.students_enrolled}")
#                 else:
#                     print(f"⚠️ Already enrolled in course {course_id}")
        
#         # Commit all changes
#         db.session.commit()
        
#         # Verify enrollment was added
#         verify_enrollments = Enrollment.query.filter_by(
#             student_id=verification.student_id
#         ).all()
        
#         print(f"\n📊 Enrollment Summary:")
#         print(f"   Total enrollments for student {verification.student_id}: {len(verify_enrollments)}")
#         for enc in verify_enrollments:
#             print(f"   - Course ID: {enc.course_id}, Status: {enc.status}")
        
#         print(f"\n✅ Payment approved successfully!")
#         print(f"   Courses added: {courses_added}")
#         print(f"{'='*60}\n")
        
#         return jsonify({
#             'success': True,
#             'message': 'Payment approved successfully! Courses added to student account.',
#             'courses_added': courses_added,
#             'total_enrollments': len(verify_enrollments)
#         }), 200
        
#     except Exception as e:
#         db.session.rollback()
#         print(f"❌ Approve error: {e}")
#         import traceback
#         traceback.print_exc()
#         return jsonify({'error': str(e)}), 500


# @payments_bp.route('/admin/payment-requests/<int:request_id>/decline', methods=['POST', 'OPTIONS'])
# @admin_required
# def decline_payment(request_id):
#     """Decline payment verification (Admin)"""
#     if request.method == 'OPTIONS':
#         return '', 200
    
#     try:
#         data = request.get_json()
#         admin_notes = data.get('notes', 'Payment verification failed.')
        
#         verification = PaymentVerification.query.get(request_id)
#         if not verification:
#             return jsonify({'error': 'Verification not found'}), 404
        
#         verification.status = 'declined'
#         verification.admin_notes = admin_notes
#         verification.verified_at = datetime.utcnow()
        
#         # Update order status
#         order = Order.query.filter_by(order_id=verification.order_id).first()
#         if order:
#             order.payment_status = 'failed'
        
#         internship_order = InternshipOrder.query.filter_by(order_id=verification.order_id).first()
#         if internship_order:
#             internship_order.payment_status = 'failed'
        
#         db.session.commit()
        
#         print(f"✅ Payment declined: {verification.verification_id}")
        
#         return jsonify({
#             'success': True,
#             'message': 'Payment declined.'
#         }), 200
#     except Exception as e:
#         db.session.rollback()
#         print(f"Decline error: {e}")
#         return jsonify({'error': str(e)}), 500


# @payments_bp.route('/admin/payment-stats', methods=['GET', 'OPTIONS'])
# @admin_required
# def get_payment_stats():
#     """Get payment statistics (Admin)"""
#     if request.method == 'OPTIONS':
#         return '', 200
    
#     try:
#         pending = PaymentVerification.query.filter_by(status='pending').count()
#         approved = PaymentVerification.query.filter_by(status='approved').count()
#         declined = PaymentVerification.query.filter_by(status='declined').count()
        
#         total_amount = db.session.query(db.func.sum(PaymentVerification.amount)).filter(
#             PaymentVerification.status == 'approved'
#         ).scalar() or 0
        
#         return jsonify({
#             'success': True,
#             'stats': {
#                 'pending': pending,
#                 'approved': approved,
#                 'declined': declined,
#                 'total_amount': float(total_amount)
#             }
#         }), 200
#     except Exception as e:
#         return jsonify({'error': str(e)}), 500




















# import cloudinary
# import cloudinary.uploader
# from flask import Blueprint, request, jsonify, current_app
# from app import db
# from app.models.order import Order
# from app.models.user import Student
# from app.models.payment import PaymentVerification
# from app.models.internship import InternshipOrder
# from app.utils.helpers import generate_verification_id, allowed_file
# from app.utils.decorators import token_required, admin_required
# import os
# from werkzeug.utils import secure_filename
# from datetime import datetime
# import smtplib
# from email.mime.text import MIMEText
# from email.mime.multipart import MIMEMultipart
# import requests
# import json

# payments_bp = Blueprint('payments', __name__)

# # Email Configuration (from your settings)
# MAIL_SERVER = os.getenv('MAIL_SERVER', 'smtp-relay.brevo.com')
# MAIL_PORT = int(os.getenv('MAIL_PORT', 587))
# MAIL_USE_TLS = os.getenv('MAIL_USE_TLS', 'True').lower() == 'true'
# MAIL_USE_SSL = os.getenv('MAIL_USE_SSL', 'False').lower() == 'true'
# MAIL_USERNAME = os.getenv('MAIL_USERNAME', '')
# MAIL_PASSWORD = os.getenv('MAIL_PASSWORD', '')
# MAIL_DEFAULT_SENDER = os.getenv('MAIL_DEFAULT_SENDER', 'sjsglobaltech@gmail.com')
# BREVO_API_KEY = os.getenv('BREVO_API_KEY', '')
# USE_REAL_EMAIL = os.getenv('USE_REAL_EMAIL', 'True').lower() == 'true'
# ADMIN_EMAIL = os.getenv('ADMIN_EMAIL', 'gangahanjra@gmail.com')  # Changed to gangahanjra@gmail.com

# # Cloudinary configuration
# CLOUDINARY_CLOUD_NAME = os.getenv('CLOUDINARY_CLOUD_NAME', 'dxxpeilta')
# CLOUDINARY_API_KEY = os.getenv('CLOUDINARY_API_KEY', '375175513582196')
# CLOUDINARY_API_SECRET = os.getenv('CLOUDINARY_API_SECRET')

# def init_cloudinary():
#     """Initialize Cloudinary if credentials are available"""
#     if CLOUDINARY_CLOUD_NAME and CLOUDINARY_API_KEY and CLOUDINARY_API_SECRET:
#         cloudinary.config(
#             cloud_name=CLOUDINARY_CLOUD_NAME,
#             api_key=CLOUDINARY_API_KEY,
#             api_secret=CLOUDINARY_API_SECRET,
#             secure=True
#         )
#         print(f"✅ Cloudinary configured with cloud name: {CLOUDINARY_CLOUD_NAME}")
#         return True
#     print("⚠️ Cloudinary not configured - using local storage")
#     return False

# CLOUDINARY_ENABLED = init_cloudinary()


# # =====================================================
# # EMAIL NOTIFICATION FUNCTIONS
# # =====================================================

# def send_email_brevo_api(to_email, subject, html_content, text_content=None):
#     """Send email using Brevo API (Sendinblue) - without external SDK"""
#     if not USE_REAL_EMAIL:
#         print(f"📧 [TEST MODE] Would send email to: {to_email}")
#         print(f"   Subject: {subject}")
#         print(f"   Content preview: {html_content[:200]}...")
#         return True
    
#     if not BREVO_API_KEY:
#         print("⚠️ BREVO_API_KEY not configured, falling back to SMTP")
#         return send_email_smtp(to_email, subject, html_content, text_content)
    
#     try:
#         # Use Brevo API directly with requests
#         url = "https://api.brevo.com/v3/smtp/email"
        
#         payload = {
#             "sender": {
#                 "name": "SJS Global Tech Academy",
#                 "email": MAIL_DEFAULT_SENDER
#             },
#             "to": [
#                 {
#                     "email": to_email,
#                     "name": to_email.split('@')[0]
#                 }
#             ],
#             "subject": subject,
#             "htmlContent": html_content
#         }
        
#         if text_content:
#             payload["textContent"] = text_content
        
#         headers = {
#             "accept": "application/json",
#             "api-key": BREVO_API_KEY,
#             "content-type": "application/json"
#         }
        
#         print(f"📤 Sending email via Brevo API to: {to_email}")
#         print(f"   Subject: {subject}")
        
#         response = requests.post(url, json=payload, headers=headers, timeout=30)
        
#         print(f"📥 Brevo API Response Status: {response.status_code}")
        
#         if response.status_code in [200, 201]:
#             print(f"✅ Email sent via Brevo API to {to_email}")
#             return True
#         else:
#             print(f"❌ Brevo API error: {response.status_code} - {response.text}")
#             return send_email_smtp(to_email, subject, html_content, text_content)
            
#     except Exception as e:
#         print(f"❌ Brevo API error: {e}")
#         return send_email_smtp(to_email, subject, html_content, text_content)


# def send_email_smtp(to_email, subject, html_content, text_content=None):
#     """Send email using SMTP (fallback method)"""
#     if not USE_REAL_EMAIL:
#         print(f"📧 [TEST MODE] Would send email to: {to_email}")
#         print(f"   Subject: {subject}")
#         return True
    
#     try:
#         if not MAIL_USERNAME or not MAIL_PASSWORD:
#             print("⚠️ SMTP credentials not configured")
#             return False
        
#         print(f"📤 Sending email via SMTP to: {to_email}")
#         print(f"   Subject: {subject}")
        
#         # Create message
#         msg = MIMEMultipart('alternative')
#         msg['From'] = MAIL_DEFAULT_SENDER
#         msg['To'] = to_email
#         msg['Subject'] = subject
        
#         # Attach text and HTML parts
#         if text_content:
#             msg.attach(MIMEText(text_content, 'plain'))
#         msg.attach(MIMEText(html_content, 'html'))
        
#         # Send email
#         with smtplib.SMTP(MAIL_SERVER, MAIL_PORT) as server:
#             if MAIL_USE_TLS:
#                 server.starttls()
#             server.login(MAIL_USERNAME, MAIL_PASSWORD)
#             server.send_message(msg)
        
#         print(f"✅ Email sent via SMTP to {to_email}")
#         return True
        
#     except Exception as e:
#         print(f"❌ SMTP email error: {e}")
#         return False


# def send_admin_notification_email(student_name, student_email, order_id, amount, transaction_id, payment_method, courses, screenshot_url):
#     """Send email notification to admin when payment verification is submitted"""
    
#     # Prepare course list HTML
#     courses_html = ""
#     course_names = []
#     for course in courses:
#         if isinstance(course, dict):
#             course_name = course.get('name', 'Unknown Course')
#             course_price = course.get('price', 0)
#         else:
#             course_name = getattr(course, 'name', 'Unknown Course')
#             course_price = getattr(course, 'price', 0)
#         course_names.append(course_name)
#         courses_html += f"""
#         <tr>
#             <td style="padding: 10px; border-bottom: 1px solid #e0e0e0;">{course_name}</td>
#             <td style="padding: 10px; border-bottom: 1px solid #e0e0e0; text-align: right;">₹{course_price:,.2f}</td>
#         </tr>
#         """
    
#     # Course names as comma separated string
#     course_names_str = ", ".join(course_names)
    
#     # Email subject
#     subject = f"🔔 New Payment Request from {student_name} - Order #{order_id}"
    
#     # Email body (HTML)
#     html_body = f"""
#     <!DOCTYPE html>
#     <html>
#     <head>
#         <style>
#             body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
#             .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
#             .header {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 25px; text-align: center; border-radius: 10px 10px 0 0; }}
#             .header h2 {{ margin: 0; }}
#             .content {{ background: #f9f9f9; padding: 25px; border-radius: 0 0 10px 10px; }}
#             .info-box {{ background: white; padding: 15px; margin: 15px 0; border-radius: 8px; border-left: 4px solid #667eea; }}
#             .label {{ font-weight: bold; color: #555; }}
#             .amount {{ font-size: 24px; font-weight: bold; color: #667eea; }}
#             table {{ width: 100%; border-collapse: collapse; margin: 10px 0; }}
#             th {{ background: #667eea; color: white; padding: 10px; text-align: left; }}
#             .footer {{ text-align: center; padding: 15px; font-size: 12px; color: #999; }}
#             .highlight {{ background: #e8f5e9; padding: 15px; border-radius: 8px; margin: 15px 0; }}
#         </style>
#     </head>
#     <body>
#         <div class="container">
#             <div class="header">
#                 <h2>🎓 SJS Global Tech Academy</h2>
#                 <p style="margin: 5px 0 0 0;">New Payment Verification Request</p>
#             </div>
#             <div class="content">
#                 <div class="highlight">
#                     <p style="margin: 0; font-size: 16px;"><strong>📢 Student:</strong> {student_name} has submitted a payment request</p>
#                 </div>
                
#                 <h3>📋 Student & Payment Details</h3>
                
#                 <div class="info-box">
#                     <p><span class="label">👤 Student Name:</span> <strong>{student_name}</strong></p>
#                     <p><span class="label">📧 Student Email:</span> <strong>{student_email}</strong></p>
#                     <p><span class="label">🆔 Order ID:</span> <strong>{order_id}</strong></p>
#                     <p><span class="label">💰 Total Amount:</span> <span class="amount">₹{amount:,.2f}</span></p>
#                     <p><span class="label">💳 Payment Method:</span> <strong>{payment_method.upper()}</strong></p>
#                     <p><span class="label">🔢 Transaction ID:</span> <strong>{transaction_id}</strong></p>
#                     <p><span class="label">⏰ Submitted At:</span> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
#                 </div>
                
#                 <h3>📚 Courses Purchased</h3>
#                 <div style="background: white; padding: 5px 15px; border-radius: 8px;">
#                     <p style="font-size: 14px; color: #555;"><strong>Total Courses:</strong> {len(course_names)}</p>
#                     <p style="font-size: 14px; color: #555;"><strong>Course Names:</strong> {course_names_str}</p>
#                 </div>
#                 <table>
#                     <thead>
#                         <tr><th>Course Name</th><th>Price</th></tr>
#                     </thead>
#                     <tbody>
#                         {courses_html}
#                         <tr style="background: #f0f0f0; font-weight: bold;">
#                             <td style="padding: 10px;">Total</td>
#                             <td style="padding: 10px; text-align: right;">₹{amount:,.2f}</td>
#                         </tr>
#                     </tbody>
#                 </table>
                
#                 <h3>📸 Payment Screenshot</h3>
#                 <div class="info-box">
#                     <p><a href="{screenshot_url}" target="_blank" style="color: #667eea; font-weight: bold;">📷 View Screenshot</a></p>
#                     <p style="font-size: 12px; color: #666;">Click the link above to view the payment proof.</p>
#                 </div>
                
#                 <div style="background: #fff3cd; padding: 15px; border-radius: 5px; margin-top: 15px; border-left: 4px solid #ffc107;">
#                     <p style="margin: 0; font-size: 14px;">💡 <strong>Action Required:</strong> Please login to admin panel to approve or decline this payment request.</p>
#                 </div>
#             </div>
#             <div class="footer">
#                 <p>This is an automated notification from SJS Global Tech Academy.</p>
#                 <p>© 2024 SJS Global Tech Academy. All rights reserved.</p>
#             </div>
#         </div>
#     </body>
#     </html>
#     """
    
#     # Plain text version
#     text_body = f"""
#     NEW PAYMENT VERIFICATION REQUEST
    
#     Student Name: {student_name}
#     Student Email: {student_email}
#     Order ID: {order_id}
#     Total Amount: ₹{amount:,.2f}
#     Payment Method: {payment_method.upper()}
#     Transaction ID: {transaction_id}
#     Submitted At: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
    
#     Courses ({len(course_names)}):
#     {chr(10).join([f"  • {c}" for c in course_names])}
    
#     Screenshot URL: {screenshot_url}
    
#     Please review in admin panel.
#     """
    
#     print(f"📧 Sending admin notification to: {ADMIN_EMAIL}")
#     print(f"   Student: {student_name}")
#     print(f"   Courses: {course_names_str}")
    
#     # Send to admin email
#     result = send_email_brevo_api(
#         to_email=ADMIN_EMAIL,
#         subject=subject,
#         html_content=html_body,
#         text_content=text_body
#     )
    
#     if result:
#         print(f"✅ Admin notification sent successfully to {ADMIN_EMAIL}")
#     else:
#         print(f"❌ Failed to send admin notification to {ADMIN_EMAIL}")
    
#     return result


# def send_student_confirmation_email(student_name, student_email, order_id, amount, courses):
#     """Send confirmation email to student when payment is approved"""
    
#     # Prepare course list
#     courses_list = "\n".join([f"• {course.get('name')} - ₹{course.get('price'):,.2f}" for course in courses])
#     courses_html = "".join([f"<li>{course.get('name')} - ₹{course.get('price'):,.2f}</li>" for course in courses])
    
#     # ✅ Subject - Clear and welcoming
#     subject = "✅ Payment Verified - Welcome to SJS Global Tech Academy!"
    
#     # ✅ HTML Body - Professional and complete
#     html_body = f"""
#     <!DOCTYPE html>
#     <html>
#     <head>
#         <meta charset="UTF-8">
#         <meta name="viewport" content="width=device-width, initial-scale=1.0">
#         <title>Payment Verified</title>
#         <style>
#             body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; max-width: 600px; margin: 0 auto; padding: 20px; }}
#             .container {{ background: #f8f9fa; border-radius: 10px; padding: 30px; border: 1px solid #e0e0e0; }}
#             .header {{ background: linear-gradient(135deg, #28a745 0%, #20c997 100%); color: white; padding: 20px; text-align: center; border-radius: 8px 8px 0 0; margin: -30px -30px 20px -30px; }}
#             .header h2 {{ margin: 0; }}
#             .content {{ padding: 10px 0; }}
#             .order-details {{ background: white; padding: 15px; border-radius: 8px; margin: 15px 0; border: 1px solid #e0e0e0; }}
#             .course-list {{ background: #f0f8ff; padding: 15px; border-radius: 8px; margin: 15px 0; }}
#             .button {{ display: inline-block; padding: 12px 30px; background: #28a745; color: white !important; text-decoration: none; border-radius: 5px; font-weight: bold; }}
#             .footer {{ text-align: center; font-size: 12px; color: #999; margin-top: 20px; padding-top: 15px; border-top: 1px solid #eee; }}
#         </style>
#     </head>
#     <body>
#         <div class="container">
#             <div class="header">
#                 <h2>🎉 Payment Verified Successfully!</h2>
#                 <p style="margin: 5px 0 0 0;">Welcome to SJS Global Tech Academy</p>
#             </div>
            
#             <div class="content">
#                 <p>Dear <strong>{student_name}</strong>,</p>
                
#                 <p>We are pleased to inform you that your payment has been <strong>successfully verified</strong>! 🎓</p>
                
#                 <div class="order-details">
#                     <h3 style="color: #4a90d9; margin-top: 0;">📋 Order Details</h3>
#                     <p><strong>Order ID:</strong> {order_id}</p>
#                     <p><strong>Total Amount:</strong> <span style="color: #28a745; font-weight: bold; font-size: 18px;">₹{amount:,.2f}</span></p>
#                     <p><strong>Payment Status:</strong> <span style="color: #28a745; font-weight: bold;">✅ Verified</span></p>
#                 </div>
                
#                 <div class="course-list">
#                     <h3 style="color: #4a90d9; margin-top: 0;">📚 Courses Enrolled</h3>
#                     <ul style="list-style: none; padding: 0;">
#                         {"".join([f"<li style='padding: 5px 0; border-bottom: 1px solid #e0e0e0;'>✅ {course.get('name')} - <strong>₹{course.get('price'):,.2f}</strong></li>" for course in courses])}
#                     </ul>
#                     <div style="text-align: right; font-weight: bold; margin-top: 10px; padding-top: 10px; border-top: 2px solid #4a90d9;">
#                         Total: ₹{amount:,.2f}
#                     </div>
#                 </div>
                
#                 <div style="text-align: center; margin: 30px 0;">
#                     <a href="https://sjs-frontend-delta.vercel.app/my-courses" class="button" style="color: white !important;">📚 Access Your Courses Now</a>
#                 </div>
                
#                 <div style="background: #e8f5e9; padding: 15px; border-radius: 8px; margin-top: 20px;">
#                     <p style="margin: 0; font-size: 14px;">💡 <strong>What's Next?</strong></p>
#                     <p style="margin: 5px 0 0 0; font-size: 13px;">Login to your dashboard and start learning your courses. Happy learning! 🚀</p>
#                 </div>
                
#                 <p style="margin-top: 20px;">Thank you for choosing SJS Global Tech Academy!</p>
#                 <p><strong>Best regards,</strong><br>SJS Global Tech Academy Team</p>
#             </div>
            
#             <div class="footer">
#                 <p>This is an automated email from SJS Global Tech Academy.</p>
#                 <p>© 2024 SJS Global Tech Academy. All rights reserved.</p>
#             </div>
#         </div>
#     </body>
#     </html>
#     """
    
#     # ✅ Plain Text Version (for email clients that don't support HTML)
#     text_body = f"""
#     PAYMENT VERIFIED - Welcome to SJS Global Tech Academy!
    
#     Dear {student_name},
    
#     Your payment has been successfully verified! 🎓
    
#     Order Details:
#     ==============
#     Order ID: {order_id}
#     Total Amount: ₹{amount:,.2f}
#     Payment Status: ✅ Verified
    
#     Courses Enrolled:
#     ================
#     {chr(10).join([f"• {course.get('name')} - ₹{course.get('price'):,.2f}" for course in courses])}
#     Total: ₹{amount:,.2f}
    
#     Access Your Courses:
#     https://sjs-frontend-delta.vercel.app/my-courses
    
#     Thank you for choosing SJS Global Tech Academy!
    
#     Best regards,
#     SJS Global Tech Academy Team
#     """
    
#     print(f"\n📧 Sending confirmation email to student: {student_email}")
#     print(f"   Student: {student_name}")
#     print(f"   Courses: {len(courses)}")
    
#     # ✅ Send email using SMTP
#     result = send_email_smtp(
#         to_email=student_email,
#         subject=subject,
#         html_content=html_body,
#         text_content=text_body
#     )
    
#     if result:
#         print(f"✅ Student confirmation email sent to {student_email}")
#     else:
#         print(f"❌ Failed to send confirmation email to {student_email}")
    
#     return result


# # =====================================================
# # BANK DETAILS ENDPOINT
# # =====================================================

# @payments_bp.route('/bank-details', methods=['GET', 'OPTIONS'])
# def get_bank_details():
#     """Get bank transfer details for manual payment"""
#     if request.method == 'OPTIONS':
#         return '', 200
    
#     bank_details = {
#         'account_name': os.getenv('BANK_ACCOUNT_NAME', 'SJS Global Tech Academy'),
#         'account_number': os.getenv('BANK_ACCOUNT_NUMBER', '123456789012'),
#         'bank_name': os.getenv('BANK_NAME', 'State Bank of India'),
#         'ifsc_code': os.getenv('BANK_IFSC_CODE', 'SBIN0012345'),
#         'branch': os.getenv('BANK_BRANCH', 'Main Branch'),
#         'upi_id': os.getenv('UPI_ID', 'gurmeetsingh1021981-1@okaxis')
#     }
    
#     return jsonify({
#         'success': True,
#         'bank_details': bank_details
#     }), 200


# # =====================================================
# # PAYMENT METHODS ENDPOINT
# # =====================================================

# @payments_bp.route('/payment-methods', methods=['GET', 'OPTIONS'])
# def get_payment_methods():
#     """Get all available payment methods"""
#     if request.method == 'OPTIONS':
#         return '', 200
    
#     payment_methods = [
#         {
#             'id': 'upi',
#             'name': 'UPI (Google Pay / PhonePe / Paytm)',
#             'description': 'Instant access after payment submission',
#             'icon': 'mobile-alt',
#             'currency': 'INR',
#             'is_available': True,
#             'requires_screenshot': True
#         },
#         {
#             'id': 'paypal',
#             'name': 'PayPal',
#             'description': 'International payments via PayPal',
#             'icon': 'paypal',
#             'currency': 'USD/INR',
#             'is_available': True,
#             'requires_screenshot': True
#         },
#         {
#             'id': 'bank_transfer',
#             'name': 'Bank Transfer / NEFT / RTGS',
#             'description': 'Manual verification (24-48 hours)',
#             'icon': 'university',
#             'currency': 'INR',
#             'is_available': True,
#             'requires_screenshot': True
#         }
#     ]
    
#     return jsonify({
#         'success': True,
#         'payment_methods': payment_methods,
#         'environment': 'production'
#     }), 200


# # =====================================================
# # USER ENDPOINTS
# # =====================================================

# @payments_bp.route('/upload-screenshot', methods=['POST', 'OPTIONS'])
# @token_required
# def upload_screenshot():
#     """Upload payment screenshot (User)"""
#     if request.method == 'OPTIONS':
#         return '', 200
    
#     try:
#         if 'screenshot' not in request.files:
#             return jsonify({'error': 'No file uploaded'}), 400
        
#         file = request.files['screenshot']
#         order_id = request.form.get('order_id')
#         payment_method = request.form.get('payment_method', 'upi')
        
#         if not order_id:
#             return jsonify({'error': 'Order ID is required'}), 400
        
#         if file.filename == '':
#             return jsonify({'error': 'No file selected'}), 400
        
#         if not allowed_file(file.filename):
#             return jsonify({'error': 'Invalid file type. Allowed: png, jpg, jpeg, gif, webp'}), 400
        
#         screenshot_url = None
        
#         # Try Cloudinary first
#         if CLOUDINARY_ENABLED:
#             try:
#                 file.seek(0)
#                 upload_result = cloudinary.uploader.upload(
#                     file,
#                     folder='sjs-academy/payments',
#                     public_id=f"{order_id}_{payment_method}_{int(datetime.now().timestamp())}",
#                     overwrite=True,
#                     resource_type='auto'
#                 )
#                 screenshot_url = upload_result['secure_url']
#                 print(f"✅ Screenshot uploaded to Cloudinary: {screenshot_url}")
#             except Exception as e:
#                 print(f"Cloudinary upload failed: {e}")
#                 screenshot_url = None
        
#         # Fallback to local storage
#         if not screenshot_url:
#             file.seek(0)
#             original_filename = secure_filename(file.filename)
#             timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
#             filename = f"{order_id}_{payment_method}_{timestamp}_{original_filename}"
#             upload_dir = os.path.join('uploads', 'screenshots')
#             os.makedirs(upload_dir, exist_ok=True)
#             filepath = os.path.join(upload_dir, filename)
#             file.save(filepath)
#             screenshot_url = f"/uploads/screenshots/{filename}"
#             print(f"✅ Screenshot saved locally: {filepath}")
        
#         # Update order with screenshot URL
#         order = Order.query.filter_by(order_id=order_id).first()
#         if order:
#             order.screenshot_url = screenshot_url
#             order.payment_method = payment_method
#             db.session.commit()
        
#         internship_order = InternshipOrder.query.filter_by(order_id=order_id).first()
#         if internship_order:
#             internship_order.screenshot_url = screenshot_url
#             internship_order.payment_method = payment_method
#             db.session.commit()
        
#         return jsonify({
#             'success': True,
#             'screenshot_url': screenshot_url,
#             'message': 'Screenshot uploaded successfully'
#         }), 200
        
#     except Exception as e:
#         print(f"Upload error: {e}")
#         import traceback
#         traceback.print_exc()
#         return jsonify({'error': str(e)}), 500


# @payments_bp.route('/submit-verification', methods=['POST', 'OPTIONS'])
# @token_required
# def submit_verification():
#     """Submit payment verification (User)"""
#     if request.method == 'OPTIONS':
#         return '', 200
    
#     try:
#         data = request.get_json()
#         order_id = data.get('order_id')
#         transaction_id = data.get('transaction_id')
#         screenshot_url = data.get('screenshot_url')
#         payment_method = data.get('payment_method', 'upi')
        
#         if not order_id:
#             return jsonify({'error': 'Order ID is required'}), 400
        
#         if not transaction_id:
#             return jsonify({'error': 'Transaction ID is required'}), 400
        
#         if not screenshot_url:
#             return jsonify({'error': 'Screenshot is required'}), 400
        
#         user = request.user
        
#         # Find order
#         order = Order.query.filter_by(order_id=order_id, student_id=user['id']).first()
#         internship_order = None
        
#         if not order:
#             internship_order = InternshipOrder.query.filter_by(order_id=order_id, student_id=user['id']).first()
        
#         if not order and not internship_order:
#             return jsonify({'error': 'Order not found'}), 404
        
#         # Check for existing verification
#         existing = PaymentVerification.query.filter_by(order_id=order_id).first()
#         if existing:
#             return jsonify({'error': 'Verification already submitted'}), 400
        
#         verification_id = generate_verification_id()
#         student = Student.query.get(user['id'])
        
#         amount = order.total_amount if order else internship_order.amount
        
#         # Get courses list
#         courses_list = []
#         if order and order.courses:
#             courses_list = order.courses if isinstance(order.courses, list) else []
        
#         # Create verification record
#         verification = PaymentVerification(
#             verification_id=verification_id,
#             order_id=order_id,
#             student_id=user['id'],
#             student_name=student.name if student else user.get('name', 'Student'),
#             student_email=student.email if student else user.get('email'),
#             amount=amount,
#             transaction_id=transaction_id,
#             screenshot_url=screenshot_url,
#             payment_method=payment_method,
#             status='pending',
#             created_at=datetime.utcnow()
#         )
        
#         db.session.add(verification)
        
#         if order:
#             order.transaction_id = transaction_id
#             order.payment_status = 'pending_verification'
#             order.payment_method = payment_method
#         elif internship_order:
#             internship_order.transaction_id = transaction_id
#             internship_order.payment_status = 'pending_verification'
#             internship_order.payment_method = payment_method
        
#         db.session.commit()
        
#         print(f"✅ Verification submitted: {verification_id} via {payment_method}")
        
#         # 📧 SEND EMAIL NOTIFICATION TO ADMIN (gangahanjra@gmail.com)
#         student_name = student.name if student else user.get('name', 'Student')
#         student_email = student.email if student else user.get('email')
        
#         print(f"\n📧 Sending payment notification for:")
#         print(f"   Student: {student_name}")
#         print(f"   Student Email: {student_email}")
#         print(f"   Order ID: {order_id}")
#         print(f"   Amount: ₹{amount:,.2f}")
#         print(f"   Payment Method: {payment_method}")
#         print(f"   Courses: {len(courses_list)} courses")
        
#         send_admin_notification_email(
#             student_name=student_name,
#             student_email=student_email,
#             order_id=order_id,
#             amount=amount,
#             transaction_id=transaction_id,
#             payment_method=payment_method,
#             courses=courses_list,
#             screenshot_url=screenshot_url
#         )
        
#         return jsonify({
#             'success': True,
#             'message': 'Verification submitted successfully! Admin has been notified.',
#             'verification_id': verification_id
#         }), 201
        
#     except Exception as e:
#         db.session.rollback()
#         print(f"❌ Submit error: {e}")
#         import traceback
#         traceback.print_exc()
#         return jsonify({'error': str(e)}), 500


# @payments_bp.route('/status/<verification_id>', methods=['GET', 'OPTIONS'])
# @token_required
# def get_verification_status(verification_id):
#     """Get verification status by ID"""
#     if request.method == 'OPTIONS':
#         return '', 200
    
#     try:
#         verification = PaymentVerification.query.filter_by(verification_id=verification_id).first()
        
#         if not verification:
#             return jsonify({'error': 'Verification not found'}), 404
        
#         user = request.user
#         if verification.student_id != user['id'] and user.get('role') != 'admin':
#             return jsonify({'error': 'Unauthorized'}), 403
        
#         status_messages = {
#             'pending': 'Your payment is being verified. We will notify you within 24 hours.',
#             'approved': '✅ Payment verified! Your courses have been activated.',
#             'declined': '❌ Payment verification failed. Please contact support.'
#         }
        
#         return jsonify({
#             'success': True,
#             'status': verification.status,
#             'message': status_messages.get(verification.status, ''),
#             'admin_notes': verification.admin_notes,
#             'payment_method': getattr(verification, 'payment_method', 'upi'),
#             'verified_at': verification.verified_at.isoformat() if hasattr(verification, 'verified_at') and verification.verified_at else None
#         }), 200
#     except Exception as e:
#         print(f"Status check error: {e}")
#         return jsonify({'error': str(e)}), 500


# # =====================================================
# # ADMIN ENDPOINTS
# # =====================================================

# @payments_bp.route('/admin/payment-requests', methods=['GET', 'OPTIONS'])
# @admin_required
# def get_payment_requests():
#     """Get all pending payment verifications (Admin)"""
#     if request.method == 'OPTIONS':
#         return '', 200
    
#     try:
#         verifications = PaymentVerification.query.filter_by(
#             status='pending'
#         ).order_by(PaymentVerification.created_at.desc()).all()
        
#         result = []
#         for v in verifications:
#             result.append({
#                 'id': v.id,
#                 'verification_id': v.verification_id,
#                 'order_id': v.order_id,
#                 'student_id': v.student_id,
#                 'student_name': v.student_name,
#                 'student_email': v.student_email,
#                 'amount': float(v.amount) if v.amount else 0,
#                 'transaction_id': v.transaction_id,
#                 'screenshot_url': v.screenshot_url,
#                 'payment_method': getattr(v, 'payment_method', 'upi'),
#                 'status': v.status,
#                 'created_at': v.created_at.isoformat() if v.created_at else None
#             })
        
#         return jsonify({
#             'success': True,
#             'verifications': result
#         }), 200
#     except Exception as e:
#         print(f"Error: {e}")
#         return jsonify({'error': str(e)}), 500


# @payments_bp.route('/admin/payment-requests/<int:request_id>/approve', methods=['POST', 'OPTIONS'])
# @admin_required
# def approve_payment(request_id):
#     """Approve payment verification (Admin)"""
#     if request.method == 'OPTIONS':
#         return '', 200
    
#     try:
#         data = request.get_json()
#         admin_notes = data.get('notes', 'Payment verified and approved.')
        
#         # Get verification record
#         verification = PaymentVerification.query.get(request_id)
#         if not verification:
#             return jsonify({'error': 'Verification not found'}), 404
        
#         # Update verification status
#         verification.status = 'approved'
#         verification.admin_notes = admin_notes
#         verification.verified_at = datetime.utcnow()
        
#         # Get the order
#         order = Order.query.filter_by(order_id=verification.order_id).first()
#         if not order:
#             # Check if it's an internship order
#             internship_order = InternshipOrder.query.filter_by(order_id=verification.order_id).first()
#             if internship_order:
#                 internship_order.payment_status = 'completed'
#                 internship_order.status = 'active'
#                 db.session.commit()
                
#                 # Send confirmation email to student
#                 send_student_confirmation_email(
#                     student_name=verification.student_name,
#                     student_email=verification.student_email,
#                     order_id=verification.order_id,
#                     amount=verification.amount,
#                     courses=[{'name': internship_order.internship_title, 'price': verification.amount}]
#                 )
                
#                 return jsonify({
#                     'success': True,
#                     'message': 'Internship payment approved successfully!'
#                 }), 200
#             return jsonify({'error': 'Order not found'}), 404
        
#         # Update order status
#         order.payment_status = 'completed'
#         order.transaction_id = verification.transaction_id
        
#         # Get courses from order
#         order_courses = order.courses if isinstance(order.courses, list) else []
        
#         print(f"\n{'='*60}")
#         print(f"📝 APPROVING PAYMENT - Adding to Enrollment")
#         print(f"Order ID: {order.order_id}")
#         print(f"Student ID: {verification.student_id}")
#         print(f"Student Email: {verification.student_email}")
#         print(f"Payment Method: {getattr(verification, 'payment_method', 'upi')}")
#         print(f"Order Courses: {order_courses}")
#         print(f"{'='*60}\n")
        
#         # Import models
#         from app.models.course import Enrollment, Course
        
#         courses_added = []
        
#         # For each course in the order, add to enrollments table
#         for course_data in order_courses:
#             # Get course ID
#             if isinstance(course_data, dict):
#                 course_id = course_data.get('id')
#                 course_name = course_data.get('name', 'Unknown')
#             else:
#                 course_id = getattr(course_data, 'id', None)
#                 course_name = getattr(course_data, 'name', 'Unknown')
            
#             if course_id:
#                 print(f"Processing course ID: {course_id} - {course_name}")
                
#                 # Check if already enrolled
#                 existing = Enrollment.query.filter_by(
#                     student_id=verification.student_id,
#                     course_id=course_id
#                 ).first()
                
#                 if not existing:
#                     # Create enrollment
#                     enrollment = Enrollment(
#                         student_id=verification.student_id,
#                         course_id=course_id,
#                         enrolled_at=datetime.utcnow(),
#                         status='active',
#                         payment_verification_id=verification.verification_id
#                     )
#                     db.session.add(enrollment)
#                     courses_added.append(course_id)
#                     print(f"✅ Added to enrollments table: student_id={verification.student_id}, course_id={course_id}")
                    
#                     # Update student's course_ids JSON field
#                     student = Student.query.get(verification.student_id)
#                     if student:
#                         if student.course_ids is None:
#                             student.course_ids = []
#                         if course_id not in student.course_ids:
#                             student.course_ids.append(course_id)
#                             print(f"✅ Added course {course_id} to student.course_ids")
                    
#                     # Update course student count
#                     course = Course.query.get(course_id)
#                     if course:
#                         course.students_enrolled = (course.students_enrolled or 0) + 1
#                         db.session.add(course)
#                         print(f"✅ Updated course {course_id} students_enrolled to {course.students_enrolled}")
#                 else:
#                     print(f"⚠️ Already enrolled in course {course_id}")
        
#         # Commit all changes
#         db.session.commit()
        
#         # Send confirmation email to student
#         send_student_confirmation_email(
#             student_name=verification.student_name,
#             student_email=verification.student_email,
#             order_id=verification.order_id,
#             amount=verification.amount,
#             courses=order_courses
#         )
        
#         # Verify enrollment was added
#         verify_enrollments = Enrollment.query.filter_by(
#             student_id=verification.student_id
#         ).all()
        
#         print(f"\n📊 Enrollment Summary:")
#         print(f"   Total enrollments for student {verification.student_id}: {len(verify_enrollments)}")
#         for enc in verify_enrollments:
#             print(f"   - Course ID: {enc.course_id}, Status: {enc.status}")
        
#         print(f"\n✅ Payment approved successfully!")
#         print(f"   Courses added: {courses_added}")
#         print(f"   Email sent to: {verification.student_email}")
#         print(f"{'='*60}\n")
        
#         return jsonify({
#             'success': True,
#             'message': 'Payment approved successfully! Courses added to student account.',
#             'courses_added': courses_added,
#             'total_enrollments': len(verify_enrollments)
#         }), 200
        
#     except Exception as e:
#         db.session.rollback()
#         print(f"❌ Approve error: {e}")
#         import traceback
#         traceback.print_exc()
#         return jsonify({'error': str(e)}), 500


# @payments_bp.route('/admin/payment-requests/<int:request_id>/decline', methods=['POST', 'OPTIONS'])
# @admin_required
# def decline_payment(request_id):
#     """Decline payment verification (Admin)"""
#     if request.method == 'OPTIONS':
#         return '', 200
    
#     try:
#         data = request.get_json()
#         admin_notes = data.get('notes', 'Payment verification failed.')
        
#         verification = PaymentVerification.query.get(request_id)
#         if not verification:
#             return jsonify({'error': 'Verification not found'}), 404
        
#         verification.status = 'declined'
#         verification.admin_notes = admin_notes
#         verification.verified_at = datetime.utcnow()
        
#         # Update order status
#         order = Order.query.filter_by(order_id=verification.order_id).first()
#         if order:
#             order.payment_status = 'failed'
        
#         internship_order = InternshipOrder.query.filter_by(order_id=verification.order_id).first()
#         if internship_order:
#             internship_order.payment_status = 'failed'
        
#         db.session.commit()
        
#         print(f"✅ Payment declined: {verification.verification_id}")
        
#         return jsonify({
#             'success': True,
#             'message': 'Payment declined.'
#         }), 200
#     except Exception as e:
#         db.session.rollback()
#         print(f"Decline error: {e}")
#         return jsonify({'error': str(e)}), 500


# @payments_bp.route('/admin/payment-stats', methods=['GET', 'OPTIONS'])
# @admin_required
# def get_payment_stats():
#     """Get payment statistics (Admin)"""
#     if request.method == 'OPTIONS':
#         return '', 200
    
#     try:
#         pending = PaymentVerification.query.filter_by(status='pending').count()
#         approved = PaymentVerification.query.filter_by(status='approved').count()
#         declined = PaymentVerification.query.filter_by(status='declined').count()
        
#         total_amount = db.session.query(db.func.sum(PaymentVerification.amount)).filter(
#             PaymentVerification.status == 'approved'
#         ).scalar() or 0
        
#         return jsonify({
#             'success': True,
#             'stats': {
#                 'pending': pending,
#                 'approved': approved,
#                 'declined': declined,
#                 'total_amount': float(total_amount)
#             }
#         }), 200
#     except Exception as e:
#         return jsonify({'error': str(e)}), 500





















import cloudinary
import cloudinary.uploader
from flask import Blueprint, request, jsonify, current_app
from app import db
from app.models.order import Order
from app.models.user import Student
from app.models.payment import PaymentVerification
from app.models.internship import InternshipOrder
from app.utils.helpers import generate_verification_id, allowed_file
from app.utils.decorators import token_required, admin_required
import os
from werkzeug.utils import secure_filename
from datetime import datetime
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

payments_bp = Blueprint('payments', __name__)

# =====================================================
# GMAIL SMTP CONFIGURATION
# =====================================================
MAIL_SERVER = os.getenv('MAIL_SERVER', 'smtp.gmail.com')
MAIL_PORT = int(os.getenv('MAIL_PORT', 587))
MAIL_USE_TLS = os.getenv('MAIL_USE_TLS', 'True').lower() == 'true'
MAIL_USERNAME = os.getenv('MAIL_USERNAME', 'sjsglobaltech@gmail.com')
MAIL_PASSWORD = os.getenv('MAIL_PASSWORD', '')  # Gmail App Password
MAIL_DEFAULT_SENDER = os.getenv('MAIL_DEFAULT_SENDER', 'sjsglobaltech@gmail.com')
ADMIN_EMAIL = os.getenv('ADMIN_EMAIL', 'sjsglobaltech@gmail.com')
USE_REAL_EMAIL = os.getenv('USE_REAL_EMAIL', 'True').lower() == 'true'

# Cloudinary configuration
CLOUDINARY_CLOUD_NAME = os.getenv('CLOUDINARY_CLOUD_NAME', 'dxxpeilta')
CLOUDINARY_API_KEY = os.getenv('CLOUDINARY_API_KEY', '375175513582196')
CLOUDINARY_API_SECRET = os.getenv('CLOUDINARY_API_SECRET')

def init_cloudinary():
    if CLOUDINARY_CLOUD_NAME and CLOUDINARY_API_KEY and CLOUDINARY_API_SECRET:
        cloudinary.config(
            cloud_name=CLOUDINARY_CLOUD_NAME,
            api_key=CLOUDINARY_API_KEY,
            api_secret=CLOUDINARY_API_SECRET,
            secure=True
        )
        print(f"✅ Cloudinary configured: {CLOUDINARY_CLOUD_NAME}")
        return True
    print("⚠️ Cloudinary not configured")
    return False

CLOUDINARY_ENABLED = init_cloudinary()


# =====================================================
# EMAIL FUNCTION - DIRECT GMAIL SMTP
# =====================================================

def send_email(to_email, subject, html_content, text_content=None, reply_to=None):
    """Send email using Gmail SMTP directly"""
    if not USE_REAL_EMAIL:
        print(f"📧 [TEST MODE] Would send to: {to_email}")
        return True
    
    try:
        if not MAIL_PASSWORD:
            print("❌ Gmail App Password not configured")
            print("   Please set MAIL_PASSWORD in environment variables")
            return False
        
        print(f"📤 Sending via Gmail to: {to_email}")
        print(f"   Subject: {subject}")
        
        msg = MIMEMultipart('alternative')
        msg['From'] = f"SJS Global Tech Academy <{MAIL_USERNAME}>"
        msg['To'] = to_email
        msg['Subject'] = subject
        if reply_to:
            msg['Reply-To'] = reply_to
        msg['X-Mailer'] = 'SJS Academy'
        msg['X-Priority'] = '1'
        msg['Importance'] = 'High'
        
        if text_content:
            msg.attach(MIMEText(text_content, 'plain'))
        msg.attach(MIMEText(html_content, 'html'))
        
        with smtplib.SMTP(MAIL_SERVER, MAIL_PORT) as server:
            if MAIL_USE_TLS:
                server.starttls()
            server.login(MAIL_USERNAME, MAIL_PASSWORD)
            server.send_message(msg)
        
        print(f"✅ Email sent to {to_email}")
        return True
        
    except smtplib.SMTPAuthenticationError as e:
        print(f"❌ Gmail Auth error: {e}")
        print("   Use App Password, not regular Gmail password")
        return False
    except Exception as e:
        print(f"❌ Email error: {e}")
        return False


# =====================================================
# ADMIN NOTIFICATION EMAIL
# =====================================================

def send_admin_notification_email(student_name, student_email, order_id, amount, transaction_id, payment_method, courses, screenshot_url):
    """Send email to admin when payment is submitted"""
    
    courses_html = ""
    course_names = []
    for course in courses:
        if isinstance(course, dict):
            course_name = course.get('name', 'Unknown Course')
            course_price = course.get('price', 0)
        else:
            course_name = getattr(course, 'name', 'Unknown Course')
            course_price = getattr(course, 'price', 0)
        course_names.append(course_name)
        courses_html += f"""
        <tr>
            <td style="padding: 8px; border-bottom: 1px solid #e0e0e0;">{course_name}</td>
            <td style="padding: 8px; border-bottom: 1px solid #e0e0e0; text-align: right;">₹{course_price:,.2f}</td>
        </tr>
        """
    
    course_names_str = ", ".join(course_names)
    
    subject = f"📧 Payment Request from {student_name} - Order #{order_id}"
    
    html_body = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
    </head>
    <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333; max-width: 600px; margin: 0 auto; padding: 20px;">
        <div style="background: #f8f9fa; border-radius: 8px; padding: 20px; border: 1px solid #e0e0e0;">
            <h2 style="color: #4a90d9; margin-top: 0;">📋 New Payment Request</h2>
            
            <div style="background: #e3f2fd; padding: 12px; border-radius: 6px; margin-bottom: 15px;">
                <p style="margin: 0; font-size: 14px;">
                    <strong>From Student:</strong> {student_name}
                    <br>
                    <strong>Email:</strong> <a href="mailto:{student_email}">{student_email}</a>
                </p>
            </div>
            
            <table style="width: 100%; border-collapse: collapse;">
                <tr><td style="padding: 8px 0; font-weight: bold;">Order ID:</td><td style="padding: 8px 0;">{order_id}</td></tr>
                <tr><td style="padding: 8px 0; font-weight: bold;">Amount:</td><td style="padding: 8px 0; color: #4a90d9; font-weight: bold;">₹{amount:,.2f}</td></tr>
                <tr><td style="padding: 8px 0; font-weight: bold;">Payment Method:</td><td style="padding: 8px 0;">{payment_method.upper()}</td></tr>
                <tr><td style="padding: 8px 0; font-weight: bold;">Transaction ID:</td><td style="padding: 8px 0;">{transaction_id}</td></tr>
            </table>
            
            <div style="background: white; padding: 12px; border-radius: 6px; margin: 12px 0;">
                <p style="margin: 0; font-weight: bold;">Courses ({len(course_names)}):</p>
                <ul style="margin: 5px 0; padding-left: 20px;">
                    {"".join([f"<li>{c}</li>" for c in course_names])}
                </ul>
                <table style="width: 100%; border-collapse: collapse; margin-top: 10px;">
                    <thead>
                        <tr><th style="text-align: left; padding: 5px;">Course</th><th style="text-align: right; padding: 5px;">Price</th></tr>
                    </thead>
                    <tbody>
                        {courses_html}
                        <tr style="background: #f0f0f0; font-weight: bold;">
                            <td style="padding: 8px;">Total</td>
                            <td style="padding: 8px; text-align: right;">₹{amount:,.2f}</td>
                        </tr>
                    </tbody>
                </table>
            </div>
            
            <div style="background: #fff3cd; padding: 12px; border-radius: 6px; border-left: 4px solid #ffc107; margin-top: 15px;">
                <p style="margin: 0; font-size: 14px;">💡 Reply to contact: <a href="mailto:{student_email}">{student_email}</a></p>
            </div>
        </div>
        <div style="text-align: center; font-size: 11px; color: #999; margin-top: 15px; padding-top: 10px; border-top: 1px solid #eee;">
            <p style="margin: 0;">SJS Global Tech Academy</p>
        </div>
    </body>
    </html>
    """
    
    text_body = f"""
    New Payment Request from {student_name}
    
    Student: {student_name}
    Student Email: {student_email}
    Order ID: {order_id}
    Amount: ₹{amount:,.2f}
    Payment Method: {payment_method.upper()}
    Transaction ID: {transaction_id}
    Courses: {course_names_str}
    """
    
    return send_email(
        to_email=ADMIN_EMAIL,
        subject=subject,
        html_content=html_body,
        text_content=text_body,
        reply_to=student_email
    )


# =====================================================
# STUDENT CONFIRMATION EMAIL
# =====================================================

def send_student_confirmation_email(student_name, student_email, order_id, amount, courses):
    """Send confirmation email to student when payment is approved"""
    
    courses_html = ""
    for course in courses:
        if isinstance(course, dict):
            course_name = course.get('name', 'Unknown Course')
            course_price = course.get('price', 0)
        else:
            course_name = getattr(course, 'name', 'Unknown Course')
            course_price = getattr(course, 'price', 0)
        courses_html += f"""
        <li style='padding: 5px 0; border-bottom: 1px solid #e0e0e0;'>
            ✅ {course_name} - <strong>₹{course_price:,.2f}</strong>
        </li>
        """
    
    subject = "✅ Payment Verified - Welcome to SJS Global Tech Academy!"
    
    html_body = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <style>
            body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; max-width: 600px; margin: 0 auto; padding: 20px; }}
            .container {{ background: #f8f9fa; border-radius: 10px; padding: 30px; border: 1px solid #e0e0e0; }}
            .header {{ background: linear-gradient(135deg, #28a745 0%, #20c997 100%); color: white; padding: 20px; text-align: center; border-radius: 8px 8px 0 0; margin: -30px -30px 20px -30px; }}
            .header h2 {{ margin: 0; }}
            .order-details {{ background: white; padding: 15px; border-radius: 8px; margin: 15px 0; border: 1px solid #e0e0e0; }}
            .course-list {{ background: #f0f8ff; padding: 15px; border-radius: 8px; margin: 15px 0; }}
            .button {{ display: inline-block; padding: 12px 30px; background: #28a745; color: white !important; text-decoration: none; border-radius: 5px; font-weight: bold; }}
            .footer {{ text-align: center; font-size: 12px; color: #999; margin-top: 20px; padding-top: 15px; border-top: 1px solid #eee; }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h2>🎉 Payment Verified Successfully!</h2>
                <p style="margin: 5px 0 0 0;">Welcome to SJS Global Tech Academy</p>
            </div>
            
            <div class="content">
                <p>Dear <strong>{student_name}</strong>,</p>
                
                <p>We are pleased to inform you that your payment has been <strong>successfully verified</strong>! 🎓</p>
                
                <div class="order-details">
                    <h3 style="color: #4a90d9; margin-top: 0;">📋 Order Details</h3>
                    <p><strong>Order ID:</strong> {order_id}</p>
                    <p><strong>Total Amount:</strong> <span style="color: #28a745; font-weight: bold; font-size: 18px;">₹{amount:,.2f}</span></p>
                    <p><strong>Payment Status:</strong> <span style="color: #28a745; font-weight: bold;">✅ Verified</span></p>
                </div>
                
                <div class="course-list">
                    <h3 style="color: #4a90d9; margin-top: 0;">📚 Courses Enrolled</h3>
                    <ul style="list-style: none; padding: 0;">
                        {courses_html}
                    </ul>
                    <div style="text-align: right; font-weight: bold; margin-top: 10px; padding-top: 10px; border-top: 2px solid #4a90d9;">
                        Total: ₹{amount:,.2f}
                    </div>
                </div>
                
                <div style="text-align: center; margin: 30px 0;">
                    <a href="https://sjs-frontend-delta.vercel.app/my-courses" class="button" style="color: white !important;">📚 Access Your Courses Now</a>
                </div>
                
                <div style="background: #e8f5e9; padding: 15px; border-radius: 8px; margin-top: 20px;">
                    <p style="margin: 0; font-size: 14px;">💡 <strong>What's Next?</strong></p>
                    <p style="margin: 5px 0 0 0; font-size: 13px;">Login to your dashboard and start learning your courses. Happy learning! 🚀</p>
                </div>
                
                <p style="margin-top: 20px;">Thank you for choosing SJS Global Tech Academy!</p>
                <p><strong>Best regards,</strong><br>SJS Global Tech Academy Team</p>
            </div>
            
            <div class="footer">
                <p>This is an automated email from SJS Global Tech Academy.</p>
                <p>© 2024 SJS Global Tech Academy. All rights reserved.</p>
            </div>
        </div>
    </body>
    </html>
    """
    
    text_body = f"""
    PAYMENT VERIFIED - Welcome to SJS Global Tech Academy!
    
    Dear {student_name},
    
    Your payment has been successfully verified! 🎓
    
    Order Details:
    ==============
    Order ID: {order_id}
    Total Amount: ₹{amount:,.2f}
    Payment Status: ✅ Verified
    
    Courses Enrolled:
    ================
    {chr(10).join([f"• {course.get('name')} - ₹{course.get('price'):,.2f}" for course in courses])}
    Total: ₹{amount:,.2f}
    
    Access Your Courses:
    https://sjs-frontend-delta.vercel.app/my-courses
    
    Thank you for choosing SJS Global Tech Academy!
    
    Best regards,
    SJS Global Tech Academy Team
    """
    
    print(f"\n📧 Sending confirmation to: {student_email}")
    
    return send_email(
        to_email=student_email,
        subject=subject,
        html_content=html_body,
        text_content=text_body
    )


# =====================================================
# BANK DETAILS ENDPOINT
# =====================================================

@payments_bp.route('/bank-details', methods=['GET', 'OPTIONS'])
def get_bank_details():
    if request.method == 'OPTIONS':
        return '', 200
    
    bank_details = {
        'account_name': os.getenv('BANK_ACCOUNT_NAME', 'SJS Global Tech Academy'),
        'account_number': os.getenv('BANK_ACCOUNT_NUMBER', '123456789012'),
        'bank_name': os.getenv('BANK_NAME', 'State Bank of India'),
        'ifsc_code': os.getenv('BANK_IFSC_CODE', 'SBIN0012345'),
        'branch': os.getenv('BANK_BRANCH', 'Main Branch'),
        'upi_id': os.getenv('UPI_ID', 'gurmeetsingh1021981-1@okaxis')
    }
    
    return jsonify({'success': True, 'bank_details': bank_details}), 200


# =====================================================
# PAYMENT METHODS ENDPOINT
# =====================================================

@payments_bp.route('/payment-methods', methods=['GET', 'OPTIONS'])
def get_payment_methods():
    if request.method == 'OPTIONS':
        return '', 200
    
    payment_methods = [
        {'id': 'upi', 'name': 'UPI (Google Pay / PhonePe / Paytm)', 'description': 'Instant access after payment submission', 'icon': 'mobile-alt', 'currency': 'INR', 'is_available': True, 'requires_screenshot': True},
        {'id': 'paypal', 'name': 'PayPal', 'description': 'International payments via PayPal', 'icon': 'paypal', 'currency': 'USD/INR', 'is_available': True, 'requires_screenshot': True},
        {'id': 'bank_transfer', 'name': 'Bank Transfer / NEFT / RTGS', 'description': 'Manual verification (24-48 hours)', 'icon': 'university', 'currency': 'INR', 'is_available': True, 'requires_screenshot': True}
    ]
    
    return jsonify({'success': True, 'payment_methods': payment_methods, 'environment': 'production'}), 200


# =====================================================
# UPLOAD SCREENSHOT
# =====================================================

@payments_bp.route('/upload-screenshot', methods=['POST', 'OPTIONS'])
@token_required
def upload_screenshot():
    if request.method == 'OPTIONS':
        return '', 200
    
    try:
        if 'screenshot' not in request.files:
            return jsonify({'error': 'No file uploaded'}), 400
        
        file = request.files['screenshot']
        order_id = request.form.get('order_id')
        payment_method = request.form.get('payment_method', 'upi')
        
        if not order_id:
            return jsonify({'error': 'Order ID is required'}), 400
        
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
        
        if not allowed_file(file.filename):
            return jsonify({'error': 'Invalid file type'}), 400
        
        screenshot_url = None
        
        if CLOUDINARY_ENABLED:
            try:
                file.seek(0)
                upload_result = cloudinary.uploader.upload(
                    file,
                    folder='sjs-academy/payments',
                    public_id=f"{order_id}_{payment_method}_{int(datetime.now().timestamp())}",
                    overwrite=True,
                    resource_type='auto'
                )
                screenshot_url = upload_result['secure_url']
            except Exception as e:
                print(f"Cloudinary failed: {e}")
                screenshot_url = None
        
        if not screenshot_url:
            file.seek(0)
            original_filename = secure_filename(file.filename)
            timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
            filename = f"{order_id}_{payment_method}_{timestamp}_{original_filename}"
            upload_dir = os.path.join('uploads', 'screenshots')
            os.makedirs(upload_dir, exist_ok=True)
            filepath = os.path.join(upload_dir, filename)
            file.save(filepath)
            screenshot_url = f"/uploads/screenshots/{filename}"
        
        order = Order.query.filter_by(order_id=order_id).first()
        if order:
            order.screenshot_url = screenshot_url
            order.payment_method = payment_method
            db.session.commit()
        
        internship_order = InternshipOrder.query.filter_by(order_id=order_id).first()
        if internship_order:
            internship_order.screenshot_url = screenshot_url
            internship_order.payment_method = payment_method
            db.session.commit()
        
        return jsonify({'success': True, 'screenshot_url': screenshot_url}), 200
        
    except Exception as e:
        print(f"Upload error: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500


# =====================================================
# SUBMIT VERIFICATION
# =====================================================

@payments_bp.route('/submit-verification', methods=['POST', 'OPTIONS'])
@token_required
def submit_verification():
    if request.method == 'OPTIONS':
        return '', 200
    
    try:
        data = request.get_json()
        order_id = data.get('order_id')
        transaction_id = data.get('transaction_id')
        screenshot_url = data.get('screenshot_url')
        payment_method = data.get('payment_method', 'upi')
        
        if not order_id:
            return jsonify({'error': 'Order ID is required'}), 400
        
        if not transaction_id:
            return jsonify({'error': 'Transaction ID is required'}), 400
        
        if not screenshot_url:
            return jsonify({'error': 'Screenshot is required'}), 400
        
        user = request.user
        
        order = Order.query.filter_by(order_id=order_id, student_id=user['id']).first()
        internship_order = None
        
        if not order:
            internship_order = InternshipOrder.query.filter_by(order_id=order_id, student_id=user['id']).first()
        
        if not order and not internship_order:
            return jsonify({'error': 'Order not found'}), 404
        
        existing = PaymentVerification.query.filter_by(order_id=order_id).first()
        if existing:
            return jsonify({'error': 'Verification already submitted'}), 400
        
        verification_id = generate_verification_id()
        student = Student.query.get(user['id'])
        
        amount = order.total_amount if order else internship_order.amount
        
        courses_list = []
        if order and order.courses:
            courses_list = order.courses if isinstance(order.courses, list) else []
        
        verification = PaymentVerification(
            verification_id=verification_id,
            order_id=order_id,
            student_id=user['id'],
            student_name=student.name if student else user.get('name', 'Student'),
            student_email=student.email if student else user.get('email'),
            amount=amount,
            transaction_id=transaction_id,
            screenshot_url=screenshot_url,
            payment_method=payment_method,
            status='pending',
            created_at=datetime.utcnow()
        )
        
        db.session.add(verification)
        
        if order:
            order.transaction_id = transaction_id
            order.payment_status = 'pending_verification'
            order.payment_method = payment_method
        elif internship_order:
            internship_order.transaction_id = transaction_id
            internship_order.payment_status = 'pending_verification'
            internship_order.payment_method = payment_method
        
        db.session.commit()
        
        print(f"✅ Verification submitted: {verification_id} via {payment_method}")
        
        student_name = student.name if student else user.get('name', 'Student')
        student_email = student.email if student else user.get('email')
        
        send_admin_notification_email(
            student_name=student_name,
            student_email=student_email,
            order_id=order_id,
            amount=amount,
            transaction_id=transaction_id,
            payment_method=payment_method,
            courses=courses_list,
            screenshot_url=screenshot_url
        )
        
        return jsonify({
            'success': True,
            'message': 'Verification submitted! Admin notified.',
            'verification_id': verification_id
        }), 201
        
    except Exception as e:
        db.session.rollback()
        print(f"❌ Submit error: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500


# =====================================================
# STATUS CHECK
# =====================================================

@payments_bp.route('/status/<verification_id>', methods=['GET', 'OPTIONS'])
@token_required
def get_verification_status(verification_id):
    if request.method == 'OPTIONS':
        return '', 200
    
    try:
        verification = PaymentVerification.query.filter_by(verification_id=verification_id).first()
        
        if not verification:
            return jsonify({'error': 'Verification not found'}), 404
        
        user = request.user
        if verification.student_id != user['id'] and user.get('role') != 'admin':
            return jsonify({'error': 'Unauthorized'}), 403
        
        status_messages = {
            'pending': 'Your payment is being verified.',
            'approved': '✅ Payment verified! Courses activated.',
            'declined': '❌ Payment verification failed.'
        }
        
        return jsonify({
            'success': True,
            'status': verification.status,
            'message': status_messages.get(verification.status, ''),
            'admin_notes': verification.admin_notes,
            'payment_method': getattr(verification, 'payment_method', 'upi')
        }), 200
    except Exception as e:
        print(f"Status check error: {e}")
        return jsonify({'error': str(e)}), 500


# =====================================================
# ADMIN ENDPOINTS
# =====================================================

@payments_bp.route('/admin/payment-requests', methods=['GET', 'OPTIONS'])
@admin_required
def get_payment_requests():
    if request.method == 'OPTIONS':
        return '', 200
    
    try:
        verifications = PaymentVerification.query.filter_by(status='pending').order_by(PaymentVerification.created_at.desc()).all()
        
        result = []
        for v in verifications:
            result.append({
                'id': v.id,
                'verification_id': v.verification_id,
                'order_id': v.order_id,
                'student_id': v.student_id,
                'student_name': v.student_name,
                'student_email': v.student_email,
                'amount': float(v.amount) if v.amount else 0,
                'transaction_id': v.transaction_id,
                'screenshot_url': v.screenshot_url,
                'payment_method': getattr(v, 'payment_method', 'upi'),
                'status': v.status,
                'created_at': v.created_at.isoformat() if v.created_at else None
            })
        
        return jsonify({'success': True, 'verifications': result}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@payments_bp.route('/admin/payment-requests/<int:request_id>/approve', methods=['POST', 'OPTIONS'])
@admin_required
def approve_payment(request_id):
    if request.method == 'OPTIONS':
        return '', 200
    
    try:
        data = request.get_json()
        admin_notes = data.get('notes', 'Payment verified and approved.')
        
        verification = PaymentVerification.query.get(request_id)
        if not verification:
            return jsonify({'error': 'Verification not found'}), 404
        
        verification.status = 'approved'
        verification.admin_notes = admin_notes
        verification.verified_at = datetime.utcnow()
        
        order = Order.query.filter_by(order_id=verification.order_id).first()
        if not order:
            internship_order = InternshipOrder.query.filter_by(order_id=verification.order_id).first()
            if internship_order:
                internship_order.payment_status = 'completed'
                internship_order.status = 'active'
                db.session.commit()
                
                send_student_confirmation_email(
                    student_name=verification.student_name,
                    student_email=verification.student_email,
                    order_id=verification.order_id,
                    amount=verification.amount,
                    courses=[{'name': internship_order.internship_title, 'price': verification.amount}]
                )
                
                return jsonify({'success': True, 'message': 'Internship approved!'}), 200
            return jsonify({'error': 'Order not found'}), 404
        
        order.payment_status = 'completed'
        order.transaction_id = verification.transaction_id
        
        order_courses = order.courses if isinstance(order.courses, list) else []
        
        from app.models.course import Enrollment, Course
        
        courses_added = []
        
        for course_data in order_courses:
            if isinstance(course_data, dict):
                course_id = course_data.get('id')
            else:
                course_id = getattr(course_data, 'id', None)
            
            if course_id:
                existing = Enrollment.query.filter_by(
                    student_id=verification.student_id,
                    course_id=course_id
                ).first()
                
                if not existing:
                    enrollment = Enrollment(
                        student_id=verification.student_id,
                        course_id=course_id,
                        enrolled_at=datetime.utcnow(),
                        status='active',
                        payment_verification_id=verification.verification_id
                    )
                    db.session.add(enrollment)
                    courses_added.append(course_id)
                    
                    student = Student.query.get(verification.student_id)
                    if student:
                        if student.course_ids is None:
                            student.course_ids = []
                        if course_id not in student.course_ids:
                            student.course_ids.append(course_id)
                    
                    course = Course.query.get(course_id)
                    if course:
                        course.students_enrolled = (course.students_enrolled or 0) + 1
                        db.session.add(course)
        
        db.session.commit()
        
        send_student_confirmation_email(
            student_name=verification.student_name,
            student_email=verification.student_email,
            order_id=verification.order_id,
            amount=verification.amount,
            courses=order_courses
        )
        
        return jsonify({
            'success': True,
            'message': 'Payment approved! Courses added.',
            'courses_added': courses_added
        }), 200
        
    except Exception as e:
        db.session.rollback()
        print(f"❌ Approve error: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500


@payments_bp.route('/admin/payment-requests/<int:request_id>/decline', methods=['POST', 'OPTIONS'])
@admin_required
def decline_payment(request_id):
    if request.method == 'OPTIONS':
        return '', 200
    
    try:
        data = request.get_json()
        admin_notes = data.get('notes', 'Payment verification failed.')
        
        verification = PaymentVerification.query.get(request_id)
        if not verification:
            return jsonify({'error': 'Verification not found'}), 404
        
        verification.status = 'declined'
        verification.admin_notes = admin_notes
        verification.verified_at = datetime.utcnow()
        
        order = Order.query.filter_by(order_id=verification.order_id).first()
        if order:
            order.payment_status = 'failed'
        
        internship_order = InternshipOrder.query.filter_by(order_id=verification.order_id).first()
        if internship_order:
            internship_order.payment_status = 'failed'
        
        db.session.commit()
        
        return jsonify({'success': True, 'message': 'Payment declined.'}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@payments_bp.route('/admin/payment-stats', methods=['GET', 'OPTIONS'])
@admin_required
def get_payment_stats():
    if request.method == 'OPTIONS':
        return '', 200
    
    try:
        pending = PaymentVerification.query.filter_by(status='pending').count()
        approved = PaymentVerification.query.filter_by(status='approved').count()
        declined = PaymentVerification.query.filter_by(status='declined').count()
        
        total_amount = db.session.query(db.func.sum(PaymentVerification.amount)).filter(
            PaymentVerification.status == 'approved'
        ).scalar() or 0
        
        return jsonify({
            'success': True,
            'stats': {
                'pending': pending,
                'approved': approved,
                'declined': declined,
                'total_amount': float(total_amount)
            }
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500