from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity

from app import db
from app.models.medicine import Medicine

medicine_bp = Blueprint("medicine", __name__)

@medicine_bp.route("/medicines", methods=["POST"])
@jwt_required()
def create_medicine():

    manufacturer_id = int(get_jwt_identity())

    data = request.get_json()

    name = data.get("name")
    description = data.get("description")

    if not name:
        return jsonify({"error": "Medicine name required"}), 400

    medicine = Medicine(
        name=name,
        description=description,
        manufacturer_id=manufacturer_id
    )

    db.session.add(medicine)
    db.session.commit()

    return jsonify({
        "message": "Medicine created",
        "medicine_id": medicine.id
    }), 201