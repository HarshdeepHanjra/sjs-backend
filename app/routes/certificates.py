from flask import Blueprint, request, jsonify, send_file
from app import db
from app.models.certificate import Certificate
from app.models.user import Student
from app.models.course import Course
from app.utils.decorators import token_required, admin_required
from datetime import datetime
import qrcode
import os
from io import BytesIO
import base64
import secrets
import hashlib
import random
import string

certificates_bp = Blueprint('certificates', __name__)

# Ensure upload directory exists
CERTIFICATE_DIR = 'uploads/certificates'
os.makedirs(CERTIFICATE_DIR, exist_ok=True)

def generate_qr_code_file(data, certificate_id):
    """Generate QR code and save as file"""
    qr = qrcode.QRCode(version=1, box_size=10, border=5)
    qr.add_data(data)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")
    
    filename = f"qr_{certificate_id}.png"
    filepath = os.path.join(CERTIFICATE_DIR, filename)
    img.save(filepath, "PNG")
    
    return f"/uploads/certificates/{filename}"

# Generate certificate ID
def generate_certificate_id():
    """Generate a unique certificate ID"""
    timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
    random_suffix = ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))
    return f"CERT{timestamp}{random_suffix}"

# Generate verification token
def generate_verification_token():
    """Generate a unique verification token"""
    return secrets.token_hex(32)

# Generate certificate hash
def generate_certificate_hash(certificate_id, student_email, course_name):
    """Generate a unique hash for the certificate"""
    data = f"{certificate_id}{student_email}{course_name}{datetime.now().timestamp()}"
    return hashlib.sha256(data.encode()).hexdigest()[:64]

# ✅ FIXED: Remove duplicate /api/ prefix - use only one route pattern
# The blueprint will be registered with /api prefix, so routes should not include /api/

@certificates_bp.route('/generate', methods=['POST', 'OPTIONS'])
@admin_required
def api_generate_certificate():
    if request.method == 'OPTIONS':
        return '', 200
    
    try:
        data = request.get_json()
        student_id = data.get('student_id')
        course_id = data.get('course_id')
        score = data.get('score', 100)
        
        print(f"Generating certificate for student_id: {student_id}, course_id: {course_id}")
        
        # Check if certificate already exists
        existing = Certificate.query.filter_by(
            student_id=student_id, 
            course_id=course_id
        ).first()
        
        if existing:
            return jsonify({'error': 'Certificate already exists for this student and course'}), 400
        
        student = Student.query.get(student_id)
        course = Course.query.get(course_id)
        
        if not student or not course:
            return jsonify({'error': 'Student or course not found'}), 404
        
        certificate_id = generate_certificate_id()
        verification_token = generate_verification_token()
        certificate_hash = generate_certificate_hash(certificate_id, student.email, course.name)
        
        # Get frontend URL for verification link
        frontend_url = os.getenv('FRONTEND_URL', 'https://sjs-frontend-delta.vercel.app')
        verification_url = f"{frontend_url}/verify-certificate?token={verification_token}"
        qr_code_url = generate_qr_code_file(verification_url, certificate_id)
        
        # Create certificate
        certificate = Certificate(
            certificate_id=certificate_id,
            student_id=student_id,
            student_name=student.name,
            student_email=student.email,
            course_id=course_id,
            course_name=course.name,
            course_duration=course.duration,
            completion_date=datetime.utcnow(),
            issue_date=datetime.utcnow(),
            verification_token=verification_token,
            certificate_hash=certificate_hash,
            qr_code_url=qr_code_url,
            score=score,
            status='active'
        )
        
        db.session.add(certificate)
        db.session.commit()
        
        print(f"✅ Certificate generated: {certificate_id} for student {student.name}")
        
        return jsonify({
            'success': True,
            'message': 'Certificate generated successfully',
            'certificate': {
                'id': certificate.id,
                'certificate_id': certificate.certificate_id,
                'student_name': certificate.student_name,
                'student_email': certificate.student_email,
                'course_name': certificate.course_name,
                'issue_date': certificate.issue_date.isoformat(),
                'verification_token': certificate.verification_token,
                'status': certificate.status,
                'score': certificate.score
            }
        }), 201
        
    except Exception as e:
        db.session.rollback()
        print(f"Error generating certificate: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500


@certificates_bp.route('/my-certificates', methods=['GET', 'OPTIONS'])
@token_required
def api_get_my_certificates():
    if request.method == 'OPTIONS':
        return '', 200
    
    try:
        user = request.user
        student = Student.query.get(user['id'])
        
        if not student:
            return jsonify({'error': 'Student not found'}), 404
        
        certificates = Certificate.query.filter_by(
            student_id=student.id,
            status='active'
        ).order_by(Certificate.issue_date.desc()).all()
        
        return jsonify({
            'success': True,
            'certificates': [{
                'id': c.id,
                'certificate_id': c.certificate_id,
                'student_name': c.student_name,
                'course_name': c.course_name,
                'issue_date': c.issue_date.isoformat(),
                'verification_token': c.verification_token,
                'score': c.score,
                'status': c.status
            } for c in certificates]
        }), 200
    except Exception as e:
        print(f"Error getting certificates: {e}")
        return jsonify({'error': str(e)}), 500


# Route to verify certificate - PUBLIC (no authentication)
@certificates_bp.route('/verify', methods=['GET', 'OPTIONS'])
def verify_certificate_public():
    if request.method == 'OPTIONS':
        return '', 200
    
    try:
        token = request.args.get('token')
        
        print(f"Verification request - Token: {token}")
        
        if not token:
            return jsonify({'valid': False, 'message': 'Verification token required'}), 400
        
        certificate = Certificate.query.filter_by(verification_token=token).first()
        
        if not certificate:
            print(f"No certificate found with token: {token}")
            return jsonify({'valid': False, 'message': 'Certificate not found'}), 404
        
        print(f"Found certificate for: {certificate.student_name}, Status: {certificate.status}")
        
        if certificate.status != 'active':
            return jsonify({'valid': False, 'message': 'Certificate has been revoked'}), 400
        
        return jsonify({
            'valid': True,
            'certificate': {
                'certificate_id': certificate.certificate_id,
                'student_name': certificate.student_name,
                'course_name': certificate.course_name,
                'issue_date': certificate.issue_date.isoformat(),
                'completion_date': certificate.completion_date.isoformat(),
                'score': certificate.score
            }
        }), 200
    except Exception as e:
        print(f"Verification error: {e}")
        return jsonify({'valid': False, 'error': str(e)}), 500


@certificates_bp.route('/download/<certificate_id>', methods=['GET', 'OPTIONS'])
@token_required
def api_download_certificate(certificate_id):
    if request.method == 'OPTIONS':
        return '', 200
    
    try:
        certificate = Certificate.query.filter_by(certificate_id=certificate_id).first()
        
        if not certificate:
            return jsonify({'error': 'Certificate not found'}), 404
        
        # Create a simple HTML certificate for download
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Certificate of Achievement</title>
            <style>
                body {{ font-family: 'Georgia', serif; padding: 40px; }}
                .certificate {{ border: 2px solid #1a3a5c; padding: 30px; text-align: center; max-width: 800px; margin: auto; }}
                h1 {{ color: #1a3a5c; }}
                .student-name {{ font-size: 24px; font-weight: bold; margin: 20px 0; }}
            </style>
        </head>
        <body>
            <div class="certificate">
                <h1>CERTIFICATE OF ACHIEVEMENT</h1>
                <p>This certificate is proudly presented to</p>
                <div class="student-name">{certificate.student_name}</div>
                <p>for successfully completing the course</p>
                <h3>{certificate.course_name}</h3>
                <p>Score: {certificate.score}%</p>
                <p>Issue Date: {certificate.issue_date.strftime('%B %d, %Y')}</p>
                <p>Certificate ID: {certificate.certificate_id}</p>
            </div>
        </body>
        </html>
        """
        
        return html_content, 200, {'Content-Type': 'text/html'}
        
    except Exception as e:
        print(f"Download error: {e}")
        return jsonify({'error': str(e)}), 500


# Admin route to get all certificates
@certificates_bp.route('/admin/certificates', methods=['GET', 'OPTIONS'])
@admin_required
def api_admin_get_certificates():
    if request.method == 'OPTIONS':
        return '', 200
    
    try:
        certificates = Certificate.query.order_by(Certificate.issue_date.desc()).all()
        
        return jsonify({
            'success': True,
            'certificates': [{
                'id': c.id,
                'certificate_id': c.certificate_id,
                'student_name': c.student_name,
                'student_email': c.student_email,
                'course_name': c.course_name,
                'issue_date': c.issue_date.isoformat(),
                'verification_token': c.verification_token,
                'status': c.status,
                'score': c.score
            } for c in certificates]
        }), 200
    except Exception as e:
        print(f"Error getting admin certificates: {e}")
        return jsonify({'error': str(e)}), 500


# Admin route to revoke certificate
@certificates_bp.route('/admin/certificates/<int:certificate_id>/revoke', methods=['POST', 'OPTIONS'])
@admin_required
def api_revoke_certificate(certificate_id):
    if request.method == 'OPTIONS':
        return '', 200
    
    try:
        certificate = Certificate.query.get(certificate_id)
        
        if not certificate:
            return jsonify({'error': 'Certificate not found'}), 404
        
        certificate.status = 'revoked'
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Certificate revoked successfully'
        }), 200
    except Exception as e:
        db.session.rollback()
        print(f"Error revoking certificate: {e}")
        return jsonify({'error': str(e)}), 500


# Admin route to delete certificate (permanently)
@certificates_bp.route('/admin/certificates/<int:certificate_id>', methods=['DELETE', 'OPTIONS'])
@admin_required
def api_delete_certificate(certificate_id):
    if request.method == 'OPTIONS':
        return '', 200
    
    try:
        certificate = Certificate.query.get(certificate_id)
        
        if not certificate:
            return jsonify({'error': 'Certificate not found'}), 404
        
        # Delete QR code file if exists
        if certificate.qr_code_url:
            qr_path = os.path.join(CERTIFICATE_DIR, os.path.basename(certificate.qr_code_url))
            if os.path.exists(qr_path):
                os.remove(qr_path)
                print(f"✅ Deleted QR file: {qr_path}")
        
        # Delete PDF file if exists
        if hasattr(certificate, 'pdf_url') and certificate.pdf_url:
            pdf_path = os.path.join(CERTIFICATE_DIR, os.path.basename(certificate.pdf_url))
            if os.path.exists(pdf_path):
                os.remove(pdf_path)
                print(f"✅ Deleted PDF file: {pdf_path}")
        
        # Delete certificate from database
        db.session.delete(certificate)
        db.session.commit()
        
        print(f"✅ Certificate {certificate.certificate_id} deleted permanently")
        
        return jsonify({
            'success': True,
            'message': 'Certificate deleted permanently from database'
        }), 200
    except Exception as e:
        db.session.rollback()
        print(f"Error deleting certificate: {e}")
        return jsonify({'error': str(e)}), 500


# Debug endpoint to check certificate by token
@certificates_bp.route('/debug/<token>', methods=['GET'])
@admin_required
def debug_certificate(token):
    """Debug endpoint to check certificate by token"""
    try:
        certificate = Certificate.query.filter_by(verification_token=token).first()
        
        if certificate:
            return jsonify({
                'found': True,
                'certificate': {
                    'id': certificate.id,
                    'certificate_id': certificate.certificate_id,
                    'student_name': certificate.student_name,
                    'verification_token': certificate.verification_token,
                    'status': certificate.status
                }
            }), 200
        else:
            all_certs = Certificate.query.all()
            tokens = [c.verification_token for c in all_certs]
            return jsonify({
                'found': False,
                'search_token': token,
                'available_tokens': tokens[:10]
            }), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500