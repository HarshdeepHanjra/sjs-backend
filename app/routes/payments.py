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

payments_bp = Blueprint('payments', __name__)

# Cloudinary configuration
CLOUDINARY_CLOUD_NAME = os.getenv('CLOUDINARY_CLOUD_NAME', 'dxxpeilta')
CLOUDINARY_API_KEY = os.getenv('CLOUDINARY_API_KEY', '375175513582196')
CLOUDINARY_API_SECRET = os.getenv('CLOUDINARY_API_SECRET', '48p-JTyxEEylHjS2733gA6KeTbU')

def init_cloudinary():
    """Initialize Cloudinary if credentials are available"""
    if CLOUDINARY_CLOUD_NAME and CLOUDINARY_API_KEY and CLOUDINARY_API_SECRET:
        cloudinary.config(
            cloud_name=CLOUDINARY_CLOUD_NAME,
            api_key=CLOUDINARY_API_KEY,
            api_secret=CLOUDINARY_API_SECRET,
            secure=True
        )
        print(f"✅ Cloudinary configured with cloud name: {CLOUDINARY_CLOUD_NAME}")
        return True
    print("⚠️ Cloudinary not configured - using local storage")
    return False

CLOUDINARY_ENABLED = init_cloudinary()


# =====================================================
# USER ENDPOINTS (with /api/ prefix)
# =====================================================

# ✅ All routes will be prefixed with /api/payment in blueprint registration
# So these endpoints become: /api/payment/upload-screenshot, etc.

@payments_bp.route('/upload-screenshot', methods=['POST', 'OPTIONS'])
@token_required
def upload_screenshot():
    """Upload payment screenshot (User)"""
    if request.method == 'OPTIONS':
        return '', 200
    
    try:
        if 'screenshot' not in request.files:
            return jsonify({'error': 'No file uploaded'}), 400
        
        file = request.files['screenshot']
        order_id = request.form.get('order_id')
        
        if not order_id:
            return jsonify({'error': 'Order ID is required'}), 400
        
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
        
        if not allowed_file(file.filename):
            return jsonify({'error': 'Invalid file type. Allowed: png, jpg, jpeg, gif, webp'}), 400
        
        screenshot_url = None
        
        # Try Cloudinary first
        if CLOUDINARY_ENABLED:
            try:
                file.seek(0)
                upload_result = cloudinary.uploader.upload(
                    file,
                    folder='sjs-academy/payments',
                    public_id=f"{order_id}_{int(datetime.now().timestamp())}",
                    overwrite=True,
                    resource_type='auto'
                )
                screenshot_url = upload_result['secure_url']
                print(f"✅ Screenshot uploaded to Cloudinary: {screenshot_url}")
            except Exception as e:
                print(f"Cloudinary upload failed: {e}")
                screenshot_url = None
        
        # Fallback to local storage
        if not screenshot_url:
            file.seek(0)
            original_filename = secure_filename(file.filename)
            timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
            filename = f"{order_id}_{timestamp}_{original_filename}"
            upload_dir = os.path.join('uploads', 'screenshots')
            os.makedirs(upload_dir, exist_ok=True)
            filepath = os.path.join(upload_dir, filename)
            file.save(filepath)
            screenshot_url = f"/uploads/screenshots/{filename}"
            print(f"✅ Screenshot saved locally: {filepath}")
        
        # Update order with screenshot URL
        order = Order.query.filter_by(order_id=order_id).first()
        if order:
            order.screenshot_url = screenshot_url
            db.session.commit()
        
        internship_order = InternshipOrder.query.filter_by(order_id=order_id).first()
        if internship_order:
            internship_order.screenshot_url = screenshot_url
            db.session.commit()
        
        return jsonify({
            'success': True,
            'screenshot_url': screenshot_url,
            'message': 'Screenshot uploaded successfully'
        }), 200
        
    except Exception as e:
        print(f"Upload error: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500


@payments_bp.route('/submit-verification', methods=['POST', 'OPTIONS'])
@token_required
def submit_verification():
    """Submit payment verification (User)"""
    if request.method == 'OPTIONS':
        return '', 200
    
    try:
        data = request.get_json()
        order_id = data.get('order_id')
        transaction_id = data.get('transaction_id')
        screenshot_url = data.get('screenshot_url')
        
        if not order_id:
            return jsonify({'error': 'Order ID is required'}), 400
        
        if not transaction_id:
            return jsonify({'error': 'Transaction ID is required'}), 400
        
        if not screenshot_url:
            return jsonify({'error': 'Screenshot is required'}), 400
        
        user = request.user
        
        # Find order
        order = Order.query.filter_by(order_id=order_id, student_id=user['id']).first()
        internship_order = None
        
        if not order:
            internship_order = InternshipOrder.query.filter_by(order_id=order_id, student_id=user['id']).first()
        
        if not order and not internship_order:
            return jsonify({'error': 'Order not found'}), 404
        
        # Check for existing verification
        existing = PaymentVerification.query.filter_by(order_id=order_id).first()
        if existing:
            return jsonify({'error': 'Verification already submitted'}), 400
        
        verification_id = generate_verification_id()
        student = Student.query.get(user['id'])
        
        amount = order.total_amount if order else internship_order.amount
        
        verification = PaymentVerification(
            verification_id=verification_id,
            order_id=order_id,
            student_id=user['id'],
            student_name=student.name if student else user.get('name', 'Student'),
            student_email=student.email if student else user.get('email'),
            amount=amount,
            transaction_id=transaction_id,
            screenshot_url=screenshot_url,
            status='pending',
            created_at=datetime.utcnow()
        )
        
        db.session.add(verification)
        
        if order:
            order.transaction_id = transaction_id
            order.payment_status = 'pending_verification'
        elif internship_order:
            internship_order.transaction_id = transaction_id
            internship_order.payment_status = 'pending_verification'
        
        db.session.commit()
        
        print(f"✅ Verification submitted: {verification_id}")
        
        return jsonify({
            'success': True,
            'message': 'Verification submitted successfully!',
            'verification_id': verification_id
        }), 201
        
    except Exception as e:
        db.session.rollback()
        print(f"Submit error: {e}")
        return jsonify({'error': str(e)}), 500


@payments_bp.route('/status/<verification_id>', methods=['GET', 'OPTIONS'])
@token_required
def get_verification_status(verification_id):
    """Get verification status by ID"""
    if request.method == 'OPTIONS':
        return '', 200
    
    try:
        verification = PaymentVerification.query.filter_by(verification_id=verification_id).first()
        
        if not verification:
            return jsonify({'error': 'Verification not found'}), 404
        
        user = request.user
        if verification.student_id != user['id']:
            return jsonify({'error': 'Unauthorized'}), 403
        
        status_messages = {
            'pending': 'Your payment is being verified. We will notify you within 24 hours.',
            'approved': '✅ Payment verified! Your courses have been activated.',
            'declined': '❌ Payment verification failed. Please contact support.'
        }
        
        return jsonify({
            'success': True,
            'status': verification.status,
            'message': status_messages.get(verification.status, ''),
            'admin_notes': verification.admin_notes,
            'verified_at': verification.verified_at.isoformat() if hasattr(verification, 'verified_at') and verification.verified_at else None
        }), 200
    except Exception as e:
        print(f"Status check error: {e}")
        return jsonify({'error': str(e)}), 500


# =====================================================
# ADMIN ENDPOINTS (with /api/ prefix)
# =====================================================

@payments_bp.route('/admin/payment-requests', methods=['GET', 'OPTIONS'])
@admin_required
def get_payment_requests():
    """Get all pending payment verifications (Admin)"""
    if request.method == 'OPTIONS':
        return '', 200
    
    try:
        verifications = PaymentVerification.query.filter_by(
            status='pending'
        ).order_by(PaymentVerification.created_at.desc()).all()
        
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
                'status': v.status,
                'created_at': v.created_at.isoformat() if v.created_at else None
            })
        
        return jsonify({
            'success': True,
            'verifications': result
        }), 200
    except Exception as e:
        print(f"Error: {e}")
        return jsonify({'error': str(e)}), 500


@payments_bp.route('/admin/payment-requests/<int:request_id>/approve', methods=['POST', 'OPTIONS'])
@admin_required
def approve_payment(request_id):
    """Approve payment verification (Admin)"""
    if request.method == 'OPTIONS':
        return '', 200
    
    try:
        data = request.get_json()
        admin_notes = data.get('notes', 'Payment verified and approved.')
        
        # Get verification record
        verification = PaymentVerification.query.get(request_id)
        if not verification:
            return jsonify({'error': 'Verification not found'}), 404
        
        # Update verification status
        verification.status = 'approved'
        verification.admin_notes = admin_notes
        verification.verified_at = datetime.utcnow()
        
        # Get the order
        order = Order.query.filter_by(order_id=verification.order_id).first()
        if not order:
            return jsonify({'error': 'Order not found'}), 404
        
        # Update order status
        order.payment_status = 'completed'
        order.transaction_id = verification.transaction_id
        
        # Get courses from order
        order_courses = order.courses if isinstance(order.courses, list) else []
        
        print(f"\n{'='*60}")
        print(f"📝 APPROVING PAYMENT - Adding to Enrollment")
        print(f"Order ID: {order.order_id}")
        print(f"Student ID: {verification.student_id}")
        print(f"Student Email: {verification.student_email}")
        print(f"Order Courses: {order_courses}")
        print(f"{'='*60}\n")
        
        # Import models
        from app.models.course import Enrollment, Course
        
        courses_added = []
        
        # For each course in the order, add to enrollments table
        for course_data in order_courses:
            # Get course ID
            if isinstance(course_data, dict):
                course_id = course_data.get('id')
                course_name = course_data.get('name', 'Unknown')
            else:
                course_id = getattr(course_data, 'id', None)
                course_name = getattr(course_data, 'name', 'Unknown')
            
            if course_id:
                print(f"Processing course ID: {course_id} - {course_name}")
                
                # Check if already enrolled
                existing = Enrollment.query.filter_by(
                    student_id=verification.student_id,
                    course_id=course_id
                ).first()
                
                if not existing:
                    # Create enrollment
                    enrollment = Enrollment(
                        student_id=verification.student_id,
                        course_id=course_id,
                        enrolled_at=datetime.utcnow(),
                        status='active',
                        payment_verification_id=verification.verification_id
                    )
                    db.session.add(enrollment)
                    courses_added.append(course_id)
                    print(f"✅ Added to enrollments table: student_id={verification.student_id}, course_id={course_id}")
                    
                    # Update student's course_ids JSON field
                    student = Student.query.get(verification.student_id)
                    if student:
                        if student.course_ids is None:
                            student.course_ids = []
                        if course_id not in student.course_ids:
                            student.course_ids.append(course_id)
                            print(f"✅ Added course {course_id} to student.course_ids")
                    
                    # Update course student count
                    course = Course.query.get(course_id)
                    if course:
                        course.students_enrolled = (course.students_enrolled or 0) + 1
                        db.session.add(course)
                        print(f"✅ Updated course {course_id} students_enrolled to {course.students_enrolled}")
                else:
                    print(f"⚠️ Already enrolled in course {course_id}")
        
        # Commit all changes
        db.session.commit()
        
        # Verify enrollment was added
        verify_enrollments = Enrollment.query.filter_by(
            student_id=verification.student_id
        ).all()
        
        print(f"\n📊 Enrollment Summary:")
        print(f"   Total enrollments for student {verification.student_id}: {len(verify_enrollments)}")
        for enc in verify_enrollments:
            print(f"   - Course ID: {enc.course_id}, Status: {enc.status}")
        
        print(f"\n✅ Payment approved successfully!")
        print(f"   Courses added: {courses_added}")
        print(f"{'='*60}\n")
        
        # Update internship order if exists
        internship_order = InternshipOrder.query.filter_by(order_id=verification.order_id).first()
        if internship_order:
            internship_order.payment_status = 'completed'
            internship_order.status = 'active'
            db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Payment approved successfully! Courses added to student account.',
            'courses_added': courses_added,
            'total_enrollments': len(verify_enrollments)
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
    """Decline payment verification (Admin)"""
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
        
        if hasattr(verification, 'verified_at'):
            verification.verified_at = datetime.utcnow()
        
        # Update order status
        order = Order.query.filter_by(order_id=verification.order_id).first()
        if order:
            order.payment_status = 'failed'
        
        internship_order = InternshipOrder.query.filter_by(order_id=verification.order_id).first()
        if internship_order:
            internship_order.payment_status = 'failed'
        
        db.session.commit()
        
        print(f"✅ Payment declined: {verification.verification_id}")
        
        return jsonify({
            'success': True,
            'message': 'Payment declined.'
        }), 200
    except Exception as e:
        db.session.rollback()
        print(f"Decline error: {e}")
        return jsonify({'error': str(e)}), 500


@payments_bp.route('/admin/payment-stats', methods=['GET', 'OPTIONS'])
@admin_required
def get_payment_stats():
    """Get payment statistics (Admin)"""
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