from datetime import datetime
from app.models.batch import Batch
from app.models.qrcode import QRCode
from app.models.scan_log import ScanLog
from app.utils.qr_security import verify_signature
from app import db


class QRService:

    @staticmethod
    def verify_qr(parsed_data, request_meta):
        batch_id = parsed_data['batch_id']
        medicine_id = parsed_data['medicine_id']
        manufacture_date = parsed_data['manufacture_date']
        expiry_date = parsed_data['expiry_date']
        signature = parsed_data['signature']
        serial = parsed_data.get('serial')

        # -------------------------
        # 🔐 STEP 1: SIGNATURE CHECK
        # -------------------------
        if not verify_signature(
            batch_id=batch_id,
            medicine_id=medicine_id,
            manufacture_date=manufacture_date,
            expiry_date=expiry_date,
            signature=signature,
            serial=serial
        ):
            QRService._log_scan(batch_id, "tampered", signature, False, request_meta)
            return {
                "status": "tampered",
                "message": "Invalid signature"
            }, 400

        # -------------------------
        # ⏳ STEP 2: DATE VALIDATION (DAY 18)
        # -------------------------
        try:
            today = datetime.utcnow().date()
            expiry = datetime.strptime(expiry_date, "%Y-%m-%d").date()
            manufacture = datetime.strptime(manufacture_date, "%Y-%m-%d").date()
        except Exception:
            return {
                "status": "tampered",
                "message": "Invalid date format inside QR"
            }, 400

        # 🚨 Future manufacture date
        if manufacture > today:
            QRService._log_scan(batch_id, "tampered", signature, False, request_meta)
            return {
                "status": "tampered",
                "message": "Invalid manufacture date (future date)"
            }, 400

        # ❌ Expired medicine
        if expiry < today:
            QRService._log_scan(batch_id, "expired", signature, True, request_meta)
            return {
                "status": "expired",
                "message": "Medicine is expired - DO NOT USE",
                "expiry_date": expiry_date
            }, 200

        days_remaining = (expiry - today).days
        near_expiry = days_remaining <= 30

        # -------------------------
        # 🗄 STEP 3: DB VALIDATION
        # -------------------------
        batch = db.session.get(Batch, batch_id)
        if not batch:
            QRService._log_scan(batch_id, "not_found", signature, True, request_meta)
            return {
                "status": "not_found",
                "message": "Batch not found"
            }, 404

        if batch.medicine_id != medicine_id:
            QRService._log_scan(batch_id, "not_found", signature, True, request_meta)
            return {
                "status": "not_found",
                "message": "Medicine mismatch"
            }, 404

        qr_record = QRCode.query.filter_by(
            batch_id=batch_id,
            signature=signature
        ).first()

        if not qr_record:
            QRService._log_scan(batch_id, "not_found", signature, True, request_meta)
            return {
                "status": "not_found",
                "message": "QR not registered (possible counterfeit)"
            }, 404

        # -------------------------
        # 🚨 STEP 4: CLONE DETECTION
        # -------------------------
        current_count = qr_record.scan_count
        qr_record.scan_count += 1

        try:
            db.session.commit()
        except Exception:
            db.session.rollback()
            raise

        if current_count > 0:
            QRService._log_scan(
                batch_id,
                "cloned",
                signature,
                True,
                request_meta,
                qr_record.scan_count
            )

            return {
                "status": "cloned",
                "message": f"QR scanned {qr_record.scan_count} times",
                "scan_count": qr_record.scan_count,
                "expiry_date": expiry_date,
                "days_remaining": days_remaining
            }, 200

        # -------------------------
        # ✅ STEP 5: AUTHENTIC RESPONSE
        # -------------------------
        QRService._log_scan(
            batch_id,
            "authentic",
            signature,
            True,
            request_meta,
            1
        )

        response = {
            "status": "authentic",
            "message": "Valid medicine",
            "batch_id": batch_id,
            "medicine_id": medicine_id,
            "scan_count": 1,
            "expiry_date": expiry_date,
            "days_remaining": days_remaining
        }

        if near_expiry:
            response["warning"] = "Medicine is near expiry"

        return response, 200

    # -------------------------
    # 🏭 REGISTER QR (DAY 16)
    # -------------------------
    @staticmethod
    def register_qr(batch_id, signature, serial=None, payload=None):
        batch = db.session.get(Batch, batch_id)

        if not batch:
            return {
                "success": False,
                "error": "Batch does not exist"
            }, 404

        existing = QRCode.query.filter_by(signature=signature).first()
        if existing:
            return {
                "success": False,
                "error": "QR already registered",
                "qr_id": existing.id
            }, 409

        try:
            qr = QRCode(
                batch_id=batch_id,
                signature=signature,
                serial_number=serial,
                payload=payload,
                scan_count=0
            )

            db.session.add(qr)
            db.session.commit()

            return {
                "success": True,
                "message": "QR registered",
                "qr_id": qr.id
            }, 201

        except Exception as e:
            db.session.rollback()
            return {
                "success": False,
                "error": str(e)
            }, 500

    # -------------------------
    # 📝 LOGGING
    # -------------------------
    @staticmethod
    def _log_scan(batch_id, status, signature, is_valid, request_meta, scan_count=None):
        try:
            log = ScanLog(
                batch_id=batch_id,
                status=status,
                signature=signature[:64],
                is_valid=is_valid,
                scan_count=scan_count,
                scanned_at=datetime.utcnow(),
                ip_address=request_meta.get("ip"),
                user_agent=request_meta.get("agent", "")[:200]
            )

            db.session.add(log)
            db.session.flush()

        except Exception:
            db.session.rollback()

    # -------------------------
    # 📊 ANALYTICS
    # -------------------------
    @staticmethod
    def get_scan_stats(batch_id):
        return {
            "batch_id": batch_id,
            "total_scans": ScanLog.query.filter_by(batch_id=batch_id).count(),
            "unique_qrs": QRCode.query.filter_by(batch_id=batch_id).count(),
            "potential_clones": QRCode.query.filter(
                QRCode.batch_id == batch_id,
                QRCode.scan_count > 1
            ).count()
        }