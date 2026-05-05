from app import db
from datetime import datetime

class ScanLog(db.Model):
    __tablename__ = "scan_logs"

    id = db.Column(db.Integer, primary_key=True)

    qr_code_id = db.Column(
        db.Integer,
        db.ForeignKey("qrcodes.id"),
        nullable=False
    )

    timestamp = db.Column(
        db.DateTime,
        default=datetime.utcnow,
        nullable=False
    )

    ip_address = db.Column(db.String(45), nullable=False)