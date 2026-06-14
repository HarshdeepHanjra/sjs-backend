# import os
# from unittest import result

# from flask import Blueprint, request, jsonify
# from app import db
# from app.models.user import Student
# from app.models.internship import Internship, InternshipOrder, InternshipEnrollment
# from app.models.payment import PaymentVerification
# from app.utils.helpers import generate_order_id, generate_verification_id
# from app.utils.decorators import token_required, admin_required
# from datetime import datetime
# from werkzeug.utils import secure_filename
# import cloudinary.uploader

# internships_bp = Blueprint("internships", __name__)

# ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "gif", "webp"}


# def allowed_file(filename):
#     """Check if file extension is allowed"""
#     return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


# @internships_bp.route("/test", methods=["GET", "OPTIONS"])
# def test_internship_route():
#     if request.method == "OPTIONS":
#         return "", 200
#     return jsonify({"status": "ok", "message": "Internship route working"}), 200


# # ✅ FIXED: Remove duplicate /internships/ - route will be /api/internships
# @internships_bp.route("", methods=["GET", "OPTIONS"])
# @internships_bp.route("/", methods=["GET", "OPTIONS"])
# def get_internships():
#     if request.method == "OPTIONS":
#         return "", 200

#     internships = Internship.query.filter_by(is_active=True).all()

#     if internships:
#         return (
#             jsonify(
#                 {
#                     "success": True,
#                     "internships": [
#                         {
#                             "id": i.id,
#                             "title": i.title,
#                             "category": i.category,
#                             "duration": i.duration,
#                             "fee": float(i.fee),
#                             "original_fee": (
#                                 float(i.original_fee) if i.original_fee else None
#                             ),
#                             "stipend": i.stipend,
#                             "mode": i.mode,
#                             "slots": i.slots,
#                             "enrolled": i.enrolled,
#                             "rating": float(i.rating),
#                             "description": i.description,
#                             "benefits": i.benefits or [],
#                         }
#                         for i in internships
#                     ],
#                 }
#             ),
#             200,
#         )
#     else:
#         # Default internship data
#         default_internships = [
#             {
#                 "id": 1,
#                 "title": "Data Science Internship",
#                 "category": "Data Science",
#                 "duration": "3 Months",
#                 "fee": 6000,
#                 "original_fee": 19999,
#                 "stipend": "Unpaid",
#                 "mode": "Online",
#                 "slots": 50,
#                 "enrolled": 234,
#                 "rating": 4.9,
#                 "description": "Learn Data Science from scratch with real-world projects.",
#                 "benefits": ["With Certification", "Live Projects", "Industry Mentors"],
#             },
#             {
#                 "id": 2,
#                 "title": "Web Development Internship",
#                 "category": "Development",
#                 "duration": "2 Months",
#                 "fee": 0,
#                 "original_fee": 14999,
#                 "stipend": "Unpaid",
#                 "mode": "Online",
#                 "slots": 40,
#                 "enrolled": 156,
#                 "rating": 4.8,
#                 "description": "Master MERN stack development.",
#                 "benefits": [
#                     "Live Coding Sessions",
#                     "Portfolio Development",
#                     "Certificate",
#                 ],
#             },
#         ]
#         return jsonify({"success": True, "internships": default_internships}), 200


# @internships_bp.route("/<int:internship_id>", methods=["GET", "OPTIONS"])
# def get_internship_detail(internship_id):
#     if request.method == "OPTIONS":
#         return "", 200

#     internship = Internship.query.get(internship_id)

#     if internship:
#         return (
#             jsonify(
#                 {
#                     "success": True,
#                     "internship": {
#                         "id": internship.id,
#                         "title": internship.title,
#                         "category": internship.category,
#                         "duration": internship.duration,
#                         "fee": float(internship.fee),
#                         "original_fee": (
#                             float(internship.original_fee)
#                             if internship.original_fee
#                             else None
#                         ),
#                         "stipend": internship.stipend,
#                         "mode": internship.mode,
#                         "slots": internship.slots,
#                         "enrolled": internship.enrolled,
#                         "rating": float(internship.rating),
#                         "description": internship.description,
#                         "syllabus": internship.syllabus or [],
#                         "benefits": internship.benefits or [],
#                         "requirements": internship.requirements or [],
#                     },
#                 }
#             ),
#             200,
#         )
#     else:
#         return jsonify({"error": "Internship not found"}), 404


# @internships_bp.route("/create-order", methods=["POST", "OPTIONS"])
# @token_required
# def create_internship_order():
#     if request.method == "OPTIONS":
#         return "", 200

#     try:
#         data = request.get_json()
#         user = request.user

#         internship_id = data.get("internship_id")
#         internship_title = data.get("internship_title")
#         amount = data.get("amount", 0)
#         phone = data.get("phone", "")

#         student = Student.query.get(user["id"])
#         if not student:
#             return jsonify({"error": "Student not found"}), 404

#         order_id = generate_order_id()

#         new_order = InternshipOrder(
#             order_id=order_id,
#             student_id=student.id,
#             student_name=student.name,
#             student_email=student.email,
#             student_phone=phone,
#             internship_id=internship_id,
#             internship_title=internship_title,
#             amount=amount,
#             payment_status="pending",
#         )

#         db.session.add(new_order)
#         db.session.commit()

#         print(
#             f"✅ Internship order created: {order_id} for student {student.name} (ID: {student.id})"
#         )

#         return (
#             jsonify(
#                 {
#                     "success": True,
#                     "message": "Order created successfully!",
#                     "order_id": order_id,
#                     "amount": amount,
#                     "internship_title": internship_title,
#                 }
#             ),
#             200,
#         )

#     except Exception as e:
#         db.session.rollback()
#         print(f"Error creating internship order: {e}")
#         import traceback

#         traceback.print_exc()
#         return jsonify({"error": str(e)}), 500


# @internships_bp.route("/enroll-free", methods=["POST", "OPTIONS"])
# @token_required
# def enroll_free_internship():
#     """Enroll in free internship"""
#     if request.method == "OPTIONS":
#         return "", 200

#     try:
#         data = request.get_json()
#         internship_id = data.get("internship_id")
#         internship_title = data.get("internship_title")

#         user = request.user
#         student = Student.query.get(user["id"])

#         if not student:
#             return jsonify({"error": "Student not found"}), 404

#         if student.internship_ids and internship_id in student.internship_ids:
#             return jsonify({"error": "Already enrolled in this internship"}), 400

#         order_id = generate_order_id()

#         new_order = InternshipOrder(
#             order_id=order_id,
#             student_id=student.id,
#             student_name=student.name,
#             student_email=student.email,
#             internship_id=internship_id,
#             internship_title=internship_title,
#             amount=0,
#             payment_status="completed",
#             status="active",
#         )

#         db.session.add(new_order)

#         if student.internship_ids is None:
#             student.internship_ids = []
#         if internship_id not in student.internship_ids:
#             student.internship_ids.append(internship_id)

#         db.session.commit()

#         return (
#             jsonify(
#                 {
#                     "success": True,
#                     "message": "Successfully enrolled in free internship!",
#                 }
#             ),
#             200,
#         )

#     except Exception as e:
#         db.session.rollback()
#         print(f"Enroll free error: {e}")
#         return jsonify({"error": str(e)}), 500


# @internships_bp.route("/upload-screenshot", methods=["POST", "OPTIONS"])
# @token_required
# def upload_internship_screenshot():
#     """Upload internship payment screenshot from frontend"""
#     if request.method == "OPTIONS":
#         return "", 200

#     try:
#         if "screenshot" not in request.files:
#             return jsonify({"error": "No file uploaded"}), 400

#         file = request.files["screenshot"]
#         order_id = request.form.get("order_id")

#         if not order_id:
#             return jsonify({"error": "Order ID is required"}), 400

#         if file.filename == "":
#             return jsonify({"error": "No file selected"}), 400

#         if not allowed_file(file.filename):
#             return (
#                 jsonify(
#                     {"error": "Invalid file type. Allowed: png, jpg, jpeg, gif, webp"}
#                 ),
#                 400,
#             )

#         original_filename = secure_filename(file.filename)
#         timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
#         filename = f"{order_id}_{timestamp}_{original_filename}"

#         result = cloudinary.uploader.upload(file, folder="internship_screenshots")

#         screenshot_url = result["secure_url"]

#         print(f"Cloudinary URL: {screenshot_url}")

#         internship_order = InternshipOrder.query.filter_by(order_id=order_id).first()
#         if internship_order:
#             internship_order.screenshot_url = screenshot_url
#             db.session.commit()
#             print(f"   Updated internship order: {order_id}")
#         else:
#             print(f"   Warning: Internship order not found: {order_id}")

#         return (
#             jsonify(
#                 {
#                     "success": True,
#                     "screenshot_url": screenshot_url,
#                     "message": "Internship payment screenshot uploaded successfully",
#                 }
#             ),
#             200,
#         )

#     except Exception as e:
#         print(f"Internship upload error: {e}")
#         import traceback

#         traceback.print_exc()
#         return jsonify({"error": str(e)}), 500


# @internships_bp.route("/verify-payment", methods=["POST", "OPTIONS"])
# @token_required
# def verify_internship_payment():
#     if request.method == "OPTIONS":
#         return "", 200

#     try:
#         data = request.get_json()
#         user = request.user
#         order_id = data.get("order_id")

#         internship_order = InternshipOrder.query.filter_by(
#             order_id=order_id, student_id=user["id"]
#         ).first()

#         if not internship_order:
#             return jsonify({"error": "Order not found"}), 404

#         verification_id = generate_verification_id()

#         verification = PaymentVerification(
#             verification_id=verification_id,
#             order_id=order_id,
#             student_id=user["id"],
#             student_name=internship_order.student_name,
#             student_email=internship_order.student_email,
#             amount=internship_order.amount,
#             transaction_id=f"TXN_{datetime.now().strftime('%Y%m%d%H%M%S')}",
#             screenshot_url=internship_order.screenshot_url,
#             status="pending",
#         )

#         db.session.add(verification)
#         internship_order.payment_status = "pending_verification"

#         db.session.commit()

#         return (
#             jsonify(
#                 {
#                     "success": True,
#                     "message": "Payment verification submitted!",
#                     "verification_id": verification_id,
#                 }
#             ),
#             200,
#         )

#     except Exception as e:
#         db.session.rollback()
#         print(f"Error verifying internship payment: {e}")
#         return jsonify({"error": str(e)}), 500


# # ✅ FIXED: Route for student's my-internships
# @internships_bp.route("/my-internships", methods=["GET", "OPTIONS"])
# @token_required
# def get_my_internships():
#     """Get all internships the student is enrolled in"""
#     if request.method == "OPTIONS":
#         return "", 200

#     try:
#         user = request.user
#         student = Student.query.get(user["id"])

#         if not student:
#             return jsonify({"error": "Student not found"}), 404

#         internships_list = []

#         # Get from internship_ids JSON field
#         if student.internship_ids and len(student.internship_ids) > 0:
#             for internship_id in student.internship_ids:
#                 internship = Internship.query.get(internship_id)
#                 if internship:
#                     internships_list.append(
#                         {
#                             "id": internship.id,
#                             "title": internship.title,
#                             "duration": internship.duration,
#                             "description": internship.description,
#                             "mode": internship.mode,
#                             "fee": float(internship.fee),
#                             "status": "active",
#                             "enrolled_at": datetime.utcnow().isoformat(),
#                         }
#                     )

#         # Also get from InternshipOrder table for completed payments
#         orders = InternshipOrder.query.filter_by(
#             student_id=student.id, payment_status="completed"
#         ).all()

#         for order in orders:
#             internship = Internship.query.get(order.internship_id)
#             if internship:
#                 if not any(i.get("id") == internship.id for i in internships_list):
#                     internships_list.append(
#                         {
#                             "id": internship.id,
#                             "title": internship.title,
#                             "duration": internship.duration,
#                             "description": internship.description,
#                             "mode": internship.mode,
#                             "fee": float(internship.fee),
#                             "status": order.status or "active",
#                             "enrolled_at": (
#                                 order.created_at.isoformat()
#                                 if order.created_at
#                                 else None
#                             ),
#                         }
#                     )

#         return (
#             jsonify(
#                 {
#                     "success": True,
#                     "internships": internships_list,
#                     "count": len(internships_list),
#                 }
#             ),
#             200,
#         )

#     except Exception as e:
#         print(f"Error getting my internships: {e}")
#         return jsonify({"error": str(e), "internships": []}), 500




import os
from unittest import result

from flask import Blueprint, request, jsonify
from app import db
from app.models.user import Student
from app.models.internship import Internship, InternshipOrder, InternshipEnrollment
from app.models.payment import PaymentVerification
from app.utils.helpers import generate_order_id, generate_verification_id
from app.utils.decorators import token_required, admin_required
from datetime import datetime
from werkzeug.utils import secure_filename
import cloudinary.uploader
import json

internships_bp = Blueprint("internships", __name__)

ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "gif", "webp"}


def allowed_file(filename):
    """Check if file extension is allowed"""
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


@internships_bp.route("/test", methods=["GET", "OPTIONS"])
def test_internship_route():
    if request.method == "OPTIONS":
        return "", 200
    return jsonify({"status": "ok", "message": "Internship route working"}), 200


# ✅ FIXED: Remove duplicate /internships/ - route will be /api/internships
@internships_bp.route("", methods=["GET", "OPTIONS"])
@internships_bp.route("/", methods=["GET", "OPTIONS"])
def get_internships():
    if request.method == "OPTIONS":
        return "", 200

    internships = Internship.query.filter_by(is_active=True).all()

    if internships:
        return (
            jsonify(
                {
                    "success": True,
                    "internships": [
                        {
                            "id": i.id,
                            "title": i.title,
                            "category": i.category,
                            "duration": i.duration,
                            "fee": float(i.fee),
                            "original_fee": (
                                float(i.original_fee) if i.original_fee else None
                            ),
                            "stipend": i.stipend,
                            "mode": i.mode,
                            "slots": i.slots,
                            "enrolled": i.enrolled,
                            "rating": float(i.rating),
                            "description": i.description,
                            "benefits": i.benefits or [],
                        }
                        for i in internships
                    ],
                }
            ),
            200,
        )
    else:
        # Default internship data
        default_internships = [
            {
                "id": 1,
                "title": "Data Science Internship",
                "category": "Data Science",
                "duration": "3 Months",
                "fee": 6000,
                "original_fee": 19999,
                "stipend": "Unpaid",
                "mode": "Online",
                "slots": 50,
                "enrolled": 234,
                "rating": 4.9,
                "description": "Learn Data Science from scratch with real-world projects.",
                "benefits": ["With Certification", "Live Projects", "Industry Mentors"],
            },
            {
                "id": 2,
                "title": "Web Development Internship",
                "category": "Development",
                "duration": "2 Months",
                "fee": 0,
                "original_fee": 14999,
                "stipend": "Unpaid",
                "mode": "Online",
                "slots": 40,
                "enrolled": 156,
                "rating": 4.8,
                "description": "Master MERN stack development.",
                "benefits": [
                    "Live Coding Sessions",
                    "Portfolio Development",
                    "Certificate",
                ],
            },
        ]
        return jsonify({"success": True, "internships": default_internships}), 200


@internships_bp.route("/<int:internship_id>", methods=["GET", "OPTIONS"])
def get_internship_detail(internship_id):
    if request.method == "OPTIONS":
        return "", 200

    internship = Internship.query.get(internship_id)

    if internship:
        return (
            jsonify(
                {
                    "success": True,
                    "internship": {
                        "id": internship.id,
                        "title": internship.title,
                        "category": internship.category,
                        "duration": internship.duration,
                        "fee": float(internship.fee),
                        "original_fee": (
                            float(internship.original_fee)
                            if internship.original_fee
                            else None
                        ),
                        "stipend": internship.stipend,
                        "mode": internship.mode,
                        "slots": internship.slots,
                        "enrolled": internship.enrolled,
                        "rating": float(internship.rating),
                        "description": internship.description,
                        "syllabus": internship.syllabus or [],
                        "benefits": internship.benefits or [],
                        "requirements": internship.requirements or [],
                    },
                }
            ),
            200,
        )
    else:
        return jsonify({"error": "Internship not found"}), 404


@internships_bp.route("/create-order", methods=["POST", "OPTIONS"])
@token_required
def create_internship_order():
    if request.method == "OPTIONS":
        return "", 200

    try:
        data = request.get_json()
        user = request.user

        internship_id = data.get("internship_id")
        internship_title = data.get("internship_title")
        amount = data.get("amount", 0)
        phone = data.get("phone", "")

        student = Student.query.get(user["id"])
        if not student:
            return jsonify({"error": "Student not found"}), 404

        order_id = generate_order_id()

        new_order = InternshipOrder(
            order_id=order_id,
            student_id=student.id,
            student_name=student.name,
            student_email=student.email,
            student_phone=phone,
            internship_id=internship_id,
            internship_title=internship_title,
            amount=amount,
            payment_status="pending",
        )

        db.session.add(new_order)
        db.session.commit()

        print(
            f"✅ Internship order created: {order_id} for student {student.name} (ID: {student.id})"
        )

        return (
            jsonify(
                {
                    "success": True,
                    "message": "Order created successfully!",
                    "order_id": order_id,
                    "amount": amount,
                    "internship_title": internship_title,
                }
            ),
            200,
        )

    except Exception as e:
        db.session.rollback()
        print(f"Error creating internship order: {e}")
        import traceback

        traceback.print_exc()
        return jsonify({"error": str(e)}), 500


@internships_bp.route("/enroll-free", methods=["POST", "OPTIONS"])
@token_required
def enroll_free_internship():
    """Enroll in free internship"""
    if request.method == "OPTIONS":
        return "", 200

    try:
        data = request.get_json()
        internship_id = data.get("internship_id")
        internship_title = data.get("internship_title")

        user = request.user
        student = Student.query.get(user["id"])

        if not student:
            return jsonify({"error": "Student not found"}), 404

        if student.internship_ids and internship_id in student.internship_ids:
            return jsonify({"error": "Already enrolled in this internship"}), 400

        order_id = generate_order_id()

        new_order = InternshipOrder(
            order_id=order_id,
            student_id=student.id,
            student_name=student.name,
            student_email=student.email,
            internship_id=internship_id,
            internship_title=internship_title,
            amount=0,
            payment_status="completed",
            status="active",
        )

        db.session.add(new_order)

        if student.internship_ids is None:
            student.internship_ids = []
        if internship_id not in student.internship_ids:
            student.internship_ids.append(internship_id)

        db.session.commit()

        return (
            jsonify(
                {
                    "success": True,
                    "message": "Successfully enrolled in free internship!",
                }
            ),
            200,
        )

    except Exception as e:
        db.session.rollback()
        print(f"Enroll free error: {e}")
        return jsonify({"error": str(e)}), 500


@internships_bp.route("/upload-screenshot", methods=["POST", "OPTIONS"])
@token_required
def upload_internship_screenshot():
    """Upload internship payment screenshot from frontend"""
    if request.method == "OPTIONS":
        return "", 200

    try:
        if "screenshot" not in request.files:
            return jsonify({"error": "No file uploaded"}), 400

        file = request.files["screenshot"]
        order_id = request.form.get("order_id")

        if not order_id:
            return jsonify({"error": "Order ID is required"}), 400

        if file.filename == "":
            return jsonify({"error": "No file selected"}), 400

        if not allowed_file(file.filename):
            return (
                jsonify(
                    {"error": "Invalid file type. Allowed: png, jpg, jpeg, gif, webp"}
                ),
                400,
            )

        original_filename = secure_filename(file.filename)
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        filename = f"{order_id}_{timestamp}_{original_filename}"

        result = cloudinary.uploader.upload(file, folder="internship_screenshots")

        screenshot_url = result["secure_url"]

        print(f"Cloudinary URL: {screenshot_url}")

        internship_order = InternshipOrder.query.filter_by(order_id=order_id).first()
        if internship_order:
            internship_order.screenshot_url = screenshot_url
            db.session.commit()
            print(f"   Updated internship order: {order_id}")
        else:
            print(f"   Warning: Internship order not found: {order_id}")

        return (
            jsonify(
                {
                    "success": True,
                    "screenshot_url": screenshot_url,
                    "message": "Internship payment screenshot uploaded successfully",
                }
            ),
            200,
        )

    except Exception as e:
        print(f"Internship upload error: {e}")
        import traceback

        traceback.print_exc()
        return jsonify({"error": str(e)}), 500


@internships_bp.route("/verify-payment", methods=["POST", "OPTIONS"])
@token_required
def verify_internship_payment():
    if request.method == "OPTIONS":
        return "", 200

    try:
        data = request.get_json()
        user = request.user
        order_id = data.get("order_id")

        internship_order = InternshipOrder.query.filter_by(
            order_id=order_id, student_id=user["id"]
        ).first()

        if not internship_order:
            return jsonify({"error": "Order not found"}), 404

        verification_id = generate_verification_id()

        verification = PaymentVerification(
            verification_id=verification_id,
            order_id=order_id,
            student_id=user["id"],
            student_name=internship_order.student_name,
            student_email=internship_order.student_email,
            amount=internship_order.amount,
            transaction_id=f"TXN_{datetime.now().strftime('%Y%m%d%H%M%S')}",
            screenshot_url=internship_order.screenshot_url,
            status="pending",
        )

        db.session.add(verification)
        internship_order.payment_status = "pending_verification"

        db.session.commit()

        return (
            jsonify(
                {
                    "success": True,
                    "message": "Payment verification submitted!",
                    "verification_id": verification_id,
                }
            ),
            200,
        )

    except Exception as e:
        db.session.rollback()
        print(f"Error verifying internship payment: {e}")
        return jsonify({"error": str(e)}), 500


# ✅ FIXED: Route for student's my-internships
@internships_bp.route("/my-internships", methods=["GET", "OPTIONS"])
@token_required
def get_my_internships():
    """Get all internships the student is enrolled in"""
    if request.method == "OPTIONS":
        return "", 200

    try:
        user = request.user
        student = Student.query.get(user["id"])

        if not student:
            return jsonify({"error": "Student not found"}), 404

        internships_list = []

        # Get from internship_ids JSON field
        if student.internship_ids and len(student.internship_ids) > 0:
            for internship_id in student.internship_ids:
                internship = Internship.query.get(internship_id)
                if internship:
                    internships_list.append(
                        {
                            "id": internship.id,
                            "title": internship.title,
                            "duration": internship.duration,
                            "description": internship.description,
                            "mode": internship.mode,
                            "fee": float(internship.fee),
                            "status": "active",
                            "enrolled_at": datetime.utcnow().isoformat(),
                        }
                    )

        # Also get from InternshipOrder table for completed payments
        orders = InternshipOrder.query.filter_by(
            student_id=student.id, payment_status="completed"
        ).all()

        for order in orders:
            internship = Internship.query.get(order.internship_id)
            if internship:
                if not any(i.get("id") == internship.id for i in internships_list):
                    internships_list.append(
                        {
                            "id": internship.id,
                            "title": internship.title,
                            "duration": internship.duration,
                            "description": internship.description,
                            "mode": internship.mode,
                            "fee": float(internship.fee),
                            "status": order.status or "active",
                            "enrolled_at": (
                                order.created_at.isoformat()
                                if order.created_at
                                else None
                            ),
                        }
                    )

        return (
            jsonify(
                {
                    "success": True,
                    "internships": internships_list,
                    "count": len(internships_list),
                }
            ),
            200,
        )

    except Exception as e:
        print(f"Error getting my internships: {e}")
        return jsonify({"error": str(e), "internships": []}), 500


# ==================== ADMIN INTERNSHIP MANAGEMENT ROUTES ====================

@internships_bp.route("/admin/all", methods=["GET", "OPTIONS"])
@token_required
@admin_required
def admin_get_all_internships():
    """Get all internships (admin only)"""
    if request.method == "OPTIONS":
        return "", 200

    try:
        internships = Internship.query.order_by(Internship.created_at.desc()).all()
        
        return jsonify({
            "success": True,
            "internships": [
                {
                    "id": i.id,
                    "title": i.title,
                    "category": i.category,
                    "duration": i.duration,
                    "fee": float(i.fee),
                    "original_fee": float(i.original_fee) if i.original_fee else None,
                    "stipend": i.stipend,
                    "mode": i.mode,
                    "start_date": i.start_date,
                    "slots": i.slots,
                    "enrolled": i.enrolled,
                    "rating": float(i.rating),
                    "description": i.description,
                    "syllabus": i.syllabus or [],
                    "benefits": i.benefits or [],
                    "requirements": i.requirements or [],
                    "is_active": i.is_active,
                    "created_at": i.created_at.isoformat() if i.created_at else None,
                    "updated_at": i.updated_at.isoformat() if hasattr(i, 'updated_at') and i.updated_at else None
                }
                for i in internships
            ]
        }), 200
    except Exception as e:
        print(f"Error fetching all internships: {e}")
        return jsonify({"success": False, "message": str(e)}), 500


@internships_bp.route("/admin/create", methods=["POST", "OPTIONS"])
@token_required
@admin_required
def admin_create_internship():
    """Create a new internship (admin only)"""
    if request.method == "OPTIONS":
        return "", 200

    try:
        data = request.get_json()
        
        # Handle syllabus, benefits, requirements (can be JSON arrays or strings)
        syllabus = data.get("syllabus", [])
        if isinstance(syllabus, str):
            syllabus = [s.strip() for s in syllabus.split(',') if s.strip()]
        
        benefits = data.get("benefits", [])
        if isinstance(benefits, str):
            benefits = [b.strip() for b in benefits.split(',') if b.strip()]
        
        requirements = data.get("requirements", [])
        if isinstance(requirements, str):
            requirements = [r.strip() for r in requirements.split(',') if r.strip()]
        
        new_internship = Internship(
            title=data.get("title"),
            category=data.get("category"),
            duration=data.get("duration"),
            fee=float(data.get("fee", 0)),
            original_fee=float(data.get("original_fee", 0)) if data.get("original_fee") else None,
            stipend=data.get("stipend", "Unpaid"),
            mode=data.get("mode", "Online"),
            start_date=data.get("start_date", "Monthly Batch"),
            slots=int(data.get("slots", 0)),
            enrolled=int(data.get("enrolled", 0)),
            rating=float(data.get("rating", 4.5)),
            description=data.get("description"),
            syllabus=syllabus,
            benefits=benefits,
            requirements=requirements,
            is_active=data.get("is_active", True)
        )
        
        db.session.add(new_internship)
        db.session.commit()
        
        return jsonify({
            "success": True,
            "message": "Internship created successfully",
            "internship": {
                "id": new_internship.id,
                "title": new_internship.title,
                "category": new_internship.category,
                "duration": new_internship.duration,
                "fee": float(new_internship.fee),
                "is_active": new_internship.is_active
            }
        }), 201
        
    except Exception as e:
        db.session.rollback()
        print(f"Error creating internship: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({"success": False, "message": str(e)}), 500


@internships_bp.route("/admin/update/<int:internship_id>", methods=["PUT", "OPTIONS"])
@token_required
@admin_required
def admin_update_internship(internship_id):
    """Update an existing internship (admin only)"""
    if request.method == "OPTIONS":
        return "", 200

    try:
        internship = Internship.query.get(internship_id)
        
        if not internship:
            return jsonify({"success": False, "message": "Internship not found"}), 404
        
        data = request.get_json()
        
        # Update fields if provided
        if "title" in data:
            internship.title = data["title"]
        if "category" in data:
            internship.category = data["category"]
        if "duration" in data:
            internship.duration = data["duration"]
        if "fee" in data:
            internship.fee = float(data["fee"])
        if "original_fee" in data:
            internship.original_fee = float(data["original_fee"]) if data["original_fee"] else None
        if "stipend" in data:
            internship.stipend = data["stipend"]
        if "mode" in data:
            internship.mode = data["mode"]
        if "start_date" in data:
            internship.start_date = data["start_date"]
        if "slots" in data:
            internship.slots = int(data["slots"])
        if "enrolled" in data:
            internship.enrolled = int(data["enrolled"])
        if "rating" in data:
            internship.rating = float(data["rating"])
        if "description" in data:
            internship.description = data["description"]
        if "is_active" in data:
            internship.is_active = data["is_active"]
        
        # Handle array fields
        if "syllabus" in data:
            syllabus = data["syllabus"]
            if isinstance(syllabus, str):
                syllabus = [s.strip() for s in syllabus.split(',') if s.strip()]
            internship.syllabus = syllabus
            
        if "benefits" in data:
            benefits = data["benefits"]
            if isinstance(benefits, str):
                benefits = [b.strip() for b in benefits.split(',') if b.strip()]
            internship.benefits = benefits
            
        if "requirements" in data:
            requirements = data["requirements"]
            if isinstance(requirements, str):
                requirements = [r.strip() for r in requirements.split(',') if r.strip()]
            internship.requirements = requirements
        
        # Update timestamp if column exists
        if hasattr(internship, 'updated_at'):
            internship.updated_at = datetime.utcnow()
        
        db.session.commit()
        
        return jsonify({
            "success": True,
            "message": "Internship updated successfully",
            "internship": {
                "id": internship.id,
                "title": internship.title,
                "category": internship.category,
                "duration": internship.duration,
                "fee": float(internship.fee),
                "is_active": internship.is_active
            }
        }), 200
        
    except Exception as e:
        db.session.rollback()
        print(f"Error updating internship: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({"success": False, "message": str(e)}), 500


@internships_bp.route("/admin/delete/<int:internship_id>", methods=["DELETE", "OPTIONS"])
@token_required
@admin_required
def admin_delete_internship(internship_id):
    """Delete an internship (admin only)"""
    if request.method == "OPTIONS":
        return "", 200

    try:
        internship = Internship.query.get(internship_id)
        
        if not internship:
            return jsonify({"success": False, "message": "Internship not found"}), 404
        
        db.session.delete(internship)
        db.session.commit()
        
        return jsonify({
            "success": True,
            "message": "Internship deleted successfully"
        }), 200
        
    except Exception as e:
        db.session.rollback()
        print(f"Error deleting internship: {e}")
        return jsonify({"success": False, "message": str(e)}), 500


@internships_bp.route("/admin/toggle-status/<int:internship_id>", methods=["PATCH", "OPTIONS"])
@token_required
@admin_required
def admin_toggle_internship_status(internship_id):
    """Toggle internship active status (admin only)"""
    if request.method == "OPTIONS":
        return "", 200

    try:
        internship = Internship.query.get(internship_id)
        
        if not internship:
            return jsonify({"success": False, "message": "Internship not found"}), 404
        
        data = request.get_json()
        is_active = data.get("is_active", not internship.is_active)
        
        internship.is_active = is_active
        
        if hasattr(internship, 'updated_at'):
            internship.updated_at = datetime.utcnow()
        
        db.session.commit()
        
        return jsonify({
            "success": True,
            "message": f"Internship {'activated' if is_active else 'deactivated'} successfully",
            "is_active": is_active
        }), 200
        
    except Exception as e:
        db.session.rollback()
        print(f"Error toggling internship status: {e}")
        return jsonify({"success": False, "message": str(e)}), 500


@internships_bp.route("/admin/stats", methods=["GET", "OPTIONS"])
@token_required
@admin_required
def admin_get_internship_stats():
    """Get internship statistics (admin only)"""
    if request.method == "OPTIONS":
        return "", 200

    try:
        total = Internship.query.count()
        active = Internship.query.filter_by(is_active=True).count()
        
        # Get total applications (from InternshipOrder)
        total_applications = InternshipOrder.query.count()
        pending_payments = InternshipOrder.query.filter_by(payment_status="pending_verification").count()
        completed_payments = InternshipOrder.query.filter_by(payment_status="completed").count()
        
        # Calculate revenue
        completed_orders = InternshipOrder.query.filter_by(payment_status="completed").all()
        total_revenue = sum(order.amount for order in completed_orders if order.amount)
        
        return jsonify({
            "success": True,
            "stats": {
                "total": total,
                "active": active,
                "inactive": total - active,
                "total_applications": total_applications,
                "pending_payments": pending_payments,
                "completed_payments": completed_payments,
                "total_revenue": float(total_revenue)
            }
        }), 200
        
    except Exception as e:
        print(f"Error fetching internship stats: {e}")
        return jsonify({"success": False, "message": str(e)}), 500


@internships_bp.route("/admin/payment-requests", methods=["GET", "OPTIONS"])
@token_required
@admin_required
def admin_get_payment_requests():
    """Get all pending internship payment requests (admin only)"""
    if request.method == "OPTIONS":
        return "", 200

    try:
        # Get pending verifications from PaymentVerification table for internship orders
        pending_verifications = PaymentVerification.query.filter_by(
            status="pending"
        ).all()
        
        payment_requests = []
        for verification in pending_verifications:
            # Check if this is an internship order
            internship_order = InternshipOrder.query.filter_by(
                order_id=verification.order_id
            ).first()
            
            if internship_order and internship_order.internship_id:
                payment_requests.append({
                    "id": verification.id,
                    "verification_id": verification.verification_id,
                    "order_id": verification.order_id,
                    "student_id": verification.student_id,
                    "student_name": verification.student_name,
                    "student_email": verification.student_email,
                    "amount": float(verification.amount),
                    "transaction_id": verification.transaction_id,
                    "screenshot_url": verification.screenshot_url,
                    "status": verification.status,
                    "created_at": verification.created_at.isoformat() if verification.created_at else None,
                    "type": "internship"
                })
        
        return jsonify({
            "success": True,
            "verifications": payment_requests
        }), 200
        
    except Exception as e:
        print(f"Error fetching payment requests: {e}")
        return jsonify({"success": False, "message": str(e)}), 500


@internships_bp.route("/admin/payment-requests/<int:request_id>/approve", methods=["POST", "OPTIONS"])
@token_required
@admin_required
def admin_approve_payment_request(request_id):
    """Approve a payment request and enroll student (admin only)"""
    if request.method == "OPTIONS":
        return "", 200

    try:
        verification = PaymentVerification.query.get(request_id)
        
        if not verification:
            return jsonify({"success": False, "message": "Payment request not found"}), 404
        
        if verification.status != "pending":
            return jsonify({"success": False, "message": f"Request already {verification.status}"}), 400
        
        # Get the internship order
        internship_order = InternshipOrder.query.filter_by(
            order_id=verification.order_id
        ).first()
        
        if not internship_order:
            return jsonify({"success": False, "message": "Associated order not found"}), 404
        
        # Update verification status
        verification.status = "approved"
        
        # Update order status
        internship_order.payment_status = "completed"
        internship_order.status = "active"
        
        # Update student's internship_ids
        student = Student.query.get(verification.student_id)
        if student:
            if student.internship_ids is None:
                student.internship_ids = []
            if internship_order.internship_id not in student.internship_ids:
                student.internship_ids.append(internship_order.internship_id)
        
        # Update internship enrolled count
        internship = Internship.query.get(internship_order.internship_id)
        if internship:
            internship.enrolled = (internship.enrolled or 0) + 1
        
        db.session.commit()
        
        return jsonify({
            "success": True,
            "message": "Payment approved and student enrolled successfully"
        }), 200
        
    except Exception as e:
        db.session.rollback()
        print(f"Error approving payment: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({"success": False, "message": str(e)}), 500


@internships_bp.route("/admin/payment-requests/<int:request_id>/decline", methods=["POST", "OPTIONS"])
@token_required
@admin_required
def admin_decline_payment_request(request_id):
    """Decline a payment request (admin only)"""
    if request.method == "OPTIONS":
        return "", 200

    try:
        verification = PaymentVerification.query.get(request_id)
        
        if not verification:
            return jsonify({"success": False, "message": "Payment request not found"}), 404
        
        if verification.status != "pending":
            return jsonify({"success": False, "message": f"Request already {verification.status}"}), 400
        
        data = request.get_json()
        notes = data.get("notes", "")
        
        # Update verification status
        verification.status = "declined"
        
        # Update order status
        internship_order = InternshipOrder.query.filter_by(
            order_id=verification.order_id
        ).first()
        if internship_order:
            internship_order.payment_status = "failed"
        
        db.session.commit()
        
        return jsonify({
            "success": True,
            "message": "Payment declined successfully"
        }), 200
        
    except Exception as e:
        db.session.rollback()
        print(f"Error declining payment: {e}")
        return jsonify({"success": False, "message": str(e)}), 500