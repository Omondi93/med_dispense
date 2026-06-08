from flask import Blueprint, jsonify
from sqlalchemy import func
from datetime import datetime, timedelta

from app import db
from app.utils.decorators import admin_required
from app.utils.services.qr_service import QRService

from app.models.batch import Batch
from app.models.scan_log import ScanLog
from app.models.qrcode import QRCode

admin_bp = Blueprint("admin", __name__, url_prefix="/api/admin")

@admin_bp.route("/fraud-summary", methods=["GET"])
@admin_required
def fraud_summary():
    try:
        total_qrs = QRCode.query.count()

        flagged_qrs = QRCode.query.filter_by(
            is_flagged=True
        ).count()

        cloned_scans = ScanLog.query.filter_by(
            status="cloned"
        ).count()

        tampered_scans = ScanLog.query.filter_by(
            status="tampered"
        ).count()

        most_scanned = QRCode.query.order_by(
            QRCode.scan_count.desc()
        ).limit(10).all()

        flagged_list = QRCode.query.filter_by(
            is_flagged=True
        ).order_by(
            QRCode.scan_count.desc()
        ).limit(10).all()

        return jsonify({
            "success": True,
            "data": {
                "total_qrs": total_qrs,
                "flagged_qrs": flagged_qrs,
                "cloned_scans": cloned_scans,
                "tampered_scans": tampered_scans,
                "most_scanned": [
                    {
                        "id": qr.id,
                        "batch_id": qr.batch_id,
                        "scan_count": qr.scan_count,
                        "is_flagged": qr.is_flagged
                    }
                    for qr in most_scanned
                ],
                "flagged_list": [
                    {
                        "id": qr.id,
                        "batch_id": qr.batch_id,
                        "scan_count": qr.scan_count,
                        "signature": qr.signature[:20] + "..."
                    }
                    for qr in flagged_list
                ]
            }
        }), 200

    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500
@admin_bp.route("/dashboard-stats", methods=["GET"])
@admin_required
def dashboard_stats():
    try:
        total_scans = ScanLog.query.count()

        fraud_alerts = ScanLog.query.filter(
            ScanLog.status.in_(["cloned", "tampered"])
        ).count()

        active_batches = Batch.query.count()

        return jsonify({
            "success": True,
            "data": {
                "total_scans": total_scans,
                "fraud_alerts": fraud_alerts,
                "active_batches": active_batches
            }
        }), 200

    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500


# -------------------------
# FRAUD ANALYTICS
# -------------------------

@admin_bp.route("/fraud-analytics", methods=["GET"])
@admin_required
def fraud_analytics():
    try:
        results = db.session.query(
            ScanLog.status,
            func.count(ScanLog.id)
        ).group_by(
            ScanLog.status
        ).all()

        analytics = []

        for status, count in results:
            analytics.append({
                "status": status,
                "count": count
            })

        return jsonify({
            "success": True,
            "data": analytics
        }), 200

    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500


# -------------------------
# FRAUD ALERTS
# -------------------------

@admin_bp.route("/fraud-alerts", methods=["GET"])
@admin_required
def get_fraud_alerts():
    try:
        alerts = QRService.get_fraud_alerts(limit=50)

        return jsonify({
            "success": True,
            "count": len(alerts),
            "alerts": alerts
        }), 200

    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500


# -------------------------
# BATCH STATS
# -------------------------

@admin_bp.route("/batch-stats/<int:batch_id>", methods=["GET"])
@admin_required
def get_batch_stats(batch_id):
    try:
        stats = QRService.get_scan_stats(batch_id)

        return jsonify({
            "success": True,
            "data": stats
        }), 200

    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500


# -------------------------
# EXPIRY ALERTS
# -------------------------

@admin_bp.route("/expiry-alerts", methods=["GET"])
@admin_required
def expiry_alerts():
    try:
        today = datetime.utcnow()
        warning_date = today + timedelta(days=30)

        batches = Batch.query.filter(
            Batch.expiry_date <= warning_date
        ).order_by(
            Batch.expiry_date.asc()
        ).all()

        results = []

        for batch in batches:
            days_remaining = (batch.expiry_date - today).days

            if days_remaining < 0:
                status = "expired"
            elif days_remaining <= 7:
                status = "critical"
            else:
                status = "warning"

            results.append({
                "id": batch.id,
                "batch_number": batch.batch_number,
                "medicine_name": batch.medicine.name if batch.medicine else None,
                "expiry_date": batch.expiry_date.isoformat(),
                "days_remaining": days_remaining,
                "status": status
            })

        return jsonify({
            "success": True,
            "data": results
        }), 200

    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500


# -------------------------
# QR REGISTRY
# -------------------------

@admin_bp.route("/qr-registry", methods=["GET"])
@admin_required
def get_qr_registry():
    try:
        qrs = QRCode.query.order_by(
            QRCode.created_at.desc()
        ).all()

        results = []

        for qr in qrs:
            results.append({
                "id": qr.id,
                "batch_id": qr.batch_id,
                "serial_number": qr.serial_number,
                "signature": qr.signature[:20] + "...",
                "scan_count": qr.scan_count,
                "is_flagged": qr.is_flagged,
                "created_at": qr.created_at.isoformat() if qr.created_at else None
            })

        return jsonify({
            "success": True,
            "data": results
        }), 200

    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500


# -------------------------
# QR SCAN HISTORY
# -------------------------
@admin_bp.route("/scan-history", methods=["GET"])
@admin_required
def get_all_scan_history():
    try:
        logs = ScanLog.query.order_by(
            ScanLog.scanned_at.desc()
        ).limit(100).all()

        results = []

        for log in logs:
            results.append({
                "id": log.id,
                "qr_id": log.qr_id,
                "batch_id": log.batch_id,
                "status": log.status,
                "signature": log.signature,
                "is_valid": log.is_valid,
                "scan_count": log.scan_count,
                "ip_address": log.ip_address,
                "user_agent": log.user_agent,
                "scanned_at": log.scanned_at.isoformat() if log.scanned_at else None
            })

        return jsonify({
            "success": True,
            "data": results
        }), 200

    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@admin_bp.route("/scan-history/<int:qr_id>", methods=["GET"])
@admin_required
def get_scan_history_by_qr(qr_id):
    try:
        logs = ScanLog.query.filter_by(
            qr_id=qr_id
        ).order_by(
            ScanLog.scanned_at.desc()
        ).all()

        results = []

        for log in logs:
            results.append({
                "id": log.id,
                "qr_id": log.qr_id,
                "batch_id": log.batch_id,
                "status": log.status,
                "signature": log.signature,
                "is_valid": log.is_valid,
                "scan_count": log.scan_count,
                "ip_address": log.ip_address,
                "user_agent": log.user_agent,
                "scanned_at": log.scanned_at.isoformat() if log.scanned_at else None
            })

        return jsonify({
            "success": True,
            "data": results
        }), 200

    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500
