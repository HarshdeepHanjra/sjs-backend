from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_mail import Mail
import os
from datetime import timedelta
from dotenv import load_dotenv
import cloudinary
import cloudinary.uploader
import cloudinary.api

cloudinary.config(
    cloud_name=os.getenv('CLOUDINARY_CLOUD_NAME'),
    api_key=os.getenv('CLOUDINARY_API_KEY'),
    api_secret=os.getenv('CLOUDINARY_API_SECRET')
)

print("✅ Cloudinary configured successfully!")

load_dotenv()

# Initialize extensions at module level
db = SQLAlchemy()
bcrypt = Bcrypt()
mail = Mail()

def create_app():
    app = Flask(__name__)
    
    # Database configuration
    DATABASE_URL = os.getenv('DATABASE_URL', 'postgresql://postgres:098%40Gangahanjra@localhost:5432/sjs_academy')
    
    app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE_URL
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['JWT_SECRET_KEY'] = os.getenv('JWT_SECRET_KEY', 'sjs-academy-secret-key')
    
    # ✅ FIXED: Use correct upload folder path
    app.config['UPLOAD_FOLDER'] = os.path.join('uploads', 'screenshots')
    app.config['MAX_CONTENT_LENGTH'] = 5 * 1024 * 1024
    
    # JWT Configuration
    app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(days=30)
    
    # =====================================================
    # EMAIL CONFIGURATION
    # =====================================================
    app.config['MAIL_SERVER'] = 'smtp.gmail.com'
    app.config['MAIL_PORT'] = 587
    app.config['MAIL_USE_TLS'] = True
    app.config['MAIL_USE_SSL'] = False
    app.config['MAIL_USERNAME'] = os.getenv('MAIL_USERNAME')
    app.config['MAIL_PASSWORD'] = os.getenv('MAIL_PASSWORD')
    app.config['MAIL_DEFAULT_SENDER'] = ('SJS Academy', 'noreply@sjsacademy.com')
    app.config['MAIL_SUPPRESS_SEND'] = os.getenv('MAIL_SUPPRESS_SEND', 'False').lower() == 'true'
    
    print(f"Email configured for: {app.config['MAIL_USERNAME']}")
    print(f"Email sending suppressed: {app.config['MAIL_SUPPRESS_SEND']}")
    
    # ✅ FIXED: Create upload folders with correct paths
    os.makedirs('uploads/screenshots', exist_ok=True)
    os.makedirs('uploads/certificates', exist_ok=True)
    os.makedirs('uploads/mentors', exist_ok=True)
    
    # CORS Configuration
    CORS(app, 
         origins=["http://localhost:3000", "http://127.0.0.1:3000"],
         methods=["GET", "POST", "PUT", "DELETE", "OPTIONS", "PATCH"],
         allow_headers=["Content-Type", "Authorization", "X-Requested-With", "Accept"],
         supports_credentials=True,
         expose_headers=["Content-Type", "Authorization"])
    
    # Handle preflight requests
    @app.before_request
    def handle_preflight():
        if request.method == "OPTIONS":
            response = app.make_default_options_response()
            response.headers.add("Access-Control-Allow-Origin", "http://localhost:3000")
            response.headers.add("Access-Control-Allow-Headers", "Content-Type, Authorization")
            response.headers.add("Access-Control-Allow-Methods", "GET, POST, PUT, DELETE, OPTIONS")
            response.headers.add("Access-Control-Allow-Credentials", "true")
            return response
    
    # Initialize extensions with app
    db.init_app(app)
    bcrypt.init_app(app)
    mail.init_app(app)
    
    # Import and register blueprints
    from app.routes.auth import auth_bp
    from app.routes.courses import courses_bp
    from app.routes.cart import cart_bp
    from app.routes.payments import payments_bp
    from app.routes.admin import admin_bp
    from app.routes.attendance import attendance_bp
    from app.routes.internships import internships_bp
    from app.routes.certificates import certificates_bp
    from app.routes.user import user_bp
    from app.routes.contact import contact_bp
    from app.routes.mentor import mentor_bp
    
    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    app.register_blueprint(courses_bp, url_prefix='/api')
    app.register_blueprint(cart_bp, url_prefix='/api/cart')
    app.register_blueprint(payments_bp, url_prefix='/api/payment')
    app.register_blueprint(admin_bp, url_prefix='/api/admin')
    app.register_blueprint(internships_bp, url_prefix='/api')
    app.register_blueprint(certificates_bp)
    app.register_blueprint(user_bp, url_prefix='/api/user')
    app.register_blueprint(attendance_bp)
    app.register_blueprint(contact_bp, url_prefix='/api')
    app.register_blueprint(mentor_bp)
    
    # ✅ FIXED: Static file serving - Check multiple locations
    @app.route('/uploads/screenshots/<filename>')
    def uploaded_file(filename):
        """Serve screenshot files - checks multiple possible locations"""
        from flask import send_from_directory, abort
        
        # List of possible directories to check
        possible_dirs = [
            'uploads/screenshots',           # Direct path
            './uploads/screenshots',         # Current directory
            'app/uploads/screenshots',       # App folder
            './app/uploads/screenshots',     # App folder with dot
            os.path.join(os.getcwd(), 'uploads', 'screenshots'),  # Absolute path
        ]
        
        # First, check if file exists in any directory
        for directory in possible_dirs:
            if os.path.exists(directory):
                file_path = os.path.join(directory, filename)
                if os.path.exists(file_path):
                    print(f"✅ Serving screenshot from: {file_path}")
                    return send_from_directory(directory, filename)
        
        # If not found, try to find it recursively
        for root, dirs, files in os.walk('.'):
            if filename in files:
                directory = os.path.dirname(os.path.join(root, filename))
                print(f"✅ Found screenshot recursively in: {directory}")
                return send_from_directory(directory, filename)
        
        print(f"❌ Screenshot not found: {filename}")
        return jsonify({'error': 'File not found'}), 404
    
    @app.route('/uploads/certificates/<filename>')
    def certificate_file(filename):
        """Serve certificate files"""
        from flask import send_from_directory
        
        possible_dirs = [
            'uploads/certificates',
            './uploads/certificates',
            'app/uploads/certificates',
            './app/uploads/certificates',
        ]
        
        for directory in possible_dirs:
            if os.path.exists(directory):
                file_path = os.path.join(directory, filename)
                if os.path.exists(file_path):
                    return send_from_directory(directory, filename)
        
        return jsonify({'error': 'File not found'}), 404
    
    @app.route('/uploads/mentors/<filename>')
    def mentor_photo(filename):
        """Serve mentor photos"""
        from flask import send_from_directory
        
        possible_dirs = [
            'uploads/mentors',
            './uploads/mentors',
            'app/uploads/mentors',
            './app/uploads/mentors',
        ]
        
        for directory in possible_dirs:
            if os.path.exists(directory):
                file_path = os.path.join(directory, filename)
                if os.path.exists(file_path):
                    return send_from_directory(directory, filename)
        
        return jsonify({'error': 'File not found'}), 404
    
    # ✅ Debug endpoint to check what files exist
    @app.route('/debug/screenshots', methods=['GET'])
    def debug_screenshots():
        """Debug endpoint to list all screenshots"""
        import os
        
        screenshots = []
        search_dirs = ['uploads/screenshots', 'app/uploads/screenshots']
        
        for search_dir in search_dirs:
            if os.path.exists(search_dir):
                for file in os.listdir(search_dir):
                    if file.endswith(('.png', '.jpg', '.jpeg', '.gif', '.webp')):
                        screenshots.append({
                            'filename': file,
                            'path': os.path.join(search_dir, file),
                            'size': os.path.getsize(os.path.join(search_dir, file))
                        })
        
        return jsonify({
            'screenshots': screenshots,
            'count': len(screenshots),
            'directories_checked': search_dirs
        })
    
    # Create certificates upload directory
    os.makedirs('uploads/certificates', exist_ok=True)
    
    # Test endpoints
    @app.route('/')
    def home():
        return jsonify({'status': 'ok', 'message': 'SJS Academy API is running'})
    
    # @app.route('/api/test')
    # def test():
    #     return jsonify({'status': 'ok', 'message': 'API is working'})
    
    return app