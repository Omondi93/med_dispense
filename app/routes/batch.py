from flask import Blueprint, request, jsonify
from app import db
from app.models.batch import Batch
from datetime import datetime

batch_bp = Blueprint('batch', __name__, url_prefix='/api/batch')


@batch_bp.route("/", methods=["POST"])
def create_batch():
    data = request.get_json()

    batch = Batch(
        batch_number=data["batch_number"],
        medicine_id=data["medicine_id"],
        manufacturer_id=data["manufacturer_id"],
        manufacture_date=datetime.strptime(data["manufacture_date"], "%Y-%m-%d"),
        expiry_date=datetime.strptime(data["expiry_date"], "%Y-%m-%d"),
        quantity=data["quantity"]
    )

    db.session.add(batch)
    db.session.commit()

    return jsonify({
        "success": True,
        "batch_id": batch.id
    }), 201