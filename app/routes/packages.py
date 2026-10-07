from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from sqlalchemy import func
import base64
from io import BytesIO
import qrcode
from app import db
from app.models.batch import Batch
from app.models.package import MedicinePackage, RepackagingEvent
from app.models.qrcode import QRCode
from app.utils.qr_security import generate_qr_payload_with_serial

packages_bp = Blueprint("packages", __name__, url_prefix="/api/packages")


def _owner_id():
    return int(get_jwt_identity())


def _qr_base64(payload):
    image = qrcode.make(payload)
    buffer = BytesIO()
    image.save(buffer, format="PNG")
    return base64.b64encode(buffer.getvalue()).decode("ascii")


def _package_dict(package):
    return {
        "id": package.id,
        "serial_number": package.serial_number,
        "batch_id": package.batch_id,
        "batch_number": package.batch.batch_number if package.batch else None,
        "medicine_name": package.batch.medicine.name if package.batch and package.batch.medicine else None,
        "parent_package_id": package.parent_package_id,
        "quantity": package.quantity,
        "status": package.status,
        "qr_id": package.qr_code_id,
        "created_at": package.created_at.isoformat() if package.created_at else None,
    }


def _create_package(batch, quantity, manufacturer_id, parent_package_id=None):
    payload, serial, signature = generate_qr_payload_with_serial(
        batch.id,
        batch.medicine_id,
        batch.manufacture_date.strftime("%Y-%m-%d"),
        batch.expiry_date.strftime("%Y-%m-%d"),
    )
    qr = QRCode(batch_id=batch.id, signature=signature, serial_number=serial,
                payload=payload, scan_count=0, is_flagged=False)
    db.session.add(qr)
    db.session.flush()
    package = MedicinePackage(
        serial_number=serial, batch_id=batch.id,
        parent_package_id=parent_package_id, qr_code_id=qr.id,
        quantity=quantity, status="active", created_by=manufacturer_id,
    )
    db.session.add(package)
    db.session.flush()
    return package


@packages_bp.route("", methods=["GET"])
@jwt_required()
def list_packages():
    packages = (MedicinePackage.query
        .join(Batch, MedicinePackage.batch_id == Batch.id)
        .filter(Batch.manufacturer_id == _owner_id())
        .order_by(MedicinePackage.created_at.desc()).all())
    return jsonify({"success": True, "data": [_package_dict(p) for p in packages]}), 200


@packages_bp.route("/initialize", methods=["POST"])
@jwt_required()
def initialize_package():
    """Allocate a quantity from a batch into a first traceable package."""
    data = request.get_json(silent=True) or {}
    try:
        batch_id = int(data.get("batch_id"))
        quantity = int(data.get("quantity"))
    except (TypeError, ValueError):
        return jsonify({"success": False, "error": "batch_id and positive integer quantity are required"}), 400
    if quantity <= 0:
        return jsonify({"success": False, "error": "quantity must be greater than zero"}), 400

    batch = Batch.query.filter_by(id=batch_id, manufacturer_id=_owner_id()).first()
    if not batch:
        return jsonify({"success": False, "error": "Batch not found"}), 404

    # Only root allocations consume new quantity from the original batch.
    allocated = db.session.query(func.coalesce(func.sum(MedicinePackage.quantity), 0)).filter(
        MedicinePackage.batch_id == batch.id,
        MedicinePackage.parent_package_id.is_(None),
    ).scalar() or 0
    if allocated + quantity > batch.quantity:
        return jsonify({"success": False, "error": f"Quantity exceeds unallocated batch stock ({batch.quantity - allocated} remaining)"}), 409

    try:
        package = _create_package(batch, quantity, _owner_id())
        db.session.commit()
        return jsonify({"success": True, "message": "Traceable package created", "data": _package_dict(package), "qr_payload": package.qr_code.payload, "qr_code": _qr_base64(package.qr_code.payload)}), 201
    except Exception as exc:
        db.session.rollback()
        return jsonify({"success": False, "error": "Package creation failed", "detail": str(exc)}), 500


@packages_bp.route("/<int:package_id>/split", methods=["POST"])
@jwt_required()
def split_package(package_id):
    data = request.get_json(silent=True) or {}
    quantities = data.get("quantities")
    notes = (data.get("notes") or "").strip() or None
    if not isinstance(quantities, list) or len(quantities) < 2:
        return jsonify({"success": False, "error": "quantities must be a list containing at least two child quantities"}), 400
    try:
        quantities = [int(q) for q in quantities]
    except (TypeError, ValueError):
        return jsonify({"success": False, "error": "Every child quantity must be a positive integer"}), 400
    if any(q <= 0 for q in quantities):
        return jsonify({"success": False, "error": "Every child quantity must be greater than zero"}), 400

    package = (MedicinePackage.query.join(Batch, MedicinePackage.batch_id == Batch.id)
               .filter(MedicinePackage.id == package_id, Batch.manufacturer_id == _owner_id()).first())
    if not package:
        return jsonify({"success": False, "error": "Package not found"}), 404
    if package.status != "active":
        return jsonify({"success": False, "error": "Only active packages can be split"}), 409
    if sum(quantities) != package.quantity:
        return jsonify({"success": False, "error": f"Child quantities must total exactly {package.quantity}"}), 400
    if len(quantities) > 100:
        return jsonify({"success": False, "error": "A single operation may create at most 100 child packages"}), 400

    try:
        source_quantity = package.quantity
        children = [_create_package(package.batch, q, _owner_id(), package.id) for q in quantities]
        package.status = "split"
        db.session.add(RepackagingEvent(
            source_package_id=package.id, manufacturer_id=_owner_id(),
            source_quantity=source_quantity, child_count=len(children), notes=notes,
        ))
        db.session.commit()
        return jsonify({
            "success": True,
            "message": "Package split recorded; source package is no longer active",
            "source_package": _package_dict(package),
            "children": [{**_package_dict(child), "qr_payload": child.qr_code.payload, "qr_code": _qr_base64(child.qr_code.payload)} for child in children],
        }), 201
    except Exception as exc:
        db.session.rollback()
        return jsonify({"success": False, "error": "Split operation failed", "detail": str(exc)}), 500


@packages_bp.route("/<int:package_id>/trace", methods=["GET"])
@jwt_required()
def package_trace(package_id):
    package = (MedicinePackage.query.join(Batch, MedicinePackage.batch_id == Batch.id)
               .filter(MedicinePackage.id == package_id, Batch.manufacturer_id == _owner_id()).first())
    if not package:
        return jsonify({"success": False, "error": "Package not found"}), 404
    # Return the package ancestry and all descendants to support forward/backward traceability.
    ancestry = []
    node = package
    while node is not None:
        ancestry.append(_package_dict(node))
        node = node.parent
    descendants = []
    queue = list(package.children)
    while queue:
        node = queue.pop(0)
        descendants.append(_package_dict(node))
        queue.extend(node.children)
    events = RepackagingEvent.query.filter_by(manufacturer_id=_owner_id()).filter(
        RepackagingEvent.source_package_id.in_([p["id"] for p in ancestry + descendants])
    ).order_by(RepackagingEvent.created_at.asc()).all()
    return jsonify({"success": True, "package": _package_dict(package), "ancestry": ancestry,
                    "descendants": descendants, "events": [{
                        "id": e.id, "source_package_id": e.source_package_id,
                        "source_quantity": e.source_quantity, "child_count": e.child_count,
                        "notes": e.notes, "created_at": e.created_at.isoformat(),
                    } for e in events]}), 200
