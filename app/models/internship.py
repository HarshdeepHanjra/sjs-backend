




from app import db
from datetime import datetime

class Internship(db.Model):
    __tablename__ = 'internships'
    id = db.Column(db.Integer, primary_key=True)
    internship_id = db.Column(db.String(20), unique=True)
    title = db.Column(db.String(100), nullable=False)
    category = db.Column(db.String(50), default='Development')
    duration = db.Column(db.String(50))
    fee = db.Column(db.Float, nullable=False, default=0)
    original_fee = db.Column(db.Float, default=0)
    stipend = db.Column(db.String(100), default='Unpaid')
    mode = db.Column(db.String(20), default='Online')
    start_date = db.Column(db.String(100), default='Monthly Batch')
    slots = db.Column(db.Integer, default=0)
    enrolled = db.Column(db.Integer, default=0)
    rating = db.Column(db.Float, default=4.5)
    description = db.Column(db.Text)
    syllabus = db.Column(db.JSON, default=list)
    benefits = db.Column(db.JSON, default=list)
    requirements = db.Column(db.JSON, default=list)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class InternshipOrder(db.Model):
    __tablename__ = 'internship_orders'
    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.String(50), unique=True, nullable=False)
    
    # ✅ ADD FOREIGN KEYS
    student_id = db.Column(db.Integer, db.ForeignKey('students.id', ondelete='CASCADE'), nullable=False)
    internship_id = db.Column(db.Integer, db.ForeignKey('internships.id', ondelete='CASCADE'), nullable=False)
    
    student_name = db.Column(db.String(100))
    student_email = db.Column(db.String(100))
    student_phone = db.Column(db.String(15))
    internship_title = db.Column(db.String(100), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    payment_status = db.Column(db.String(20), default='pending')
    status = db.Column(db.String(20), default='pending')
    payment_method = db.Column(db.String(50))
    transaction_id = db.Column(db.String(100))
    screenshot_url = db.Column(db.String(500))
    admin_notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class InternshipEnrollment(db.Model):
    __tablename__ = 'internship_enrollments'
    id = db.Column(db.Integer, primary_key=True)
    
    # ✅ ADD FOREIGN KEYS
    student_id = db.Column(db.Integer, db.ForeignKey('students.id', ondelete='CASCADE'), nullable=False)
    internship_id = db.Column(db.Integer, db.ForeignKey('internships.id', ondelete='CASCADE'), nullable=False)
    
    order_id = db.Column(db.String(50), nullable=False)
    status = db.Column(db.String(20), default='pending')
    enrolled_at = db.Column(db.DateTime, default=datetime.utcnow)