from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token

from app import db
from app.models.manufacturer import Manufacturer
from app.utils.security import hash_password, verify_password


# -------------------------
# 🔐 AUTH BLUEPRINT
# -------------------------

auth_bp = Blueprint("auth", __name__, url_prefix="/api/auth")


# -------------------------
# 📝 REGISTER
# -------------------------

@auth_bp.route("/register", methods=["POST"])
def register():

    data = request.get_json()

    if not data:
        return jsonify({
            "error": "Request must be JSON"
        }), 400

    name = data.get("name")
    email = data.get("email")
    password = data.get("password")

    # Validate required fields
    if not name or not email or not password:
        return jsonify({
            "error": "Missing required fields"
        }), 400

    # Check if email already exists
    existing = Manufacturer.query.filter_by(email=email).first()

    if existing:
        return jsonify({
            "error": "Email already registered"
        }), 409

    # Hash password
    hashed_password = hash_password(password)

    # Create manufacturer
    manufacturer = Manufacturer(
        name=name,
        email=email,
        password_hash=hashed_password
    )

    # Save to database
    db.session.add(manufacturer)
    db.session.commit()

    return jsonify({
        "message": "Manufacturer registered successfully"
    }), 201


# -------------------------
# 🔑 LOGIN
# -------------------------

@auth_bp.route("/login", methods=["POST"])
def login():

    data = request.get_json()

    if not data:
        return jsonify({
            "error": "Request must be JSON"
        }), 400

    email = data.get("email")
    password = data.get("password")

    # Validate input
    if not email or not password:
        return jsonify({
            "error": "Missing email or password"
        }), 400

    # Find manufacturer
    manufacturer = Manufacturer.query.filter_by(email=email).first()

    # Validate account
    if not manufacturer:
        return jsonify({
            "error": "Invalid credentials"
        }), 401

    # Verify password
    if not verify_password(password, manufacturer.password_hash):
        return jsonify({
            "error": "Invalid credentials"
        }), 401

    # Generate JWT token
    access_token = create_access_token(
        identity=str(manufacturer.id),
        additional_claims={
            "role": "admin"
        }
    )

    # Success response
    return jsonify({
        "message": "Login successful",
        "access_token": access_token,
        "role": "admin",
        "manufacturer": {
            "id": manufacturer.id,
            "name": manufacturer.name,
            "email": manufacturer.email
        }
    }), 200