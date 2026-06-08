from app import db
from datetime import datetime
import hashlib
import secrets

class Certificate(db.Model):
    __tablename__ = 'certificates'
    
    id = db.Column(db.Integer, primary_key=True)
    certificate_id = db.Column(db.String(100), unique=True, nullable=False)
    student_id = db.Column(db.Integer, db.ForeignKey('students.id'), nullable=False)
    student_name = db.Column(db.String(200), nullable=False)
    student_email = db.Column(db.String(200), nullable=False)
    course_id = db.Column(db.Integer, db.ForeignKey('courses.id'), nullable=False)
    course_name = db.Column(db.String(200), nullable=False)
    course_duration = db.Column(db.String(100))
    completion_date = db.Column(db.DateTime, default=datetime.utcnow)
    issue_date = db.Column(db.DateTime, default=datetime.utcnow)
    verification_token = db.Column(db.String(200), unique=True, nullable=False)
    certificate_hash = db.Column(db.String(300), unique=True, nullable=False)
    qr_code_url = db.Column(db.Text)
    pdf_url = db.Column(db.String(500))
    status = db.Column(db.String(20), default='active')
    score = db.Column(db.Integer, default=100)
    issued_by = db.Column(db.String(100), default='SJS Academy')
    organization_name = db.Column(db.String(200), default='SJS Global Tech Academy')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    student = db.relationship('Student', backref='certificates')
    course = db.relationship('Course', backref='certificates')
    
    @staticmethod
    def generate_certificate_id(student_id):
        """Generate certificate ID in format: SJS-GT-YYYY-MM-XXXXX"""
        year = datetime.now().strftime('%Y')
        month = datetime.now().strftime('%m')
        
        # Count existing certificates for this student
        count = Certificate.query.filter_by(student_id=student_id).count()
        sequential_number = str(count + 1).zfill(5)  # 5 digits with leading zeros
        
        return f"SJS-GT-{year}-{month}-{sequential_number}"
    
    @staticmethod
    def generate_verification_token():
        return secrets.token_hex(32)
    
    @staticmethod
    def generate_certificate_hash(certificate_id, student_email, course_name):
        data = f"{certificate_id}{student_email}{course_name}{datetime.now().timestamp()}"
        return hashlib.sha256(data.encode()).hexdigest()[:64]
    
    def to_dict(self):
        return {
            'id': self.id,
            'certificate_id': self.certificate_id,
            'student_name': self.student_name,
            'student_email': self.student_email,
            'course_name': self.course_name,
            'completion_date': self.completion_date.isoformat() if self.completion_date else None,
            'issue_date': self.issue_date.isoformat() if self.issue_date else None,
            'verification_token': self.verification_token,
            'status': self.status,
            'score': self.score
        }


class CertificateTemplate(db.Model):
    """Certificate template model for customizable certificate designs"""
    __tablename__ = 'certificate_templates'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    template_html = db.Column(db.Text, nullable=False)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'template_html': self.template_html,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }


class StudentProgress(db.Model):
    __tablename__ = 'student_progress'
    
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('students.id'), nullable=False)
    course_id = db.Column(db.Integer, db.ForeignKey('courses.id'), nullable=False)
    attendance_percentage = db.Column(db.Float, default=0)
    assignment_score = db.Column(db.Float, default=0)
    project_score = db.Column(db.Float, default=0)
    assessment_score = db.Column(db.Float, default=0)
    training_hours = db.Column(db.Integer, default=0)
    assignments_completed = db.Column(db.Integer, default=0)
    total_assignments = db.Column(db.Integer, default=0)
    project_submitted = db.Column(db.Boolean, default=False)
    assessment_passed = db.Column(db.Boolean, default=False)
    is_eligible = db.Column(db.Boolean, default=False)
    eligible_date = db.Column(db.DateTime)
    completed_at = db.Column(db.DateTime)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    student = db.relationship('Student', backref='progress')
    course = db.relationship('Course', backref='progress')
    
    def to_dict(self):
        return {
            'id': self.id,
            'student_id': self.student_id,
            'course_id': self.course_id,
            'attendance_percentage': self.attendance_percentage,
            'assignment_score': self.assignment_score,
            'project_score': self.project_score,
            'assessment_score': self.assessment_score,
            'training_hours': self.training_hours,
            'assignments_completed': self.assignments_completed,
            'total_assignments': self.total_assignments,
            'project_submitted': self.project_submitted,
            'assessment_passed': self.assessment_passed,
            'is_eligible': self.is_eligible,
            'eligible_date': self.eligible_date.isoformat() if self.eligible_date else None,
            'completed_at': self.completed_at.isoformat() if self.completed_at else None
        }


class VerificationLog(db.Model):
    __tablename__ = 'verification_logs'
    
    id = db.Column(db.Integer, primary_key=True)
    certificate_id = db.Column(db.String(50), nullable=False)
    verifier_ip = db.Column(db.String(45))
    verifier_user_agent = db.Column(db.String(500))
    verification_method = db.Column(db.String(20))
    status = db.Column(db.String(20))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'certificate_id': self.certificate_id,
            'verifier_ip': self.verifier_ip,
            'verifier_user_agent': self.verifier_user_agent,
            'verification_method': self.verification_method,
            'status': self.status,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }


class StudentPublicProfile(db.Model):
    __tablename__ = 'student_public_profiles'
    
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('students.id'), unique=True, nullable=False)
    linkedin_url = db.Column(db.String(500))
    github_url = db.Column(db.String(500))
    portfolio_url = db.Column(db.String(500))
    skills = db.Column(db.JSON, default=[])
    bio = db.Column(db.Text)
    is_public = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    student = db.relationship('Student', backref='public_profile')
    
    def to_dict(self):
        return {
            'id': self.id,
            'student_id': self.student_id,
            'linkedin_url': self.linkedin_url,
            'github_url': self.github_url,
            'portfolio_url': self.portfolio_url,
            'skills': self.skills or [],
            'bio': self.bio,
            'is_public': self.is_public
        }