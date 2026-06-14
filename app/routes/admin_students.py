from flask import Blueprint, request, jsonify
from app import db
from app.models.user import Student
from app.models.internship import InternshipOrder, InternshipEnrollment
from app.models.payment import PaymentVerification
from app.models.certificate import Certificate
from app.models.attendance import Attendance
from app.utils.decorators import token_required, admin_required
from datetime import datetime

# Create blueprint WITHOUT url_prefix (will be set in __init__.py)
admin_students_bp = Blueprint('admin_students', __name__)


# =====================================================
# GET all students
# =====================================================
@admin_students_bp.route("/students", methods=["GET", "OPTIONS"])
@token_required
@admin_required
def get_all_students():
    """Get all students"""
    if request.method == "OPTIONS":
        return "", 200
    
    try:
        students = Student.query.order_by(Student.created_at.desc()).all()
        return jsonify({
            "success": True,
            "students": [s.to_dict() for s in students]
        }), 200
    except Exception as e:
        print(f"Error fetching students: {e}")
        return jsonify({"success": False, "message": str(e)}), 500


# =====================================================
# DELETE student (SINGLE ROUTE - NO DUPLICATES)
# =====================================================
@admin_students_bp.route("/students/<int:student_id>", methods=["DELETE", "OPTIONS"])
@token_required
@admin_required
def delete_student(student_id):
    """Delete a student and all related data"""
    if request.method == "OPTIONS":
        response = jsonify({})
        response.headers.add('Access-Control-Allow-Origin', '*')
        response.headers.add('Access-Control-Allow-Methods', 'DELETE, OPTIONS')
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type, Authorization')
        return response, 200
    
    try:
        print(f"📥 Attempting to delete student ID: {student_id}")
        
        # Find student
        student = Student.query.get(student_id)
        
        if not student:
            print(f"❌ Student with ID {student_id} not found")
            return jsonify({"success": False, "message": "Student not found"}), 404
        
        print(f"📋 Student found: {student.name} (ID: {student.id})")
        
        # Delete related data
        deleted_orders = InternshipOrder.query.filter_by(student_id=student_id).delete()
        print(f"   Deleted {deleted_orders} internship orders")
        
        deleted_enrollments = InternshipEnrollment.query.filter_by(student_id=student_id).delete()
        print(f"   Deleted {deleted_enrollments} internship enrollments")
        
        deleted_payments = PaymentVerification.query.filter_by(student_id=student_id).delete()
        print(f"   Deleted {deleted_payments} payment verifications")
        
        # Delete certificates
        try:
            deleted_certs = Certificate.query.filter_by(student_id=student_id).delete()
            print(f"   Deleted {deleted_certs} certificates")
        except Exception as e:
            print(f"   Certificate deletion skipped: {e}")
        
        # Delete attendance
        try:
            deleted_attendance = Attendance.query.filter_by(student_id=student_id).delete()
            print(f"   Deleted {deleted_attendance} attendance records")
        except Exception as e:
            print(f"   Attendance deletion skipped: {e}")
        
        # Delete the student
        student_name = student.name
        db.session.delete(student)
        db.session.commit()
        
        print(f"✅ Student '{student_name}' (ID: {student_id}) deleted successfully!")
        
        return jsonify({
            "success": True,
            "message": f"Student '{student_name}' and all related data deleted successfully"
        }), 200
        
    except Exception as e:
        db.session.rollback()
        print(f"❌ Error deleting student: {str(e)}")
        import traceback
        traceback.print_exc()
        
        return jsonify({
            "success": False, 
            "message": f"Error: {str(e)}"
        }), 500


# =====================================================
# UPDATE student
# =====================================================
@admin_students_bp.route("/students/<int:student_id>", methods=["PUT", "OPTIONS"])
@token_required
@admin_required
def update_student(student_id):
    """Update student information"""
    if request.method == "OPTIONS":
        return "", 200
    
    try:
        student = Student.query.get(student_id)
        
        if not student:
            return jsonify({"success": False, "message": "Student not found"}), 404
        
        data = request.get_json()
        
        if "name" in data:
            student.name = data["name"]
        if "email" in data:
            student.email = data["email"]
        if "phone" in data:
            student.phone = data["phone"]
        if "status" in data:
            student.status = data["status"]
        
        student.updated_at = datetime.utcnow()
        db.session.commit()
        
        return jsonify({
            "success": True,
            "message": "Student updated successfully",
            "student": student.to_dict()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        print(f"Error updating student: {e}")
        return jsonify({"success": False, "message": str(e)}), 500


# =====================================================
# TOGGLE student status
# =====================================================
@admin_students_bp.route("/students/<int:student_id>/status", methods=["PATCH", "OPTIONS"])
@token_required
@admin_required
def toggle_student_status(student_id):
    """Toggle student active/inactive status"""
    if request.method == "OPTIONS":
        return "", 200
    
    try:
        student = Student.query.get(student_id)
        
        if not student:
            return jsonify({"success": False, "message": "Student not found"}), 404
        
        data = request.get_json()
        new_status = data.get("status", "inactive" if student.status == "active" else "active")
        
        student.status = new_status
        student.updated_at = datetime.utcnow()
        db.session.commit()
        
        return jsonify({
            "success": True,
            "message": f"Student status changed to {new_status}",
            "status": new_status
        }), 200
        
    except Exception as e:
        db.session.rollback()
        print(f"Error toggling student status: {e}")
        return jsonify({"success": False, "message": str(e)}), 500


# =====================================================
# BULK DELETE students
# =====================================================
@admin_students_bp.route("/students/bulk-delete", methods=["POST", "OPTIONS"])
@token_required
@admin_required
def bulk_delete_students():
    """Delete multiple students at once"""
    if request.method == "OPTIONS":
        return "", 200
    
    try:
        data = request.get_json()
        student_ids = data.get("student_ids", [])
        
        if not student_ids:
            return jsonify({"success": False, "message": "No student IDs provided"}), 400
        
        deleted_count = 0
        failed_ids = []
        
        for student_id in student_ids:
            try:
                student = Student.query.get(student_id)
                if student:
                    # Delete related data
                    InternshipOrder.query.filter_by(student_id=student_id).delete()
                    InternshipEnrollment.query.filter_by(student_id=student_id).delete()
                    PaymentVerification.query.filter_by(student_id=student_id).delete()
                    
                    try:
                        Certificate.query.filter_by(student_id=student_id).delete()
                    except:
                        pass
                    
                    try:
                        Attendance.query.filter_by(student_id=student_id).delete()
                    except:
                        pass
                    
                    db.session.delete(student)
                    deleted_count += 1
                else:
                    failed_ids.append(student_id)
            except Exception as e:
                failed_ids.append(student_id)
                print(f"Error deleting student {student_id}: {e}")
        
        db.session.commit()
        
        return jsonify({
            "success": True,
            "message": f"Deleted {deleted_count} students successfully",
            "deleted_count": deleted_count,
            "failed_ids": failed_ids
        }), 200
        
    except Exception as e:
        db.session.rollback()
        print(f"Error in bulk delete: {e}")
        return jsonify({"success": False, "message": str(e)}), 500


# =====================================================
# SEARCH students
# =====================================================
@admin_students_bp.route("/students/search", methods=["GET", "OPTIONS"])
@token_required
@admin_required
def search_students():
    """Search students by name, email, or student_id"""
    if request.method == "OPTIONS":
        return "", 200
    
    try:
        query = request.args.get('q', '')
        if not query:
            return jsonify({"success": False, "message": "Search query required"}), 400
        
        students = Student.query.filter(
            (Student.name.ilike(f'%{query}%')) |
            (Student.email.ilike(f'%{query}%')) |
            (Student.student_id.ilike(f'%{query}%'))
        ).all()
        
        return jsonify({
            "success": True,
            "students": [s.to_dict() for s in students],
            "count": len(students)
        }), 200
        
    except Exception as e:
        print(f"Error searching students: {e}")
        return jsonify({"success": False, "message": str(e)}), 500