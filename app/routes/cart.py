from flask import Blueprint, request, jsonify, make_response
from app import db
from app.models.user import Student
from app.models.course import Course, Enrollment
from app.models.order import Order
from app.utils.helpers import generate_order_id, verify_token
from app.utils.decorators import token_required
import json
import os

cart_bp = Blueprint('cart', __name__)

# ✅ Get frontend URL from environment
FRONTEND_URL = os.getenv('FRONTEND_URL', 'https://sjs-frontend-delta.vercel.app')
ALLOWED_ORIGINS = [
    FRONTEND_URL,
    'http://localhost:3000',
    'http://localhost:5173',
    'https://sjs-frontend-delta.vercel.app'
]

# Add CORS headers helper
def add_cors_headers(response):
    origin = request.headers.get('Origin', '')
    if origin in ALLOWED_ORIGINS:
        response.headers.add('Access-Control-Allow-Origin', origin)
    else:
        response.headers.add('Access-Control-Allow-Origin', ALLOWED_ORIGINS[0])
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
    response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS')
    response.headers.add('Access-Control-Allow-Credentials', 'true')
    return response


@cart_bp.route('/create-order', methods=['POST', 'OPTIONS'])
@cart_bp.route('/create-order/', methods=['POST', 'OPTIONS'])
@token_required
def create_order():
    if request.method == 'OPTIONS':
        response = make_response()
        return add_cors_headers(response)
    
    try:
        data = request.get_json()
        courses = data.get('courses', [])
        total_amount = data.get('total_amount', 0)
        
        user = request.user
        student = Student.query.get(user['id'])
        
        if not student:
            return jsonify({'error': 'Student not found'}), 404
        
        # Store courses with their IDs
        order_courses = []
        for course in courses:
            order_courses.append({
                'id': course.get('id'),
                'name': course.get('name'),
                'price': course.get('price'),
                'quantity': course.get('quantity', 1)
            })
        
        order_id = generate_order_id()
        
        new_order = Order(
            order_id=order_id,
            student_id=student.id,
            student_name=student.name,
            student_email=student.email,
            total_amount=total_amount,
            courses=order_courses,  # Store as JSON
            payment_status='pending'
        )
        
        db.session.add(new_order)
        db.session.commit()
        
        response = jsonify({
            'success': True,
            'order_id': order_id,
            'total_amount': total_amount,
            'courses': order_courses
        })
        return add_cors_headers(response), 200
        
    except Exception as e:
        db.session.rollback()
        print(f"Create order error: {e}")
        import traceback
        traceback.print_exc()
        response = jsonify({'error': str(e)})
        return add_cors_headers(response), 500


@cart_bp.route('/my-courses', methods=['OPTIONS', 'GET'])
@cart_bp.route('/my-courses/', methods=['OPTIONS', 'GET'])
@token_required
def get_my_courses():
    """Get all enrolled courses for the current student"""
    if request.method == 'OPTIONS':
        response = make_response()
        return add_cors_headers(response)
    
    try:
        user = request.user
        student = Student.query.get(user['id'])
        
        if not student:
            response = jsonify({'success': True, 'courses': [], 'count': 0})
            return add_cors_headers(response), 200
        
        # Get enrolled courses from Enrollment table
        enrollments = Enrollment.query.filter_by(
            student_id=student.id,
            status='active'
        ).all()
        
        courses = []
        for enrollment in enrollments:
            course = Course.query.get(enrollment.course_id)
            if course and course.is_active:
                courses.append({
                    'id': course.id,
                    'name': course.name or course.title,
                    'title': course.title,
                    'duration': course.duration,
                    'price': float(course.price) if course.price else 0,
                    'description': course.description or '',
                    'level': course.level,
                    'rating': float(course.rating) if course.rating else 4.5,
                    'enrolled_at': enrollment.enrolled_at.isoformat() if enrollment.enrolled_at else None
                })
        
        response = jsonify({
            'success': True,
            'courses': courses,
            'count': len(courses)
        })
        return add_cors_headers(response), 200
        
    except Exception as e:
        print(f"Error in get_my_courses: {e}")
        import traceback
        traceback.print_exc()
        response = jsonify({'error': str(e), 'courses': [], 'count': 0})
        return add_cors_headers(response), 500


@cart_bp.route('/latest-prices', methods=['OPTIONS', 'GET'])
@cart_bp.route('/latest-prices/', methods=['OPTIONS', 'GET'])
@token_required
def get_latest_prices():
    """Get latest prices for courses in cart"""
    if request.method == 'OPTIONS':
        response = make_response()
        return add_cors_headers(response)
    
    try:
        courses = Course.query.filter_by(is_active=True).all()
        
        courses_data = []
        for course in courses:
            courses_data.append({
                'id': course.id,
                'name': course.name,
                'price': float(course.price) if course.price else 0,
                'duration': course.duration
            })
        
        response = jsonify({
            'success': True,
            'courses': courses_data
        })
        return add_cors_headers(response), 200
        
    except Exception as e:
        print(f"Error in get_latest_prices: {e}")
        response = jsonify({'error': str(e), 'courses': []})
        return add_cors_headers(response), 500


@cart_bp.route('/verify-payment', methods=['POST', 'OPTIONS'])
@cart_bp.route('/verify-payment/', methods=['POST', 'OPTIONS'])
@token_required
def verify_payment():
    """Verify payment (for instant access)"""
    if request.method == 'OPTIONS':
        response = make_response()
        return add_cors_headers(response)
    
    try:
        data = request.get_json()
        order_id = data.get('order_id')
        payment_method = data.get('payment_method', 'upi')
        
        if not order_id:
            return jsonify({'error': 'Order ID is required'}), 400
        
        order = Order.query.filter_by(order_id=order_id).first()
        if not order:
            return jsonify({'error': 'Order not found'}), 404
        
        # For demo purposes, auto-approve for testing
        # In production, this should check actual payment status
        order.payment_status = 'completed'
        db.session.commit()
        
        # Add courses to student's enrollment
        student = Student.query.get(order.student_id)
        order_courses = order.courses if isinstance(order.courses, list) else []
        
        for course_data in order_courses:
            course_id = course_data.get('id')
            if course_id:
                existing = Enrollment.query.filter_by(
                    student_id=student.id,
                    course_id=course_id
                ).first()
                if not existing:
                    enrollment = Enrollment(
                        student_id=student.id,
                        course_id=course_id,
                        status='active'
                    )
                    db.session.add(enrollment)
                    
                    if student.course_ids is None:
                        student.course_ids = []
                    if course_id not in student.course_ids:
                        student.course_ids.append(course_id)
        
        db.session.commit()
        
        response = jsonify({
            'success': True,
            'message': 'Payment verified successfully!'
        })
        return add_cors_headers(response), 200
        
    except Exception as e:
        db.session.rollback()
        print(f"Verify payment error: {e}")
        response = jsonify({'error': str(e)})
        return add_cors_headers(response), 500