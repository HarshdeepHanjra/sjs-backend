from flask import Blueprint, request, jsonify
from app import db
from app.models.attendance import Attendance, AttendanceSummary
from app.models.course import Course
from app.utils.decorators import student_required

student_attendance_bp = Blueprint('student_attendance', __name__)

@student_attendance_bp.route('/api/student/attendance/my-attendance', methods=['GET', 'OPTIONS'])
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