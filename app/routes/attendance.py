from flask import Blueprint, request, jsonify
from app import db
from app.models.user import Student, Admin
from app.models.course import Course
from app.models.attendance import Attendance, AttendanceSummary
from app.utils.decorators import admin_required, student_required
from datetime import datetime, timedelta
import json

# Change blueprint name to 'attendance_routes' to avoid conflict
attendance_bp = Blueprint('attendance_routes', __name__)

def update_attendance_summary(student_id, course_id, date_obj):
    """Update attendance summary for a student"""
    # Get first day of the month
    start_date = date_obj.replace(day=1)
    # Get last day of the month
    if date_obj.month == 12:
        end_date = date_obj.replace(year=date_obj.year + 1, month=1, day=1)
    else:
        end_date = date_obj.replace(month=date_obj.month + 1, day=1)
    
    # Get all attendances for this month
    attendances = Attendance.query.filter(
        Attendance.student_id == student_id,
        Attendance.course_id == course_id,
        Attendance.date >= start_date,
        Attendance.date < end_date
    ).all()
    
    total = len(attendances)
    present = sum(1 for a in attendances if a.status == 'present')
    absent = sum(1 for a in attendances if a.status == 'absent')
    late = sum(1 for a in attendances if a.status == 'late')
    percentage = (present / total * 100) if total > 0 else 0
    
    # Update or create summary
    summary = AttendanceSummary.query.filter_by(
        student_id=student_id,
        course_id=course_id,
        month=start_date
    ).first()
    
    if summary:
        summary.total_classes = total
        summary.present_count = present
        summary.absent_count = absent
        summary.late_count = late
        summary.percentage = percentage
        summary.updated_at = datetime.utcnow()
    else:
        summary = AttendanceSummary(
            student_id=student_id,
            course_id=course_id,
            month=start_date,
            total_classes=total,
            present_count=present,
            absent_count=absent,
            late_count=late,
            percentage=percentage
        )
        db.session.add(summary)
    
    db.session.commit()

# ✅ Routes with /api/ prefix removed (will be added by blueprint registration)
# The blueprint will be registered with url_prefix='/api' or similar

@attendance_bp.route('/admin/attendance/courses', methods=['GET', 'OPTIONS'])
@admin_required
def get_attendance_courses():
    """Get all courses for attendance marking"""
    if request.method == 'OPTIONS':
        return '', 200
    
    try:
        from app.models.course import Course
        courses = Course.query.filter_by(is_active=True).all()
        
        return jsonify({
            'success': True,
            'courses': [{
                'id': c.id,
                'name': c.name,
                'duration': c.duration,
                'students_enrolled': c.students_enrolled
            } for c in courses]
        }), 200
    except Exception as e:
        print(f"Error fetching courses: {e}")
        return jsonify({'error': str(e)}), 500


@attendance_bp.route('/admin/attendance/courses/<int:course_id>/students', methods=['GET', 'OPTIONS'])
@admin_required
def get_course_students_for_attendance(course_id):
    if request.method == 'OPTIONS':
        return '', 200
    
    try:
        # Get students who have purchased this course
        students = Student.query.all()
        
        # Filter students who have this course in their course_ids
        enrolled_students = []
        for student in students:
            course_ids = student.course_ids or []
            if isinstance(course_ids, str):
                course_ids = json.loads(course_ids)
            
            if course_id in course_ids:
                enrolled_students.append({
                    'id': student.id,
                    'name': student.name,
                    'email': student.email,
                    'student_id': student.student_id
                })
        
        return jsonify({
            'success': True,
            'students': enrolled_students
        }), 200
    except Exception as e:
        print(f"Error fetching students: {e}")
        return jsonify({'error': str(e)}), 500


@attendance_bp.route('/admin/attendance/course/<int:course_id>/date/<date_str>', methods=['GET', 'OPTIONS'])
@admin_required
def get_attendance_by_date(course_id, date_str):
    if request.method == 'OPTIONS':
        return '', 200
    
    try:
        date_obj = datetime.strptime(date_str, '%Y-%m-%d').date()
        
        attendances = Attendance.query.filter_by(
            course_id=course_id,
            date=date_obj
        ).all()
        
        return jsonify({
            'success': True,
            'attendances': [{
                'student_id': a.student_id,
                'student_name': a.student.name,
                'status': a.status,
                'remarks': a.remarks
            } for a in attendances]
        }), 200
    except Exception as e:
        print(f"Error getting attendance: {e}")
        return jsonify({'error': str(e)}), 500


@attendance_bp.route('/admin/attendance/mark', methods=['POST', 'OPTIONS'])
@admin_required
def mark_attendance():
    if request.method == 'OPTIONS':
        return '', 200
    
    try:
        data = request.get_json()
        course_id = data.get('course_id')
        date_str = data.get('date')
        attendances_data = data.get('attendances', [])
        
        if not course_id:
            return jsonify({'error': 'Course ID required'}), 400
        
        if not date_str:
            return jsonify({'error': 'Date required'}), 400
        
        date_obj = datetime.strptime(date_str, '%Y-%m-%d').date()
        admin_id = request.user.get('id', 1)
        
        marked_count = 0
        errors = []
        
        for att in attendances_data:
            student_id = att.get('student_id')
            status = att.get('status', 'present')
            remarks = att.get('remarks', '')
            
            if not student_id:
                errors.append(f"Missing student_id for attendance entry")
                continue
            
            try:
                # Check if attendance already exists for this date
                existing = Attendance.query.filter_by(
                    student_id=student_id,
                    course_id=course_id,
                    date=date_obj
                ).first()
                
                if existing:
                    existing.status = status
                    existing.remarks = remarks
                    existing.marked_by = admin_id
                    existing.updated_at = datetime.utcnow()
                else:
                    new_attendance = Attendance(
                        student_id=student_id,
                        course_id=course_id,
                        date=date_obj,
                        status=status,
                        remarks=remarks,
                        marked_by=admin_id
                    )
                    db.session.add(new_attendance)
                
                # Update summary for the month
                update_attendance_summary(student_id, course_id, date_obj)
                marked_count += 1
                
            except Exception as e:
                errors.append(f"Error for student {student_id}: {str(e)}")
        
        db.session.commit()
        
        if errors:
            return jsonify({
                'success': True,
                'message': f'Attendance marked for {marked_count} students, but had errors: {errors}',
                'date': date_str,
                'errors': errors
            }), 200
        else:
            return jsonify({
                'success': True,
                'message': f'Attendance marked for {marked_count} students',
                'date': date_str
            }), 200
            
    except Exception as e:
        db.session.rollback()
        print(f"Error marking attendance: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500


@attendance_bp.route('/admin/attendance/summary/<int:course_id>', methods=['GET', 'OPTIONS'])
@admin_required
def get_attendance_summary(course_id):
    if request.method == 'OPTIONS':
        return '', 200
    
    try:
        # Get students who have this course
        students = Student.query.all()
        
        summaries = []
        for student in students:
            course_ids = student.course_ids or []
            if isinstance(course_ids, str):
                course_ids = json.loads(course_ids)
            
            if course_id in course_ids:
                summary = AttendanceSummary.query.filter_by(
                    student_id=student.id,
                    course_id=course_id
                ).order_by(AttendanceSummary.month.desc()).first()
                
                summaries.append({
                    'student_id': student.id,
                    'student_name': student.name,
                    'student_email': student.email,
                    'total_classes': summary.total_classes if summary else 0,
                    'present': summary.present_count if summary else 0,
                    'absent': summary.absent_count if summary else 0,
                    'late': summary.late_count if summary else 0,
                    'percentage': round(summary.percentage, 2) if summary else 0
                })
        
        return jsonify({
            'success': True,
            'summaries': summaries
        }), 200
    except Exception as e:
        print(f"Error getting summary: {e}")
        return jsonify({'error': str(e)}), 500


@attendance_bp.route('/student/attendance/my-attendance', methods=['GET', 'OPTIONS'])
@student_required
def get_my_attendance():
    if request.method == 'OPTIONS':
        return '', 200
    
    try:
        student_id = request.user['id']
        
        attendances = Attendance.query.filter_by(student_id=student_id).order_by(Attendance.date.desc()).all()
        summaries = AttendanceSummary.query.filter_by(student_id=student_id).all()
        
        course_summaries = {}
        for summary in summaries:
            course = Course.query.get(summary.course_id)
            if course:
                course_summaries[course.name] = {
                    'course_id': summary.course_id,
                    'course_name': course.name,
                    'total_classes': summary.total_classes,
                    'present': summary.present_count,
                    'absent': summary.absent_count,
                    'late': summary.late_count,
                    'percentage': round(summary.percentage, 2)
                }
        
        total_present = sum(s.present_count for s in summaries)
        total_classes = sum(s.total_classes for s in summaries)
        overall_percentage = round((total_present / total_classes * 100), 2) if total_classes > 0 else 0
        
        return jsonify({
            'success': True,
            'attendances': [{
                'id': a.id,
                'date': a.date.strftime('%Y-%m-%d'),
                'status': a.status,
                'remarks': a.remarks,
                'course_name': a.course.name if a.course else 'Unknown'
            } for a in attendances],
            'course_summaries': course_summaries,
            'overall': {
                'total_present': total_present,
                'total_classes': total_classes,
                'percentage': overall_percentage
            }
        }), 200
    except Exception as e:
        print(f"Error getting my attendance: {e}")
        return jsonify({'error': str(e)}), 500


@attendance_bp.route('/student/attendance/monthly', methods=['GET', 'OPTIONS'])
@student_required
def get_monthly_attendance():
    if request.method == 'OPTIONS':
        return '', 200
    
    try:
        student_id = request.user['id']
        
        summaries = AttendanceSummary.query.filter_by(student_id=student_id).order_by(AttendanceSummary.month.desc()).all()
        
        monthly_data = []
        for summary in summaries:
            course = Course.query.get(summary.course_id)
            monthly_data.append({
                'month': summary.month.strftime('%B %Y'),
                'course_name': course.name if course else 'Unknown',
                'total_classes': summary.total_classes,
                'present': summary.present_count,
                'absent': summary.absent_count,
                'late': summary.late_count,
                'percentage': round(summary.percentage, 2)
            })
        
        return jsonify({
            'success': True,
            'monthly_data': monthly_data
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500