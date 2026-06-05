import base64
from io import BytesIO
import qrcode

from flask import Blueprint, request, jsonify, send_file

from app import limiter
from app.models.batch import Batch
from app.utils.services.qr_service import QRService
from app.utils.qr_security import (
    generate_qr_payload,
    generate_qr_payload_with_serial,
    parse_qr_payload
)

qr_bp = Blueprint("qrcode", __name__, url_prefix="/api/qr")


def make_qr_base64(payload):
    qr = qrcode.QRCode(
        error_correction=qrcode.constants.ERROR_CORRECT_Q,
        box_size=10,
        border=4
    )

    qr.add_data(payload)
    qr.make(fit=True)

    img = qr.make_image(
        fill_color="black",
        back_color="white"
    )

    buffer = BytesIO()
    img.save(buffer, format="PNG")
    buffer.seek(0)

    return base64.b64encode(
        buffer.getvalue()
    ).decode("utf-8")


def get_batch_data(batch_id):
    batch = Batch.query.get(batch_id)

    if not batch:
        return None

    return {
        "batch": batch,
        "batch_id": batch.id,
        "medicine_id": batch.medicine_id,
        "manufacture_date": batch.manufacture_date.strftime("%Y-%m-%d"),
        "expiry_date": batch.expiry_date.strftime("%Y-%m-%d")
    }


@qr_bp.route("/verify", methods=["POST"])
@limiter.limit("10 per minute")
def verify_qr():
    data = request.get_json()

    if not data or "qr_data" not in data:
        return jsonify({
            "status": "error",
            "message": "Missing qr_data field"
        }), 400

    try:
        parsed = parse_qr_payload(data["qr_data"])
    except Exception:
        return jsonify({
            "status": "tampered",
            "message": "Invalid QR format"
        }), 400

    request_meta = {
        "ip": request.remote_addr,
        "agent": request.headers.get("User-Agent", "")[:200]
    }

    response, status_code = QRService.verify_qr(
        parsed,
        request_meta
    )

    return jsonify(response), status_code


@qr_bp.route("/generate", methods=["POST"])
def generate_qr():
    try:
        data = request.get_json()

        if not data or "batch_id" not in data:
            return jsonify({
                "success": False,
                "error": "batch_id is required"
            }), 400

        batch_data = get_batch_data(data["batch_id"])

        if not batch_data:
            return jsonify({
                "success": False,
                "error": "Batch does not exist"
            }), 404

        payload = generate_qr_payload(
            batch_data["batch_id"],
            batch_data["medicine_id"],
            batch_data["manufacture_date"],
            batch_data["expiry_date"]
        )

        signature = payload.split("|")[-1]

        reg_response, reg_status = QRService.register_qr(
            batch_id=batch_data["batch_id"],
            signature=signature,
            payload=payload
        )

        if not reg_response.get("success"):
            return jsonify(reg_response), reg_status

        qr_code = make_qr_base64(payload)

        return jsonify({
            "success": True,
            "message": "QR generated and saved successfully",
            "qr_code": qr_code,
            "payload": payload,
            "qr_id": reg_response["qr_id"],
            "batch_id": batch_data["batch_id"],
            "medicine_id": batch_data["medicine_id"],
            "manufacture_date": batch_data["manufacture_date"],
            "expiry_date": batch_data["expiry_date"],
            "registered": True
        }), 201

    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500


@qr_bp.route("/generate/bulk", methods=["POST"])
def generate_bulk_qr():
    try:
        data = request.get_json()

        if not data or "batch_id" not in data or "quantity" not in data:
            return jsonify({
                "success": False,
                "error": "batch_id and quantity are required"
            }), 400

        quantity = int(data["quantity"])

        if quantity <= 0 or quantity > 5000:
            return jsonify({
                "success": False,
                "error": "Quantity must be between 1 and 5000"
            }), 400

        batch_data = get_batch_data(data["batch_id"])

        if not batch_data:
            return jsonify({
                "success": False,
                "error": "Batch does not exist"
            }), 404

        results = []

        for _ in range(quantity):
            payload, serial, signature = generate_qr_payload_with_serial(
                batch_data["batch_id"],
                batch_data["medicine_id"],
                batch_data["manufacture_date"],
                batch_data["expiry_date"]
            )

            reg_response, reg_status = QRService.register_qr(
                batch_id=batch_data["batch_id"],
                signature=signature,
                serial=serial,
                payload=payload
            )

            if not reg_response.get("success"):
                return jsonify(reg_response), reg_status

            results.append({
                "qr_id": reg_response["qr_id"],
                "serial": serial,
                "payload": payload
            })

        return jsonify({
            "success": True,
            "message": "Bulk QR codes generated and saved",
            "batch_id": batch_data["batch_id"],
            "medicine_id": batch_data["medicine_id"],
            "generated": quantity,
            "preview": results[:5]
        }), 201

    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500


@qr_bp.route("/generate/file", methods=["POST"])
def generate_qr_file():
    try:
        data = request.get_json()

        if not data or "batch_id" not in data:
            return jsonify({
                "success": False,
                "error": "batch_id is required"
            }), 400

        batch_data = get_batch_data(data["batch_id"])

        if not batch_data:
            return jsonify({
                "success": False,
                "error": "Batch does not exist"
            }), 404

        payload = generate_qr_payload(
            batch_data["batch_id"],
            batch_data["medicine_id"],
            batch_data["manufacture_date"],
            batch_data["expiry_date"]
        )

        signature = payload.split("|")[-1]

        QRService.register_qr(
            batch_id=batch_data["batch_id"],
            signature=signature,
            payload=payload
        )

        qr = qrcode.make(payload)

        buffer = BytesIO()
        qr.save(buffer, format="PNG")
        buffer.seek(0)

        return send_file(
            buffer,
            mimetype="image/png",
            as_attachment=True,
            download_name=f"medicine_qr_batch_{batch_data['batch_id']}.png"
        )

    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500


@qr_bp.route("/stats/<int:batch_id>", methods=["GET"])
def get_batch_stats(batch_id):
    stats = QRService.get_scan_stats(batch_id)

    return jsonify({
        "success": True,
        "data": stats
    }), 200