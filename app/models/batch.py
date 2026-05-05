from app import db
from datetime import datetime


class Batch(db.Model):
    __tablename__ = "batches"

    id = db.Column(db.Integer, primary_key=True)

    batch_number = db.Column(db.String(100), unique=True, nullable=False)

    medicine_id = db.Column(
        db.Integer,
        db.ForeignKey("medicines.id"),
        nullable=False
    )

    manufacture_date = db.Column(db.DateTime, nullable=False)
    expiry_date = db.Column(db.DateTime, nullable=False)

    quantity = db.Column(db.Integer, nullable=False)

    created_at = db.Column(db.DateTime, default=datetime.utcnow)