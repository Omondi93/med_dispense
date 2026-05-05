from datetime import datetime
from app.models.batch import Batch
from app.models.qrcode import QRCode
from app.models.scan_log import ScanLog
from app.utils.qr_security import verify_signature
from app import db
import logging

logging.info(f"QR verified: batch={batch_id}, status=authentic")
logging.warning(f"Tampered QR detected: batch={batch_id}")

FRAUD_SCAN_THRESHOLD = 5
FRAUD_TIME_WINDOW = 60  # seconds


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
            return {"status": "tampered", "message": "Invalid signature"}, 400

        # -------------------------
        # ⏳ STEP 2: DATE VALIDATION (DAY 18)
        # -------------------------
        try:
            today = datetime.utcnow().date()
            expiry = datetime.strptime(expiry_date, "%Y-%m-%d").date()
            manufacture = datetime.strptime(manufacture_date, "%Y-%m-%d").date()
        except Exception:
            return {"status": "tampered", "message": "Invalid date format"}, 400

        if manufacture > today:
            QRService._log_scan(batch_id, "tampered", signature, False, request_meta)
            return {"status": "tampered", "message": "Future manufacture date"}, 400

        if expiry < today:
            QRService._log_scan(batch_id, "expired", signature, True, request_meta)
            return {
                "status": "expired",
                "message": "Medicine expired",
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
            return {"status": "not_found", "message": "Batch not found"}, 404

        if batch.medicine_id != medicine_id:
            QRService._log_scan(batch_id, "not_found", signature, True, request_meta)
            return {"status": "not_found", "message": "Medicine mismatch"}, 404

        qr_record = QRCode.query.filter_by(
            batch_id=batch_id,
            signature=signature
        ).first()

        if not qr_record:
            QRService._log_scan(batch_id, "not_found", signature, True, request_meta)
            return {"status": "not_found", "message": "QR not registered"}, 404

        # -------------------------
        # 🚨 STEP 4: SCAN + FRAUD DETECTION
        # -------------------------
        current_count = qr_record.scan_count
        qr_record.scan_count += 1

        try:
            db.session.commit()
        except Exception:
            db.session.rollback()
            raise

        # 🔍 Detect fraud patterns
        risk_flags = QRService._detect_fraud(qr_record)
        risk_level = QRService._risk_level(risk_flags)

        # -------------------------
        # 🚨 CLONED
        # -------------------------
        if current_count > 0:
            QRService._log_scan(
                batch_id, "cloned", signature, True,
                request_meta, qr_record.scan_count
            )

            return {
                "status": "cloned",
                "message": f"QR scanned {qr_record.scan_count} times",
                "scan_count": qr_record.scan_count,
                "risk_flags": risk_flags,
                "risk_level": risk_level,
                "expiry_date": expiry_date,
                "days_remaining": days_remaining
            }, 200

        # -------------------------
        # ✅ AUTHENTIC
        # -------------------------
        QRService._log_scan(
            batch_id, "authentic", signature, True,
            request_meta, 1
        )

        response = {
            "status": "authentic",
            "message": "Valid medicine",
            "batch_id": batch_id,
            "medicine_id": medicine_id,
            "scan_count": 1,
            "expiry_date": expiry_date,
            "days_remaining": days_remaining,
            "risk_flags": risk_flags,
            "risk_level": risk_level
        }

        if near_expiry:
            response["warning"] = "Medicine near expiry"

        return response, 200

    # =========================================================
    # 🚨 FRAUD DETECTION (DAY 19)
    # =========================================================
    @staticmethod
    def _detect_fraud(qr_record):
        recent_logs = ScanLog.query.filter_by(
            batch_id=qr_record.batch_id
        ).order_by(ScanLog.scanned_at.desc()).limit(10).all()

        flags = []

        # High frequency
        if qr_record.scan_count >= FRAUD_SCAN_THRESHOLD:
            flags.append("high_frequency")

        # Multiple IPs
        ips = set(log.ip_address for log in recent_logs if log.ip_address)
        if len(ips) > 2:
            flags.append("multiple_locations")

        # Rapid scans
        if len(recent_logs) >= 2:
            t1 = recent_logs[0].scanned_at
            t2 = recent_logs[1].scanned_at
            if (t1 - t2).total_seconds() < FRAUD_TIME_WINDOW:
                flags.append("rapid_scan")

        return flags

    @staticmethod
    def _risk_level(flags):
        if not flags:
            return "low"
        if "high_frequency" in flags or "multiple_locations" in flags:
            return "high"
        return "medium"

    # =========================================================
    # 📝 LOGGING
    # =========================================================
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

    # =========================================================
    # 📊 ANALYTICS
    # =========================================================
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

    # =========================================================
    # 🚨 FRAUD ALERTS (DAY 20)
    # =========================================================
    @staticmethod
    def get_fraud_alerts(limit=50):
        suspicious = ["cloned", "tampered", "expired"]

        logs = ScanLog.query.filter(
            ScanLog.status.in_(suspicious)
        ).order_by(ScanLog.scanned_at.desc()).limit(limit).all()

        results = []

        for log in logs:
            results.append({
                "batch_id": log.batch_id,
                "status": log.status,
                "is_valid": log.is_valid,
                "scan_count": log.scan_count,
                "ip_address": log.ip_address,
                "timestamp": log.scanned_at.isoformat() if log.scanned_at else None,
                "risk_level": "high" if log.status in ["cloned", "tampered"] else "medium"
            })

        return results