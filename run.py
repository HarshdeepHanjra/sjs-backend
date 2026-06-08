from app import create_app, db
from app.models.user import Student, Admin
from app.models.course import Course
from app.models.order import Order
from app.models.payment import PaymentVerification
from app.models.attendance import Attendance, AttendanceSummary
from app.models.internship import Internship, InternshipOrder, InternshipEnrollment
from app.models.certificate import Certificate, StudentProgress, VerificationLog, StudentPublicProfile
from flask import jsonify
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

app = create_app()

# =====================================================
# HEALTH CHECK ENDPOINTS (for Render)
# =====================================================

@app.route('/health')
def health():
    """Health check endpoint for Render"""
    return jsonify({'status': 'ok', 'message': 'Server is healthy'})

@app.route('/db-test')
def db_test():
    """Test database connection"""
    try:
        from sqlalchemy import text
        result = db.session.execute(text('SELECT 1')).scalar()
        return jsonify({
            'status': 'success',
            'message': 'Database connected successfully',
            'result': result
        })
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

# =====================================================
# RUN APPLICATION
# =====================================================

if __name__ == '__main__':
    with app.app_context():
        try:
            db.create_all()
            print("✅ Database tables created successfully!")
        except Exception as e:
            print(f"⚠️ Database tables note: {e}")
    
    # Get port from environment (Render provides PORT)
    port = int(os.environ.get('PORT', 5000))
    
    # Debug mode - False for production
    debug_mode = os.environ.get('FLASK_DEBUG', 'False').lower() == 'true'
    
    print("=" * 60)
    print("🚀 SJS Academy Backend Server")
    print("=" * 60)
    print(f"📡 Server running on: http://0.0.0.0:{port}")
    print(f"🔐 Environment: {'Development' if debug_mode else 'Production'}")
    print(f"🐘 Database: Supabase")
    print("=" * 60)
    
    app.run(
        debug=debug_mode,
        host='0.0.0.0',
        port=port
    )