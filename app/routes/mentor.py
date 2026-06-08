from flask import Blueprint, request, jsonify, send_from_directory
from app.utils.decorators import token_required
import os

mentor_bp = Blueprint('mentor', __name__)

# Sample mentor data
MENTORS = [
    {
        'id': 1,
        'name': 'Dr. Sarah Johnson',
        'role': 'Founder & Lead Data Scientist',
        'bio': 'PhD in Computer Science with over 15 years of experience in Data Science and AI. Former Senior Data Scientist at Google.',
        'expertise': ['Data Science', 'Machine Learning', 'Deep Learning', 'Python'],
        'experience': '15+ years',
        'students_trained': 5000,
        'rating': 4.9,
        'image': 'mentors/sarah.jpg',
        'email': 'sarah@sjsacademy.com',
        'linkedin': 'https://linkedin.com/in/sarah-johnson',
        'github': 'https://github.com/sarahjohnson'
    },
    {
        'id': 2,
        'name': 'Prof. Michael Chen',
        'role': 'AI Research Director',
        'bio': 'Former AI researcher at MIT, specializing in Natural Language Processing and Computer Vision.',
        'expertise': ['NLP', 'Computer Vision', 'TensorFlow', 'PyTorch'],
        'experience': '12+ years',
        'students_trained': 3500,
        'rating': 4.8,
        'image': 'mentors/michael.jpg',
        'email': 'michael@sjsacademy.com',
        'linkedin': 'https://linkedin.com/in/michael-chen',
        'github': 'https://github.com/michaelchen'
    },
    {
        'id': 3,
        'name': 'Dr. Emily Rodriguez',
        'role': 'Lead Web Development Mentor',
        'bio': 'Full-stack developer with expertise in React, Node.js, and cloud architecture.',
        'expertise': ['React', 'Node.js', 'MongoDB', 'AWS'],
        'experience': '10+ years',
        'students_trained': 4200,
        'rating': 4.9,
        'image': 'mentors/emily.jpg',
        'email': 'emily@sjsacademy.com',
        'linkedin': 'https://linkedin.com/in/emily-rodriguez',
        'github': 'https://github.com/emilyrod'
    },
    {
        'id': 4,
        'name': 'Dr. Harshdeep Singh',
        'role': 'Founder & CEO',
        'bio': 'Visionary leader in tech education, dedicated to empowering students with cutting-edge skills.',
        'expertise': ['Leadership', 'Business Strategy', 'Tech Education'],
        'experience': '8+ years',
        'students_trained': 10000,
        'rating': 5.0,
        'image': 'mentors/founder.jpg',
        'email': 'harshdeep@sjsacademy.com',
        'linkedin': 'https://linkedin.com/in/harshdeep-singh',
        'github': 'https://github.com/harshdeep'
    }
]

@mentor_bp.route('/api/mentor/info', methods=['GET', 'OPTIONS'])
def get_mentor_info():
    if request.method == 'OPTIONS':
        return '', 200
    
    try:
        return jsonify({
            'success': True,
            'mentors': MENTORS
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@mentor_bp.route('/api/mentor/<int:mentor_id>', methods=['GET', 'OPTIONS'])
def get_mentor_details(mentor_id):
    if request.method == 'OPTIONS':
        return '', 200
    
    try:
        mentor = next((m for m in MENTORS if m['id'] == mentor_id), None)
        if mentor:
            return jsonify({
                'success': True,
                'mentor': mentor
            }), 200
        return jsonify({'error': 'Mentor not found'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    
@mentor_bp.route('/api/mentor/placeholder', methods=['GET'])
def get_placeholder():
    """Return a placeholder image"""
    from flask import send_file
    from io import BytesIO
    from PIL import Image, ImageDraw
    
    img = Image.new('RGB', (400, 400), color='#3498db')
    draw = ImageDraw.Draw(img)
    draw.ellipse([50, 50, 350, 350], fill='#3498db', outline='white', width=3)
    
    img_io = BytesIO()
    img.save(img_io, 'PNG')
    img_io.seek(0)
    
    return send_file(img_io, mimetype='image/png')

@mentor_bp.route('/uploads/mentors/<filename>')
def get_mentor_image(filename):
    """Serve mentor images"""
    # Create a default image if not exists
    upload_folder = 'uploads/mentors'
    os.makedirs(upload_folder, exist_ok=True)
    
    filepath = os.path.join(upload_folder, filename)
    if not os.path.exists(filepath):
        # Return a default image or placeholder
        return jsonify({'error': 'Image not found'}), 404
    
    return send_from_directory(upload_folder, filename)