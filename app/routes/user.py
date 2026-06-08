from datetime import datetime
from flask import Blueprint, request, jsonify
from app import db
from app.models.user import Student, Admin
from app.models.course import Course
from app.utils.decorators import token_required

user_bp = Blueprint('user', __name__)

@user_bp.route('/profile', methods=['GET', 'OPTIONS'])
@token_required
def get_user_profile():
    if request.method == 'OPTIONS':
        return '', 200
    
    try:
        if request.user.get('role') == 'student':
            student = Student.query.get(request.user['id'])
            if not student:
                return jsonify({'error': 'User not found'}), 404
            
            return jsonify({
                'success': True,
                'user': {
                    'id': student.id,
                    'student_id': student.student_id,
                    'name': student.name,
                    'email': student.email,
                    'phone': student.phone or '',
                    'status': student.status,
                    'course_ids': student.course_ids or [],
                    'occupation': student.occupation or '',
                    'company': student.company or '',
                    'skills': student.skills or '',
                    'interests': student.interests or '',
                    'achievements': student.achievements or '',
                    'website': student.website or '',
                    'github': student.github or '',
                    'linkedin': student.linkedin or '',
                    'created_at': student.created_at.isoformat() if student.created_at else None,
                    'updated_at': student.updated_at.isoformat() if student.updated_at else None
                }
            }), 200
        
        return jsonify({'error': 'User not found'}), 404
    except Exception as e:
        print(f"Error in get_user_profile: {e}")
        return jsonify({'error': str(e)}), 500


@user_bp.route('/activity-log', methods=['GET', 'OPTIONS'])
@token_required
def get_activity_log():
    if request.method == 'OPTIONS':
        return '', 200
    
    try:
        # Return sample activity log (you can implement actual logging later)
        activities = [
            {'action': 'Profile updated', 'date': '2024-01-15', 'status': 'success'},
            {'action': 'Course enrolled: Data Science', 'date': '2024-01-10', 'status': 'success'},
            {'action': 'Certificate earned: Python', 'date': '2024-01-05', 'status': 'success'},
        ]
        return jsonify({
            'success': True,
            'activities': activities
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@user_bp.route('/notification-preferences', methods=['PUT', 'OPTIONS'])
@token_required
def update_notification_preferences():
    if request.method == 'OPTIONS':
        return '', 200
    
    try:
        data = request.get_json()
        preferences = data.get('preferences', {})
        
        if request.user.get('role') == 'student':
            student = Student.query.get(request.user['id'])
            if not student:
                return jsonify({'error': 'User not found'}), 404
            
            # Update notification preferences (you may want to add these fields to the Student model)
            # For now, just return success
            db.session.commit()
            
            return jsonify({
                'success': True,
                'message': 'Preferences updated successfully'
            }), 200
        
        return jsonify({'error': 'Invalid user role'}), 400
    except Exception as e:
        db.session.rollback()
        print(f"Error in update_notification_preferences: {e}")
        return jsonify({'error': str(e)}), 500


@user_bp.route('/my-courses', methods=['GET', 'OPTIONS'])
@token_required
def get_my_courses():
    if request.method == 'OPTIONS':
        return '', 200
    
    try:
        user = request.user
        print(f"User from token: {user}")
        
        student = Student.query.get(user['id'])
        
        if not student:
            return jsonify({'error': 'Student not found'}), 404
        
        # Get purchased course IDs
        purchased_ids = student.course_ids or []
        
        # Handle if course_ids is stored as JSON string
        if isinstance(purchased_ids, str):
            import json
            purchased_ids = json.loads(purchased_ids)
        
        print(f"Student {student.name} purchased course IDs: {purchased_ids}")
        
        # If no courses purchased
        if not purchased_ids:
            return jsonify({
                'success': True,
                'courses': []
            }), 200
        
        # Fetch all purchased courses
        courses = Course.query.filter(Course.id.in_(purchased_ids)).all()
        
        print(f"Found {len(courses)} courses for student")
        
        # Format course data
        courses_data = []
        for course in courses:
            courses_data.append({
                'id': course.id,
                'name': course.name,
                'price': float(course.price),
                'duration': course.duration,
                'description': course.description or '',
                'level': course.level,
                'rating': float(course.rating),
                'course_code': course.course_code,
                'students_enrolled': course.students_enrolled
            })
        
        return jsonify({
            'success': True,
            'courses': courses_data
        }), 200
    except Exception as e:
        print(f"Error in get_my_courses: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500


@user_bp.route('/update-profile', methods=['PUT', 'OPTIONS'])
@token_required
def update_user_profile():
    if request.method == 'OPTIONS':
        return '', 200
    
    try:
        data = request.get_json()
        print(f"Received update data: {data}")
        
        if request.user.get('role') == 'student':
            student = Student.query.get(request.user['id'])
            if not student:
                return jsonify({'error': 'User not found'}), 404
            
            # Update all fields
            if 'name' in data:
                student.name = data['name']
            if 'occupation' in data:
                student.occupation = data['occupation']
            if 'company' in data:
                student.company = data['company']
            if 'skills' in data:
                student.skills = data['skills']
            if 'interests' in data:
                student.interests = data['interests']
            if 'achievements' in data:
                student.achievements = data['achievements']
            if 'website' in data:
                student.website = data['website']
            if 'github' in data:
                student.github = data['github']
            if 'linkedin' in data:
                student.linkedin = data['linkedin']
            
            student.updated_at = db.func.now()
            db.session.commit()
            
            # Return all updated data
            return jsonify({
                'success': True,
                'message': 'Profile updated successfully',
                'user': {
                    'id': student.id,
                    'student_id': student.student_id,
                    'name': student.name,
                    'email': student.email,
                    'phone': student.phone or '',
                    'status': student.status,
                    'course_ids': student.course_ids or [],
                    'occupation': student.occupation or '',
                    'company': student.company or '',
                    'skills': student.skills or '',
                    'interests': student.interests or '',
                    'achievements': student.achievements or '',
                    'website': student.website or '',
                    'github': student.github or '',
                    'linkedin': student.linkedin or '',
                    'created_at': student.created_at.isoformat() if student.created_at else None,
                    'updated_at': student.updated_at.isoformat() if student.updated_at else None
                }
            }), 200
        
        return jsonify({'error': 'User not found'}), 404
    except Exception as e:
        db.session.rollback()
        print(f"Error in update_user_profile: {e}")
        return jsonify({'error': str(e)}), 500


@user_bp.route('/refresh-courses', methods=['GET', 'OPTIONS'])
@token_required
def refresh_courses():
    """Force refresh course data from database"""
    if request.method == 'OPTIONS':
        return '', 200
    
    try:
        user = request.user
        student = Student.query.get(user['id'])
        
        if not student:
            return jsonify({'error': 'Student not found'}), 404
        
        purchased_ids = student.course_ids or []
        if isinstance(purchased_ids, str):
            import json
            purchased_ids = json.loads(purchased_ids)
        
        # Get fresh course data from database
        courses = Course.query.filter(Course.id.in_(purchased_ids)).all()
        
        # Update course enrollment counts if needed
        for course in courses:
            if course.students_enrolled is None:
                course.students_enrolled = 0
            db.session.commit()
        
        courses_data = [{
            'id': c.id,
            'name': c.name,
            'price': float(c.price),
            'duration': c.duration,
            'description': c.description or '',
            'level': c.level,
            'rating': float(c.rating),
            'students_enrolled': c.students_enrolled
        } for c in courses]
        
        return jsonify({
            'success': True,
            'courses': courses_data,
            'count': len(courses_data)
        }), 200
    except Exception as e:
        print(f"Error refreshing courses: {e}")
        return jsonify({'error': str(e)}), 500


@user_bp.route('/enrolled-courses', methods=['GET', 'OPTIONS'])
@token_required
def get_enrolled_courses():
    """Get all enrolled courses for the current student"""
    if request.method == 'OPTIONS':
        return '', 200
    
    try:
        user = request.user
        student = Student.query.get(user['id'])
        
        if not student:
            return jsonify({'error': 'Student not found'}), 404
        
        courses = []
        
        # Method 1: Get from enrollments table
        try:
            from app.models.course import Enrollment, Course
            enrollments = Enrollment.query.filter_by(
                student_id=student.id,
                status='active'
            ).all()
            
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
            print(f"✅ Found {len(courses)} courses from enrollments table")
        except Exception as e:
            print(f"Enrollment table error: {e}")
        
        # Method 2: If no courses found, try from student.course_ids
        if len(courses) == 0 and student.course_ids:
            from app.models.course import Course
            for course_id in student.course_ids:
                course = Course.query.get(course_id)
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
                        'enrolled_at': None
                    })
            print(f"✅ Found {len(courses)} courses from student.course_ids")
        
        return jsonify({
            'success': True,
            'courses': courses,
            'count': len(courses)
        }), 200
        
    except Exception as e:
        print(f"Error fetching enrolled courses: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e), 'courses': []}), 500


@user_bp.route('/my-internships', methods=['GET', 'OPTIONS'])
@token_required
def get_my_internships():
    """Get all internships the student is enrolled in"""
    if request.method == 'OPTIONS':
        return '', 200
    
    try:
        user = request.user
        student = Student.query.get(user['id'])
        
        if not student:
            return jsonify({'error': 'Student not found'}), 404
        
        internships = []
        
        # Get from internship_ids JSON field
        if student.internship_ids and len(student.internship_ids) > 0:
            from app.models.internship import Internship
            for internship_id in student.internship_ids:
                internship = Internship.query.get(internship_id)
                if internship:
                    internships.append({
                        'id': internship.id,
                        'internship_id': internship.id,
                        'title': internship.title,
                        'duration': internship.duration,
                        'description': internship.description,
                        'mode': internship.mode,
                        'fee': float(internship.fee) if internship.fee else 0,
                        'status': 'active',
                        'enrolled_at': datetime.utcnow().isoformat()
                    })
        
        # Also get from InternshipOrder table for completed payments
        from app.models.internship import InternshipOrder
        orders = InternshipOrder.query.filter_by(
            student_id=student.id,
            payment_status='completed'
        ).all()
        
        for order in orders:
            from app.models.internship import Internship
            internship = Internship.query.get(order.internship_id)
            if internship:
                # Check if already added
                if not any(i.get('id') == internship.id for i in internships):
                    internships.append({
                        'id': internship.id,
                        'internship_id': internship.id,
                        'title': internship.title,
                        'duration': internship.duration,
                        'description': internship.description,
                        'mode': internship.mode,
                        'fee': float(internship.fee) if internship.fee else 0,
                        'status': order.status or 'active',
                        'enrolled_at': order.created_at.isoformat() if order.created_at else None
                    })
        
        print(f"✅ Found {len(internships)} internships for student {student.id}")
        
        return jsonify({
            'success': True,
            'internships': internships,
            'count': len(internships)
        }), 200
        
    except Exception as e:
        print(f"Error fetching my internships: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e), 'internships': []}), 500