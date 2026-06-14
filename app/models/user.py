from app import db
from datetime import datetime

class Student(db.Model):
    __tablename__ = 'students'
    
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.String(20), unique=True, nullable=False)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    phone = db.Column(db.String(15), default='')
    password_hash = db.Column(db.String(255), nullable=False)
    status = db.Column(db.String(20), default='active')
    course_ids = db.Column(db.JSON, default=[])
    certificate_count = db.Column(db.Integer, default=0)
    internship_ids = db.Column(db.JSON, default=[])  # ✅ Add this field
    
    # Password reset fields
    reset_token = db.Column(db.String(200), nullable=True)
    reset_expiry = db.Column(db.DateTime, nullable=True)
    
    # Professional fields
    occupation = db.Column(db.String(100), default='')
    company = db.Column(db.String(200), default='')
    skills = db.Column(db.Text, default='')
    interests = db.Column(db.Text, default='')
    achievements = db.Column(db.Text, default='')
    website = db.Column(db.String(500), default='')
    github = db.Column(db.String(500), default='')
    linkedin = db.Column(db.String(500), default='')
    
    # Additional fields
    bio = db.Column(db.Text, default='')
    address = db.Column(db.String(500), default='')
    city = db.Column(db.String(100), default='')
    twitter = db.Column(db.String(500), default='')
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # ✅ FIXED: Remove backref to avoid conflict (backref will be defined in Enrollment)
    # enrollments = db.relationship('Enrollment', backref='student', lazy='dynamic')
    
    def increment_certificate_count(self):
        self.certificate_count += 1
        db.session.commit()
        return self.certificate_count
    
    def to_dict(self):
        return {
            'id': self.id,
            'student_id': self.student_id,
            'name': self.name,
            'email': self.email,
            'phone': self.phone or '',
            'status': self.status,
            'course_ids': self.course_ids or [],
            'certificate_count': self.certificate_count,
            'occupation': self.occupation or '',
            'company': self.company or '',
            'skills': self.skills or '',
            'interests': self.interests or '',
            'achievements': self.achievements or '',
            'website': self.website or '',
            'github': self.github or '',
            'linkedin': self.linkedin or '',
            'bio': self.bio or '',
            'address': self.address or '',
            'city': self.city or '',
            'twitter': self.twitter or '',
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
    
    def __repr__(self):
        return f'<Student {self.name}>'


class Admin(db.Model):
    __tablename__ = 'admins'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    full_name = db.Column(db.String(100))
    role = db.Column(db.String(20), default='staff')
    is_active = db.Column(db.Boolean, default=True)
    
    # Password reset fields
    reset_token = db.Column(db.String(200), nullable=True)
    reset_expiry = db.Column(db.DateTime, nullable=True)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def set_password(self, password):
        from app import bcrypt
        self.password_hash = bcrypt.generate_password_hash(password).decode('utf-8')
    
    def check_password(self, password):
        from app import bcrypt
        return bcrypt.check_password_hash(self.password_hash, password)
    
    def to_dict(self):
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'full_name': self.full_name,
            'role': self.role,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
    
    def __repr__(self):
        return f'<Admin {self.username}>'



