from datetime import datetime
from app import db


class MedicinePackage(db.Model):
    """A traceable physical package containing a quantity from a production batch."""
    __tablename__ = "medicine_packages"

    id = db.Column(db.Integer, primary_key=True)
    serial_number = db.Column(db.String(64), unique=True, nullable=False, index=True)
    batch_id = db.Column(db.Integer, db.ForeignKey("batches.id"), nullable=False, index=True)
    parent_package_id = db.Column(db.Integer, db.ForeignKey("medicine_packages.id"), nullable=True, index=True)
    qr_code_id = db.Column(db.Integer, db.ForeignKey("qrcodes.id"), unique=True, nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    status = db.Column(db.String(20), nullable=False, default="active", index=True)  # active, split, recalled
    created_by = db.Column(db.Integer, db.ForeignKey("manufacturers.id"), nullable=False, index=True)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    batch = db.relationship("Batch", backref=db.backref("packages", lazy=True))
    parent = db.relationship("MedicinePackage", remote_side=[id], backref=db.backref("children", lazy=True))
    qr_code = db.relationship("QRCode")


class RepackagingEvent(db.Model):
    """Immutable audit record for a split operation."""
    __tablename__ = "repackaging_events"

    id = db.Column(db.Integer, primary_key=True)
    source_package_id = db.Column(db.Integer, db.ForeignKey("medicine_packages.id"), nullable=False, index=True)
    manufacturer_id = db.Column(db.Integer, db.ForeignKey("manufacturers.id"), nullable=False, index=True)
    source_quantity = db.Column(db.Integer, nullable=False)
    child_count = db.Column(db.Integer, nullable=False)
    notes = db.Column(db.String(500), nullable=True)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    source_package = db.relationship("MedicinePackage")
