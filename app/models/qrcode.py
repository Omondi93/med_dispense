from datetime import datetime
from app import db

class QRCode(db.Model):
    __tablename__ = "qrcodes"

    id = db.Column(db.Integer, primary_key=True)

    # Optional: if you still want tracking beyond signature
    serial_number = db.Column(
        db.String(255),
        unique=True,
        nullable=True,   # make optional unless you're actively using it
        index=True
    )

    # 🔐 Core anti-counterfeit field (must be unique)
    signature = db.Column(
        db.String(128),
        unique=True,      # IMPORTANT for Day 16
        nullable=False,
        index=True
    )

    # 📊 Clone detection
    scan_count = db.Column(
        db.Integer,
        default=0,
        nullable=False
    )

    is_flagged = db.Column(
        db.Boolean,
        default=False,
        nullable=False
    )

    # 🏷 Link to batch
    batch_id = db.Column(
        db.Integer,
        db.ForeignKey("batches.id"),
        nullable=False
    )

    # 🧾 Optional audit/debug
    payload = db.Column(db.Text)

    created_at = db.Column(
        db.DateTime,
        default=datetime.utcnow,
        nullable=False
    )

    # 🔗 Relationships
    scan_logs = db.relationship("ScanLog", backref="qrcode", lazy=True)

    def __repr__(self):
        return f"<QRCode id={self.id} batch={self.batch_id} scans={self.scan_count}>"