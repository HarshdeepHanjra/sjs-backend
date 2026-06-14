# from app import db
# from datetime import datetime

# class Internship(db.Model):
#     __tablename__ = 'internships'
#     id = db.Column(db.Integer, primary_key=True)
#     internship_id = db.Column(db.String(20), unique=True, nullable=False)
#     title = db.Column(db.String(100), nullable=False)
#     category = db.Column(db.String(50), default='Development')
#     duration = db.Column(db.String(50))
#     fee = db.Column(db.Float, nullable=False)
#     original_fee = db.Column(db.Float)
#     stipend = db.Column(db.String(100))
#     mode = db.Column(db.String(20), default='Online')
#     slots = db.Column(db.Integer, default=0)
#     enrolled = db.Column(db.Integer, default=0)
#     rating = db.Column(db.Float, default=4.5)
#     description = db.Column(db.Text)
#     syllabus = db.Column(db.JSON, default=[])
#     benefits = db.Column(db.JSON, default=[])
#     requirements = db.Column(db.JSON, default=[])
#     is_active = db.Column(db.Boolean, default=True)
#     created_at = db.Column(db.DateTime, default=datetime.utcnow)

# class InternshipOrder(db.Model):
#     __tablename__ = 'internship_orders'
#     id = db.Column(db.Integer, primary_key=True)
#     order_id = db.Column(db.String(50), unique=True, nullable=False)
#     student_id = db.Column(db.Integer, nullable=False)
#     student_name = db.Column(db.String(100))
#     student_email = db.Column(db.String(100))
#     student_phone = db.Column(db.String(15))
#     internship_id = db.Column(db.Integer, nullable=False)
#     internship_title = db.Column(db.String(100), nullable=False)
#     amount = db.Column(db.Float, nullable=False)
#     payment_status = db.Column(db.String(20), default='pending')
#     payment_method = db.Column(db.String(50))
#     transaction_id = db.Column(db.String(100))
#     screenshot_url = db.Column(db.String(500))
#     admin_notes = db.Column(db.Text)
#     created_at = db.Column(db.DateTime, default=datetime.utcnow)
#     updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

# class InternshipEnrollment(db.Model):
#     __tablename__ = 'internship_enrollments'
#     id = db.Column(db.Integer, primary_key=True)
#     student_id = db.Column(db.Integer, nullable=False)
#     internship_id = db.Column(db.Integer, nullable=False)
#     order_id = db.Column(db.String(50), nullable=False)
#     status = db.Column(db.String(20), default='pending')
#     enrolled_at = db.Column(db.DateTime, default=datetime.utcnow)



from app import db
from datetime import datetime

class Internship(db.Model):
    __tablename__ = 'internships'
    id = db.Column(db.Integer, primary_key=True)
    internship_id = db.Column(db.String(20), unique=True, nullable=False)
    title = db.Column(db.String(100), nullable=False)
    category = db.Column(db.String(50), default='Development')
    duration = db.Column(db.String(50))
    fee = db.Column(db.Float, nullable=False, default=0)
    original_fee = db.Column(db.Float, default=0)
    stipend = db.Column(db.String(100), default='Unpaid')
    mode = db.Column(db.String(20), default='Online')
    start_date = db.Column(db.String(100), default='Monthly Batch')  # ✅ Add this field
    slots = db.Column(db.Integer, default=0)
    enrolled = db.Column(db.Integer, default=0)
    rating = db.Column(db.Float, default=4.5)
    description = db.Column(db.Text)
    syllabus = db.Column(db.JSON, default=list)  # ✅ Change to list
    benefits = db.Column(db.JSON, default=list)  # ✅ Change to list
    requirements = db.Column(db.JSON, default=list)  # ✅ Change to list
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)  # ✅ Add this field

    def __init__(self, **kwargs):
        # Auto-generate internship_id if not provided
        if 'internship_id' not in kwargs:
            # This will be set after insert, but we'll set a placeholder
            kwargs['internship_id'] = 'TEMP'
        super(Internship, self).__init__(**kwargs)

    def to_dict(self):
        return {
            'id': self.id,
            'internship_id': self.internship_id,
            'title': self.title,
            'category': self.category,
            'duration': self.duration,
            'fee': float(self.fee) if self.fee else 0,
            'original_fee': float(self.original_fee) if self.original_fee else None,
            'stipend': self.stipend,
            'mode': self.mode,
            'start_date': self.start_date,
            'slots': self.slots,
            'enrolled': self.enrolled,
            'rating': float(self.rating) if self.rating else 4.5,
            'description': self.description,
            'syllabus': self.syllabus or [],
            'benefits': self.benefits or [],
            'requirements': self.requirements or [],
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

class InternshipOrder(db.Model):
    __tablename__ = 'internship_orders'
    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.String(50), unique=True, nullable=False)
    student_id = db.Column(db.Integer, nullable=False)
    student_name = db.Column(db.String(100))
    student_email = db.Column(db.String(100))
    student_phone = db.Column(db.String(15))
    internship_id = db.Column(db.Integer, nullable=False)
    internship_title = db.Column(db.String(100), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    payment_status = db.Column(db.String(20), default='pending')
    payment_method = db.Column(db.String(50))
    transaction_id = db.Column(db.String(100))
    screenshot_url = db.Column(db.String(500))
    admin_notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class InternshipEnrollment(db.Model):
    __tablename__ = 'internship_enrollments'
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, nullable=False)
    internship_id = db.Column(db.Integer, nullable=False)
    order_id = db.Column(db.String(50), nullable=False)
    status = db.Column(db.String(20), default='pending')
    enrolled_at = db.Column(db.DateTime, default=datetime.utcnow)