from datetime import datetime, timedelta

from flask import Blueprint, jsonify
from flask_jwt_extended import get_jwt_identity
from sqlalchemy import func

from app import db
from app.models.batch import Batch
from app.models.qrcode import QRCode
from app.models.scan_log import ScanLog
from app.utils.decorators import admin_required
from app.utils.services.qr_service import QRService

admin_bp = Blueprint("admin", __name__, url_prefix="/api/admin")


def _manufacturer_id():
    return int(get_jwt_identity())


def _owned_qrs(manufacturer_id):
    return QRCode.query.join(Batch, QRCode.batch_id == Batch.id).filter(
        Batch.manufacturer_id == manufacturer_id
    )


def _owned_logs(manufacturer_id):
    return ScanLog.query.join(Batch, ScanLog.batch_id == Batch.id).filter(
        Batch.manufacturer_id == manufacturer_id
    )


def _serialize_log(log):
    return {
        "id": log.id, "qr_id": log.qr_id, "batch_id": log.batch_id,
        "status": log.status, "signature": log.signature,
        "is_valid": log.is_valid, "scan_count": log.scan_count,
        "ip_address": log.ip_address, "user_agent": log.user_agent,
        "scanned_at": log.scanned_at.isoformat() if log.scanned_at else None
    }


@admin_bp.route("/fraud-summary", methods=["GET"])
@admin_required
def fraud_summary():
    manufacturer_id = _manufacturer_id()
    qrs = _owned_qrs(manufacturer_id)
    logs = _owned_logs(manufacturer_id)
    most_scanned = qrs.order_by(QRCode.scan_count.desc()).limit(10).all()
    flagged = qrs.filter(QRCode.is_flagged.is_(True)).order_by(QRCode.scan_count.desc()).limit(10).all()
    return jsonify({"success": True, "data": {
        "total_qrs": qrs.count(),
        "flagged_qrs": _owned_qrs(manufacturer_id).filter(QRCode.is_flagged.is_(True)).count(),
        "cloned_scans": logs.filter(ScanLog.status == "cloned").count(),
        "tampered_scans": _owned_logs(manufacturer_id).filter(ScanLog.status == "tampered").count(),
        "most_scanned": [{"id": q.id, "batch_id": q.batch_id, "scan_count": q.scan_count,
                          "is_flagged": q.is_flagged} for q in most_scanned],
        "flagged_list": [{"id": q.id, "batch_id": q.batch_id, "scan_count": q.scan_count,
                          "signature": q.signature[:20] + "..."} for q in flagged]
    }}), 200


@admin_bp.route("/dashboard-stats", methods=["GET"])
@admin_required
def dashboard_stats():
    manufacturer_id = _manufacturer_id()
    logs = _owned_logs(manufacturer_id)
    return jsonify({"success": True, "data": {
        "total_scans": logs.count(),
        "fraud_alerts": _owned_logs(manufacturer_id).filter(ScanLog.status.in_(["cloned", "tampered"])).count(),
        "active_batches": Batch.query.filter_by(manufacturer_id=manufacturer_id).count()
    }}), 200


@admin_bp.route("/fraud-analytics", methods=["GET"])
@admin_required
def fraud_analytics():
    manufacturer_id = _manufacturer_id()
    results = db.session.query(ScanLog.status, func.count(ScanLog.id)).join(
        Batch, ScanLog.batch_id == Batch.id
    ).filter(Batch.manufacturer_id == manufacturer_id).group_by(ScanLog.status).all()
    return jsonify({"success": True, "data": [{"status": status, "count": count}
                                                   for status, count in results]}), 200


@admin_bp.route("/fraud-alerts", methods=["GET"])
@admin_required
def get_fraud_alerts():
    manufacturer_id = _manufacturer_id()
    logs = _owned_logs(manufacturer_id).filter(ScanLog.status.in_(["tampered", "cloned"])).order_by(
        ScanLog.scanned_at.desc()).limit(50).all()
    alerts = [{"qr_id": log.qr_id, "batch_id": log.batch_id, "status": log.status,
               "scan_count": log.scan_count, "timestamp": log.scanned_at.isoformat() if log.scanned_at else None,
               "ip": log.ip_address} for log in logs]
    return jsonify({"success": True, "count": len(alerts), "alerts": alerts}), 200


@admin_bp.route("/batch-stats/<int:batch_id>", methods=["GET"])
@admin_required
def get_batch_stats(batch_id):
    manufacturer_id = _manufacturer_id()
    batch = Batch.query.filter_by(id=batch_id, manufacturer_id=manufacturer_id).first()
    if not batch:
        return jsonify({"success": False, "error": "Batch not found"}), 404
    return jsonify({"success": True, "data": QRService.get_scan_stats(batch_id)}), 200


@admin_bp.route("/expiry-alerts", methods=["GET"])
@admin_required
def expiry_alerts():
    manufacturer_id = _manufacturer_id()
    today = datetime.utcnow()
    warning_date = today + timedelta(days=30)
    batches = Batch.query.filter(Batch.manufacturer_id == manufacturer_id,
                                 Batch.expiry_date <= warning_date).order_by(Batch.expiry_date.asc()).all()
    results = []
    for batch in batches:
        days_remaining = (batch.expiry_date - today).days
        status = "expired" if days_remaining < 0 else "critical" if days_remaining <= 7 else "warning"
        results.append({"id": batch.id, "batch_number": batch.batch_number,
                        "medicine_name": batch.medicine.name if batch.medicine else None,
                        "expiry_date": batch.expiry_date.isoformat(), "days_remaining": days_remaining,
                        "status": status})
    return jsonify({"success": True, "data": results}), 200


@admin_bp.route("/qr-registry", methods=["GET"])
@admin_required
def get_qr_registry():
    manufacturer_id = _manufacturer_id()
    qrs = _owned_qrs(manufacturer_id).order_by(QRCode.created_at.desc()).all()
    return jsonify({"success": True, "data": [
        {"id": q.id, "batch_id": q.batch_id, "serial_number": q.serial_number,
         "signature": q.signature[:20] + "...", "scan_count": q.scan_count,
         "is_flagged": q.is_flagged, "created_at": q.created_at.isoformat() if q.created_at else None}
        for q in qrs
    ]}), 200


@admin_bp.route("/scan-history", methods=["GET"])
@admin_required
def get_all_scan_history():
    logs = _owned_logs(_manufacturer_id()).order_by(ScanLog.scanned_at.desc()).limit(100).all()
    return jsonify({"success": True, "data": [_serialize_log(log) for log in logs]}), 200


@admin_bp.route("/scan-history/<int:qr_id>", methods=["GET"])
@admin_required
def get_scan_history_by_qr(qr_id):
    manufacturer_id = _manufacturer_id()
    qr = _owned_qrs(manufacturer_id).filter(QRCode.id == qr_id).first()
    if not qr:
        return jsonify({"success": False, "error": "QR code not found"}), 404
    logs = ScanLog.query.filter_by(qr_id=qr_id).order_by(ScanLog.scanned_at.desc()).all()
    return jsonify({"success": True, "data": [_serialize_log(log) for log in logs]}), 200
