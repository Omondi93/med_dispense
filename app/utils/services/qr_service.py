import logging
from datetime import datetime

from app.models.batch import Batch
from app.models.qrcode import QRCode
from app.models.scan_log import ScanLog
from app.utils.qr_security import verify_signature
from app import db


class QRService:

    # -------------------------
    # 🆕 QR REGISTRATION (DAY 16)
    # -------------------------
    @staticmethod
    def register_qr(batch_id, signature, payload=None):
        """
        Register QR code in database
        """

        # Check batch exists
        batch = db.session.get(Batch, batch_id)
        if not batch:
            return {
                "success": False,
                "error": "Batch does not exist"
            }, 404

        # Prevent duplicate QR
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
                scan_count=0,
                is_flagged=False
            )

            db.session.add(qr)
            db.session.commit()

            logging.info(f"QR registered: batch={batch_id}, qr_id={qr.id}")

            return {
                "success": True,
                "qr_id": qr.id,
                "batch_id": batch_id
            }, 201

        except Exception as e:
            db.session.rollback()
            logging.error(f"QR registration failed: {str(e)}")

            return {
                "success": False,
                "error": str(e)
            }, 500

    # -------------------------
    # 🔐 VERIFY QR
    # -------------------------
    @staticmethod
    def verify_qr(parsed_data, request_meta):
        batch_id = parsed_data['batch_id']
        medicine_id = parsed_data['medicine_id']
        manufacture_date = parsed_data['manufacture_date']
        expiry_date = parsed_data['expiry_date']
        signature = parsed_data['signature']

        # 🔐 STEP 1 — VERIFY SIGNATURE
        if not verify_signature(
            batch_id=batch_id,
            medicine_id=medicine_id,
            manufacture_date=manufacture_date,
            expiry_date=expiry_date,
            signature=signature
        ):
            logging.warning(f"Tampered QR attempt: batch={batch_id}")

            QRService._log_scan(batch_id, "tampered", signature, False, request_meta)

            return {
                "status": "tampered",
                "message": "Invalid signature"
            }, 400

        # 🗄 STEP 2 — CHECK BATCH
        batch = db.session.get(Batch, batch_id)
        if not batch:
            logging.warning(f"Batch not found: batch={batch_id}")

            QRService._log_scan(batch_id, "not_found", signature, True, request_meta)

            return {
                "status": "not_found",
                "message": "Batch not found"
            }, 404

        # 🧪 STEP 3 — VALIDATE MEDICINE
        if batch.medicine_id != medicine_id:
            logging.warning(f"Medicine mismatch: batch={batch_id}")

            QRService._log_scan(batch_id, "not_found", signature, True, request_meta)

            return {
                "status": "not_found",
                "message": "Medicine mismatch"
            }, 404

        # 🔎 STEP 4 — FIND QR RECORD
        qr_record = QRCode.query.filter_by(
            batch_id=batch_id,
            signature=signature
        ).first()

        if not qr_record:
            logging.warning(f"QR not registered: batch={batch_id}")

            QRService._log_scan(batch_id, "not_found", signature, True, request_meta)

            return {
                "status": "not_found",
                "message": "QR not registered"
            }, 404

        # 🚨 STEP 5 — CLONE DETECTION
        current_count = qr_record.scan_count

        try:
            qr_record.scan_count += 1
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            logging.error(f"DB error during scan update: {str(e)}")
            raise

        # 🔴 CLONED
        if current_count >= 1:
            logging.warning(
                f"CLONED QR detected: batch={batch_id}, scans={qr_record.scan_count}"
            )

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
                "scan_count": qr_record.scan_count
            }, 200

        # 🟢 AUTHENTIC
        logging.info(f"QR verified: batch={batch_id}, status=authentic")

        QRService._log_scan(
            batch_id,
            "authentic",
            signature,
            True,
            request_meta,
            1
        )

        return {
            "status": "authentic",
            "message": "Valid medicine",
            "batch_id": batch_id,
            "medicine_id": medicine_id,
            "scan_count": 1
        }, 200

    # -------------------------
    # 📝 LOGGING HELPER
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
            db.session.commit()

        except Exception as e:
            db.session.rollback()
            logging.error(f"Scan log failed: {str(e)}")

    # -------------------------
    # 📊 ANALYTICS
    # -------------------------
    @staticmethod
    def get_scan_stats(batch_id):
        total_scans = ScanLog.query.filter_by(batch_id=batch_id).count()

        unique_qrs = QRCode.query.filter_by(batch_id=batch_id).count()

        cloned_count = QRCode.query.filter(
            QRCode.batch_id == batch_id,
            QRCode.scan_count > 1
        ).count()

        return {
            "batch_id": batch_id,
            "total_scans": total_scans,
            "unique_qrs": unique_qrs,
            "potential_clones": cloned_count
        }

    # -------------------------
    # 🚨 FRAUD ALERTS
    # -------------------------
    @staticmethod
    def get_fraud_alerts(limit=50):
        logs = ScanLog.query.filter(
            ScanLog.status.in_(["tampered", "cloned"])
        ).order_by(ScanLog.scanned_at.desc()).limit(limit).all()

        return [
            {
                "batch_id": log.batch_id,
                "status": log.status,
                "scan_count": log.scan_count,
                "timestamp": log.scanned_at.isoformat() if log.scanned_at else None,
                "ip": log.ip_address
            }
            for log in logs
        ]