# from flask import Blueprint, request, jsonify, make_response
# from app import db
# from app.models.user import Student
# from app.models.course import Course
# from app.models.order import Order
# from app.utils.helpers import generate_order_id, verify_token
# from app.utils.decorators import token_required
# import json

# cart_bp = Blueprint('cart', __name__)

# # Add CORS headers helper
# def add_cors_headers(response):
#     response.headers.add('Access-Control-Allow-Origin', 'http://localhost:3000')
#     response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
#     response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS')
#     response.headers.add('Access-Control-Allow-Credentials', 'true')
#     return response

# @cart_bp.route('/create-order', methods=['OPTIONS', 'POST'])
# def create_order():
#     # Handle preflight OPTIONS request
#     if request.method == 'OPTIONS':
#         response = make_response()
#         return add_cors_headers(response)
    
#     try:
#         auth_header = request.headers.get('Authorization')
#         if not auth_header:
#             return add_cors_headers(jsonify({'error': 'No token provided'})), 401
        
#         token = auth_header.replace('Bearer ', '')
#         payload = verify_token(token)
        
#         if not payload:
#             return add_cors_headers(jsonify({'error': 'Invalid token'})), 401
        
#         data = request.get_json()
#         courses = data.get('courses', [])
#         total_amount = data.get('total_amount', 0)
        
#         student = Student.query.get(payload['id'])
        
#         if not student:
#             return add_cors_headers(jsonify({'error': 'Student not found'})), 404
        
#         order_id = generate_order_id()
        
#         new_order = Order(
#             order_id=order_id,
#             student_id=payload['id'],
#             student_name=student.name,
#             student_email=student.email,
#             total_amount=total_amount,
#             courses=courses,
#             payment_status='pending'
#         )
        
#         db.session.add(new_order)
#         db.session.commit()
        
#         response = jsonify({
#             'success': True, 
#             'order_id': order_id, 
#             'total_amount': total_amount, 
#             'courses': courses
#         })
#         return add_cors_headers(response), 200
        
#     except Exception as e:
#         db.session.rollback()
#         response = jsonify({'error': str(e)})
#         return add_cors_headers(response), 500

# @cart_bp.route('/my-courses', methods=['OPTIONS', 'GET'])
# @token_required
# def get_my_courses():
#     if request.method == 'OPTIONS':
#         response = make_response()
#         return add_cors_headers(response)
    
#     try:
#         user = request.user
#         student = Student.query.get(user['id'])
        
#         if not student or not student.course_ids:
#             response = jsonify({'courses': []})
#             return add_cors_headers(response), 200
        
#         purchased_ids = student.course_ids
#         courses = Course.query.filter(Course.id.in_(purchased_ids), Course.is_active == True).all()
        
#         response = jsonify({
#             'courses': [{
#                 'id': c.id,
#                 'name': c.name,
#                 'duration': c.duration,
#                 'price': float(c.price),
#                 'description': c.description or ''
#             } for c in courses]
#         })
#         return add_cors_headers(response), 200
        
#     except Exception as e:
#         response = jsonify({'error': str(e)})
#         return add_cors_headers(response), 500


from flask import Blueprint, request, jsonify, make_response
from app import db
from app.models.user import Student
from app.models.course import Course, Enrollment
from app.models.order import Order
from app.utils.helpers import generate_order_id, verify_token
from app.utils.decorators import token_required
import json

cart_bp = Blueprint('cart', __name__)

# Add CORS headers helper
def add_cors_headers(response):
    response.headers.add('Access-Control-Allow-Origin', 'http://localhost:3000')
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
    response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS')
    response.headers.add('Access-Control-Allow-Credentials', 'true')
    return response


@cart_bp.route('/create-order', methods=['POST', 'OPTIONS'])
@token_required
def create_order():
    if request.method == 'OPTIONS':
        return '', 200
    
    try:
        data = request.get_json()
        courses = data.get('courses', [])
        total_amount = data.get('total_amount', 0)
        
        user = request.user
        student = Student.query.get(user['id'])
        
        if not student:
            return jsonify({'error': 'Student not found'}), 404
        
        # ✅ Store courses with their IDs
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
        
        return jsonify({
            'success': True,
            'order_id': order_id,
            'total_amount': total_amount,
            'courses': order_courses
        }), 200
        
    except Exception as e:
        db.session.rollback()
        print(f"Create order error: {e}")
        return jsonify({'error': str(e)}), 500


@cart_bp.route('/my-courses', methods=['OPTIONS', 'GET'])
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
            response = jsonify({'courses': []})
            return add_cors_headers(response), 200
        
        # ✅ FIXED: Get enrolled courses from Enrollment table
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
                    'price': float(course.price),
                    'description': course.description or '',
                    'level': course.level,
                    'rating': float(course.rating),
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
        response = jsonify({'error': str(e), 'courses': []})
        return add_cors_headers(response), 500