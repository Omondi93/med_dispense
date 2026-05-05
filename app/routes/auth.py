from flask import Blueprint, request, jsonify
from app import db
from app.models.manufacturer import Manufacturer
from app.utils.security import hash_password, verify_password
from flask_jwt_extended import create_access_token

auth_bp = Blueprint("auth", __name__)


@auth_bp.route("/register", methods=["POST"])
def register():
    data = request.get_json()

    if not data:
        return jsonify({"error": "Request must be JSON"}), 400

    name = data.get("name")
    email = data.get("email")
    password = data.get("password")

    if not name or not email or not password:
        return jsonify({"error": "Missing required fields"}), 400

    existing = Manufacturer.query.filter_by(email=email).first()
    if existing:
        return jsonify({"error": "Email already registered"}), 409

    hashed_password = hash_password(password)

    manufacturer = Manufacturer(
        name=name,
        email=email,
        password_hash=hashed_password     
    )

    db.session.add(manufacturer)
    db.session.commit()

    return jsonify({"message": "Manufacturer registered"}), 201


@auth_bp.route("/login", methods=["POST"])
def login():
    data = request.get_json()

    if not data:
        return jsonify({"error": "Request must be JSON"}), 400

    email = data.get("email")
    password = data.get("password")

    if not email or not password:
        return jsonify({"error": "Missing email or password"}), 400

    manufacturer = Manufacturer.query.filter_by(email=email).first()

    if not manufacturer:
        return jsonify({"error": "Invalid credentials"}), 401

    if not verify_password(password, manufacturer.password_hash):
        return jsonify({"error": "Invalid credentials"}), 401

    access_token = create_access_token(identity=str(manufacturer.id))

    return jsonify({
    "message": "Login successful",
    "access_token": access_token
}), 200

