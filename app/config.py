# # =====================================================
# # DATABASE CONNECTION
# # =====================================================
# import os
# from flask import Flask
# from flask_cors import CORS
# from flask_sqlalchemy import SQLAlchemy
# from flask_bcrypt import Bcrypt
# from datetime import timedelta

# # Database configuration
# DATABASE_URL = os.getenv('DATABASE_URL', 'postgresql://postgres:098%40Gangahanjra@localhost:5432/sjs_academy')

# app = Flask(__name__)

# # App configurations
# app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE_URL
# app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
# app.config['JWT_SECRET_KEY'] = os.getenv('JWT_SECRET_KEY', 'sjs-academy-secret-key')
# app.config['UPLOAD_FOLDER'] = 'uploads/screenshots'
# app.config['MAX_CONTENT_LENGTH'] = 5 * 1024 * 1024

# # JWT Configuration
# app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(days=30)

# # Create upload folder
# os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# # Initialize extensions with proper CORS configuration
# CORS(app, 
#      origins=["http://localhost:3000", "http://127.0.0.1:3000"],
#      supports_credentials=True,
#      allow_headers=["Content-Type", "Authorization", "X-Requested-With"],
#      methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
#      expose_headers=["Content-Type", "Authorization"])

# db = SQLAlchemy(app)
# bcrypt = Bcrypt(app)




# =====================================================
# DATABASE CONNECTION
# =====================================================
import os
from flask import Flask
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from datetime import timedelta

# Database configuration
DATABASE_URL = os.getenv('DATABASE_URL', 'postgresql://postgres:098%40Gangahanjra@localhost:5432/sjs_academy')

app = Flask(__name__)

# App configurations
app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE_URL
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['JWT_SECRET_KEY'] = os.getenv('JWT_SECRET_KEY', 'sjs-academy-secret-key')
app.config['UPLOAD_FOLDER'] = 'uploads/screenshots'
app.config['MAX_CONTENT_LENGTH'] = 5 * 1024 * 1024

# JWT Configuration
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(days=30)

# Create upload folder
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# =====================================================
# CORS Configuration - FIXED ✅
# =====================================================

# Allowed origins (Production + Development)
ALLOWED_ORIGINS = [
    "https://sjsglobaltech.com",
    "https://www.sjsglobaltech.com",
    "https://sjs-frontend-delta.vercel.app",
    "https://sjs-frontend.vercel.app",
    "http://localhost:3000",
    "http://127.0.0.1:3000",
    "http://localhost:5173"
]

# Initialize extensions with proper CORS configuration
CORS(app, 
     origins=ALLOWED_ORIGINS,
     supports_credentials=True,
     allow_headers=["Content-Type", "Authorization", "X-Requested-With", "Accept"],
     methods=["GET", "POST", "PUT", "DELETE", "OPTIONS", "PATCH"],
     expose_headers=["Content-Type", "Authorization"],
     max_age=3600)

print(f"✅ CORS configured with origins: {ALLOWED_ORIGINS}")

db = SQLAlchemy(app)
bcrypt = Bcrypt(app)