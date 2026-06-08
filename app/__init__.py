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

load_dotenv()

# Initialize extensions at module level
db = SQLAlchemy()
bcrypt = Bcrypt()
mail = Mail()

def create_app():
    app = Flask(__name__)
    
    # =====================================================
    # CLOUDINARY CONFIGURATION
    # =====================================================
    cloudinary.config(
        cloud_name=os.getenv('CLOUDINARY_CLOUD_NAME', 'dxxpeilta'),
        api_key=os.getenv('CLOUDINARY_API_KEY', '375175513582196'),
        api_secret=os.getenv('CLOUDINARY_API_SECRET', '48p-JTyxEEylHjS2733gA6KeTbU'),
        secure=True
    )
    print("✅ Cloudinary configured successfully!")
    
    # =====================================================
    # DATABASE CONFIGURATION (Your Supabase)
    # =====================================================
    SUPABASE_HOST = "aws-1-ap-south-1.pooler.supabase.com"
    SUPABASE_PORT = "5432"
    SUPABASE_DATABASE = "postgres"
    SUPABASE_USER = "postgres.fswgvwxebocygqjotgrv"
    SUPABASE_PASSWORD = "098@Sjsglobaltech"
    
    DATABASE_URL = f"postgresql://{SUPABASE_USER}:{SUPABASE_PASSWORD.replace('@', '%40')}@{SUPABASE_HOST}:{SUPABASE_PORT}/{SUPABASE_DATABASE}"
    
    app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL', DATABASE_URL)
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['JWT_SECRET_KEY'] = os.getenv('JWT_SECRET_KEY', 'sjs-academy-secret-key-2024')
    
    app.config['UPLOAD_FOLDER'] = os.path.join('uploads', 'screenshots')
    app.config['MAX_CONTENT_LENGTH'] = 5 * 1024 * 1024
    
    app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(days=30)
    
    # =====================================================
    # EMAIL CONFIGURATION
    # =====================================================
    app.config['MAIL_SERVER'] = 'smtp.gmail.com'
    app.config['MAIL_PORT'] = 587
    app.config['MAIL_USE_TLS'] = True
    app.config['MAIL_USE_SSL'] = False
    app.config['MAIL_USERNAME'] = os.getenv('MAIL_USERNAME', 'sjsglobaltech@gmail.com')
    app.config['MAIL_PASSWORD'] = os.getenv('MAIL_PASSWORD', 'oijb jpqd ivgc upbt')
    app.config['MAIL_DEFAULT_SENDER'] = ('SJS Academy', 'noreply@sjsacademy.com')
    app.config['MAIL_SUPPRESS_SEND'] = os.getenv('MAIL_SUPPRESS_SEND', 'False').lower() == 'true'
    
    print(f"Email configured for: {app.config['MAIL_USERNAME']}")
    
    # Create upload folders
    os.makedirs('uploads/screenshots', exist_ok=True)
    os.makedirs('uploads/certificates', exist_ok=True)
    os.makedirs('uploads/mentors', exist_ok=True)
    
    # =====================================================
    # CORS Configuration - ENHANCED FIX
    # =====================================================
    
    # Allowed origins for CORS
    ALLOWED_ORIGINS = [
        "https://sjs-frontend-delta.vercel.app",
        "https://sjs-frontend.vercel.app",
        "http://localhost:3000",
        "http://localhost:5173",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:5173"
    ]
    
    # Get from environment variable if set
    env_origins = os.getenv('CORS_ORIGINS', '')
    if env_origins:
        ALLOWED_ORIGINS.extend([origin.strip() for origin in env_origins.split(',')])
    
    # Remove duplicates
    ALLOWED_ORIGINS = list(set(ALLOWED_ORIGINS))
    
    # Configure CORS
    CORS(app, 
         origins=ALLOWED_ORIGINS,
         methods=["GET", "POST", "PUT", "DELETE", "OPTIONS", "PATCH"],
         allow_headers=["Content-Type", "Authorization", "X-Requested-With", "Accept"],
         supports_credentials=True,
         expose_headers=["Content-Type", "Authorization"],
         max_age=3600)
    
    # ✅ Add after_request handler for extra CORS safety
    @app.after_request
    def after_request(response):
        origin = request.headers.get('Origin')
        if origin in ALLOWED_ORIGINS:
            response.headers.add('Access-Control-Allow-Origin', origin)
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization,X-Requested-With,Accept')
        response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS,PATCH')
        response.headers.add('Access-Control-Allow-Credentials', 'true')
        return response
    
    print(f"✅ CORS configured successfully!")
    print(f"   Allowed origins: {ALLOWED_ORIGINS}")
    
    # Initialize extensions with app
    db.init_app(app)
    bcrypt.init_app(app)
    mail.init_app(app)
    
    # =====================================================
    # IMPORT AND REGISTER BLUEPRINTS
    # =====================================================
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
    
    # Register blueprints with consistent /api prefix
    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    app.register_blueprint(courses_bp, url_prefix='/api/courses')
    app.register_blueprint(cart_bp, url_prefix='/api/cart')
    app.register_blueprint(payments_bp, url_prefix='/api/payment')
    app.register_blueprint(admin_bp, url_prefix='/api/admin')
    app.register_blueprint(internships_bp, url_prefix='/api/internships')
    app.register_blueprint(certificates_bp, url_prefix='/api/certificates')
    app.register_blueprint(user_bp, url_prefix='/api/user')
    app.register_blueprint(attendance_bp, url_prefix='/api')
    app.register_blueprint(contact_bp, url_prefix='/api/contact')
    app.register_blueprint(mentor_bp, url_prefix='/api/mentor')
    
    # =====================================================
    # STATIC FILE SERVING
    # =====================================================
    @app.route('/uploads/screenshots/<filename>')
    def uploaded_file(filename):
        """Serve screenshot files"""
        possible_dirs = [
            'uploads/screenshots',
            './uploads/screenshots',
            'app/uploads/screenshots',
            './app/uploads/screenshots',
            os.path.join(os.getcwd(), 'uploads', 'screenshots'),
        ]
        
        for directory in possible_dirs:
            if os.path.exists(directory):
                file_path = os.path.join(directory, filename)
                if os.path.exists(file_path):
                    print(f"✅ Serving screenshot from: {file_path}")
                    return send_from_directory(directory, filename)
        
        print(f"❌ Screenshot not found: {filename}")
        return jsonify({'error': 'File not found'}), 404
    
    @app.route('/uploads/certificates/<filename>')
    def certificate_file(filename):
        """Serve certificate files"""
        possible_dirs = ['uploads/certificates', './uploads/certificates', 'app/uploads/certificates', './app/uploads/certificates']
        for directory in possible_dirs:
            if os.path.exists(directory) and os.path.exists(os.path.join(directory, filename)):
                return send_from_directory(directory, filename)
        return jsonify({'error': 'File not found'}), 404
    
    @app.route('/uploads/mentors/<filename>')
    def mentor_photo(filename):
        """Serve mentor photos"""
        possible_dirs = ['uploads/mentors', './uploads/mentors', 'app/uploads/mentors', './app/uploads/mentors']
        for directory in possible_dirs:
            if os.path.exists(directory) and os.path.exists(os.path.join(directory, filename)):
                return send_from_directory(directory, filename)
        return jsonify({'error': 'File not found'}), 404
    
    # =====================================================
    # TEST ENDPOINTS
    # =====================================================
    @app.route('/')
    def home():
        return jsonify({'status': 'ok', 'message': 'SJS Academy API is running'})
    
    @app.route('/health')
    def health():
        return jsonify({'status': 'ok', 'message': 'Server is healthy'})
    
    # ✅ Add OPTIONS handler for all routes (extra CORS safety)
    @app.route('/<path:path>', methods=['OPTIONS'])
    def handle_options(path):
        response = jsonify({})
        response.headers.add('Access-Control-Allow-Origin', '*')
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
        response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS')
        return response
    
    return app