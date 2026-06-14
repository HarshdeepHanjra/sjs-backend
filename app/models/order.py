# from app import db
# from datetime import datetime

# class Order(db.Model):
#     __tablename__ = 'orders'
    
#     id = db.Column(db.Integer, primary_key=True)
#     order_id = db.Column(db.String(50), unique=True, nullable=False)
#     student_id = db.Column(db.Integer, nullable=False)
#     student_name = db.Column(db.String(100))
#     student_email = db.Column(db.String(100))
#     total_amount = db.Column(db.Float, nullable=False)
#     courses = db.Column(db.JSON, nullable=False, default=[])
#     payment_status = db.Column(db.String(20), default='pending')
#     payment_method = db.Column(db.String(50))
#     transaction_id = db.Column(db.String(100))
#     screenshot_url = db.Column(db.String(500))
#     created_at = db.Column(db.DateTime, default=datetime.utcnow)
#     updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
#     def to_dict(self):
#         return {
#             'id': self.id,
#             'order_id': self.order_id,
#             'student_id': self.student_id,
#             'student_name': self.student_name,
#             'student_email': self.student_email,
#             'total_amount': float(self.total_amount),
#             'courses': self.courses or [],
#             'payment_status': self.payment_status,
#             'payment_method': self.payment_method,
#             'transaction_id': self.transaction_id,
#             'screenshot_url': self.screenshot_url,
#             'created_at': self.created_at.isoformat() if self.created_at else None,
#             'updated_at': self.updated_at.isoformat() if self.updated_at else None
#         }








from app import db
from datetime import datetime

class Order(db.Model):
    __tablename__ = 'orders'
    
    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.String(50), unique=True, nullable=False)
    
    # ✅ Add Foreign Key to Student
    student_id = db.Column(db.Integer, db.ForeignKey('students.id', ondelete='CASCADE'), nullable=False)
    
    student_name = db.Column(db.String(100))
    student_email = db.Column(db.String(100))
    total_amount = db.Column(db.Float, nullable=False)
    courses = db.Column(db.JSON, nullable=False, default=list)
    payment_status = db.Column(db.String(20), default='pending')
    payment_method = db.Column(db.String(50), default='bank_transfer')  # ✅ Default value
    transaction_id = db.Column(db.String(100))
    screenshot_url = db.Column(db.String(500))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # ✅ Add relationship to Student (optional)
    # student = db.relationship('Student', backref='orders', cascade='all, delete-orphan')
    
    def to_dict(self):
        return {
            'id': self.id,
            'order_id': self.order_id,
            'student_id': self.student_id,
            'student_name': self.student_name,
            'student_email': self.student_email,
            'total_amount': float(self.total_amount) if self.total_amount else 0,
            'courses': self.courses or [],
            'payment_status': self.payment_status,
            'payment_method': self.payment_method or 'bank_transfer',
            'transaction_id': self.transaction_id,
            'screenshot_url': self.screenshot_url,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
    
    def __repr__(self):
        return f'<Order {self.order_id}>'