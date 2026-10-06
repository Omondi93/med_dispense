from datetime import datetime
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity

from app import db
from app.models.batch import Batch
from app.models.medicine import Medicine

batch_bp = Blueprint("batch", __name__, url_prefix="/api/batch")


@batch_bp.route("/", methods=["POST"])
@jwt_required()
def create_batch():
    data = request.get_json(silent=True)
    if not data:
        return jsonify({"success": False, "error": "No JSON data"}), 400

    medicine_id = data.get("medicine_id")
    batch_number = data.get("batch_number")
    manufacture_date = data.get("manufacture_date")
    expiry_date = data.get("expiry_date")
    quantity = data.get("quantity")

    if not all([medicine_id, batch_number, manufacture_date, expiry_date, quantity]):
        return jsonify({"success": False, "error": "All fields required"}), 400

    manufacturer_id = int(get_jwt_identity())
    medicine = db.session.get(Medicine, medicine_id)
    # Return the same response for missing and foreign-owned medicines to avoid ID probing.
    if not medicine or medicine.manufacturer_id != manufacturer_id:
        return jsonify({"success": False, "error": "Medicine not found"}), 404

    try:
        quantity = int(quantity)
        if quantity <= 0:
            return jsonify({"success": False, "error": "Quantity must be greater than zero"}), 400
        manufacture_dt = datetime.strptime(manufacture_date, "%Y-%m-%d")
        expiry_dt = datetime.strptime(expiry_date, "%Y-%m-%d")
        if expiry_dt <= manufacture_dt:
            return jsonify({"success": False, "error": "Expiry date must be after manufacture date"}), 400
    except (TypeError, ValueError):
        return jsonify({"success": False, "error": "Invalid quantity or date format; use YYYY-MM-DD"}), 400

    batch = Batch(batch_number=batch_number.strip(), medicine_id=medicine.id,
                  manufacturer_id=manufacturer_id, manufacture_date=manufacture_dt,
                  expiry_date=expiry_dt, quantity=quantity)
    try:
        db.session.add(batch)
        db.session.commit()
    except Exception:
        db.session.rollback()
        return jsonify({"success": False, "error": "Could not create batch; check that the batch number is unique"}), 400

    return jsonify({"success": True, "message": "Batch created successfully", "batch_id": batch.id}), 201


@batch_bp.route("/", methods=["GET"])
@jwt_required()
def get_batches():
    manufacturer_id = int(get_jwt_identity())
    batches = Batch.query.filter_by(manufacturer_id=manufacturer_id).order_by(Batch.id.asc()).all()
    return jsonify({"success": True, "data": [
        {"id": b.id, "batch_number": b.batch_number, "medicine_id": b.medicine_id,
         "medicine_name": b.medicine.name if b.medicine else None,
         "quantity": b.quantity, "manufacture_date": b.manufacture_date.isoformat(),
         "expiry_date": b.expiry_date.isoformat()}
        for b in batches
    ]}), 200
