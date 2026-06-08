# from flask import Blueprint, request, jsonify
# from app import db
# from app.models.user import Student, Admin
# from app.models.course import Course
# from app.models.order import Order
# from app.models.payment import PaymentVerification
# from app.models.internship import Internship, InternshipOrder, InternshipEnrollment
# from app.utils.decorators import admin_required
# from datetime import datetime
# import json

# admin_bp = Blueprint('admin', __name__)

# # =====================================================
# # COURSE PAYMENT VERIFICATION FUNCTIONS
# # =====================================================

# @admin_bp.route('/payment-requests', methods=['GET', 'OPTIONS'])
# @admin_required
# def get_admin_payment_requests():
#     if request.method == 'OPTIONS':
#         return '', 200
    
#     try:
#         verifications = PaymentVerification.query.order_by(PaymentVerification.created_at.desc()).all()
        
#         return jsonify({
#             'success': True,
#             'verifications': [v.to_dict() for v in verifications]
#         }), 200
#     except Exception as e:
#         return jsonify({'error': str(e)}), 500

# @admin_bp.route('/payment-requests/<int:request_id>/approve', methods=['POST', 'OPTIONS'])
# @admin_required
# def approve_course_payment(request_id):
#     if request.method == 'OPTIONS':
#         return '', 200
    
#     try:
#         data = request.get_json()
#         verification = PaymentVerification.query.get(request_id)
        
#         if not verification:
#             return jsonify({'error': 'Payment request not found'}), 404
        
#         # Update verification status
#         verification.status = 'approved'
#         verification.admin_notes = data.get('notes', 'Payment approved')
        
#         # Get the order
#         order = Order.query.filter_by(order_id=verification.order_id).first()
        
#         if not order:
#             return jsonify({'error': 'Order not found'}), 404
        
#         order.payment_status = 'completed'
        
#         # Get the student
#         student = Student.query.get(verification.student_id)
        
#         if not student:
#             return jsonify({'error': 'Student not found'}), 404
        
#         # Get current purchased courses
#         purchased_ids = student.course_ids or []
#         if isinstance(purchased_ids, str):
#             import json
#             purchased_ids = json.loads(purchased_ids)
        
#         # Add courses from order
#         courses_added = []
#         order_courses = order.courses
#         if isinstance(order_courses, str):
#             import json
#             order_courses = json.loads(order_courses)
        
#         for course_item in order_courses:
#             course_id = course_item.get('id')
#             if course_id and course_id not in purchased_ids:
#                 purchased_ids.append(course_id)
#                 courses_added.append(course_id)
                
#                 # Update course enrollment count
#                 course_obj = Course.query.get(course_id)
#                 if course_obj:
#                     course_obj.students_enrolled = (course_obj.students_enrolled or 0) + 1
#                     print(f"Updated course {course_obj.name} enrollment to {course_obj.students_enrolled}")
        
#         # Update student's course list
#         student.course_ids = purchased_ids
#         student.updated_at = datetime.utcnow()
        
#         db.session.commit()
        
#         print(f"✅ Payment approved! Added courses {courses_added} to student {student.name}")
#         print(f"Student now has courses: {purchased_ids}")
        
#         return jsonify({
#             'success': True, 
#             'message': 'Payment approved! Courses added to student account.',
#             'courses_added': courses_added,
#             'student_courses': purchased_ids
#         }), 200
        
#     except Exception as e:
#         db.session.rollback()
#         print(f"Error approving payment: {e}")
#         import traceback
#         traceback.print_exc()
#         return jsonify({'error': str(e)}), 500

# @admin_bp.route('/payment-requests/<int:request_id>/decline', methods=['POST', 'OPTIONS'])
# @admin_required
# def decline_course_payment(request_id):
#     if request.method == 'OPTIONS':
#         return '', 200
    
#     try:
#         data = request.get_json()
#         verification = PaymentVerification.query.get(request_id)
        
#         if not verification:
#             return jsonify({'error': 'Payment request not found'}), 404
        
#         verification.status = 'declined'
#         verification.admin_notes = data.get('notes', 'Payment verification failed')
        
#         db.session.commit()
        
#         return jsonify({'success': True, 'message': 'Payment declined!'}), 200
#     except Exception as e:
#         db.session.rollback()
#         return jsonify({'error': str(e)}), 500

# @admin_bp.route('/payment-stats', methods=['GET', 'OPTIONS'])
# @admin_required
# def get_payment_stats():
#     if request.method == 'OPTIONS':
#         return '', 200
    
#     try:
#         pending_count = PaymentVerification.query.filter_by(status='pending').count()
#         approved_count = PaymentVerification.query.filter_by(status='approved').count()
#         declined_count = PaymentVerification.query.filter_by(status='declined').count()
#         total_amount = db.session.query(db.func.sum(PaymentVerification.amount)).filter_by(status='approved').scalar() or 0
        
#         return jsonify({
#             'success': True,
#             'stats': {
#                 'pending': pending_count,
#                 'approved': approved_count,
#                 'declined': declined_count,
#                 'total_amount': float(total_amount)
#             }
#         }), 200
#     except Exception as e:
#         return jsonify({'error': str(e)}), 500

# # =====================================================
# # STUDENT MANAGEMENT FUNCTIONS
# # =====================================================

# @admin_bp.route('/students', methods=['GET', 'OPTIONS'])
# @admin_required
# def get_all_students():
#     if request.method == 'OPTIONS':
#         return '', 200
    
#     try:
#         students = Student.query.all()
#         return jsonify({
#             'success': True,
#             'students': [s.to_dict() for s in students]
#         }), 200
#     except Exception as e:
#         return jsonify({'error': str(e)}), 500

# @admin_bp.route('/orders', methods=['GET', 'OPTIONS'])
# @admin_required
# def get_all_orders():
#     if request.method == 'OPTIONS':
#         return '', 200
    
#     try:
#         orders = Order.query.all()
#         return jsonify({
#             'success': True,
#             'orders': [o.to_dict() for o in orders]
#         }), 200
#     except Exception as e:
#         return jsonify({'error': str(e)}), 500

# # =====================================================
# # COURSE MANAGEMENT FUNCTIONS
# # =====================================================

# @admin_bp.route('/courses', methods=['GET', 'OPTIONS'])
# @admin_required
# def admin_get_courses():
#     if request.method == 'OPTIONS':
#         return '', 200
    
#     try:
#         courses = Course.query.order_by(Course.created_at.desc()).all()
#         return jsonify({
#             'success': True,
#             'courses': [c.to_dict() for c in courses]
#         }), 200
#     except Exception as e:
#         return jsonify({'error': str(e)}), 500

# @admin_bp.route('/courses', methods=['POST', 'OPTIONS'])
# @admin_required
# def admin_add_course():
#     if request.method == 'OPTIONS':
#         return '', 200
    
#     try:
#         data = request.get_json()
        
#         course_code = data.get('course_code') or f"CRS{datetime.now().strftime('%Y%m%d%H%M%S')}"
        
#         new_course = Course(
#             course_code=course_code,
#             name=data.get('name'),
#             price=float(data.get('price')),
#             duration=data.get('duration'),
#             description=data.get('description', ''),
#             level=data.get('level', 'Beginner'),
#             rating=float(data.get('rating', 4.5)),
#             students_enrolled=int(data.get('students_enrolled', 0)),
#             is_active=data.get('is_active', True)
#         )
        
#         db.session.add(new_course)
#         db.session.commit()
        
#         return jsonify({
#             'success': True,
#             'message': 'Course added successfully',
#             'course': new_course.to_dict()
#         }), 201
#     except Exception as e:
#         db.session.rollback()
#         return jsonify({'error': str(e)}), 500

# @admin_bp.route('/courses/<int:course_id>', methods=['PUT', 'OPTIONS'])
# @admin_required
# def admin_update_course(course_id):
#     if request.method == 'OPTIONS':
#         return '', 200
    
#     try:
#         course = Course.query.get(course_id)
#         if not course:
#             return jsonify({'error': 'Course not found'}), 404
        
#         data = request.get_json()
        
#         if 'name' in data:
#             course.name = data['name']
#         if 'price' in data:
#             course.price = float(data['price'])
#         if 'duration' in data:
#             course.duration = data['duration']
#         if 'description' in data:
#             course.description = data['description']
#         if 'level' in data:
#             course.level = data['level']
#         if 'rating' in data:
#             course.rating = float(data['rating'])
#         if 'students_enrolled' in data:
#             course.students_enrolled = int(data['students_enrolled'])
#         if 'is_active' in data:
#             course.is_active = data['is_active']
        
#         course.updated_at = datetime.utcnow()
#         db.session.commit()
        
#         return jsonify({
#             'success': True,
#             'message': 'Course updated successfully',
#             'course': course.to_dict()
#         }), 200
#     except Exception as e:
#         db.session.rollback()
#         return jsonify({'error': str(e)}), 500

# @admin_bp.route('/courses/<int:course_id>', methods=['DELETE', 'OPTIONS'])
# @admin_required
# def admin_delete_course(course_id):
#     if request.method == 'OPTIONS':
#         return '', 200
    
#     try:
#         course = Course.query.get(course_id)
#         if not course:
#             return jsonify({'error': 'Course not found'}), 404
        
#         db.session.delete(course)
#         db.session.commit()
        
#         return jsonify({
#             'success': True,
#             'message': 'Course deleted successfully'
#         }), 200
#     except Exception as e:
#         db.session.rollback()
#         return jsonify({'error': str(e)}), 500

# # =====================================================
# # INTERNSHIP PAYMENT VERIFICATION FUNCTIONS
# # =====================================================

# @admin_bp.route('/internship-payment-requests', methods=['GET', 'OPTIONS'])
# @admin_required
# def get_internship_payment_requests():
#     if request.method == 'OPTIONS':
#         return '', 200
    
#     try:
#         # Get all internship orders with pending verification
#         internship_orders = InternshipOrder.query.filter(
#             InternshipOrder.payment_status.in_(['pending_verification', 'pending'])
#         ).order_by(InternshipOrder.created_at.desc()).all()
        
#         result = []
#         for order in internship_orders:
#             result.append({
#                 'id': order.id,
#                 'order_id': order.order_id,
#                 'student_name': order.student_name,
#                 'student_email': order.student_email,
#                 'internship_title': order.internship_title,
#                 'amount': float(order.amount),
#                 'screenshot_url': order.screenshot_url,
#                 'transaction_id': order.transaction_id,
#                 'status': order.payment_status,
#                 'created_at': order.created_at.isoformat()
#             })
        
#         return jsonify({
#             'success': True,
#             'payments': result
#         }), 200
#     except Exception as e:
#         print(f"Error fetching internship payments: {e}")
#         return jsonify({'error': str(e)}), 500

# @admin_bp.route('/internship-payment-requests/<int:payment_id>/approve', methods=['POST', 'OPTIONS'])
# @admin_required
# def approve_internship_payment_request(payment_id):
#     if request.method == 'OPTIONS':
#         return '', 200
    
#     try:
#         data = request.get_json()
#         internship_order = InternshipOrder.query.get(payment_id)
        
#         if not internship_order:
#             return jsonify({'error': 'Internship order not found'}), 404
        
#         print(f"Processing internship order: {internship_order.order_id}")
#         print(f"Student ID in order: {internship_order.student_id}")
        
#         # Get the student
#         student = Student.query.get(internship_order.student_id)
        
#         if not student:
#             print(f"❌ Student not found with ID: {internship_order.student_id}")
#             return jsonify({'error': f'Student not found with ID: {internship_order.student_id}'}), 404
        
#         # Update order status
#         internship_order.payment_status = 'completed'
#         internship_order.admin_notes = data.get('notes', 'Payment approved')
        
#         # Check if already enrolled
#         from app.models.internship import InternshipEnrollment
        
#         existing = InternshipEnrollment.query.filter_by(
#             student_id=student.id,
#             internship_id=internship_order.internship_id
#         ).first()
        
#         if existing:
#             print(f"Student already enrolled in this internship")
#             return jsonify({'success': True, 'message': 'Student already enrolled!'}), 200
        
#         # Create enrollment
#         enrollment = InternshipEnrollment(
#             student_id=student.id,
#             internship_id=internship_order.internship_id,
#             order_id=internship_order.order_id,
#             status='active'
#         )
#         db.session.add(enrollment)
        
#         # Update internship enrolled count
#         from app.models.internship import Internship
#         internship = Internship.query.get(internship_order.internship_id)
#         if internship:
#             internship.enrolled = (internship.enrolled or 0) + 1
        
#         db.session.commit()
        
#         print(f"✅ Internship approved! Student {student.name} (ID: {student.id}) enrolled in {internship_order.internship_title}")
#         print(f"Enrollment ID: {enrollment.id}")
        
#         return jsonify({
#             'success': True, 
#             'message': 'Internship payment approved! Student enrolled.',
#             'student_id': student.id,
#             'enrollment_id': enrollment.id
#         }), 200
        
#     except Exception as e:
#         db.session.rollback()
#         print(f"Error approving internship payment: {e}")
#         import traceback
#         traceback.print_exc()
#         return jsonify({'error': str(e)}), 500

# @admin_bp.route('/internship-payment-requests/<int:payment_id>/decline', methods=['POST', 'OPTIONS'])
# @admin_required
# def decline_internship_payment_request(payment_id):
#     if request.method == 'OPTIONS':
#         return '', 200
    
#     try:
#         data = request.get_json()
#         internship_order = InternshipOrder.query.get(payment_id)
        
#         if not internship_order:
#             return jsonify({'error': 'Internship order not found'}), 404
        
#         internship_order.payment_status = 'declined'
#         internship_order.admin_notes = data.get('notes', 'Payment declined')
        
#         # Update payment verification if exists
#         verification = PaymentVerification.query.filter_by(order_id=internship_order.order_id).first()
#         if verification:
#             verification.status = 'declined'
#             verification.admin_notes = data.get('notes', 'Payment declined')
        
#         db.session.commit()
        
#         return jsonify({
#             'success': True, 
#             'message': 'Internship payment declined!'
#         }), 200
        
#     except Exception as e:
#         db.session.rollback()
#         print(f"Error declining internship payment: {e}")
#         return jsonify({'error': str(e)}), 500

# # =====================================================
# # INTERNSHIP STATS (Optional)
# # =====================================================

# @admin_bp.route('/internship-payment-stats', methods=['GET', 'OPTIONS'])
# @admin_required
# def get_internship_payment_stats():
#     if request.method == 'OPTIONS':
#         return '', 200
    
#     try:
#         pending_count = InternshipOrder.query.filter(
#             InternshipOrder.payment_status.in_(['pending_verification', 'pending'])
#         ).count()
#         approved_count = InternshipOrder.query.filter_by(payment_status='completed').count()
#         declined_count = InternshipOrder.query.filter_by(payment_status='declined').count()
#         total_amount = db.session.query(db.func.sum(InternshipOrder.amount)).filter_by(payment_status='completed').scalar() or 0
        
#         return jsonify({
#             'success': True,
#             'stats': {
#                 'pending': pending_count,
#                 'approved': approved_count,
#                 'declined': declined_count,
#                 'total_amount': float(total_amount)
#             }
#         }), 200
#     except Exception as e:
#         return jsonify({'error': str(e)}), 500
    
    
# @admin_bp.route('/debug/check-student/<int:student_id>', methods=['GET', 'OPTIONS'])
# @admin_required
# def debug_check_student(student_id):
#     try:
#         student = Student.query.get(student_id)
#         if not student:
#             return jsonify({'error': 'Student not found'}), 404
        
#         from app.models.internship import InternshipEnrollment
#         enrollments = InternshipEnrollment.query.filter_by(student_id=student.id).all()
        
#         return jsonify({
#             'student': {
#                 'id': student.id,
#                 'name': student.name,
#                 'email': student.email,
#                 'course_ids': student.course_ids
#             },
#             'internship_enrollments': [{
#                 'id': e.id,
#                 'internship_id': e.internship_id,
#                 'status': e.status,
#                 'enrolled_at': e.enrolled_at.isoformat()
#             } for e in enrollments]
#         }), 200
#     except Exception as e:
#         return jsonify({'error': str(e)}), 500
    
    
# # =====================================================
# # COURSE MANAGEMENT FUNCTIONS
# # =====================================================

# @admin_bp.route('/courses', methods=['GET', 'OPTIONS'])
# @admin_required
# def admin_get_courses():
#     if request.method == 'OPTIONS':
#         return '', 200
    
#     try:
#         courses = Course.query.order_by(Course.created_at.desc()).all()
        
#         courses_data = []
#         for course in courses:
#             courses_data.append({
#                 'id': course.id,
#                 'course_code': course.course_code,
#                 'name': course.name,
#                 'price': float(course.price),
#                 'duration': course.duration,
#                 'description': course.description or '',
#                 'level': course.level,
#                 'rating': float(course.rating),
#                 'students_enrolled': course.students_enrolled,
#                 'is_active': course.is_active,
#                 'created_at': course.created_at.isoformat() if course.created_at else None,
#                 'updated_at': course.updated_at.isoformat() if course.updated_at else None
#             })
        
#         return jsonify({
#             'success': True,
#             'courses': courses_data
#         }), 200
#     except Exception as e:
#         print(f"Error fetching courses: {e}")
#         return jsonify({'error': str(e)}), 500

# @admin_bp.route('/courses', methods=['POST', 'OPTIONS'])
# @admin_required
# def admin_add_course():
#     if request.method == 'OPTIONS':
#         return '', 200
    
#     try:
#         data = request.get_json()
#         print(f"Received course data: {data}")
        
#         # Validate required fields
#         if not data.get('name'):
#             return jsonify({'error': 'Course name is required'}), 400
#         if not data.get('price'):
#             return jsonify({'error': 'Course price is required'}), 400
#         if not data.get('duration'):
#             return jsonify({'error': 'Course duration is required'}), 400
        
#         # Generate course code
#         course_code = data.get('course_code') or f"CRS{datetime.now().strftime('%Y%m%d%H%M%S')}"
        
#         # Create new course
#         new_course = Course(
#             course_code=course_code,
#             name=data.get('name'),
#             price=float(data.get('price')),
#             duration=data.get('duration'),
#             description=data.get('description', ''),
#             level=data.get('level', 'Beginner'),
#             rating=float(data.get('rating', 4.5)),
#             students_enrolled=int(data.get('students_enrolled', 0)),
#             is_active=data.get('is_active', True)
#         )
        
#         db.session.add(new_course)
#         db.session.commit()
        
#         print(f"✅ Course added successfully: {new_course.name} (ID: {new_course.id})")
        
#         # Dispatch event for frontend
#         from flask import current_app
#         current_app.extensions.get('socketio', None)
        
#         return jsonify({
#             'success': True,
#             'message': 'Course added successfully',
#             'course': {
#                 'id': new_course.id,
#                 'course_code': new_course.course_code,
#                 'name': new_course.name,
#                 'price': float(new_course.price),
#                 'duration': new_course.duration,
#                 'description': new_course.description,
#                 'level': new_course.level,
#                 'rating': float(new_course.rating),
#                 'students_enrolled': new_course.students_enrolled,
#                 'is_active': new_course.is_active
#             }
#         }), 201
        
#     except Exception as e:
#         db.session.rollback()
#         print(f"Error adding course: {e}")
#         import traceback
#         traceback.print_exc()
#         return jsonify({'error': str(e)}), 500

# @admin_bp.route('/courses/<int:course_id>', methods=['PUT', 'OPTIONS'])
# @admin_required
# def admin_update_course(course_id):
#     if request.method == 'OPTIONS':
#         return '', 200
    
#     try:
#         course = Course.query.get(course_id)
#         if not course:
#             return jsonify({'error': 'Course not found'}), 404
        
#         data = request.get_json()
#         print(f"Updating course {course_id} with data: {data}")
        
#         if 'name' in data:
#             course.name = data['name']
#         if 'price' in data:
#             course.price = float(data['price'])
#         if 'duration' in data:
#             course.duration = data['duration']
#         if 'description' in data:
#             course.description = data['description']
#         if 'level' in data:
#             course.level = data['level']
#         if 'rating' in data:
#             course.rating = float(data['rating'])
#         if 'students_enrolled' in data:
#             course.students_enrolled = int(data['students_enrolled'])
#         if 'is_active' in data:
#             course.is_active = data['is_active']
        
#         course.updated_at = datetime.utcnow()
#         db.session.commit()
        
#         print(f"✅ Course updated successfully: {course.name}")
        
#         return jsonify({
#             'success': True,
#             'message': 'Course updated successfully',
#             'course': {
#                 'id': course.id,
#                 'course_code': course.course_code,
#                 'name': course.name,
#                 'price': float(course.price),
#                 'duration': course.duration,
#                 'description': course.description,
#                 'level': course.level,
#                 'rating': float(course.rating),
#                 'students_enrolled': course.students_enrolled,
#                 'is_active': course.is_active
#             }
#         }), 200
#     except Exception as e:
#         db.session.rollback()
#         print(f"Error updating course: {e}")
#         import traceback
#         traceback.print_exc()
#         return jsonify({'error': str(e)}), 500

# @admin_bp.route('/courses/<int:course_id>', methods=['DELETE', 'OPTIONS'])
# @admin_required
# def admin_delete_course(course_id):
#     if request.method == 'OPTIONS':
#         return '', 200
    
#     try:
#         course = Course.query.get(course_id)
#         if not course:
#             return jsonify({'error': 'Course not found'}), 404
        
#         course_name = course.name
#         db.session.delete(course)
#         db.session.commit()
        
#         print(f"✅ Course deleted successfully: {course_name}")
        
#         return jsonify({
#             'success': True,
#             'message': 'Course deleted successfully'
#         }), 200
#     except Exception as e:
#         db.session.rollback()
#         print(f"Error deleting course: {e}")
#         return jsonify({'error': str(e)}), 500



from flask import Blueprint, request, jsonify
from app import db
from app.models.user import Student, Admin
from app.models.course import Course
from app.models.order import Order
from app.models.payment import PaymentVerification
from app.models.internship import Internship, InternshipOrder, InternshipEnrollment
from app.utils.decorators import admin_required
from datetime import datetime
import json

admin_bp = Blueprint('admin', __name__)

# =====================================================
# COURSE MANAGEMENT FUNCTIONS
# =====================================================

@admin_bp.route('/courses', methods=['GET', 'OPTIONS'])
@admin_required
def admin_get_courses():
    if request.method == 'OPTIONS':
        return '', 200
    
    try:
        courses = Course.query.order_by(Course.created_at.desc()).all()
        
        courses_data = []
        for course in courses:
            courses_data.append({
                'id': course.id,
                'course_code': course.course_code,
                'name': course.name,
                'price': float(course.price),
                'duration': course.duration,
                'description': course.description or '',
                'level': course.level,
                'rating': float(course.rating),
                'students_enrolled': course.students_enrolled,
                'is_active': course.is_active,
                'created_at': course.created_at.isoformat() if course.created_at else None,
                'updated_at': course.updated_at.isoformat() if course.updated_at else None
            })
        
        return jsonify({
            'success': True,
            'courses': courses_data
        }), 200
    except Exception as e:
        print(f"Error fetching courses: {e}")
        return jsonify({'error': str(e)}), 500

@admin_bp.route('/courses', methods=['POST', 'OPTIONS'])
@admin_required
def admin_add_course():
    if request.method == 'OPTIONS':
        return '', 200
    
    try:
        data = request.get_json()
        print(f"Received course data: {data}")
        
        # Validate required fields
        if not data.get('name'):
            return jsonify({'error': 'Course name is required'}), 400
        if not data.get('price'):
            return jsonify({'error': 'Course price is required'}), 400
        if not data.get('duration'):
            return jsonify({'error': 'Course duration is required'}), 400
        
        # Generate a simple course code
        import random
        import string
        from datetime import datetime
        
        year = datetime.now().strftime('%Y')
        random_chars = ''.join(random.choices(string.ascii_uppercase + string.digits, k=4))
        course_code = f"CRS{year}{random_chars}"
        
        # Create new course
        new_course = Course(
            course_code=course_code,
            name=data['name'],
            price=float(data['price']),
            duration=data['duration'],
            description=data.get('description', ''),
            level=data.get('level', 'Beginner'),
            rating=float(data.get('rating', 4.5)),
            students_enrolled=int(data.get('students_enrolled', 0)),
            is_active=data.get('is_active', True)
        )
        
        db.session.add(new_course)
        db.session.commit()
        
        print(f"✅ Course added: {new_course.name}")
        
        return jsonify({
            'success': True,
            'message': 'Course added successfully',
            'course': {
                'id': new_course.id,
                'course_code': new_course.course_code,
                'name': new_course.name,
                'price': float(new_course.price),
                'duration': new_course.duration,
                'description': new_course.description,
                'level': new_course.level,
                'rating': float(new_course.rating),
                'students_enrolled': new_course.students_enrolled,
                'is_active': new_course.is_active
            }
        }), 201
        
    except Exception as e:
        db.session.rollback()
        print(f"Error adding course: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500

@admin_bp.route('/courses/<int:course_id>', methods=['PUT', 'OPTIONS'])
@admin_required
def admin_update_course(course_id):
    if request.method == 'OPTIONS':
        return '', 200
    
    try:
        course = Course.query.get(course_id)
        if not course:
            return jsonify({'error': 'Course not found'}), 404
        
        data = request.get_json()
        print(f"Updating course {course_id} with data: {data}")
        
        if 'name' in data:
            course.name = data['name']
        if 'price' in data:
            course.price = float(data['price'])
        if 'duration' in data:
            course.duration = data['duration']
        if 'description' in data:
            course.description = data['description']
        if 'level' in data:
            course.level = data['level']
        if 'rating' in data:
            course.rating = float(data['rating'])
        if 'students_enrolled' in data:
            course.students_enrolled = int(data['students_enrolled'])
        if 'is_active' in data:
            course.is_active = data['is_active']
        
        course.updated_at = datetime.utcnow()
        db.session.commit()
        
        print(f"✅ Course updated successfully: {course.name}")
        
        return jsonify({
            'success': True,
            'message': 'Course updated successfully',
            'course': {
                'id': course.id,
                'course_code': course.course_code,
                'name': course.name,
                'price': float(course.price),
                'duration': course.duration,
                'description': course.description,
                'level': course.level,
                'rating': float(course.rating),
                'students_enrolled': course.students_enrolled,
                'is_active': course.is_active
            }
        }), 200
    except Exception as e:
        db.session.rollback()
        print(f"Error updating course: {e}")
        return jsonify({'error': str(e)}), 500

@admin_bp.route('/courses/<int:course_id>', methods=['DELETE', 'OPTIONS'])
@admin_required
def admin_delete_course(course_id):
    if request.method == 'OPTIONS':
        return '', 200
    
    try:
        course = Course.query.get(course_id)
        if not course:
            return jsonify({'error': 'Course not found'}), 404
        
        course_name = course.name
        
        # Remove course from all students' course_ids
        students = Student.query.all()
        for student in students:
            if student.course_ids and course_id in student.course_ids:
                student.course_ids = [cid for cid in student.course_ids if cid != course_id]
        
        # Delete related records manually to avoid foreign key issues
        from app.models.attendance import Attendance, AttendanceSummary
        from app.models.certificate import Certificate
        
        # Delete attendance records
        Attendance.query.filter_by(course_id=course_id).delete()
        AttendanceSummary.query.filter_by(course_id=course_id).delete()
        
        # Delete certificates
        Certificate.query.filter_by(course_id=course_id).delete()
        
        # Now delete the course
        db.session.delete(course)
        db.session.commit()
        
        print(f"✅ Course deleted successfully: {course_name}")
        
        return jsonify({
            'success': True,
            'message': 'Course deleted successfully'
        }), 200
    except Exception as e:
        db.session.rollback()
        print(f"Error deleting course: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500
    

    
# # =====================================================
# # COURSE PAYMENT VERIFICATION FUNCTIONS
# # ====================================================
# @admin_bp.route('/payment-requests', methods=['GET', 'OPTIONS'])
# @admin_required
# def get_admin_payment_requests():
#     if request.method == 'OPTIONS':
#         return '', 200
    
#     try:
#         verifications = PaymentVerification.query.order_by(PaymentVerification.created_at.desc()).all()
        
#         return jsonify({
#             'success': True,
#             'verifications': [v.to_dict() for v in verifications]
#         }), 200
#     except Exception as e:
#         return jsonify({'error': str(e)}), 500

# @admin_bp.route('/payment-requests/<int:request_id>/approve', methods=['POST', 'OPTIONS'])
# @admin_required
# def approve_course_payment(request_id):
#     if request.method == 'OPTIONS':
#         return '', 200
    
#     try:
#         data = request.get_json()
#         verification = PaymentVerification.query.get(request_id)
        
#         if not verification:
#             return jsonify({'error': 'Payment request not found'}), 404
        
#         verification.status = 'approved'
#         verification.admin_notes = data.get('notes', 'Payment approved')
        
#         order = Order.query.filter_by(order_id=verification.order_id).first()
        
#         if order:
#             order.payment_status = 'completed'
            
#             student = Student.query.get(verification.student_id)
#             if student:
#                 purchased_ids = student.course_ids or []
#                 if isinstance(purchased_ids, str):
#                     purchased_ids = json.loads(purchased_ids)
                
#                 courses_added = []
#                 order_courses = order.courses
#                 if isinstance(order_courses, str):
#                     order_courses = json.loads(order_courses)
                
#                 for course_item in order_courses:
#                     course_id = course_item.get('id')
#                     if course_id and course_id not in purchased_ids:
#                         purchased_ids.append(course_id)
#                         courses_added.append(course_id)
                        
#                         course_obj = Course.query.get(course_id)
#                         if course_obj:
#                             course_obj.students_enrolled = (course_obj.students_enrolled or 0) + 1
                
#                 student.course_ids = purchased_ids
#                 student.updated_at = datetime.utcnow()
        
#         db.session.commit()
        
#         return jsonify({
#             'success': True, 
#             'message': 'Payment approved! Courses added to student account.'
#         }), 200
        
#     except Exception as e:
#         db.session.rollback()
#         print(f"Error approving payment: {e}")
#         return jsonify({'error': str(e)}), 500

# @admin_bp.route('/payment-requests/<int:request_id>/decline', methods=['POST', 'OPTIONS'])
# @admin_required
# def decline_course_payment(request_id):
#     if request.method == 'OPTIONS':
#         return '', 200
    
#     try:
#         data = request.get_json()
#         verification = PaymentVerification.query.get(request_id)
        
#         if not verification:
#             return jsonify({'error': 'Payment request not found'}), 404
        
#         verification.status = 'declined'
#         verification.admin_notes = data.get('notes', 'Payment verification failed')
        
#         db.session.commit()
        
#         return jsonify({'success': True, 'message': 'Payment declined!'}), 200
#     except Exception as e:
#         db.session.rollback()
#         return jsonify({'error': str(e)}), 500

# @admin_bp.route('/payment-stats', methods=['GET', 'OPTIONS'])
# @admin_required
# def get_payment_stats():
#     if request.method == 'OPTIONS':
#         return '', 200
    
#     try:
#         pending_count = PaymentVerification.query.filter_by(status='pending').count()
#         approved_count = PaymentVerification.query.filter_by(status='approved').count()
#         declined_count = PaymentVerification.query.filter_by(status='declined').count()
#         total_amount = db.session.query(db.func.sum(PaymentVerification.amount)).filter_by(status='approved').scalar() or 0
        
#         return jsonify({
#             'success': True,
#             'stats': {
#                 'pending': pending_count,
#                 'approved': approved_count,
#                 'declined': declined_count,
#                 'total_amount': float(total_amount)
#             }
#         }), 200
#     except Exception as e:
#         return jsonify({'error': str(e)}), 500


# =====================================================
# COURSE PAYMENT VERIFICATION FUNCTIONS
# =====================================================
@admin_bp.route('/payment-requests', methods=['GET', 'OPTIONS'])
@admin_required
def get_admin_payment_requests():
    if request.method == 'OPTIONS':
        return '', 200
    
    try:
        verifications = PaymentVerification.query.order_by(PaymentVerification.created_at.desc()).all()
        
        return jsonify({
            'success': True,
            'verifications': [v.to_dict() for v in verifications]
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@admin_bp.route('/payment-requests/<int:request_id>/approve', methods=['POST', 'OPTIONS'])
@admin_required
def approve_course_payment(request_id):
    if request.method == 'OPTIONS':
        return '', 200
    
    try:
        data = request.get_json()
        verification = PaymentVerification.query.get(request_id)
        
        if not verification:
            return jsonify({'error': 'Payment request not found'}), 404
        
        verification.status = 'approved'
        verification.admin_notes = data.get('notes', 'Payment approved')
        verification.verified_at = datetime.utcnow()
        
        order = Order.query.filter_by(order_id=verification.order_id).first()
        
        courses_added = []
        
        if order:
            order.payment_status = 'completed'
            order.transaction_id = verification.transaction_id
            
            student = Student.query.get(verification.student_id)
            if student:
                # Get existing course IDs
                purchased_ids = student.course_ids or []
                if isinstance(purchased_ids, str):
                    purchased_ids = json.loads(purchased_ids)
                
                # Get courses from order
                order_courses = order.courses
                if isinstance(order_courses, str):
                    order_courses = json.loads(order_courses)
                
                # ✅ Import Enrollment model
                from app.models.course import Enrollment, Course
                
                for course_item in order_courses:
                    course_id = course_item.get('id')
                    course_name = course_item.get('name', 'Unknown')
                    
                    if course_id:
                        # ✅ Add to enrollments table
                        existing_enrollment = Enrollment.query.filter_by(
                            student_id=verification.student_id,
                            course_id=course_id
                        ).first()
                        
                        if not existing_enrollment:
                            enrollment = Enrollment(
                                student_id=verification.student_id,
                                course_id=course_id,
                                enrolled_at=datetime.utcnow(),
                                status='active',
                                payment_verification_id=verification.verification_id
                            )
                            db.session.add(enrollment)
                            print(f"✅ Added to enrollments table: student_id={verification.student_id}, course_id={course_id}")
                        
                        # ✅ Add to student.course_ids JSON
                        if course_id not in purchased_ids:
                            purchased_ids.append(course_id)
                            courses_added.append(course_id)
                            print(f"✅ Added course {course_id} to student.course_ids")
                        
                        # ✅ Update course students_enrolled count
                        course_obj = Course.query.get(course_id)
                        if course_obj:
                            course_obj.students_enrolled = (course_obj.students_enrolled or 0) + 1
                            print(f"✅ Updated course {course_id} students_enrolled to {course_obj.students_enrolled}")
                
                # Update student's course_ids
                student.course_ids = purchased_ids
                student.updated_at = datetime.utcnow()
        
        db.session.commit()
        
        print(f"\n✅ Payment approved for student {verification.student_id}")
        print(f"   Courses added: {courses_added}")
        
        return jsonify({
            'success': True, 
            'message': 'Payment approved! Courses added to student account.',
            'courses_added': courses_added
        }), 200
        
    except Exception as e:
        db.session.rollback()
        print(f"Error approving payment: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500


@admin_bp.route('/payment-requests/<int:request_id>/decline', methods=['POST', 'OPTIONS'])
@admin_required
def decline_course_payment(request_id):
    if request.method == 'OPTIONS':
        return '', 200
    
    try:
        data = request.get_json()
        verification = PaymentVerification.query.get(request_id)
        
        if not verification:
            return jsonify({'error': 'Payment request not found'}), 404
        
        verification.status = 'declined'
        verification.admin_notes = data.get('notes', 'Payment verification failed')
        verification.verified_at = datetime.utcnow()
        
        db.session.commit()
        
        return jsonify({'success': True, 'message': 'Payment declined!'}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@admin_bp.route('/payment-stats', methods=['GET', 'OPTIONS'])
@admin_required
def get_payment_stats():
    if request.method == 'OPTIONS':
        return '', 200
    
    try:
        pending_count = PaymentVerification.query.filter_by(status='pending').count()
        approved_count = PaymentVerification.query.filter_by(status='approved').count()
        declined_count = PaymentVerification.query.filter_by(status='declined').count()
        total_amount = db.session.query(db.func.sum(PaymentVerification.amount)).filter_by(status='approved').scalar() or 0
        
        return jsonify({
            'success': True,
            'stats': {
                'pending': pending_count,
                'approved': approved_count,
                'declined': declined_count,
                'total_amount': float(total_amount)
            }
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# =====================================================
# DEBUG ENDPOINT - Check Enrollments
# =====================================================
@admin_bp.route('/debug/check-enrollments/<int:student_id>', methods=['GET'])
@admin_required
def debug_check_enrollments(student_id):
    """Debug endpoint to check student enrollments"""
    try:
        from app.models.course import Enrollment, Course
        
        student = Student.query.get(student_id)
        if not student:
            return jsonify({'error': 'Student not found'}), 404
        
        enrollments = Enrollment.query.filter_by(student_id=student_id).all()
        
        enrollment_data = []
        for enc in enrollments:
            course = Course.query.get(enc.course_id)
            enrollment_data.append({
                'id': enc.id,
                'student_id': enc.student_id,
                'course_id': enc.course_id,
                'course_name': course.name if course else 'Unknown',
                'enrolled_at': enc.enrolled_at.isoformat() if enc.enrolled_at else None,
                'status': enc.status,
                'payment_verification_id': enc.payment_verification_id
            })
        
        return jsonify({
            'student_id': student_id,
            'student_name': student.name,
            'student_email': student.email,
            'course_ids_from_json': student.course_ids or [],
            'enrollments_from_table': enrollment_data,
            'total_enrollments': len(enrollment_data)
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# =====================================================
# STUDENT AND ORDER MANAGEMENT
# =====================================================

@admin_bp.route('/students', methods=['GET', 'OPTIONS'])
@admin_required
def get_all_students():
    if request.method == 'OPTIONS':
        return '', 200
    
    try:
        students = Student.query.all()
        return jsonify({
            'success': True,
            'students': [s.to_dict() for s in students]
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@admin_bp.route('/orders', methods=['GET', 'OPTIONS'])
@admin_required
def get_all_orders():
    if request.method == 'OPTIONS':
        return '', 200
    
    try:
        orders = Order.query.all()
        return jsonify({
            'success': True,
            'orders': [o.to_dict() for o in orders]
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# =====================================================
# INTERNSHIP PAYMENT FUNCTIONS
# =====================================================

@admin_bp.route('/internship-payment-requests', methods=['GET', 'OPTIONS'])
@admin_required
def get_internship_payment_requests():
    if request.method == 'OPTIONS':
        return '', 200
    
    try:
        internship_orders = InternshipOrder.query.filter(
            InternshipOrder.payment_status.in_(['pending_verification', 'pending'])
        ).order_by(InternshipOrder.created_at.desc()).all()
        
        result = []
        for order in internship_orders:
            result.append({
                'id': order.id,
                'order_id': order.order_id,
                'student_name': order.student_name,
                'student_email': order.student_email,
                'internship_title': order.internship_title,
                'amount': float(order.amount),
                'screenshot_url': order.screenshot_url,
                'transaction_id': order.transaction_id,
                'status': order.payment_status,
                'created_at': order.created_at.isoformat()
            })
        
        return jsonify({
            'success': True,
            'payments': result
        }), 200
    except Exception as e:
        print(f"Error fetching internship payments: {e}")
        return jsonify({'error': str(e)}), 500

@admin_bp.route('/internship-payment-requests/<int:payment_id>/approve', methods=['POST', 'OPTIONS'])
@admin_required
def approve_internship_payment_request(payment_id):
    if request.method == 'OPTIONS':
        return '', 200
    
    try:
        data = request.get_json()
        internship_order = InternshipOrder.query.get(payment_id)
        
        if not internship_order:
            return jsonify({'error': 'Internship order not found'}), 404
        
        internship_order.payment_status = 'completed'
        internship_order.admin_notes = data.get('notes', 'Payment approved')
        
        existing = InternshipEnrollment.query.filter_by(
            student_id=internship_order.student_id,
            internship_id=internship_order.internship_id
        ).first()
        
        if not existing:
            enrollment = InternshipEnrollment(
                student_id=internship_order.student_id,
                internship_id=internship_order.internship_id,
                order_id=internship_order.order_id,
                status='active'
            )
            db.session.add(enrollment)
            
            internship = Internship.query.get(internship_order.internship_id)
            if internship:
                internship.enrolled = (internship.enrolled or 0) + 1
        
        db.session.commit()
        
        return jsonify({
            'success': True, 
            'message': 'Internship payment approved! Student enrolled.'
        }), 200
        
    except Exception as e:
        db.session.rollback()
        print(f"Error approving internship payment: {e}")
        return jsonify({'error': str(e)}), 500

@admin_bp.route('/internship-payment-requests/<int:payment_id>/decline', methods=['POST', 'OPTIONS'])
@admin_required
def decline_internship_payment_request(payment_id):
    if request.method == 'OPTIONS':
        return '', 200
    
    try:
        data = request.get_json()
        internship_order = InternshipOrder.query.get(payment_id)
        
        if not internship_order:
            return jsonify({'error': 'Internship order not found'}), 404
        
        internship_order.payment_status = 'declined'
        internship_order.admin_notes = data.get('notes', 'Payment declined')
        
        db.session.commit()
        
        return jsonify({
            'success': True, 
            'message': 'Internship payment declined!'
        }), 200
        
    except Exception as e:
        db.session.rollback()
        print(f"Error declining internship payment: {e}")
        return jsonify({'error': str(e)}), 500