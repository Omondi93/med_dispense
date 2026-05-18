from flask import Blueprint, jsonify
from app.utils.services.qr_service import QRService   # ✅ matches your structure
from app.utils.decorators import admin_required
from app.models.batch import Batch
from app.models.scan_log import ScanLog
from sqlalchemy import func

admin_bp = Blueprint('admin', __name__, url_prefix='/api/admin')


# -------------------------
# 🚨 FRAUD ALERTS
# -------------------------
@admin_bp.route("/fraud-analytics", methods=["GET"])
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
@admin_bp.route("/dashboard-stats", methods=["GET"])
def dashboard_stats():
    """
    GET /api/admin/dashboard-stats
    """

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
@admin_bp.route("/fraud-alerts", methods=["GET"])
@admin_required   # 🔐 protect endpoint
def get_fraud_alerts():
    """
    GET /api/admin/fraud-alerts

    Returns recent high-risk scan activities.
    """
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
# 📊 BATCH STATS
# -------------------------
@admin_bp.route("/batch-stats/<int:batch_id>", methods=["GET"])
@admin_required   # 🔐 protect endpoint
def get_batch_stats(batch_id):
    """
    GET /api/admin/batch-stats/<batch_id>

    Returns scan analytics for a batch.
    """
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