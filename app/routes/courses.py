from flask import Blueprint, request, jsonify
from app import db
from app.models.course import Course
from app.utils.decorators import token_required, admin_required

courses_bp = Blueprint('courses', __name__)

@courses_bp.route('/courses', methods=['GET', 'OPTIONS'])
def get_courses():
    if request.method == 'OPTIONS':
        return '', 200
    
    try:
        # Get only active courses for public view
        courses = Course.query.filter_by(is_active=True).order_by(Course.id).all()
        
        courses_data = []
        for course in courses:
            courses_data.append({
                'id': course.id,
                'name': course.name,
                'price': float(course.price),
                'duration': course.duration,
                'level': course.level,
                'rating': float(course.rating),
                'students': course.students_enrolled,
                'description': course.description or ''
            })
        
        return jsonify({'courses': courses_data}), 200
    except Exception as e:
        print(f"Error fetching courses: {e}")
        return jsonify({'courses': []}), 200

@courses_bp.route('/courses/<int:course_id>', methods=['GET', 'OPTIONS'])
def get_course_detail(course_id):
    if request.method == 'OPTIONS':
        return '', 200
    
    try:
        course = Course.query.get(course_id)
        
        if not course:
            return jsonify({'error': 'Course not found'}), 404
        
        return jsonify({
            'id': course.id,
            'name': course.name,
            'price': float(course.price),
            'duration': course.duration,
            'level': course.level,
            'rating': float(course.rating),
            'students': course.students_enrolled,
            'description': course.description or '',
            'course_code': course.course_code,
            'is_active': course.is_active,
            'updated_at': course.updated_at.isoformat() if course.updated_at else None,
            # Default values for additional fields (can be customized later)
            'syllabus': [
                'Module 1: Introduction',
                'Module 2: Core Concepts',
                'Module 3: Advanced Topics',
                'Module 4: Practical Projects'
            ],
            'tools': ['Tool 1', 'Tool 2', 'Tool 3'],
            'projects': ['Project 1', 'Project 2', 'Project 3'],
            'benefits': ['Certificate of Completion', 'Lifetime Access', 'Support']
        }), 200
    except Exception as e:
        print(f"Error fetching course detail: {e}")
        return jsonify({'error': str(e)}), 500

@courses_bp.route('/courses/latest-prices', methods=['GET', 'OPTIONS'])
def get_latest_course_prices():
    if request.method == 'OPTIONS':
        return '', 200
    
    try:
        courses = Course.query.filter_by(is_active=True).all()
        
        return jsonify({
            'success': True,
            'courses': [{
                'id': c.id,
                'name': c.name,
                'price': float(c.price),
                'duration': c.duration,
                'is_active': c.is_active
            } for c in courses]
        }), 200
    except Exception as e:
        print(f"Error fetching latest prices: {e}")
        return jsonify({'success': False, 'courses': [], 'error': str(e)}), 500