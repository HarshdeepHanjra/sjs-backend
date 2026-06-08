from app import db
from datetime import datetime

class PaymentVerification(db.Model):
    __tablename__ = 'payment_verifications'
    
    id = db.Column(db.Integer, primary_key=True)
    verification_id = db.Column(db.String(50), unique=True, nullable=False)
    order_id = db.Column(db.String(50), nullable=False)
    student_id = db.Column(db.Integer, nullable=False)
    student_name = db.Column(db.String(200), nullable=False)
    student_email = db.Column(db.String(200), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    transaction_id = db.Column(db.String(100), nullable=False)
    screenshot_url = db.Column(db.String(500), nullable=False)
    status = db.Column(db.String(20), default='pending')
    admin_notes = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    verified_at = db.Column(db.DateTime, nullable=True)
    
    def to_dict(self):
        return {
            'id': self.id,
            'verification_id': self.verification_id,
            'order_id': self.order_id,
            'student_id': self.student_id,
            'student_name': self.student_name,
            'student_email': self.student_email,
            'amount': self.amount,
            'transaction_id': self.transaction_id,
            'screenshot_url': self.screenshot_url,
            'status': self.status,
            'admin_notes': self.admin_notes,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'verified_at': self.verified_at.isoformat() if self.verified_at else None
        }