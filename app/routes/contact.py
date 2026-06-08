from flask import Blueprint, request, jsonify
from app import mail
from flask_mail import Message
from app.utils.decorators import token_required
import os
from datetime import datetime

contact_bp = Blueprint('contact', __name__)

# ✅ FIXED: Remove duplicate /contact/ - route will be /api/contact/send
@contact_bp.route('/send', methods=['POST', 'OPTIONS'])
def send_contact_email():
    if request.method == 'OPTIONS':
        return '', 200
    
    try:
        data = request.get_json()
        name = data.get('name')
        email = data.get('email')
        message = data.get('message')
        phone = data.get('phone', '')
        
        if not name or not email or not message:
            return jsonify({'error': 'Name, email, and message are required'}), 400
        
        # Get frontend URL from environment
        frontend_url = os.getenv('FRONTEND_URL', 'https://sjs-frontend-delta.vercel.app')
        
        # Create email to send to sjsglobaltech@gmail.com
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <style>
                body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
                .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                .header {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                          color: white; padding: 30px; text-align: center; }}
                .content {{ padding: 30px; background: #f9f9f9; }}
                .footer {{ text-align: center; padding: 20px; font-size: 12px; color: #666; }}
                .info-box {{ background: white; padding: 15px; margin: 10px 0; border-radius: 8px; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>New Contact Form Message</h1>
                    <p>SJS Global Tech Academy</p>
                </div>
                <div class="content">
                    <div class="info-box">
                        <h3>Sender Information:</h3>
                        <p><strong>Name:</strong> {name}</p>
                        <p><strong>Email:</strong> {email}</p>
                        {f'<p><strong>Phone:</strong> {phone}</p>' if phone else ''}
                        <p><strong>Date:</strong> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
                    </div>
                    <div class="info-box">
                        <h3>Message:</h3>
                        <p>{message.replace(chr(10), '<br>')}</p>
                    </div>
                </div>
                <div class="footer">
                    <p>This message was sent from the SJS Global Tech Academy website contact form.</p>
                    <p>© 2024 SJS Global Tech Academy. All rights reserved.</p>
                </div>
            </div>
        </body>
        </html>
        """
        
        text_content = f"""
        New Contact Form Message
        {'='*40}
        
        From: {name}
        Email: {email}
        {'Phone: ' + phone if phone else ''}
        Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
        
        Message:
        {message}
        
        {'='*40}
        This message was sent from the SJS Global Tech Academy website contact form.
        """
        
        # Send email to sjsglobaltech@gmail.com
        msg = Message(
            subject=f"New Contact Form Message from {name}",
            recipients=['sjsglobaltech@gmail.com'],
            html=html_content,
            body=text_content,
            reply_to=email
        )
        
        mail.send(msg)
        
        # Send auto-reply to the user
        auto_reply_html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <style>
                body {{ font-family: Arial, sans-serif; line-height: 1.6; }}
                .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                .header {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                          color: white; padding: 30px; text-align: center; }}
                .content {{ padding: 30px; }}
                .footer {{ text-align: center; padding: 20px; font-size: 12px; color: #666; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>Thank You for Contacting Us!</h1>
                    <p>SJS Global Tech Academy</p>
                </div>
                <div class="content">
                    <p>Dear <strong>{name}</strong>,</p>
                    <p>Thank you for reaching out to SJS Global Tech Academy. We have received your message and will get back to you within 24 hours.</p>
                    <p>Here's a copy of your message:</p>
                    <div style="background: #f9f9f9; padding: 15px; border-left: 4px solid #667eea; margin: 15px 0;">
                        <p>{message}</p>
                    </div>
                    <p>In the meantime, feel free to:</p>
                    <ul>
                        <li>Browse our courses at <a href="{frontend_url}/courses">{frontend_url}/courses</a></li>
                        <li>Check out our internship opportunities</li>
                        <li>Follow us on social media for updates</li>
                    </ul>
                    <p>Best regards,<br>
                    <strong>SJS Global Tech Academy Team</strong></p>
                </div>
                <div class="footer">
                    <p>© 2024 SJS Global Tech Academy. All rights reserved.</p>
                    <p>This is an automated response, please do not reply directly to this email.</p>
                </div>
            </div>
        </body>
        </html>
        """
        
        auto_reply = Message(
            subject="Thank you for contacting SJS Global Tech Academy",
            recipients=[email],
            html=auto_reply_html,
            body=f"Thank you for contacting us, {name}!\n\nWe have received your message and will get back to you within 24 hours.\n\nYour message:\n{message}\n\nBest regards,\nSJS Global Tech Academy Team"
        )
        
        mail.send(auto_reply)
        
        return jsonify({
            'success': True,
            'message': 'Message sent successfully! We will get back to you soon.'
        }), 200
        
    except Exception as e:
        print(f"Error sending email: {e}")
        return jsonify({'error': str(e)}), 500