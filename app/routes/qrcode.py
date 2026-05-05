import base64
from io import BytesIO
from datetime import datetime
import qrcode
from app import limiter

from flask import Blueprint, request, jsonify, send_file

from app.utils.services.qr_service import QRService
from app.utils.qr_security import (
    generate_qr_payload,
    generate_qr_payload_with_serial
)

qr_bp = Blueprint('qrcode', __name__, url_prefix='/api/qr')


# -------------------------
# 🔧 HELPERS
# -------------------------

def validate_date(date_str):
    try:
        datetime.strptime(date_str, "%Y-%m-%d")
        return True
    except ValueError:
        return False


def parse_qr_payload(qr_data):
    try:
        parts = qr_data.split('|')

        # SINGLE QR
        if len(parts) == 5:
            return {
                "batch_id": int(parts[0]),
                "medicine_id": int(parts[1]),
                "manufacture_date": parts[2],
                "expiry_date": parts[3],
                "serial": None,
                "signature": parts[4]
            }

        # BULK QR
        elif len(parts) == 6:
            return {
                "batch_id": int(parts[0]),
                "medicine_id": int(parts[1]),
                "manufacture_date": parts[2],
                "expiry_date": parts[3],
                "serial": parts[4],
                "signature": parts[5]
            }

        return None

    except Exception:
        return None


# -------------------------
# 🔐 VERIFY QR
# -------------------------

@qr_bp.route("/verify", methods=["POST"])
@limiter.limit("10 per minute")
def verify_qr():
    data = request.get_json()

    if not data or "qr_data" not in data:
        return jsonify({
            "status": "error",
            "message": "Missing qr_data field"
        }), 400

    parsed = parse_qr_payload(data["qr_data"])
    if not parsed:
        return jsonify({
            "status": "tampered",
            "message": "Invalid QR format"
        }), 400

    request_meta = {
        "ip": request.remote_addr,
        "agent": request.headers.get("User-Agent", "")[:200]
    }

    response, status_code = QRService.verify_qr(parsed, request_meta)

    return jsonify(response), status_code


# -------------------------
# 📊 STATS
# -------------------------

@qr_bp.route("/stats/<int:batch_id>", methods=["GET"])
def get_batch_stats(batch_id):
    stats = QRService.get_scan_stats(batch_id)

    return jsonify({
        "success": True,
        "data": stats
    }), 200


# -------------------------
# 🔳 GENERATE + REGISTER SINGLE QR
# -------------------------

@qr_bp.route("/generate", methods=["POST"])
def generate_qr():
    try:
        data = request.get_json()

        if not data:
            return jsonify({"success": False, "error": "No JSON data provided"}), 400

        required = ['batch_id', 'medicine_id', 'manufacture_date', 'expiry_date']
        missing = [f for f in required if f not in data]

        if missing:
            return jsonify({
                "success": False,
                "error": f"Missing fields: {', '.join(missing)}"
            }), 400

        batch_id = data['batch_id']
        medicine_id = data['medicine_id']
        manufacture_date = data['manufacture_date']
        expiry_date = data['expiry_date']

        if not validate_date(manufacture_date) or not validate_date(expiry_date):
            return jsonify({
                "success": False,
                "error": "Invalid date format (YYYY-MM-DD required)"
            }), 400

        # Step 1: Generate payload
        payload = generate_qr_payload(
            batch_id,
            medicine_id,
            manufacture_date,
            expiry_date
        )

        # Step 2: Extract signature
        signature = payload.split('|')[-1]

        # Step 3: Register QR
        reg_response, reg_status = QRService.register_qr(
            batch_id=batch_id,
            signature=signature,
            payload=payload
        )

        if not reg_response.get("success"):
            return jsonify(reg_response), reg_status

        qr_id = reg_response["qr_id"]

        # Step 4: Generate QR image
        qr = qrcode.QRCode(
            error_correction=qrcode.constants.ERROR_CORRECT_Q,
            box_size=10,
            border=4
        )
        qr.add_data(payload)
        qr.make(fit=True)

        img = qr.make_image(fill_color="black", back_color="white")

        buffered = BytesIO()
        img.save(buffered, format="PNG")
        buffered.seek(0)

        img_str = base64.b64encode(buffered.getvalue()).decode("utf-8")

        return jsonify({
            "success": True,
            "qr_code": img_str,
            "payload": payload,
            "qr_id": qr_id,
            "registered": True
        }), 201

    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500


# -------------------------
# 🏭 BULK GENERATE QR (DAY 17)
# -------------------------

@qr_bp.route("/generate/bulk", methods=["POST"])
def generate_bulk_qr():
    try:
        data = request.get_json()

        required = [
            "batch_id",
            "medicine_id",
            "manufacture_date",
            "expiry_date",
            "quantity"
        ]

        if not data or any(field not in data for field in required):
            return jsonify({
                "success": False,
                "error": "Missing required fields"
            }), 400

        batch_id = data["batch_id"]
        medicine_id = data["medicine_id"]
        manufacture_date = data["manufacture_date"]
        expiry_date = data["expiry_date"]
        quantity = data["quantity"]

        if not validate_date(manufacture_date) or not validate_date(expiry_date):
            return jsonify({
                "success": False,
                "error": "Invalid date format"
            }), 400

        if quantity <= 0 or quantity > 5000:
            return jsonify({
                "success": False,
                "error": "Quantity must be between 1 and 5000"
            }), 400

        results = []

        for _ in range(quantity):
            payload, serial, signature = generate_qr_payload_with_serial(
                batch_id,
                medicine_id,
                manufacture_date,
                expiry_date
            )

            reg_response, reg_status = QRService.register_qr(
                batch_id=batch_id,
                signature=signature,
                serial=serial,
                payload=payload
            )

            if not reg_response.get("success"):
                return jsonify(reg_response), reg_status

            results.append({
                "qr_id": reg_response["qr_id"],
                "serial": serial
            })

        return jsonify({
            "success": True,
            "batch_id": batch_id,
            "generated": quantity,
            "preview": results[:5]
        }), 201

    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500


# -------------------------
# 📥 DOWNLOAD QR FILE
# -------------------------

@qr_bp.route("/generate/file", methods=["POST"])
def generate_qr_file():
    try:
        data = request.get_json()

        if not data:
            return jsonify({"success": False, "error": "No JSON data"}), 400

        required = ['batch_id', 'medicine_id', 'manufacture_date', 'expiry_date']
        missing = [f for f in required if f not in data]

        if missing:
            return jsonify({
                "success": False,
                "error": f"Missing: {', '.join(missing)}"
            }), 400

        batch_id = data['batch_id']
        medicine_id = data['medicine_id']
        manufacture_date = data['manufacture_date']
        expiry_date = data['expiry_date']

        if not validate_date(manufacture_date) or not validate_date(expiry_date):
            return jsonify({
                "success": False,
                "error": "Invalid date format"
            }), 400

        payload = generate_qr_payload(
            batch_id,
            medicine_id,
            manufacture_date,
            expiry_date
        )

        qr = qrcode.make(payload)

        buffered = BytesIO()
        qr.save(buffered, format="PNG")
        buffered.seek(0)

        return send_file(
            buffered,
            mimetype='image/png',
            as_attachment=True,
            download_name=f"medicine_qr_{batch_id}.png"
        )

    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500