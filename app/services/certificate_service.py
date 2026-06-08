import qrcode
from io import BytesIO
import base64
from app.models.certificate import StudentProgress
from datetime import datetime

def generate_qr_code(certificate_id):
    """Generate QR code for certificate verification"""
    verification_url = f"https://verify.sjsglobaltech.com/certificate/{certificate_id}"
    
    qr = qrcode.QRCode(version=1, box_size=10, border=5)
    qr.add_data(verification_url)
    qr.make(fit=True)
    
    img = qr.make_image(fill_color="black", back_color="white")
    
    # Convert to base64 for storing in database
    buffered = BytesIO()
    img.save(buffered, format="PNG")
    img_str = base64.b64encode(buffered.getvalue()).decode()
    
    return img_str, verification_url

def check_certificate_eligibility(student_id, course_id):
    """Check if student is eligible for certificate"""
    from app import db
    
    progress = StudentProgress.query.filter_by(
        student_id=student_id, 
        course_id=course_id
    ).first()
    
    if not progress:
        return False, "No progress record found"
    
    conditions = [
        (progress.attendance_percentage >= 75, f"Attendance: {progress.attendance_percentage}% (need 75%)"),
        (progress.assignments_completed == progress.total_assignments, f"Assignments: {progress.assignments_completed}/{progress.total_assignments}"),
        (progress.project_submitted, "Project not submitted"),
        (progress.assessment_passed, "Assessment not passed")
    ]
    
    all_met = all(condition for condition, _ in conditions)
    
    if all_met:
        progress.is_eligible = True
        progress.eligible_date = datetime.utcnow()
        db.session.commit()
        return True, "Eligible for certificate"
    else:
        failed = [msg for condition, msg in conditions if not condition]
        return False, "; ".join(failed)