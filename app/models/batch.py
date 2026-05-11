from app import db
from datetime import datetime


class Batch(db.Model):
    __tablename__ = "batches"

    id = db.Column(db.Integer, primary_key=True)

    batch_number = db.Column(db.String(100), unique=True, nullable=False)

    # 🔗 Link to Medicine (already correct)
    medicine_id = db.Column(
        db.Integer,
        db.ForeignKey("medicines.id"),
        nullable=False
    )

    # 🔗 ADD THIS (CRITICAL FIX)
    manufacturer_id = db.Column(
        db.Integer,
        db.ForeignKey("manufacturers.id"),
        nullable=False
    )

    manufacture_date = db.Column(db.DateTime, nullable=False)
    expiry_date = db.Column(db.DateTime, nullable=False)

    quantity = db.Column(db.Integer, nullable=False)

    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f"<Batch id={self.id} batch_number={self.batch_number}>"