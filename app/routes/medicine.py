from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity

from app import db
from app.models.medicine import Medicine

medicine_bp = Blueprint("medicine", __name__, url_prefix="/api/medicine")


@medicine_bp.route("/", methods=["POST"])
@jwt_required()
def create_medicine():
    data = request.get_json(silent=True)
    if not data:
        return jsonify({"success": False, "error": "No JSON data received"}), 400

    name = data.get("name")
    if not isinstance(name, str) or not name.strip():
        return jsonify({"success": False, "error": "Medicine name required"}), 400

    manufacturer_id = int(get_jwt_identity())
    medicine = Medicine(name=name.strip(), manufacturer_id=manufacturer_id,
                        description=data.get("description"))
    try:
        db.session.add(medicine)
        db.session.commit()
    except Exception:
        db.session.rollback()
        return jsonify({"success": False, "error": "Could not create medicine"}), 500

    return jsonify({"success": True, "message": "Medicine created successfully",
                    "medicine_id": medicine.id}), 201


@medicine_bp.route("/", methods=["GET"])
@jwt_required()
def get_medicines():
    manufacturer_id = int(get_jwt_identity())
    medicines = Medicine.query.filter_by(manufacturer_id=manufacturer_id).order_by(Medicine.id.asc()).all()
    return jsonify({"success": True, "data": [
        {"id": m.id, "name": m.name, "description": m.description,
         "manufacturer_id": m.manufacturer_id}
        for m in medicines
    ]}), 200
