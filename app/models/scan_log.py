from app import db
from datetime import datetime


class ScanLog(db.Model):
    __tablename__ = "scan_logs"

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    # Exact QR code scanned
    qr_id = db.Column(
        db.Integer,
        db.ForeignKey("qrcodes.id"),
        nullable=True
    )

    # Related batch
    batch_id = db.Column(
        db.Integer,
        db.ForeignKey("batches.id"),
        nullable=False
    )

    # QR verification result:
    # authentic, cloned, tampered, expired, not_found
    status = db.Column(
        db.String(50),
        nullable=False
    )

    # QR signature used during scan
    signature = db.Column(
        db.String(255),
        nullable=False
    )

    # Whether QR passed signature validation
    is_valid = db.Column(
        db.Boolean,
        default=False,
        nullable=False
    )

    # Scan count at the time of scan
    scan_count = db.Column(
        db.Integer,
        default=1
    )

    # Scan timestamp
    scanned_at = db.Column(
        db.DateTime,
        default=datetime.utcnow,
        nullable=False
    )

    # Request metadata
    ip_address = db.Column(
        db.String(45)
    )

    user_agent = db.Column(
        db.String(255)
    )

    def __repr__(self):
        return (
            f"<ScanLog id={self.id} "
            f"qr_id={self.qr_id} "
            f"batch_id={self.batch_id} "
            f"status={self.status}>"
        )